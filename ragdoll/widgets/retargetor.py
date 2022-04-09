import os
import json
from maya import cmds, OpenMayaUI
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from . import px, base
from .. import dump, commands

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


def _get_all_solver_size(registry):
    solvers = list(registry.view("SolverComponent"))
    solver_size = dict.fromkeys(solvers, 0)
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        solver_size[scene_comp["entity"]] += 1
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


class _Connection(object):
    def __init__(self, marker, dest, level, natural, icon_m, icon_d,
                 dot_color, check_state):
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


class MarkerTreeModel(base.BaseItemModel):
    destination_toggled = QtCore.Signal(str, str, bool)

    NodeRole = QtCore.Qt.UserRole + 10
    LevelRole = QtCore.Qt.UserRole + 11
    NameSortingRole = QtCore.Qt.UserRole + 12
    NaturalSortingRole = QtCore.Qt.UserRole + 13
    ColorDotRole = QtCore.Qt.UserRole + 14

    Headers = [
        "Name",
        "Destination",
    ]

    def __init__(self, *args, **kwargs):
        super(MarkerTreeModel, self).__init__(*args, **kwargs)
        self.flipped = False
        self._dump = None
        self._internal = []  # type: list[_Solver]
        self._pixmap_list = {
            "rdSolver": QtGui.QPixmap(_resource("icons", "solver.png")),
            "rdMarker_0": QtGui.QPixmap(_resource("icons", "box.png")),
            "rdMarker_1": QtGui.QPixmap(_resource("icons", "sphere.png")),
            "rdMarker_2": QtGui.QPixmap(_resource("icons", "rigid.png")),
            "rdMarker_4": QtGui.QPixmap(_resource("icons", "mesh.png")),
        }

    def flags(self, index):
        base_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.parent().isValid():
            if index.column() == (0 if self.flipped else 1):
                return base_flags | QtCore.Qt.ItemIsUserCheckable
        return base_flags

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
            return super(MarkerTreeModel, self).data(index, role)

        solver_index = index.parent().row()
        solver_repr = self._internal[solver_index]
        conn = solver_repr.conn_list[index.row()]  # type: _Connection

        column = not index.column() if self.flipped else index.column()
        key = ["marker", "dest"][column]

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if key == "marker":
                return cmdx.fromHex(conn.marker).name()
            if key == "dest":
                return cmdx.fromHex(conn.dest).name() if conn.dest else ""

        if role == QtCore.Qt.DecorationRole:
            if key == "marker":
                return conn.icon_m
            if key == "dest":
                return conn.icon_d

        if role == QtCore.Qt.CheckStateRole:
            if key == "marker":
                return
            if key == "dest":
                return conn.check_state

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

        if role == QtCore.Qt.CheckStateRole:
            solver_index = index.parent().row()
            solver_repr = self._internal[solver_index]
            conn = solver_repr.conn_list[index.row()]  # type: _Connection

            column = not index.column() if self.flipped else index.column()
            key = ["marker", "dest"][column]

            if key == "marker":
                return False

            if key == "dest":
                conn.check_state = value
                self.destination_toggled.emit(conn.marker, conn.dest, bool(value))
                return True

        return False

    @property
    def dump(self):
        return self._dump

    def sync(self):
        self._dump = json.loads(cmds.ragdollDump())
        self._dump.pop("info")  # for comparing on `enterEvent`

    def ordered_first_column(self, sort, reverse):
        column = 1 if self.flipped else 0
        key = ["marker", "dest"][column]

        ordered = []
        for _s in self._internal:
            ordered.append(cmdx.fromHex(_s.solver).shortest_path())

            path_list = []
            for _c in _s.conn_list:
                # node path affects alt row coloring
                path = cmdx.fromHex(_c.marker).name() if key == "marker" else \
                    cmdx.fromHex(_c.dest).name() if _c.dest else ""
                if path not in path_list:
                    path_list.append(path)

            if sort:
                path_list.sort(key=lambda n: n.lower(), reverse=reverse)
            ordered += path_list

        return ordered

    def refresh(self, keep_unchecked=False):
        self.reset()
        self._build_internal_model(keep_unchecked)

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

    def _iter_ragdoll_content(self, registry):
        """Hierarchically iterate solver, marker, destination

        Args:
            registry (dump.Registry): a parsed ragdoll dump object

        Returns:
            An iterator yields tuple of (solver, level, marker, destination).
            The solver and marker are cmdx.Node type, level is int, the
            destination is cmdx.Node or None if marker has no destination set.

        """
        _r = registry  # for short
        for solver in cmdx.ls(type="rdSolver"):
            solver_id = int(solver["ragdollId"])

            markers = cmdx.ls([
                _r.get(entity, "NameComponent")["value"]  # marker name
                for entity in _r.view()
                if _r.has(entity, "MarkerUIComponent")
                and _r.get(entity, "SceneComponent")["entity"] == solver_id
            ])

            marker_by_id = {
                int(mk["ragdollId"]): mk
                for mk in markers
            }

            def child_count(d):
                return sum(
                    _r.get(e, "RigidComponent")["parentRigid"] == d
                    for e in marker_by_id.keys()
                )

            def iter_children(parent_id):
                for entity_ in marker_by_id.keys():
                    rigid = _r.get(entity_, "RigidComponent")
                    if rigid["parentRigid"] == parent_id:
                        yield marker_by_id[entity_]

            def walk_hierarchy(parent_id, _level=0):
                _sibling_count = child_count(parent_id)
                for _marker in iter_children(parent_id):
                    yield _marker, _level

                    _ragdoll_id = int(_marker["ragdollId"])
                    _child_count = child_count(_ragdoll_id)
                    _next_level = _level
                    if not (_sibling_count <= 1 and _child_count <= 1):
                        _next_level += 1

                    for mk, lvl in walk_hierarchy(_ragdoll_id, _next_level):
                        yield mk, lvl

            for marker_node, level in walk_hierarchy(0):
                input_plugs = list(
                    plug for plug in marker_node["destinationTransforms"]
                    if plug.input() is not None
                )
                if input_plugs:
                    for plug in input_plugs:
                        destination_node = plug.input()
                        yield solver, level, marker_node, destination_node
                else:
                    yield solver, level, marker_node, None

    def _build_internal_model(self, keep_unchecked):
        unchecked = list()
        if keep_unchecked:
            for _s in self._internal:
                for _c in _s.conn_list:
                    if _c.dest \
                            and _c.check_state == QtCore.Qt.Unchecked \
                            and _hex_exists(_c.dest):
                        unchecked.append((_s.solver, _c.marker, _c.dest))

        # reset
        del self._internal[:]
        self.sync()
        reg = dump.Registry(self._dump)

        solver_sizes = _get_all_solver_size(reg)
        # todo: what will happen if marker exceeds the non-commercial limit ?

        the_solver = None
        rd_content_iter = self._iter_ragdoll_content(reg)
        for _i, (solver, level, marker, dest) in enumerate(rd_content_iter):
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
                found.icon_d = QtGui.QIcon(":/%s" % _d.type())
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
        # marker icon/color
        _pix = self._pixmap_list["rdMarker_%d" % int(marker["shapeType"])]
        icon_m = QtGui.QIcon(_pix)
        dot_color = QtGui.QColor.fromRgbF(*marker["color"]).lighter()

        # dest icon
        icon_d = QtGui.QIcon(":/%s" % dest.type()) if dest else None

        conn = _Connection(
            marker=marker.hex,
            dest=dest.hex if dest else None,
            icon_m=icon_m,
            icon_d=icon_d,
            dot_color=dot_color,
            level=level,
            natural=natural,
            check_state=check_state if dest else None,
        )
        return conn

    def _check_conn_by_row(self, conn, solver_row, conn_row):
        dest_col = 0 if self.flipped else 1
        solver_index = self.index(solver_row, 0)
        dest_index = self.index(conn_row, dest_col, solver_index)
        if conn.check_state != QtCore.Qt.Checked:
            # will trigger `MarkerTreeWidget.on_destination_toggled`
            self.setData(dest_index, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
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
                    _c.icon_d = QtGui.QIcon(":/%s" % dest.type())
                    return self._check_conn_by_row(_c, x, y)

                elif _c.dest == dest.hex:
                    # already in model, ensure checked
                    if _c.check_state != QtCore.Qt.Checked:
                        return self._check_conn_by_row(_c, x, y)
                    else:
                        return

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

    def any_missing_dest(self):
        for _s in self._internal:
            for _c in _s.conn_list:
                if _c.dest \
                        and _c.check_state == QtCore.Qt.Unchecked \
                        and not _hex_exists(_c.dest):
                    return True
        return False


class MarkerIndentDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent):
        super(MarkerIndentDelegate, self).__init__(parent=parent)
        self._enabled = False
        self._indent = 28
        self._dot_size = 20

    def set_enabled(self, value):
        self._enabled = value

    def _compute(self, index):
        dot_color = index.data(MarkerTreeModel.ColorDotRole)
        level = 0
        if self._enabled and index.column() == 0:
            level = index.data(MarkerTreeModel.LevelRole) or level
        offset = self._indent * level + (self._dot_size if dot_color else 0)
        return offset, dot_color

    def paint(self, painter, option, index):
        offset, dot_color = self._compute(index)
        if offset:
            # paint the gap after offset
            _width = option.rect.width()
            _rect = QtCore.QRect(option.rect)
            _rect.adjust(-offset, 0, -(_width - offset), 0)
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
            pos_x = option.rect.x() - 18
            pos_y = option.rect.center().y() - 9
            border = 2
            inner = self._dot_size - border * 2
            painter.save()
            painter.setRenderHint(painter.Antialiasing)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor("#404040"))
            painter.drawEllipse(pos_x, pos_y, self._dot_size, self._dot_size)
            painter.setBrush(dot_color)
            painter.drawEllipse(pos_x + border, pos_y + border, inner, inner)
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


def _maya_outliner_cursor():
    # Take Maya Outliner cursor (or any other Maya widget that has context
    # menu, e.g. Shelf) to indicate the view has context menu.
    #   note: I tried to find/export cursor bitmap but no success.
    outliner_name = cmds.outlinerEditor()
    ptr = OpenMayaUI.MQtUtil.findControl(outliner_name)
    outliner = base.qt_wrap_instance(long(ptr), QtWidgets.QWidget)
    cursor = QtGui.QCursor(outliner.cursor())
    cmds.deleteUI(outliner_name, editor=True)
    return cursor


class MarkerTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super(MarkerTreeView, self).__init__(parent=parent)
        self.setCursor(_maya_outliner_cursor())
        self._current_order = []

    def drawRow(self, painter, options, index):
        """Draw alternative row color base on connection pair node name
        Args:
            painter (QtGui.QPainter):
            options (QtWidgets.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        Returns:
            None
        """
        if self._current_order:
            proxy = self.model()
            # column is always 0.
            node = proxy.data(index, MarkerTreeModel.NodeRole)
            path = cmdx.fromHex(node).name() if node else ""
            try:
                ordered_index = self._current_order.index(path)
            except ValueError:
                pass
            else:
                if ordered_index % 2:
                    options.features = options.features | options.Alternate

        super(MarkerTreeView, self).drawRow(painter, options, index)

    def update_order(self):
        proxy = self.model()
        model = proxy.sourceModel()
        sort = proxy.sortRole() == MarkerTreeModel.NameSortingRole
        reverse = proxy.sortOrder() == QtCore.Qt.DescendingOrder
        self._current_order = model.ordered_first_column(sort, reverse)


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

        view.setAllColumnsShowFocus(True)
        view.setTextElideMode(QtCore.Qt.ElideLeft)
        view.setSelectionMode(view.ExtendedSelection)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.setHeaderHidden(True)

        header = view.header()
        header.setSectionResizeMode(0, header.ResizeToContents)

        indent_delegate = MarkerIndentDelegate(self)
        view.setItemDelegate(indent_delegate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        view.doubleClicked.connect(self.on_double_clicked)
        view.customContextMenuRequested.connect(self.on_right_clicked)
        model.destination_toggled.connect(self.on_destination_toggled)

        self._view = view
        self._proxy = proxy
        self._model = model
        self._delegate = indent_delegate

    @property
    def view(self):
        return self._view

    @property
    def proxy(self):
        return self._proxy

    @property
    def model(self):
        return self._model

    def refresh(self, keep_unchecked=False):
        self._model.refresh(keep_unchecked)
        self._view.expandToDepth(1)

    def on_double_clicked(self, index):
        node = self._proxy.data(index, MarkerTreeModel.NodeRole)
        if node is not None:
            node = cmdx.fromHex(node)
            cmds.select(node.shortest_path(), replace=True)

    def on_right_clicked(self, position):
        index = self._view.indexAt(position)

        if not index.isValid():
            # Clicked outside any item
            return

        menu = QtWidgets.QMenu(self)

        manipulate = QtWidgets.QAction("Manipulate", menu)
        select_marker = QtWidgets.QAction("Select Marker", menu)
        select_dest = QtWidgets.QAction("Select Destination", menu)
        append_dest = QtWidgets.QAction("Add Destination From Selection", menu)

        menu.addAction(manipulate)
        menu.addSeparator()
        menu.addAction(select_marker)
        menu.addAction(select_dest)
        menu.addSeparator()
        menu.addAction(append_dest)

        def _select_node(column):
            selection = []
            for _index in self._view.selectedIndexes():
                _index = self._proxy.mapToSource(_index)
                _index = self._model.index(
                    _index.row(),
                    column,
                    _index.parent()
                )
                node = _index.data(MarkerTreeModel.NodeRole)
                if node:
                    node = cmdx.fromHex(node)
                    selection.append(node.shortest_path())
            cmds.select(selection)

        def on_manipulate():
            _select_node(1 if self._model.flipped else 0)
            cmds.setToolTo("ShowManips")

        def on_select_marker():
            _select_node(1 if self._model.flipped else 0)

        def on_select_dest():
            _select_node(0 if self._model.flipped else 1)

        def on_append_dest():
            valid_dest_list = [
                node
                for node in cmdx.selection()
                if node.isA(cmdx.kDagNode)
            ]
            marker_col = 1 if self._model.flipped else 0

            selected_markers = []
            for i in self._view.selectedIndexes():
                i = self._proxy.mapToSource(i)
                if not i.parent().isValid() or i.column() != marker_col:
                    continue
                marker_node = cmdx.fromHex(i.data(MarkerTreeModel.NodeRole))
                selected_markers.append(marker_node)

            parsed_indexes = []
            for marker_node in selected_markers:
                for dest_node in valid_dest_list:
                    _index = self._model.append_dest(marker_node, dest_node)
                    if _index:
                        parsed_indexes.append(_index)

            self._proxy.invalidate()
            # select all processed
            self._view.clearSelection()
            sele_model = self._view.selectionModel()
            for _index in parsed_indexes:
                dest_index = self._proxy.mapFromSource(_index)
                marker_index = self._proxy.index(
                    dest_index.row(),
                    marker_col,
                    dest_index.parent()
                )
                sele_model.select(marker_index, sele_model.Select)
                sele_model.select(dest_index, sele_model.Select)

        manipulate.triggered.connect(on_manipulate)
        select_marker.triggered.connect(on_select_marker)
        select_dest.triggered.connect(on_select_dest)
        append_dest.triggered.connect(on_append_dest)

        menu.move(QtGui.QCursor.pos())
        menu.show()

    def on_destination_toggled(self, marker_node, dest_node, checked):
        marker_node = cmdx.fromHex(marker_node)
        dest_node = cmdx.fromHex(dest_node)

        if checked:
            opts = {"append": True}
            commands.retarget_marker(marker_node, dest_node, opts)
        else:
            dest_list = [
                plug.input() for plug in marker_node["destinationTransforms"]
                if plug.input() is not None and plug.input() != dest_node
            ]
            commands.untarget_marker(marker_node)
            opts = {"append": True}
            for transform in dest_list:
                commands.retarget_marker(marker_node, transform, opts)

        self._model.sync()
        # trigger Maya viewport update
        cmds.dgdirty(marker_node.shortest_path())

    def flip(self, state):
        self._model.flipped = state
        self._view.update_order()
        self._proxy.invalidate()

    def set_sort_by_name(self, ascending):
        self._delegate.set_enabled(False)
        self._proxy.setSortRole(MarkerTreeModel.NameSortingRole)
        if ascending:
            self._view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        else:
            self._view.sortByColumn(0, QtCore.Qt.DescendingOrder)
        self._view.update_order()

    def set_sort_by_hierarchy(self):
        self._delegate.set_enabled(True)
        self._proxy.setSortRole(MarkerTreeModel.NaturalSortingRole)
        self._view.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self._view.update_order()


class RetargetWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(RetargetWindow, self).__init__(parent=parent)
        self.setWindowTitle("Marker Retargeting")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)  # For helptext

        panels = {
            "Central": QtWidgets.QWidget(),
            "TopBar": QtWidgets.QWidget(),
            "SideBar": QtWidgets.QWidget(),
            "Markers": QtWidgets.QWidget(),
        }

        widgets = {
            "SearchBar": QtWidgets.QLineEdit(),
            "SearchType": base.ToggleButton(),
            "SearchCase": base.ToggleButton(),
            "MarkerView": MarkerTreeWidget(),
            "Refresh": QtWidgets.QPushButton(),
            "Sorting": base.StateRotateButton(),
        }

        timers = {
            "OnSearched": QtCore.QTimer(self),
        }

        timers["OnSearched"].setSingleShot(True)
        widgets["SearchBar"].setClearButtonEnabled(True)
        widgets["Refresh"].setIcon(QtGui.QIcon(_resource("icons", "reset.png")))

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

        layout = QtWidgets.QVBoxLayout(panels["SideBar"])
        layout.setContentsMargins(4, 2, 4, 0)
        layout.setSpacing(4)
        layout.addWidget(widgets["Sorting"])
        layout.addStretch(1)
        layout.addWidget(widgets["Refresh"])

        layout = QtWidgets.QHBoxLayout(panels["TopBar"])
        layout.setContentsMargins(6, 10, 12, 4)
        layout.addWidget(widgets["SearchType"])
        layout.addWidget(widgets["SearchBar"])
        layout.addWidget(widgets["SearchCase"])

        layout = QtWidgets.QHBoxLayout(panels["Markers"])
        layout.setContentsMargins(2, 4, 10, 10)
        layout.addWidget(panels["SideBar"])
        layout.addWidget(widgets["MarkerView"])

        layout = QtWidgets.QVBoxLayout(panels["Central"])
        layout.addWidget(panels["TopBar"])
        layout.addWidget(panels["Markers"])

        widgets["Sorting"].stateChanged.connect(self.on_sorting_clicked)
        widgets["SearchCase"].toggled.connect(self.on_search_case_toggled)
        widgets["SearchType"].toggled.connect(self.on_search_type_toggled)
        widgets["SearchBar"].textChanged.connect(self.on_searched_defer)
        widgets["Refresh"].clicked.connect(self.on_refresh_clicked)
        timers["OnSearched"].timeout.connect(self.on_searched)

        self._panels = panels
        self._widgets = widgets
        self._timers = timers

        self.setCentralWidget(panels["Central"])
        self.setStyleSheet(_treeview_style_sheet + _sidebar_style_sheet)
        self.setMinimumSize(QtCore.QSize(600, 500))

        # init
        self._widgets["MarkerView"].refresh()
        self._widgets["MarkerView"].set_sort_by_name(ascending=True)

    def on_refresh_clicked(self):
        self._widgets["MarkerView"].refresh()

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
        self._widgets["MarkerView"].proxy.setFilterRegExp(text)
        self._widgets["MarkerView"].view.expandToDepth(1)

    def enterEvent(self, event):
        super(RetargetWindow, self).enterEvent(event)
        view = self._widgets["MarkerView"]

        current_dump = json.loads(cmds.ragdollDump())
        current_dump.pop("info")  # we don't compare with timestamp
        if view.model.dump != current_dump or view.model.any_missing_dest():
            view.refresh(keep_unchecked=True)


_treeview_style_sheet = """
QAbstractItemView {{
    show-decoration-selected: 1;  /* highlight decoration (branch) */
    border: none;
    selection-color: {on_primary};
    selection-background-color: {primary};
    background-color: {background};
    alternate-background-color: {background_alt};
}}
QAbstractItemView:focus {{
    border: none;
}}

QTreeView::item {{
    border: 0px;
    padding: {padding};
    padding-right: {padding_right}px;
    padding-left: {padding_left}px;  /* more space for icon and indicator */
}}
QTreeView::icon {{
    right: {icon_right}px;
}}
QTreeView::indicator {{
    right: {indicator_right}px;
}}

/* note: transparent background color is really hard to look good */

QTreeView::branch:selected,
QAbstractItemView::item:selected:active,
QAbstractItemView::item:selected:!focus {{
    color: {on_secondary};
    background-color: {secondary};
}}

QTreeView::branch:hover,
QAbstractItemView::item:hover,
QAbstractItemView::item:hover:selected {{
    color: {on_primary};
    background-color: {primary};
}}

QTreeView::branch::has-children::!has-siblings:closed {{
    image: url({branch_right});
}}
QTreeView::branch:closed::has-children::has-siblings {{
    image: url({branch_right});
}}
QTreeView::branch:open::has-children::!has-siblings {{
    image: url({branch_down});
}}
QTreeView::branch:open::has-children::has-siblings {{
    image: url({branch_down});
}}
QTreeView::branch::has-children::!has-siblings:closed:hover {{
    image: url({branch_right_on});
}}
QTreeView::branch:closed::has-children::has-siblings:hover {{
    image: url({branch_right_on});
}}
QTreeView::branch:open::has-children::!has-siblings:hover {{
    image: url({branch_down_on});
}}
QTreeView::branch:open::has-children::has-siblings:hover {{
    image: url({branch_down_on});
}}

QTreeView::indicator:unchecked {{
    image: url({indicator_unchecked});
}}
QTreeView::indicator:checked {{
    image: url({indicator_checked});
}}

""".format(
    padding="%dpx" % px(3),
    padding_right=px(10),
    padding_left=px(8),
    icon_right=px(2),
    indicator_right=px(6),
    primary="#515D6A",
    secondary="#5285A6",
    on_primary="#FFFFFF",
    on_secondary="#000000",
    background="#2B2B2B",
    background_alt="#323232",
    branch_down=_resource("ui", "caret-down-fill.svg"),
    branch_down_on=_resource("ui", "caret-down-fill-on.svg"),
    branch_right=_resource("ui", "caret-right-fill.svg"),
    branch_right_on=_resource("ui", "caret-right-fill-on.svg"),
    indicator_checked=_resource("ui", "square-check.svg"),
    indicator_unchecked=_resource("ui", "square.svg"),
)

_sidebar_style_sheet = """
QPushButton {{
    background: transparent;
    border: none;
    border-radius: {radius}px;
    width: {size}px;
    height: {size}px;
}}
QPushButton:pressed {{
    background: rgba(50,50,50,100);
}}
QPushButton:!pressed:hover,
QPushButton:!pressed:hover:checked,
QPushButton:!pressed:hover:!checked {{
    background: rgba(255,255,255,60);
}}

""".format(
    radius=px(2),
    size=px(22),
)
