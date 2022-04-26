
import os
import logging
from itertools import chain
from maya import cmds, OpenMayaUI
from maya.api import OpenMaya as om
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from . import px, base
from .. import commands, internal, ui, options as _opts

log = logging.getLogger("ragdoll")

try:
    long  # noqa
except NameError:
    # Python 3 compatibility
    long = int


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname)).replace("\\", "/")


def _get_all_solver_size(solvers):
    solver_size = dict()
    for solver in solvers:
        solver_id = int(solver["ragdollId"])
        solver_size[solver_id] = internal.compute_solver_size(solver)
    return solver_size


def _solver_ui_name_by_sizes(solver_sizes, solver):
    solver_id = int(solver["ragdollId"])
    solver_size = solver_sizes[solver_id]

    has_same_size = any(
        _id != solver_id and size == solver_size
        for _id, size in solver_sizes.items()
    )
    transform = solver.parent()
    return transform.shortest_path() if has_same_size else transform.name()


def _hex_exists(node_hex):
    node = cmdx.fromHex(node_hex)
    return node and node.exists


def _repeat_this(fn):
    cmd = 'python("import {0};{0}.{1}()")'.format(fn.__module__, fn.__name__)
    cmds.repeatLast(
        addCommand=cmd,
        addCommandLabel=fn.__name__
    )


class _Solver(object):
    def __init__(self, solver, size, ui_name, conn_list):
        assert isinstance(solver, str), "Must be hex(str)"
        # It seems to be that, in Maya 2018, PySide2 is not able to
        # handle/passing cmdx.Node object as item data in model.
        # Maya crashes instantly if you do so.
        # Hence here we can only keep the hash code (hex string) of
        # the Node so the Qt model won't panic.
        self.solver = solver
        self.size = size
        self.ui_name = ui_name
        self.conn_list = conn_list

    @property
    def has_bad_conn(self):
        return any(c.is_bad for c in self.conn_list)


class _Connection(object):
    def __init__(self, marker, dest, level, natural, icon_m, icon_d,
                 dot_color, channel, is_bad):
        assert isinstance(marker, str), "Must be hex(str)"
        assert isinstance(dest, str) or dest is None, "Must be hex(str) or None"
        self.marker = marker
        self.dest = dest
        self.level = level
        self.natural = natural
        self.icon_m = icon_m
        self.icon_d = icon_d
        self.dot_color = dot_color
        self.channel = channel
        self.is_bad = is_bad


_kAnimCurve = int(om.MFn.kAnimCurve)
_kConstraint = int(om.MFn.kConstraint)
_kPairBlend = int(om.MFn.kPairBlend)
# channel status color
_ChClear = "#404040"
_ChNonKeyable = "#6A6A6A"
_ChHasKey = "#DD727A"
_ChLocked = "#5C6874"
_ChConstrained = "#94B9FF"
_ChPairBlended = "#9AE345"
_ChHasConnection = "#F1D832"
_IKDriven = "#C800C8"


def _destination_status(node):
    status = dict()
    status["IK"] = _is_part_of_IK(node) if node.type() == "joint" else False

    for at in {"t", "r"}:
        for ax in {"x", "y", "z"}:
            ch = at + ax

            if status["IK"]:
                status[ch] = _IKDriven
                continue  # non of the rest matter..

            if node[ch].locked:
                status[ch] = _ChLocked
            elif node[ch].connected or node[at].connected:
                i = node[ch].input() or node[at].input()
                if i.isA(_kAnimCurve):
                    status[ch] = _ChHasKey
                elif i.isA(_kConstraint):
                    status[ch] = _ChConstrained
                elif i.isA(_kPairBlend):
                    status[ch] = _ChPairBlended
                else:
                    status[ch] = _ChHasConnection
            elif not node[ch].keyable:
                status[ch] = _ChNonKeyable
            else:
                status[ch] = _ChClear

    return status


def _is_part_of_IK(joint, max_depth=3):
    depth = 0
    ik_found = False
    while depth < max_depth:
        down = joint["scale"].output()
        if down and down.type() == "joint":
            depth += 1
            joint = down
            continue

        down = joint["tx"].output()
        if down and down.type() == "ikEffector":
            ik_found = True

        break

    return ik_found


class _Scene(object):

    def __init__(self):
        self._solvers = None
        self._markers = None
        self._destinations = None
        self._dest_status = None
        self._bad_retarget = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot compare with type %r" % type(other))
        return self.solvers == other.solvers \
            and self.markers == other.markers \
            and self.destinations == other.destinations \
            and self.dest_status == other.dest_status \
            and self.bad_retarget == other.bad_retarget

    def __ne__(self, other):  # for '!=' in py2
        return not self.__eq__(other)

    def _iter_markers(self, solver):
        for entity in [el.input() for el in solver["inputStart"]]:
            if entity is None:
                continue

            if entity.isA("rdMarker"):
                yield entity

            elif entity.isA("rdGroup"):
                for other in [el.input() for el in entity["inputStart"]]:
                    if other is not None:
                        yield other

            elif entity.isA("rdSolver"):
                for e in self._iter_markers(entity):
                    yield e

    @property
    def solvers(self):
        if self._solvers is None:
            self._solvers = {
                solver: set(self._iter_markers(solver))
                for solver in cmdx.ls(type="rdSolver")
                if solver["startState"].connection() is None
                # unlinked solvers, a.k.a. primary solvers
            }
        return self._solvers

    @property
    def markers(self):
        if self._markers is None:
            self._markers = {
                marker: {
                    "id": int(marker["ragdollId"]),
                    "parent": int(marker["parentMarker"]),
                    "shape": int(marker["shapeType"]),
                    "color": tuple(marker["color"].asVector()),
                    "hash": marker.hex,
                }
                for marker in chain(*self.solvers.values())
            }
        return self._markers

    @property
    def destinations(self):
        if self._destinations is None:
            self._destinations = {
                marker: set(
                    dest for dest in filter(None, (
                        p.input() for p in marker["destinationTransforms"]
                    ))
                )
                for marker in self.markers.keys()
            }
        return self._destinations

    @property
    def dest_status(self):
        if self._dest_status is None:
            self._dest_status = {
                dest.hex: _destination_status(dest)
                for dest in set(chain(*self.destinations.values()))
            }
        return self._dest_status

    @property
    def bad_retarget(self):
        if self._bad_retarget is None:
            self._bad_retarget = {
                marker.hex: {
                    dest.hex: self.is_bad_retarget(marker, dest)
                    for dest in destinations
                }
                for marker, destinations in self.destinations.items()
            }
        return self._bad_retarget

    def is_bad_retarget(self, marker, dest):
        """Checking common bad recording setup
        * Locked translate and rotate channels.
        * Constrained translate/rotate channels.
        * Any connection to translate/rotate channels that isn't
            an animation curve.
        * Locked rotate, but unlocked translate, with a
            Translate Motion = Locked, meaning no translation.
        * A joint being driven by IK.
        """
        s = self.dest_status.get(dest.hex) or _destination_status(dest)
        all_ch = {"tx", "ty", "tz", "rx", "ry", "rz"}

        if all(s[ch] == _ChLocked for ch in all_ch):
            return "Both translate and rotate channels are all being locked, " \
                   "cannot record."

        if any(s[ch] in {_ChConstrained, _ChPairBlended} for ch in all_ch):
            return "Some channel is being constrained or blended, may have " \
                   "unexpected recording result."

        if any(s[ch] == _ChHasConnection for ch in all_ch):
            return "Some channel is being connected, may have unexpected " \
                   "recording result."

        if s["IK"]:
            return "Destination is a joint within IK chain, recording will " \
                   "be incorrect."

        if marker["linearMotion"] == 0 \
                and all(s[ch] == _ChLocked for ch in {"rx", "ry", "rz"}) \
                and all(s[ch] != _ChLocked for ch in {"tx", "ty", "tz"}):
            return "Marker's translate motion has been set to 'Locked' but " \
                   "destination's rotation is locked."

    @internal.with_undo_chunk
    def add_connection(self, marker, dest, **kwargs):
        from .. import interactive

        opts = {"append": True}
        opts.update(kwargs)
        commands.retarget_marker(marker, dest, opts)

        if not opts["append"]:
            self.destinations[marker].clear()
            self.bad_retarget[marker.hex].clear()
            self._dest_status = None  # update this

        self.destinations[marker].add(dest)
        self.dest_status[dest.hex] = _destination_status(dest)
        self.bad_retarget[marker.hex][dest.hex] = \
            self.is_bad_retarget(marker, dest)

        # save optionVar
        _opts.write("markersAppendTarget", opts["append"])
        # trigger Maya viewport update
        cmds.dgdirty(marker.shortest_path())
        # register command to repeat
        _repeat_this(interactive.retarget_marker)

    @internal.with_undo_chunk
    def del_connection(self, markers):
        from .. import interactive

        for marker in markers:
            commands.untarget_marker(marker)
            self.destinations[marker].clear()
            self.bad_retarget[marker.hex].clear()
            self._dest_status = None  # update this

            # trigger Maya viewport update
            cmds.dgdirty(marker.shortest_path())
        # register command to repeat
        _repeat_this(interactive.untarget_marker)

    def iter_connection(self):
        """Hierarchically iterate solver, marker, destination

        Returns:
            An iterator yields tuple of (solver, level, marker, destination).
            The solver and marker are cmdx.Node type, level is int, the
            destination is cmdx.Node or None if marker has no destination set.

        """
        data = self.markers
        children_by_id = {
            d["id"]: [m for m, _ in data.items() if _["parent"] == d["id"]]
            for d in chain(data.values(), [{"id": -1}])
        }

        def list_children(parent_id, lvl):
            return [(m, lvl) for m in children_by_id[parent_id]]

        def walk_hierarchy(markers_):  # depth first
            root_markers = [(m, 0) for m in children_by_id[-1] if m in markers_]
            visiting_list = root_markers
            while visiting_list:
                visited, lvl = visiting_list[0]

                id_ = int(visited["ragdollId"])
                pa_ = int(visited["parentMarker"])
                _child_num = len(children_by_id[id_])
                _sibling_num = len(children_by_id[pa_])
                _retain_level = _sibling_num <= 1 and _child_num <= 1

                next_lvl = lvl if _retain_level else (lvl + 1)
                children = list_children(id_, next_lvl)
                visiting_list = children + visiting_list[1:]

                yield visited, lvl

        for solver, markers in self.solvers.items():
            for marker_node, level in walk_hierarchy(markers):
                destinations = self.destinations[marker_node]
                if destinations:
                    for dest_node in destinations:
                        yield solver, level, marker_node, dest_node
                else:
                    yield solver, level, marker_node, None


class MarkerTreeModel(base.BaseItemModel):
    NodeRole = QtCore.Qt.UserRole + 10
    LevelRole = QtCore.Qt.UserRole + 11
    NameSortingRole = QtCore.Qt.UserRole + 12
    NaturalSortingRole = QtCore.Qt.UserRole + 13
    ColorDotRole = QtCore.Qt.UserRole + 14
    DestChannelRole = QtCore.Qt.UserRole + 15
    BadRetargetRole = QtCore.Qt.UserRole + 16

    Headers = [
        "Name",
        "Destination",
        "Connect",
    ]

    def __init__(self, *args, **kwargs):
        super(MarkerTreeModel, self).__init__(*args, **kwargs)
        self.flipped = False
        self._scene = None
        self._internal = []  # type: list[_Solver]
        self._pixmap_list = {
            "rdSolver": QtGui.QPixmap(_resource("icons", "solver.png")),
            "rdMarker_0": QtGui.QPixmap(_resource("icons", "box.png")),
            "rdMarker_1": QtGui.QPixmap(_resource("icons", "sphere.png")),
            "rdMarker_2": QtGui.QPixmap(_resource("icons", "rigid.png")),
            "rdMarker_4": QtGui.QPixmap(_resource("icons", "mesh.png")),
        }
        self._maya_node_icons = dict()
        self._empty_dst_color = QtGui.QColor("#6C6C6C")
        self._empty_dst_icon = QtGui.QIcon(_resource("icons", "empty.png"))
        self._bad_conn_icon = QtGui.QIcon(_resource("icons", "warning.png"))

    def flags(self, index):
        if index.column() == 2 \
                or (not index.parent().isValid() and index.column() == 1):
            return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """
        Args:
            index (QtCore.QModelIndex):
            role (int):
        Returns:
            typing.Any
        """
        if not index.isValid():
            return False

        if not index.parent().isValid():
            if role == self.BadRetargetRole:
                solver_index = index.row()
                solver_repr = self._internal[solver_index]
                return solver_repr.has_bad_conn
            return super(MarkerTreeModel, self).data(index, role)

        solver_index = index.parent().row()
        solver_repr = self._internal[solver_index]
        conn = solver_repr.conn_list[index.row()]  # type: _Connection

        if role == self.BadRetargetRole:
            return conn.is_bad

        column = index.column()
        if column == 2:
            if role == self.DestChannelRole:
                return conn.channel
            if role == QtCore.Qt.DecorationRole and conn.is_bad:
                return self._bad_conn_icon
            return

        column = not column if self.flipped else column
        key = ["marker", "dest"][column]

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            # todo: When user press DEL/Backspace while mouse in view,
            #   current selected node in Maya gets deleted and since the
            #   mouse is in view, no enterEvent will trigger auto refresh
            #   hence, data corrupted.
            #   We either block the DEL/Backspace in widget, or we trigger
            #   update when data missing.
            if key == "marker":
                return cmdx.fromHex(conn.marker).name()
            if key == "dest":
                return cmdx.fromHex(conn.dest).name() if conn.dest else "Empty"

        if role == QtCore.Qt.ForegroundRole:
            if key == "dest" and not conn.dest:
                return self._empty_dst_color
            else:
                return

        if role == QtCore.Qt.DecorationRole:
            if key == "marker":
                return conn.icon_m
            if key == "dest":
                return conn.icon_d or self._empty_dst_icon

        if role == self.NodeRole:
            if key == "marker":
                return conn.marker
            if key == "dest":
                return conn.dest

        if role == self.LevelRole:
            if key == "marker":
                return conn.level
            if key == "dest":
                return

        if role == self.NameSortingRole:  # node path affects alt row coloring
            if key == "marker":
                return cmdx.fromHex(conn.marker).name()
            if key == "dest":
                return cmdx.fromHex(conn.dest).name() if conn.dest else ""

        if role == self.NaturalSortingRole:
            if key == "marker":
                return conn.natural
            if key == "dest":
                return

        if role == self.ColorDotRole:
            if key == "marker":
                return conn.dot_color
            if key == "dest":
                return

    @property
    def scene(self):
        return self._scene

    def refresh(self, scene=None):
        scene = scene or _Scene()
        self.reset()

        with internal.Timer() as t:
            self._build_internal_model(scene)
        log.debug("Internal data model built in total %.2fms" % t.ms)

        for solver_repr in self._internal:
            solver_item = self._mk_solver_item(solver_repr)
            self.appendRow(solver_item)
            solver_item.setColumnCount(len(self.Headers))
            solver_item.setRowCount(len(solver_repr.conn_list))

    def _mk_solver_item(self, solver_repr):
        item = QtGui.QStandardItem()
        item.setText("[%d] %s" % (solver_repr.size, solver_repr.ui_name))
        item.setIcon(self._pixmap_list["rdSolver"])
        item.setData(solver_repr.solver, self.NodeRole)
        return item

    def _build_internal_model(self, scene):
        # reset
        del self._internal[:]
        self._scene = scene

        solver_sizes = _get_all_solver_size(scene.solvers)

        with internal.Timer() as t:
            conns = list(scene.iter_connection())
        log.debug("Connection iterated (%d) in %.2fms" % (len(conns), t.ms))

        with internal.Timer() as t:
            the_solver = None
            for _i, (solver, level, marker, dest) in enumerate(conns):
                if the_solver is None or solver.hex != the_solver.solver:
                    the_solver = _Solver(
                        solver=solver.hex,
                        size=solver_sizes[int(solver["ragdollId"])],
                        ui_name=_solver_ui_name_by_sizes(solver_sizes, solver),
                        conn_list=[],
                    )
                    self._internal.append(the_solver)

                conn = self._mk_conn(marker, dest, level, _i)
                the_solver.conn_list.append(conn)
        log.debug("Scene iterated in %.2fms" % t.ms)

    def _mk_conn(self, marker, dest, level, natural):
        dest_hex = dest.hex if dest else None

        # marker icon/color
        _pix = self._pixmap_list["rdMarker_%d" % int(marker["shapeType"])]
        icon_m = QtGui.QIcon(_pix)
        dot_color = QtGui.QColor.fromRgbF(*marker["color"]).lighter()

        # dest icon
        icon_d = self._maya_node_icon(dest) if dest else None

        conn = _Connection(
            marker=marker.hex,
            dest=dest_hex,
            icon_m=icon_m,
            icon_d=icon_d,
            dot_color=dot_color,
            level=level,
            natural=natural,
            channel=self._scene.dest_status.get(dest_hex),
            is_bad=self._scene.bad_retarget[marker.hex].get(dest_hex),
        )
        return conn

    def _maya_node_icon(self, node):
        if node.isA(cmdx.kDagNode):
            node = node.shape() or node
        typ = node.type()
        if typ not in self._maya_node_icons:
            self._maya_node_icons[typ] = QtGui.QIcon(":/%s" % typ)
        return self._maya_node_icons[typ]

    def find_solver(self, solver):
        for i, _s in enumerate(self._internal):
            if _s.solver == solver.hex:
                return self.index(i, 0)

    def find_markers(self, marker, solver_index=None):
        if not solver_index:
            solver = None
            other = marker["startState"].output()
            if other.isA("rdSolver"):
                solver = other
            elif other.isA("rdGroup"):
                other = other["startState"].output(type="rdSolver")
                if other:
                    solver = other

            if solver:
                solver_index = self.find_solver(solver)
            else:
                return

        _s = self._internal[solver_index.row()]
        _matched = False
        for j, _c in enumerate(_s.conn_list):
            if _c.marker == marker.hex:
                _matched = True
                yield self.index(j, int(self.flipped), solver_index)
            if _matched and _c.marker != marker.hex:
                break

    def find_destinations(self, dest):
        for i, _s in enumerate(self._internal):
            solver_index = self.index(i, 0)
            for j, _c in enumerate(_s.conn_list):
                if _c.dest == dest.hex:
                    yield self.index(j, int(not self.flipped), solver_index)

    def add_connection(self, marker, dest, append=False):
        self._scene.add_connection(marker, dest, append=append)

        marker_index = next(self.find_markers(marker))
        solver_index = marker_index.parent()

        def get_dest_index(conn_row):
            dest_col = 0 if self.flipped else 1
            dest_index = self.index(conn_row, dest_col, solver_index)
            return dest_index

        _r = marker_index.row()
        _s = self._internal[solver_index.row()]
        consumed = False
        remove = []
        ref = None
        row = j = 0
        for j, _c in enumerate(_s.conn_list[_r:]):
            if _c.marker != marker.hex:
                consumed = True
                j -= 1
                break

            ref = _c
            row = _r + j
            if _c.dest is None:
                # plug dest into connection
                _c.dest = dest.hex
                _c.icon_d = self._maya_node_icon(dest)
                break

            elif _c.dest == dest.hex:
                # already in model (but should not happen in current imp.)
                break

            elif not append:
                # replace dest
                remove.append(_c)
                continue

        if consumed:
            solver_item = self.itemFromIndex(solver_index)

            if append:
                # new connection
                # get level, natural from other connection to make a new one
                new_conn = self._mk_conn(marker, dest, ref.level, ref.natural)
                _s.conn_list.insert(row, new_conn)
                solver_item.setRowCount(solver_item.rowCount() + 1)
            else:
                ref.dest = dest.hex
                ref.icon_d = self._maya_node_icon(dest)
                for _c in remove[:-1]:
                    _s.conn_list.remove(_c)
                solver_item.setRowCount(solver_item.rowCount() - j)
                row -= j

        return get_dest_index(row)

    def del_connection(self, markers):
        self._scene.del_connection(markers)

        marker_indexes = []
        for marker in markers:
            marker_index = next(self.find_markers(marker))
            solver_index = marker_index.parent()
            marker_indexes.append(marker_index)

            _r = marker_index.row()
            _s = self._internal[solver_index.row()]
            remove = []
            j = 0
            for j, _c in enumerate(_s.conn_list[_r:]):
                if _c.marker != marker.hex:
                    j -= 1
                    break

                if _c.dest is None:
                    pass  # already been deleted, but should not happen

                else:
                    _c.dest = None
                    _c.icon_d = None
                    remove.append(_c)

            if j == 0:
                continue

            for _c in remove[:-1]:
                _s.conn_list.remove(_c)
            solver_item = self.itemFromIndex(solver_index)
            solver_item.setRowCount(solver_item.rowCount() - j)

        return marker_indexes


class MarkerIndentDelegate(QtWidgets.QStyledItemDelegate):
    HierarchyIndent = 28
    ColorDotSize = 20
    ChannelIndicatorWidth = 84
    SelectionBorder = 2

    def __init__(self, parent):
        super(MarkerIndentDelegate, self).__init__(parent=parent)
        self._enabled = False

    def set_enabled(self, value):
        self._enabled = value

    def _compute(self, index):
        dot_color = index.data(MarkerTreeModel.ColorDotRole)
        dot_size = self.ColorDotSize if dot_color else 0
        level = 0
        if self._enabled and index.column() == 0:
            level = index.data(MarkerTreeModel.LevelRole) or level
        offset = self.HierarchyIndent * level + dot_size
        return offset, dot_color

    def paint(self, painter, option, index):
        offset, dot_color = self._compute(index)

        if option.state & QtWidgets.QStyle.State_Selected:
            # draw selection highlight
            #   we cannot use stylesheet to achieve this due to the offset for
            #   color-dot, could not get a clean border from original paint().
            b = self.SelectionBorder
            rect = QtCore.QRect(option.rect)
            rect.adjust(b, b, -b, -b)  # shrink a bit for border
            path = QtGui.QPainterPath()
            path.addRoundedRect(rect, 12, 12)
            painter.save()
            painter.setRenderHint(painter.Antialiasing)
            painter.setPen(QtCore.Qt.NoPen)
            painter.fillPath(path, QtGui.QColor("#515D6A"))

        if index.column() == 2:
            option.decorationPosition = option.Right  # warning sign

        if dot_color:
            offset -= self.ColorDotSize
            painter.translate(self.ColorDotSize, 0)

        if offset:
            # paint the gap after offset
            style_proxy = option.widget.style().proxy()
            style_proxy.drawPrimitive(
                QtWidgets.QStyle.PE_PanelItemViewItem,
                option,
                painter,
                option.widget
            )
            # offset item
            option.rect.adjust(offset, 0, 0, 0)

        super(MarkerIndentDelegate, self).paint(painter, option, index)

        if dot_color:
            painter.translate(-self.ColorDotSize, 0)
            dot_size = self.ColorDotSize
            pos_x = option.rect.x() + 6
            pos_y = option.rect.center().y() - int(dot_size / 2) + 1
            border = 2
            inner = dot_size - border * 2
            painter.save()
            painter.setRenderHint(painter.Antialiasing)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor("#404040"))
            painter.drawEllipse(pos_x, pos_y, dot_size, dot_size)
            painter.setBrush(dot_color)
            painter.drawEllipse(pos_x + border, pos_y + border, inner, inner)
            painter.restore()

        cell_colors = index.data(MarkerTreeModel.DestChannelRole)
        if cell_colors:
            # channels
            _bg_color = "#2B2B2B"
            border = 2
            cell_gap = 2
            cell_w = 11
            cell_h = 4
            _base_w = border * 2 + cell_w * 2 + border
            _base_h = border * 2 + cell_h * 3 + cell_gap * 2
            _base_x = option.rect.x() + 8
            _base_y = option.rect.center().y() - int(_base_h / 2) + 1
            painter.save()
            painter.setRenderHint(painter.Antialiasing, False)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(_bg_color))
            painter.drawRect(QtCore.QRect(_base_x, _base_y, _base_w, _base_h))
            _base_x += border
            _base_y += border
            for at in ("t", "r"):
                _y = _base_y
                for ax in ("x", "y", "z"):
                    color = cell_colors.get(at + ax)
                    if color == _ChNonKeyable:
                        rect = QtCore.QRect(_base_x, _y, cell_w - 1, cell_h - 1)
                        painter.setPen(QtGui.QColor(color))
                        painter.setBrush(QtGui.QColor(_bg_color))
                    else:
                        rect = QtCore.QRect(_base_x, _y, cell_w, cell_h)
                        painter.setPen(QtCore.Qt.NoPen)
                        painter.setBrush(QtGui.QColor(color or _bg_color))
                    painter.drawRect(rect)
                    _y += cell_h + cell_gap
                _base_x += cell_w + border
            painter.restore()

    def sizeHint(self, option, index):
        size = super(MarkerIndentDelegate, self).sizeHint(option, index)
        offset, _ = self._compute(index)
        if offset:
            size.setWidth(size.width() + offset)
        return size


class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    if base.is_filtering_recursible():
        pass
    else:
        # Patch future function
        setRecursiveFilteringEnabled = (lambda *args: None)

        def filterAcceptsRow(self, source_row, source_parent):
            """
            Args:
                source_row (int):
                source_parent (QtCore.QModelIndex):
            Returns:
                bool
            """
            if source_parent.isValid():
                return super(SortFilterProxyModel, self).filterAcceptsRow(
                    source_row, source_parent)
            else:
                return True  # always accept solver item


class MarkerTreeView(QtWidgets.QTreeView):
    leave = QtCore.Signal()
    released = QtCore.Signal()
    menu_requested = QtCore.Signal(QtCore.QPoint)  # menu on right mouse press

    def drawRow(self, painter, options, index):
        """
        Args:
            painter (QtGui.QPainter):
            options (QtWidgets.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        is_bad = index.data(MarkerTreeModel.BadRetargetRole)
        if is_bad and index.parent().isValid():
            painter.fillRect(options.rect, QtGui.QColor("#5b3138"))
        elif is_bad:
            painter.fillRect(options.rect, QtGui.QColor("#4b373a"))
        super(MarkerTreeView, self).drawRow(painter, options, index)

    def leaveEvent(self, event):
        super(MarkerTreeView, self).leaveEvent(event)
        self.leave.emit()

    def mousePressEvent(self, event):
        position = self.mapFromGlobal(event.globalPos())
        if event.button() is QtCore.Qt.MouseButton.RightButton:
            self.menu_requested.emit(position)
        else:
            super(MarkerTreeView, self).mousePressEvent(event)
            index = self.indexAt(position)
            if not index.isValid():
                self.clearSelection()

    def mouseReleaseEvent(self, event):
        super(MarkerTreeView, self).mouseReleaseEvent(event)
        self.released.emit()


class DestStageButton(QtWidgets.QPushButton):

    def __init__(self, parent=None):
        super(DestStageButton, self).__init__(parent=parent)

        _pixmap = QtGui.QPixmap(_resource("icons", "marker_group.png"))
        _pixmap = _pixmap.scaledToWidth(px(16), QtCore.Qt.SmoothTransformation)
        icon = QtWidgets.QLabel()
        icon.setPixmap(_pixmap)

        text = QtWidgets.QLabel("Retarget To..")

        node_icon = QtWidgets.QLabel()
        node_icon.setFixedWidth(px(16))
        node_icon.setPixmap(QtGui.QPixmap(""))
        node_name = QtWidgets.QLineEdit()
        node_name.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        node_name.setReadOnly(True)
        node_name.setPlaceholderText("Select one marker and one destination..")
        node_name.setStyleSheet("""
        QLineEdit {background: transparent; border: none;}
        """)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(px(20), 0, px(20), 0)
        layout.addWidget(icon)
        layout.addWidget(text)
        layout.addSpacing(px(2))
        layout.addWidget(node_icon)
        layout.addWidget(node_name)
        layout.addSpacing(px(4))

        self.node_icon = node_icon
        self.node_name = node_name


class RetargetButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()
    appended = QtCore.Signal()

    def __init__(self, parent=None):
        super(RetargetButton, self).__init__(parent=parent)

        dest_stage = DestStageButton()
        dest_actions = QtWidgets.QPushButton()  # todo: change to 3 dots icon
        dest_action_menu = QtWidgets.QMenu(self)
        append_action = QtWidgets.QAction(
            QtGui.QIcon(_resource("icons", "children.png")),
            "Append",
            dest_action_menu
        )
        dest_action_menu.addAction(append_action)
        dest_actions.setMenu(dest_action_menu)
        dest_actions.setFixedWidth(px(15))

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(dest_stage)
        layout.addWidget(dest_actions)

        dest_stage.clicked.connect(self.clicked)
        append_action.triggered.connect(self.appended)

        self.dest_stage = dest_stage

    def display_dest(self, node):
        self.dest_stage.node_name.setText(node.shortest_path() if node else "")
        if node is None:
            self.dest_stage.node_icon.pixmap().load("")
        else:
            if node.isA(cmdx.kDagNode):
                node = node.shape() or node
            self.dest_stage.node_icon.setPixmap(
                QtGui.QPixmap(":/%s" % node.type())
                .scaledToWidth(px(16), QtCore.Qt.SmoothTransformation)
            )


class MarkerTreeWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MarkerTreeWidget, self).__init__(parent=parent)

        view = MarkerTreeView()
        model = MarkerTreeModel()
        proxy = SortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        proxy.setRecursiveFilteringEnabled(True)
        proxy.setFilterCaseSensitivity(QtCore.Qt.CaseSensitive)
        view.setModel(proxy)

        view.setTextElideMode(QtCore.Qt.ElideLeft)
        view.setSelectionMode(view.ExtendedSelection)
        view.setSelectionBehavior(view.SelectItems)
        view.setHeaderHidden(True)

        indent_delegate = MarkerIndentDelegate(self)
        view.setItemDelegate(indent_delegate)

        action_bar = QtWidgets.QWidget()
        action_bar.setFixedHeight(px(34))

        retarget_btn = RetargetButton()
        untarget_btn = QtWidgets.QPushButton(
            QtGui.QIcon(_resource("icons", "disconnect.png")),
            "Untarget",
        )
        untarget_btn.setFixedWidth(px(182))

        retarget_btn.setEnabled(False)
        untarget_btn.setEnabled(False)

        layout = QtWidgets.QHBoxLayout(action_bar)
        layout.setContentsMargins(px(5), px(5), px(5), px(5))
        layout.addWidget(retarget_btn)
        layout.addWidget(untarget_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)
        layout.addWidget(action_bar)
        layout.setSpacing(px(2))

        view.released.connect(self.on_view_released)
        retarget_btn.appended.connect(self.on_retarget_appended)
        retarget_btn.clicked.connect(self.on_retarget_clicked)
        untarget_btn.clicked.connect(self.on_untarget_clicked)

        self._view = view
        self._proxy = proxy
        self._model = model
        self._delegate = indent_delegate
        self._retarget_btn = retarget_btn
        self._untarget_btn = untarget_btn
        self._staged_marker = None
        self._staged_dest = None

        self.setup_header(False)

    def setup_header(self, flip):
        header = self._view.header()
        marker_col = int(flip)
        dest_col = int(not flip)
        header.setSectionResizeMode(marker_col, header.ResizeToContents)
        header.setSectionResizeMode(dest_col, header.Stretch)
        header.setSectionResizeMode(2, header.Fixed)
        header.setStretchLastSection(False)
        header.resizeSection(2, MarkerIndentDelegate.ChannelIndicatorWidth)

    @property
    def view(self):
        return self._view

    @property
    def proxy(self):
        return self._proxy

    @property
    def model(self):
        return self._model

    def select(self, index):
        self._view.scrollTo(index, self._view.EnsureVisible)
        self._view.selectionModel().select(
            index, QtCore.QItemSelectionModel.Select
        )

    def refresh(self, scene=None):
        self._model.refresh(scene)
        self._view.expandToDepth(1)
        self.sync_maya_selection()
        self.update_actions()

    def on_view_released(self):
        nodes = []
        for index in self._view.selectedIndexes():
            if not index.parent().isValid():
                index = self._proxy.index(index.row(), 0)
            node = self._proxy.data(index, MarkerTreeModel.NodeRole)
            if node is not None and node not in nodes:
                nodes.append(cmdx.fromHex(node))

        cmds.select(nodes, replace=True)

    def on_selection_changed(self):
        self.sync_maya_selection()
        self.update_actions()

    def sync_maya_selection(self):
        selection = cmdx.ls(sl=True)
        selected_solver = [n for n in selection if n.isA("rdSolver")]
        selected_marker = [n for n in selection if n.isA("rdMarker")]
        selected_dest = [n for n in selection if n.isA(cmdx.kTransform)]

        # sync selection

        new_selection = [
            self._proxy.mapFromSource(self._model.find_solver(s))
            for s in selected_solver
        ] + [
            self._proxy.mapFromSource(m_)
            for m in selected_marker
            for m_ in self._model.find_markers(m)
        ] + [
            self._proxy.mapFromSource(d_)
            for d in selected_dest
            for d_ in self._model.find_destinations(d)
        ]

        if new_selection and set(self._view.selectedIndexes()) != new_selection:
            self._view.clearSelection()
            sele_model = self._view.selectionModel()
            for index in new_selection:
                sele_model.select(index, QtCore.QItemSelectionModel.Select)
            # try scroll to the index is in first column (align perspective)
            scroll_to = next(
                (i for i in reversed(new_selection) if i.column() == 0),
                new_selection[-1]
            )
            self._view.scrollTo(scroll_to, self._view.EnsureVisible)

        elif not new_selection:
            self._view.clearSelection()

    def update_actions(self):
        selection = dict()
        _seen = set()
        for index in self._view.selectedIndexes():
            if index.parent().isValid():
                node_hex = index.data(self._model.NodeRole)
                if node_hex in _seen:
                    continue
                _seen.add(node_hex)
                node = cmdx.fromHex(node_hex)
                if node and node.exists:
                    selection[index] = node

        selected_marker = [
            i for i, n in selection.items() if n.isA("rdMarker")
        ]
        selected_dest = [
            i for i, n in selection.items() if n.isA(cmdx.kTransform)
        ]

        # un-targeting
        self._untarget_btn.setEnabled(False)
        if len(selected_marker) and not selected_dest:
            dest_column = int(not selected_marker[0].column())
            if any(m.siblingAtColumn(dest_column).data(self._model.NodeRole)
                   for m in selected_marker):
                self._untarget_btn.setEnabled(True)

        # re-targeting
        marker = None
        dest = None

        if len(selected_marker) == 1:
            marker_index = selected_marker[0]
            marker = selection[marker_index]
            marker_dest = self._model.scene.destinations[marker]

            wild_dest = cmdx.ls(sl=True, type="transform")
            if len(wild_dest) == 1 and wild_dest[0] not in marker_dest:
                dest = wild_dest[0]

            self._retarget_btn.display_dest(dest)
            self._retarget_btn.setEnabled(bool(dest))

        else:
            self._retarget_btn.display_dest(None)
            self._retarget_btn.setEnabled(False)

        self._staged_marker = marker
        self._staged_dest = dest

    def on_retarget_appended(self):
        marker, dest = self._staged_marker, self._staged_dest
        updated = self._model.add_connection(marker, dest, append=True)
        self._view.clearSelection()
        self.select(self._proxy.mapFromSource(updated))
        self._proxy.invalidate()  # update sort/filter
        self.update_actions()

    def on_retarget_clicked(self):
        marker, dest = self._staged_marker, self._staged_dest
        updated = self._model.add_connection(marker, dest, append=False)
        self._view.clearSelection()
        self.select(self._proxy.mapFromSource(updated))
        self._proxy.invalidate()  # update sort/filter
        self.update_actions()

    def on_untarget_clicked(self):
        markers = []
        _seen = set()
        marker_column = int(self._model.flipped)
        dest_column = int(not marker_column)
        for index in self._view.selectedIndexes():
            if index.parent().isValid() and index.column() == marker_column:
                marker_hex = index.data(self._model.NodeRole)
                if marker_hex in _seen:
                    continue
                dest_index = index.siblingAtColumn(dest_column)
                if dest_index.data(self._model.NodeRole):
                    _seen.add(marker_hex)
                    node_hex = index.data(self._model.NodeRole)
                    markers.append(cmdx.fromHex(node_hex))

        marker_indexes = self._model.del_connection(markers)
        i = None
        self._view.clearSelection()
        for i in marker_indexes:
            i = self._proxy.mapFromSource(i)
            self._view.selectionModel().select(
                i, QtCore.QItemSelectionModel.Select
            )
        self._view.scrollTo(i, self._view.EnsureVisible)
        self._proxy.invalidate()  # update sort/filter
        self.update_actions()

    def flip(self, state):
        selected = [
            self._proxy.mapToSource(i) for i in self._view.selectedIndexes()
        ]

        self.setup_header(state)
        self._model.flipped = state
        self._proxy.invalidate()

        self._view.clearSelection()
        sele_model = self._view.selectionModel()
        index = None
        for index in selected:
            index = self._proxy.mapFromSource(index)
            if index.parent().isValid():
                index = index.siblingAtColumn(int(not index.column()))
            sele_model.select(index, sele_model.Select)
        if index:
            self._view.scrollTo(index, self._view.PositionAtCenter)

    def set_filter(self, text):
        self._proxy.setFilterRegExp(text)
        self._view.expandToDepth(1)
        self.sync_maya_selection()
        self.update_actions()

    def set_sort_by_name(self, ascending):
        self._delegate.set_enabled(False)
        self._proxy.setSortRole(MarkerTreeModel.NameSortingRole)
        if ascending:
            self._view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        else:
            self._view.sortByColumn(0, QtCore.Qt.DescendingOrder)

        selected = self._view.selectedIndexes()
        if selected:
            self._view.scrollTo(selected[-1], self._view.PositionAtCenter)

    def set_sort_by_hierarchy(self):
        self._delegate.set_enabled(True)
        self._proxy.setSortRole(MarkerTreeModel.NaturalSortingRole)
        self._view.sortByColumn(0, QtCore.Qt.AscendingOrder)

        selected = self._view.selectedIndexes()
        if selected:
            self._view.scrollTo(selected[-1], self._view.PositionAtCenter)


class SelectionScriptJob(QtCore.QObject):
    selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(SelectionScriptJob, self).__init__(parent=parent)
        self.setObjectName("ragdoll:retargetor-scriptJob")
        self.job_id = None

    def init(self):
        if self.job_id:
            return
        self.job_id = cmds.scriptJob(
            event=["SelectionChanged", self.selection_changed.emit],
            parent=self.objectName(),  # job killed on object destroyed
        )


class RetargetWidget(QtWidgets.QWidget):
    prompted = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(RetargetWidget, self).__init__(parent=parent)

        panels = {
            "TopBar": QtWidgets.QWidget(),
            "Markers": QtWidgets.QWidget(),
        }

        widgets = {
            "SearchBar": QtWidgets.QLineEdit(),
            "SearchType": _with_entered_exited_signals(base.ToggleButton)(),
            "SearchCase": _with_entered_exited_signals(base.ToggleButton)(),
            "MarkerView": MarkerTreeWidget(),
            "Sorting": _with_entered_exited_signals(base.StateRotateButton)(),
        }

        timers = {
            "OnSearched": QtCore.QTimer(self),
        }

        objects = {
            "ScriptJob": SelectionScriptJob(self),
        }

        panels["TopBar"].setObjectName("RetargetWidgetTop")

        timers["OnSearched"].setSingleShot(True)
        widgets["SearchBar"].setClearButtonEnabled(True)
        widgets["MarkerView"].view.setMouseTracking(True)  # for retarget warn

        def set_toggle(w, unchecked, checked):
            widgets[w].set_unchecked_icon(QtGui.QIcon(unchecked))
            widgets[w].set_checked_icon(QtGui.QIcon(checked))

        set_toggle("SearchType",
                   unchecked=_resource("icons", "parent.png"),
                   checked=_resource("icons", "children.png"))
        set_toggle("SearchCase",
                   unchecked=_resource("ui", "alpha-case-opac.svg"),
                   checked=_resource("ui", "alpha-case.svg"))

        # sort marker by name A -> Z as default
        widgets["Sorting"].add_state(
            "name_az", QtGui.QIcon(_resource("ui", "sort-alpha-down.svg"))
        )
        widgets["Sorting"].add_state(
            "name_za", QtGui.QIcon(_resource("ui", "sort-alpha-down-alt.svg"))
        )
        widgets["Sorting"].add_state(
            "hierarchy", QtGui.QIcon(_resource("ui", "list-nested.svg"))
        )
        # filtering with case sensitive enabled by default
        widgets["SearchCase"].setChecked(True)
        # marker oriented by default
        widgets["SearchBar"].setPlaceholderText("Find markers..")

        layout = QtWidgets.QHBoxLayout(panels["TopBar"])
        layout.setContentsMargins(12, 10, 12, 2)
        layout.setSpacing(6)
        layout.addWidget(widgets["Sorting"])
        layout.addWidget(widgets["SearchType"])
        layout.addWidget(widgets["SearchBar"])
        layout.addWidget(widgets["SearchCase"])

        layout = QtWidgets.QHBoxLayout(panels["Markers"])
        layout.setContentsMargins(0, 4, 0, 2)
        layout.addWidget(widgets["MarkerView"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(panels["TopBar"])
        layout.addWidget(panels["Markers"])

        def add_help(button, text):
            def on_entered():
                self.prompted.emit(text)

            def on_exited():
                self.prompted.emit("")

            button.entered.connect(on_entered)
            button.exited.connect(on_exited)

        add_help(widgets["SearchType"],
                 "Toggle to change the marker-destination list perspective.")
        add_help(widgets["SearchCase"],
                 "Toggle to change searching with case sensitive or not.")
        add_help(widgets["Sorting"],
                 "Change marker-destination list sorting order. Note that "
                 "hierarchy ordering doesn't work in destination perspective.")

        widgets["MarkerView"].view.entered.connect(self.on_view_item_entered)
        widgets["MarkerView"].view.leave.connect(lambda: self.prompted.emit(""))
        widgets["Sorting"].stateChanged.connect(self.on_sorting_clicked)
        widgets["SearchCase"].toggled.connect(self.on_search_case_toggled)
        widgets["SearchType"].toggled.connect(self.on_search_type_toggled)
        widgets["SearchBar"].textChanged.connect(self.on_searched_defer)
        timers["OnSearched"].timeout.connect(self.on_searched)
        objects["ScriptJob"].selection_changed.connect(
            widgets["MarkerView"].on_selection_changed
        )

        self._panels = panels
        self._widgets = widgets
        self._timers = timers
        self._objects = objects

        self.setStyleSheet(_scaled_stylesheet(stylesheet))

    def init(self):
        self._objects["ScriptJob"].init()
        self._widgets["MarkerView"].refresh()
        self._widgets["MarkerView"].set_sort_by_name(ascending=True)

    def on_view_item_entered(self, index):
        warn = index.data(MarkerTreeModel.BadRetargetRole) or " "
        self.prompted.emit(warn)

    def on_sorting_clicked(self, state):
        if state == "name_az":
            self._widgets["MarkerView"].set_sort_by_name(ascending=True)
        elif state == "name_za":
            self._widgets["MarkerView"].set_sort_by_name(ascending=False)
        else:
            self._widgets["MarkerView"].set_sort_by_hierarchy()

    def on_search_case_toggled(self, state):
        proxy = self._widgets["MarkerView"].proxy
        if state:
            proxy.setFilterCaseSensitivity(QtCore.Qt.CaseSensitive)
        else:
            proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def on_search_type_toggled(self, state):
        if state:
            self._widgets["SearchBar"].setPlaceholderText("Find destinations..")
            self._widgets["Sorting"].block("hierarchy")
            if self._widgets["Sorting"].state() == "hierarchy":
                self._widgets["Sorting"].set_state("name_az")
            self._widgets["MarkerView"].flip(True)
        else:
            self._widgets["SearchBar"].setPlaceholderText("Find markers..")
            self._widgets["Sorting"].unblock("hierarchy")
            self._widgets["MarkerView"].flip(False)

    def on_searched_defer(self):
        self._timers["OnSearched"].start(200)

    def on_searched(self):
        text = self._widgets["SearchBar"].text()
        widget = self._widgets["MarkerView"]
        widget.set_filter(text)

    def enterEvent(self, event):
        super(RetargetWidget, self).enterEvent(event)
        view = self._widgets["MarkerView"]
        model = view.model
        scene = _Scene()
        with internal.Timer() as t:
            outdated = model.scene != scene
        log.debug("Checking for update finished in %0.2fms" % t.ms)
        if outdated:
            view.refresh(scene)


def _with_entered_exited_signals(cls):
    class WidgetHoverFactory(cls):
        entered = QtCore.Signal()
        exited = QtCore.Signal()

        def enterEvent(self, event):
            self.entered.emit()
            return super(WidgetHoverFactory, self).enterEvent(event)

        def leaveEvent(self, event):
            self.exited.emit()
            return super(WidgetHoverFactory, self).leaveEvent(event)

    return WidgetHoverFactory


with open(_resource("ui", "style_retargetor.css")) as f:
    stylesheet = f.read()


def _scaled_stylesheet(style):
    """Replace any mention of <num>px with scaled version

    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.

    """

    output = []
    for line in style.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            key, value = line.rsplit(" ", 1)
            value = px(int(value[:-3]))
            line = "%s %dpx;" % (key, value)
        output += [line]
    result = "\n".join(output)
    result = result % dict(
        res=_resource().replace("\\", "/"),
        on_primary="#C8C8C8",
        background="#2B2B2B",
        background_alt="#323232",
        branch_down=_resource("ui", "caret-down-fill.svg"),
        branch_down_on=_resource("ui", "caret-down-fill-on.svg"),
        branch_right=_resource("ui", "caret-right-fill.svg"),
        branch_right_on=_resource("ui", "caret-right-fill-on.svg"),
        indicator_checked=_resource("ui", "square-check.svg"),
        indicator_unchecked=_resource("ui", "square.svg"),
    )
    return result


class RetargetWindow(ui.Options):

    def __init__(self, *args, **kwargs):
        super(RetargetWindow, self).__init__(*args, **kwargs)

        widgets = {
            "Retarget": RetargetWidget(),
            "Tabs": QtWidgets.QTabBar(),
            "TabBar": QtWidgets.QWidget(),
        }

        widgets["Tabs"].addTab("Options")
        widgets["Tabs"].addTab("Overview")
        widgets["TabBar"].setStyleSheet("background-color: #373737")

        layout = QtWidgets.QHBoxLayout(widgets["TabBar"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Tabs"])
        layout.addStretch(1)

        # Integrate with other options
        layout = self._panels["Central"].layout()  # type: QtWidgets.QVBoxLayout
        layout.insertWidget(0, widgets["TabBar"])
        layout.insertSpacing(0, 8)

        self._panels["Body"].addWidget(widgets["Retarget"])
        self.OverviewPage = 3

        widgets["Retarget"].prompted.connect(self.on_retarget_prompted)
        widgets["Tabs"].currentChanged.connect(self.on_overview)

        self._widgets.update(widgets)
        self._inited = False

    def on_retarget_prompted(self, message):
        if message:
            self._widgets["Hint"].setText(message)
        else:
            self.on_exited()

    def on_overview(self, _):
        if self._panels["Body"].currentIndex() != self.OverviewPage:
            self.overview_state()
            if not self._inited:
                # ensure tab switched
                QtWidgets.QApplication.instance().processEvents()
                # then run the time consuming task
                self._widgets["Retarget"].init()
                self._inited = True
        else:
            self.options_state()

    def on_back(self):
        if self._widgets["Tabs"].currentIndex():
            self.transition(to=self.overview_state)
        else:
            self.transition(to=self.options_state)

    def overview_state(self):
        self._panels["Body"].setCurrentIndex(self.OverviewPage)
        self._widgets["PlayerButton"].setChecked(False)
        self._widgets["Player"].stop()
        self._panels["Buttons"].hide()
        self._panels["Footer"].show()
        self._panels["Timeline"].hide()
        self._widgets["TabBar"].show()
        self.menuBar().show()
        self._keys["Escape"].setEnabled(False)

    def options_state(self):
        # todo: update optionVar
        super(RetargetWindow, self).options_state()
        self._widgets["TabBar"].show()

    def play_state(self):
        super(RetargetWindow, self).play_state()
        self._widgets["TabBar"].hide()

    def help_state(self):
        super(RetargetWindow, self).help_state()
        self._widgets["TabBar"].hide()
