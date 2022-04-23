
import os
import logging
from itertools import chain
from maya import cmds, OpenMayaUI
from maya.api import OpenMaya as om
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from . import px, base
from .. import commands, internal, ui

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
                 dot_color, check_state, channel, is_bad):
        assert isinstance(marker, str), "Must be hex(str)"
        assert isinstance(dest, str) or dest is None, "Must be hex(str) or None"
        self.marker = marker
        self.dest = dest
        self.level = level
        self.natural = natural
        self.icon_m = icon_m
        self.icon_d = icon_d
        self.dot_color = dot_color
        self.check_state = check_state
        self.channel = channel
        self.is_bad = is_bad


_kAnimCurve = int(om.MFn.kAnimCurve)
_kConstraint = int(om.MFn.kConstraint)
_kPairBlend = int(om.MFn.kPairBlend)
# channel status color
_ChClear = "#404040"
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

    def add_dest(self, marker, dest):
        self.destinations[marker].add(dest)
        self.dest_status[dest.hex] = _destination_status(dest)
        self.bad_retarget[marker.hex][dest.hex] = \
            self.is_bad_retarget(marker, dest)

    def del_dest(self, marker, dest):
        self.destinations[marker].remove(dest)
        self.bad_retarget[marker.hex].pop(dest.hex)
        for ds in self.bad_retarget.values():
            if dest.hex in ds:
                break
        else:
            self.dest_status.pop(dest.hex)

    def set_destination(self, marker, dest, connect):
        if connect:
            opts = {"append": True}
            commands.retarget_marker(marker, dest, opts)
            self.add_dest(marker, dest)

        else:
            dest_list = [
                plug.input() for plug in marker["destinationTransforms"]
                if plug.input() is not None and plug.input() != dest
            ]
            commands.untarget_marker(marker)
            self.del_dest(marker, dest)

            opts = {"append": True}
            for transform in dest_list:
                commands.retarget_marker(marker, transform, opts)

        # trigger Maya viewport update
        cmds.dgdirty(marker.shortest_path())

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

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """
        Args:
            index (QtCore.QModelIndex):
            value (typing.Any):
            role (int):
        Returns:
            bool
        """
        if not index.isValid() or not index.parent().isValid():
            return False

        if index.column() == 2 and role == QtCore.Qt.CheckStateRole:
            solver_index = index.parent().row()
            solver_repr = self._internal[solver_index]
            conn = solver_repr.conn_list[index.row()]  # type: _Connection
            marker_hex = conn.marker
            dest_hex = conn.dest

            if conn.check_state is not None:
                marker = cmdx.fromHex(marker_hex)
                dest = cmdx.fromHex(dest_hex)
                self._scene.set_destination(marker, dest, connect=bool(value))
                conn.check_state = value
                conn.is_bad = self._scene.bad_retarget[marker_hex].get(dest_hex)
                conn.channel = self._scene.dest_status[dest_hex] \
                    if value else None
                return True

        return False

    @property
    def scene(self):
        return self._scene

    def refresh(self, scene=None, keep_unchecked=False, index_to_map=None):
        selected_row = None
        if index_to_map:
            row, parent = index_to_map.row(), index_to_map.parent()
            col_m, col_d = int(self.flipped), int(not self.flipped)
            selected_row = (
                self.index(row, col_m, parent).data(self.NodeRole),
                self.index(row, col_d, parent).data(self.NodeRole),
                self.index(parent.row(), 0).data(self.NodeRole),
            )
        # start refresh
        scene = scene or _Scene()
        self.reset()

        with internal.Timer() as t:
            self._build_internal_model(scene, keep_unchecked)
        log.debug("Internal data model built in total %.2fms" % t.ms)

        for solver_repr in self._internal:
            solver_item = self._mk_solver_item(solver_repr)
            self.appendRow(solver_item)
            solver_item.setColumnCount(len(self.Headers))
            solver_item.setRowCount(len(solver_repr.conn_list))
        # end refresh
        if selected_row:
            col = index_to_map.column()
            col_m, col_d, parent = selected_row
            if parent:
                for i, _s in enumerate(self._internal):
                    if _s.solver == parent:
                        for j, conn in enumerate(_s.conn_list):
                            if conn.marker == col_m and conn.dest == col_d:
                                solver_index = self.index(i, 0)
                                return self.index(j, col, solver_index)
                        break
            else:
                for i, _s in enumerate(self._internal):
                    if _s.solver == col_m:
                        return self.index(i, 0)

    def _mk_solver_item(self, solver_repr):
        item = QtGui.QStandardItem()
        item.setText("[%d] %s" % (solver_repr.size, solver_repr.ui_name))
        item.setIcon(self._pixmap_list["rdSolver"])
        item.setData(solver_repr.solver, self.NodeRole)
        return item

    def _iter_unchecked_connection(self):
        for _s in self._internal:
            for _c in _s.conn_list:
                if _c.check_state == QtCore.Qt.Unchecked:
                    yield _s.solver, _c.marker, _c.dest

    def _build_internal_model(self, scene, keep_unchecked):
        unchecked = list()
        if keep_unchecked:
            for _solver, _marker, _dest in self._iter_unchecked_connection():
                if _dest and _hex_exists(_dest):
                    unchecked.append((_solver, _marker, _dest))

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

                conn = self._mk_conn(marker, dest, level, _i, QtCore.Qt.Checked)
                the_solver.conn_list.append(conn)
        log.debug("Scene iterated in %.2fms" % t.ms)

        # add back unchecked
        for (s_hex, m_hex, d_hex) in unchecked:
            _s = next((_ for _ in self._internal if _.solver == s_hex), None)
            if not _s:
                continue
            conn_iter = (_c for _c in _s.conn_list if _c.marker == m_hex)
            found = next(conn_iter, None)
            if not found:
                continue
            if found.dest == d_hex or any(_c.dest == d_hex for _c in conn_iter):
                continue

            if found.dest is None:
                _d = cmdx.fromHex(d_hex)
                found.dest = _d.hex
                found.icon_d = self._maya_node_icon(_d)
                found.check_state = QtCore.Qt.Unchecked
            else:
                _m = cmdx.fromHex(m_hex)
                _d = cmdx.fromHex(d_hex)
                _l = found.level
                _i = found.natural
                conn = self._mk_conn(_m, _d, _l, _i, QtCore.Qt.Unchecked)
                the_solver.conn_list.append(conn)

    def _mk_conn(self, marker, dest, level, natural, check_state=None):
        check_state = check_state or QtCore.Qt.Unchecked
        check_state = check_state if dest else None
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
            check_state=check_state,
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

    def _check_conn_by_row(self, conn, solver_row, conn_row):
        dest_col = 0 if self.flipped else 1
        solver_index = self.index(solver_row, 0)
        dest_index = self.index(conn_row, dest_col, solver_index)
        if conn.check_state != QtCore.Qt.Checked:
            conn.check_state = QtCore.Qt.Checked
            chk_index = self.index(conn_row, 2, solver_index)
            self.setData(chk_index, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        return dest_index

    def append_dest(self, marker, dest):
        marker_matched = False
        index_matched = None
        ref = None
        for x, _s in enumerate(self._internal):
            for y, _c in enumerate(_s.conn_list):
                if _c.marker != marker.hex:
                    continue
                marker_matched = True
                index_matched = y
                ref = _c

                if _c.dest is None:
                    # plug dest into connection
                    _c.dest = dest.hex
                    _c.icon_d = self._maya_node_icon(dest)
                    return self._check_conn_by_row(_c, x, y)

                elif _c.dest == dest.hex:
                    # already in model, ensure checked
                    return self._check_conn_by_row(_c, x, y)

            if marker_matched:
                # new connection
                # get level, natural from other connection to make a new one
                new_conn = self._mk_conn(marker, dest, ref.level, ref.natural)
                _s.conn_list.insert(index_matched, new_conn)

                solver_item = self.item(x, 0)
                solver_item.setRowCount(solver_item.rowCount() + 1)
                return self._check_conn_by_row(new_conn, x, index_matched)

        # should not happen.
        raise Exception("No matched marker found in model.")

    def any_unchecked_missing(self):
        return any(
            not _dest or not _hex_exists(_dest)
            for _, _, _dest in self._iter_unchecked_connection()
        )


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
            # draw border as selection highlight
            #   we cannot use stylesheet to achieve this due to the offset for
            #   color-dot, could not get a clean border from original paint().
            b = self.SelectionBorder
            rect = QtCore.QRect(option.rect)
            rect.adjust(b, b, -b, -b)  # shrink a bit for border
            pen = QtGui.QPen(QtGui.QColor("#5285A6"))
            pen.setWidth(b)
            path = QtGui.QPainterPath()
            path.addRoundedRect(rect, 12, 12)
            painter.save()
            painter.setRenderHint(painter.Antialiasing)
            painter.setPen(pen)
            painter.fillPath(path, QtGui.QColor("#515D6A"))
            painter.drawPath(path)

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
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(_bg_color))
            painter.drawRect(QtCore.QRect(_base_x, _base_y, _base_w, _base_h))
            _base_x += border
            _base_y += border
            for at in ("t", "r"):
                _y = _base_y
                for ax in ("x", "y", "z"):
                    color = cell_colors.get(at + ax, _bg_color)
                    painter.setBrush(QtGui.QColor(color))
                    painter.drawRect(QtCore.QRect(_base_x, _y, cell_w, cell_h))
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
    released = QtCore.Signal(QtCore.QModelIndex)
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
        # we don't want to grab index from mouse released position because
        #   mouse could have been moved away from view while index did get
        #   selected.
        indexes = self.selectedIndexes()
        if indexes:
            self.released.emit(indexes[0])


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
        view.setSelectionMode(view.SingleSelection)
        view.setSelectionBehavior(view.SelectItems)
        view.setHeaderHidden(True)

        indent_delegate = MarkerIndentDelegate(self)
        view.setItemDelegate(indent_delegate)

        action_bar = QtWidgets.QWidget()
        action_bar.setFixedHeight(px(34))

        replace_dest = QtWidgets.QPushButton(
            QtGui.QIcon(_resource("icons", "add.png")),
            "Add/Replace Destinations",
        )
        append_dest = QtWidgets.QPushButton()  # todo: change to 3 dots icon
        append_dest_menu = QtWidgets.QMenu(self)
        manipulate = QtWidgets.QAction(
            QtGui.QIcon(_resource("icons", "manipulator.png")),
            "Append",
            append_dest_menu
        )
        append_dest_menu.addAction(manipulate)
        append_dest.setMenu(append_dest_menu)
        append_dest.setFixedWidth(px(15))

        remove_dest = QtWidgets.QPushButton(
            QtGui.QIcon(_resource("icons", "manipulator.png")),
            "Remove",
        )
        remove_dest.setFixedWidth(px(182))

        layout = QtWidgets.QHBoxLayout(action_bar)
        layout.setContentsMargins(px(5), px(5), px(5), px(5))
        layout.setSpacing(px(1))
        layout.addWidget(replace_dest)
        layout.addWidget(append_dest)
        layout.addSpacing(px(6))
        layout.addWidget(remove_dest)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)
        layout.addWidget(action_bar)
        layout.setSpacing(px(2))

        view.released.connect(self.on_view_released)

        self._view = view
        self._proxy = proxy
        self._model = model
        self._delegate = indent_delegate

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

    def refresh(self, scene=None, keep_unchecked=False):
        selected = self._view.selectedIndexes()
        selected = self._proxy.mapToSource(selected[-1]) if selected else None

        selected = self._model.refresh(scene, keep_unchecked, selected)
        self._view.expandToDepth(1)

        # todo: check selection (only for first run ?)
        self.process_maya_selection()

        if selected:
            selected = self._proxy.mapFromSource(selected)
            sele_model = self._view.selectionModel()
            sele_model.select(selected, sele_model.Select)
            self._view.scrollTo(selected, self._view.EnsureVisible)

    def on_view_released(self, index):
        if not index.parent().isValid():
            index = self._proxy.index(index.row(), 0)
        node = self._proxy.data(index, MarkerTreeModel.NodeRole)
        if node is not None:
            node = cmdx.fromHex(node)
            cmds.select(node.shortest_path(), replace=True)

    def on_selection_changed(self):
        self.process_maya_selection()

    def process_maya_selection(self):
        selection = cmdx.ls(sl=True)
        marker = next((n for n in selection if n.isA("rdMarker")), None)
        dest = next((n for n in selection if n.isA(cmdx.kTransform)), None)
        if marker and dest:
            self.stage_connection(marker, dest)
        elif marker and not self._model.flipped:
            self.stage_marker(marker)
        elif dest and self._model.flipped:
            self.stage_marker(marker)
        else:
            self.clear_stage()

    def stage_marker(self, marker):
        pass

    def stage_dest(self, dest):
        pass

    def stage_connection(self, marker, dest):
        self.stage_marker(marker)
        print(dest)

    def clear_stage(self):
        pass

    def on_menu_requested(self, position):
        # todo: deprecated
        index = self._view.indexAt(position)

        if not index.isValid():
            # Clicked outside any item
            return

        is_solver = not index.parent().isValid()
        marker = None

        # get selected marker and, check if it's default target connected
        show_default_target_action = False
        marker_col = 1 if self._model.flipped else 0
        if not is_solver:
            if index.column() == marker_col:
                marker = cmdx.fromHex(index.data(MarkerTreeModel.NodeRole))
            else:
                _ = self._proxy.index(index.row(), marker_col, index.parent())
                marker = cmdx.fromHex(_.data(MarkerTreeModel.NodeRole))

            if marker and marker.exists:
                src = marker["sourceTransform"].input()
                if src:
                    for plug in marker["destinationTransforms"]:
                        if plug.input() == src:
                            break
                    else:
                        show_default_target_action = True
            else:
                marker = None

        menu = QtWidgets.QMenu(self)

        manipulate = QtWidgets.QAction(
            QtGui.QIcon(_resource("icons", "manipulator.png")),
            "Manipulate",
            menu
        )
        append_dest = QtWidgets.QAction(
            QtGui.QIcon(_resource("icons", "retarget.png")),
            "Add Target From Selection",
            menu
        )
        add_default = QtWidgets.QAction(
            QtGui.QIcon(_resource("icons", "add.png")),
            "Add Default Target",
            menu
        )

        menu.addAction(append_dest)
        menu.addAction(add_default)
        menu.addSeparator()
        menu.addAction(manipulate)

        append_dest.setEnabled(bool(not is_solver and marker))
        add_default.setEnabled(show_default_target_action)

        def _select_indexes(parsed_indexes):
            self._view.clearSelection()
            sele_model = self._view.selectionModel()
            for _index in parsed_indexes:
                ind = self._proxy.mapFromSource(_index)
                sele_model.select(ind, sele_model.Select | sele_model.Rows)

        def on_manipulate():
            node = None
            if is_solver:
                _index = self._proxy.index(index.row(), 0)
                node = cmdx.fromHex(_index.data(MarkerTreeModel.NodeRole))
            elif marker:
                node = marker

            if node:
                cmds.select(node.shortest_path())
                cmds.setToolTo("ShowManips")

        def on_add_default():
            dest_node = marker["sourceTransform"].input()
            _index = self._model.append_dest(marker, dest_node)
            # select all processed
            _select_indexes([_index])

        def on_append_dest():
            parsed_indexes = []
            for dest in (n for n in cmdx.selection() if n.isA(cmdx.kDagNode)):
                _index = self._model.append_dest(marker, dest)
                if _index:
                    parsed_indexes.append(_index)
            # select all processed
            _select_indexes(parsed_indexes)
            # update sort/filter
            self._proxy.invalidate()

        manipulate.triggered.connect(on_manipulate)
        add_default.triggered.connect(on_add_default)
        append_dest.triggered.connect(on_append_dest)

        menu.move(QtGui.QCursor.pos())
        menu.show()

    def flip(self, state):
        selected = [
            self._proxy.mapToSource(i) for i in self._view.selectedIndexes()
        ]

        self.setup_header(state)
        self._model.flipped = state
        self._proxy.invalidate()

        if selected:
            index = selected[-1]
            index = self._proxy.mapFromSource(index)
            if index.parent().isValid():
                self._view.clearSelection()
                index = index.siblingAtColumn(int(not index.column()))
                sele_model = self._view.selectionModel()
                sele_model.select(index, sele_model.Select)
            self._view.scrollTo(index, self._view.PositionAtCenter)

    def set_filter(self, text):
        self._proxy.setFilterRegExp(text)
        self._view.expandToDepth(1)

        selected = self._view.selectedIndexes()
        if selected:
            self._view.scrollTo(selected[-1], self._view.PositionAtCenter)

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
            outdated = model.scene != scene or model.any_unchecked_missing()
        log.debug("Checking for update finished in %0.2fms" % t.ms)
        if outdated:
            view.refresh(scene, keep_unchecked=True)


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
        super(RetargetWindow, self).options_state()
        self._widgets["TabBar"].show()

    def play_state(self):
        super(RetargetWindow, self).play_state()
        self._widgets["TabBar"].hide()

    def help_state(self):
        super(RetargetWindow, self).help_state()
        self._widgets["TabBar"].hide()
