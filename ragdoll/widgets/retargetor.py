import os
import json
import typing
import shiboken2
from maya import cmds, OpenMayaUI
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from . import px, base
from .. import dump, commands

# Unused, for type hint in IDEs
__ = typing

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


def _qt_get_cpp_pointer(obj):
    return shiboken2.getCppPointer(obj)[0]


def _qt_wrap_instance(ptr, base=None):
    assert isinstance(ptr, long), "Argument 'ptr' must be of type <long>"
    assert (base is None) or issubclass(base, QtCore.QObject), (
        "Argument 'base' must be of type <QObject>")

    func = shiboken2.wrapInstance

    if base is None:
        q_object = func(long(ptr), QtCore.QObject)
        meta_object = q_object.metaObject()

        while True:
            class_name = meta_object.className()
            try:
                base = getattr(QtWidgets, class_name)
            except AttributeError:
                try:
                    base = getattr(QtCore, class_name)
                except AttributeError:
                    meta_object = meta_object.superClass()
                    continue
            break

    return func(long(ptr), base)


class MayaOutlinerEventFilter(QtCore.QObject):
    """An eventFilter to restrain Maya outliner

    Following features are blocked:
        * Drag-Drop item re-parenting
        * Double-Click rename
        * Right-Click context menu

    Although the command `outlinerEditor` has a flag 'dropIsParent' which
    stated in document as it can be used for disable item re-parenting on
    drag-drop, but it's not working as expected. Hence this filter.

    """

    def eventFilter(self, watched, event):
        """
        Args:
            watched (QtCore.QObject):
            event (QtCore.QEvent):
        Returns:
            bool
        """
        if event.type() in (
            QtCore.QEvent.Drop,
            QtCore.QEvent.DragEnter,
            QtCore.QEvent.MouseButtonDblClick,
        ):
            return True

        elif isinstance(event, QtGui.QMouseEvent) \
                and event.button() is QtCore.Qt.RightButton:
            return True

        return False


class MayaOutliner(QtWidgets.QDialog):
    """A widget that embedded a restrained Maya outliner
    """

    def __init__(self, parent=None):
        super(MayaOutliner, self).__init__(parent=parent)

        outliner_filter = MayaOutlinerEventFilter(self)
        outliner_name = cmds.outlinerEditor(
            mainListConnection=self._get_sel_connection("mainList"),
            selectionConnection=self._get_sel_connection("seleList"),
            showShapes=False,
            showNamespace=True,  # todo: toggle this
            showAttributes=False,
            showCompounds=False,
            showReferenceNodes=False,
            showReferenceMembers=False,
            showSetMembers=False,
            autoExpand=True,
            showDagOnly=True,
            ignoreDagHierarchy=True,
            ignoreHiddenAttribute=True,
            ignoreOutlinerColor=False,
            autoSelectNewObjects=False,
            doNotSelectNewObjects=True,
            highlightActive=True,
        )
        ptr = OpenMayaUI.MQtUtil.findControl(outliner_name)
        outliner = _qt_wrap_instance(long(ptr), QtWidgets.QWidget)
        outliner.installEventFilter(outliner_filter)
        outliner.unsetCursor()  # menu blocked, restore arrow cursor

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(outliner)

        self.destroyed.connect(self.on_destroyed)

        self._outliner_name = outliner_name
        self._outliner_filter = outliner_filter

    def on_destroyed(self):
        self._del_sel_connection("mainList")
        self._del_sel_connection("seleList")

    def _del_sel_connection(self, name):
        name = "%s_%d" % (name, id(self))
        if cmds.selectionConnection(name, query=True, exists=True):
            cmds.deleteUI(name)

    def _get_sel_connection(self, name):
        name = "%s_%d" % (name, id(self))
        if not cmds.selectionConnection(name, query=True, exists=True):
            cmds.selectionConnection(name)
        return name

    def clear(self):
        sele = self._get_sel_connection("mainList")
        cmds.selectionConnection(sele, edit=True, clear=True)

    def active_items(self):
        name = self._outliner_name
        sele = cmds.outlinerEditor(name, query=True, selectionConnection=True)
        return cmds.selectionConnection(sele, query=True, object=True)

    def items(self):
        name = self._outliner_name
        sele = cmds.outlinerEditor(name, query=True, mainListConnection=True)
        return cmds.selectionConnection(sele, query=True, object=True)

    def set_items(self, nodes):
        sele = self._get_sel_connection("mainList")
        cmds.selectionConnection(sele, edit=True, clear=True)
        for node in nodes:
            cmds.selectionConnection(sele, edit=True, select=node)

    def set_global_selection(self, link):
        name = self._outliner_name
        sele = "modelList" if link else self._get_sel_connection("seleList")
        cmds.outlinerEditor(name, edit=True, selectionConnection=sele)

    def show_namespace(self, show):
        pass  # todo: toggle namespace


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


class MarkerTreeModel(base.BaseItemModel):
    target_toggled = QtCore.Signal(cmdx.Node, cmdx.Node, bool)

    NodeRole = QtCore.Qt.UserRole + 10
    DepthRole = QtCore.Qt.UserRole + 11
    NameSortingRole = QtCore.Qt.UserRole + 12
    NaturalSortingRole = QtCore.Qt.UserRole + 13

    Headers = [
        "Name",
        "Target",
    ]

    def __init__(self, *args, **kwargs):
        super(MarkerTreeModel, self).__init__(*args, **kwargs)
        self._target_by_marker = dict()  # type: dict[cmdx.Node: set[cmdx.Node]]
        self._marker_by_solver = dict()  # type: dict[cmdx.Node: list[cmdx.Node]]
        self._dump = None
        self._icons = {
            "rdSolver": QtGui.QIcon(_resource("icons", "solver.png")),
            "rdMarker_0": QtGui.QIcon(_resource("icons", "box.png")),
            "rdMarker_1": QtGui.QIcon(_resource("icons", "sphere.png")),
            "rdMarker_2": QtGui.QIcon(_resource("icons", "rigid.png")),
            "rdMarker_4": QtGui.QIcon(_resource("icons", "mesh.png")),
        }
        # self.__text_matching = False

    def flags(self, index):
        base_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 1:
            return base_flags | QtCore.Qt.ItemIsUserCheckable
        return base_flags

    # def findItems(self, text, flags=QtCore.Qt.MatchExactly, column=0):
    #     self.__text_matching = True
    #     result = super(MarkerTreeModel, self).findItems(text, flags, column)
    #     self.__text_matching = False
    #     return result
    #
    # def data(self, index, role=QtCore.Qt.DisplayRole):
    #     # type: (QtCore.QModelIndex, int) -> typing.Any
    #     if not index.isValid():
    #         return
    #
    #     if index.parent().isValid() \
    #             and index.column() == 0 \
    #             and role == QtCore.Qt.DisplayRole \
    #             and not self.__text_matching:
    #         marker_node = index.data(self.NodeRole)
    #         target_count = len(self._nodes[marker_node])
    #         if target_count > 1:
    #             return "[%d] %s" % (target_count, marker_node.name())
    #
    #     if role == QtCore.Qt.BackgroundRole:
    #         if index.column() != 0:
    #             index = self.index(index.row(), 0, index.parent())
    #         natural_order = index.data(self.NaturalSortingRole)
    #         if natural_order % 2:
    #             return QtGui.QColor("red")
    #         else:
    #             return QtGui.QColor("blue")
    #
    #     return super(MarkerTreeModel, self).data(index, role)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        # type: (QtCore.QModelIndex, typing.Any, int) -> bool
        if not index.isValid():
            return False
        if role == QtCore.Qt.CheckStateRole:
            marker_index = self.index(index.row(), 0, index.parent())
            marker_node = marker_index.data(self.NodeRole)
            target_node = index.data(self.NodeRole)
            self.target_toggled.emit(marker_node, target_node, bool(value))

        return super(MarkerTreeModel, self).setData(index, value, role)

    def all_rd_node_names(self, sort=False):
        for solver, markers in self._marker_by_solver.items():
            yield solver.shortest_path()
            markers = [m.name() for m in markers]
            if sort:
                markers = sorted(markers)
            for marker in markers:
                yield marker

    @property
    def dump(self):
        return self._dump

    def refresh(self):
        self.reset()
        self._target_by_marker.clear()
        self._marker_by_solver.clear()
        self._dump = json.loads(cmds.ragdollDump())
        self._dump.pop("info")

        reg = dump.Registry(self._dump)
        solver_sizes = _get_all_solver_size(reg)
        # todo: what will happen if marker exceeds the non-commercial limit ?

        _natural_ind = 0
        for solver in cmdx.ls(type="rdSolver"):
            solver_id = int(solver["ragdollId"])
            solver_name = _solver_ui_name_by_sizes(solver_sizes, solver)
            solver_size = solver_sizes[int(solver["ragdollId"])]

            markers = cmdx.ls([
                reg.get(entity, "NameComponent")["value"]  # marker name
                for entity in reg.view()
                if reg.has(entity, "MarkerUIComponent")
                and reg.get(entity, "SceneComponent")["entity"] == solver_id
            ])

            # solver item
            solver_item = QtGui.QStandardItem()
            solver_item.setText("[%d] %s" % (solver_size, solver_name))
            solver_item.setIcon(self._icons["rdSolver"])
            solver_item.setData(solver, self.NodeRole)
            solver_item.setData(_natural_ind, self.NaturalSortingRole)
            self.appendRow(solver_item)
            _natural_ind += 1

            # marker-target pairs
            #
            marker_by_id = {
                int(mk["ragdollId"]): mk
                for mk in markers
            }

            def child_count(d):
                return sum(
                    reg.get(e, "RigidComponent")["parentRigid"] == d
                    for e in marker_by_id.keys()
                )

            def iter_children(parent_id):
                for entity_ in marker_by_id.keys():
                    rigid = reg.get(entity_, "RigidComponent")
                    if rigid["parentRigid"] == parent_id:
                        yield marker_by_id[entity_]

            def walk_hierarchy(parent_id, _depth=0):
                _sibling_count = child_count(parent_id)
                for marker_ in iter_children(parent_id):
                    yield marker_, _depth

                    _ragdoll_id = int(marker_["ragdollId"])
                    _child_count = child_count(_ragdoll_id)
                    _depth_next = _depth
                    if not (_sibling_count <= 1 and _child_count <= 1):
                        _depth_next += 1

                    for m, d in walk_hierarchy(_ragdoll_id, _depth_next):
                        yield m, d

            self._marker_by_solver[solver] = list()

            for marker, depth in walk_hierarchy(0):
                for row_columns in self._mk_rows(marker, depth):
                    name_item = row_columns[0]
                    name_item.setData(_natural_ind, self.NaturalSortingRole)
                    solver_item.appendRow(row_columns)

                _natural_ind += 1
                self._marker_by_solver[solver].append(marker)

    def _mk_rows(self, marker_node, depth):
        self._target_by_marker[marker_node] = set()

        input_plugs = list(
            plug for plug in marker_node["destinationTransforms"]
            if plug.input() is not None
        )
        if input_plugs:
            for plug in input_plugs:
                p_input = plug.input()
                self._target_by_marker[marker_node].add(p_input)
                yield self._mk_row(marker_node, depth, p_input)
        else:
            yield self._mk_row(marker_node, depth, None)

    def _mk_row(self, marker_node, depth, target_node):
        name = marker_node.name()
        icon = self._icons[
            "rdMarker_%d" % int(marker_node["shapeType"])
        ]
        name_item = QtGui.QStandardItem()
        name_item.setText(name)
        name_item.setIcon(icon)
        name_item.setData(marker_node, self.NodeRole)
        name_item.setData(depth, self.DepthRole)
        name_item.setData(name, self.NameSortingRole)
        if target_node is None:
            return name_item,
        else:
            target_item = self._mk_target_item(target_node)
            return name_item, target_item

    def _mk_target_item(self, target_node):
        target_item = QtGui.QStandardItem()
        target_item.setText(target_node.name())
        target_item.setIcon(QtGui.QIcon(":/%s" % target_node.type()))
        target_item.setData(target_node, self.NodeRole)
        target_item.setCheckable(True)
        target_item.setCheckState(QtCore.Qt.Checked)
        return target_item

    def append_target(self, marker_node, target_node):
        target_set = self._target_by_marker[marker_node]
        # Marker node must already been added into this model, so KeyError
        # shouldn't raise.
        # If we ever implement "target removal" feature, make sure marker
        # still be kept in a row with empty target column.
        marker_items = self.findItems(
            marker_node.name(),
            QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive
        )
        # Must have at least one marker item, even if it doesn't have any
        # target would have paired with an empty target column
        assert marker_items

        if target_node in target_set:
            # Ensure target is checked
            for marker_item in marker_items:
                index = marker_item.index().siblingAtColumn(1)
                if index.data(self.NodeRole) == target_node:
                    self.setData(
                        index, QtCore.Qt.Checked, QtCore.Qt.CheckStateRole
                    )
                    break
        else:
            if len(target_set):
                # copy depth, naturalOrder from the same marker in other row
                marker_sibling = marker_items[-1]  # type: QtGui.QStandardItem
                depth = marker_sibling.data(self.DepthRole)
                natural = marker_sibling.data(self.NaturalSortingRole)
                marker_item, target_item = self._mk_row(
                    marker_node, depth, target_node
                )
                marker_item.setData(natural, self.NaturalSortingRole)
                solver_item = marker_sibling.parent()
                solver_item.insertRow(
                    marker_sibling.row(), [marker_item, target_item]
                )
            else:
                target_item = self._mk_target_item(target_node)
                marker_item = marker_items[0]  # type: QtGui.QStandardItem
                marker_item.appendColumn([target_item])

            # Ensure new added target is checked
            self.setData(
                target_item.index(),
                QtCore.Qt.Checked,
                QtCore.Qt.CheckStateRole
            )

    def remove_unchecked(self):
        pass


class MarkerIndentDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent):
        super(MarkerIndentDelegate, self).__init__(parent=parent)
        self._enabled = False
        self._indent = 28

    def set_enabled(self, value):
        self._enabled = value

    def paint(self, painter, option, index):
        if self._enabled and index.column() == 0:
            depth = index.data(MarkerTreeModel.DepthRole)
            if depth:
                offset = self._indent * depth
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

    def sizeHint(self, option, index):
        size = super(MarkerIndentDelegate, self).sizeHint(option, index)
        if self._enabled and index.column() == 0:
            depth = index.data(MarkerTreeModel.DepthRole) or 0
            size.setWidth(size.width() + (self._indent * depth))
        return size


class MarkerTreeView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super(MarkerTreeView, self).__init__(parent=parent)
        self._current_sorted = []

    def drawRow(self, painter, options, index):
        # type: (QtGui.QPainter, QtWidgets.QStyleOptionViewItem, QtCore.QModelIndex) -> None
        if self._current_sorted:
            if index.column() != 0:
                _index = self.model().index(index.row(), 0, index.parent())
                node = self.model().data(_index, MarkerTreeModel.NodeRole)
            else:
                node = self.model().data(index, MarkerTreeModel.NodeRole)

            sorted_index = self._current_sorted.index(node.shortest_path())
            if sorted_index % 2:
                options.features = options.features | options.Alternate

        super(MarkerTreeView, self).drawRow(painter, options, index)

    def set_sort_by_name(self, ascending):
        proxy = self.model()  # type: QtCore.QSortFilterProxyModel
        model = proxy.sourceModel()  # type: MarkerTreeModel
        self._current_sorted = list(model.all_rd_node_names(sort=True))
        if ascending:
            self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        else:
            self._current_sorted.reverse()
            self.sortByColumn(0, QtCore.Qt.DescendingOrder)

    def set_sort_by_hierarchy(self):
        proxy = self.model()  # type: QtCore.QSortFilterProxyModel
        model = proxy.sourceModel()  # type: MarkerTreeModel
        self._current_sorted = list(model.all_rd_node_names(sort=False))
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)


class MarkerTreeWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MarkerTreeWidget, self).__init__(parent=parent)

        view = MarkerTreeView()
        model = MarkerTreeModel()
        proxy = QtCore.QSortFilterProxyModel()
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
        view.setItemDelegateForColumn(0, indent_delegate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)

        view.customContextMenuRequested.connect(self.on_right_click)
        model.target_toggled.connect(self.on_target_toggled)

        self._view = view
        self._proxy = proxy
        self._model = model
        self._delegate = indent_delegate

    @property
    def proxy(self):
        return self._proxy

    @property
    def model(self):
        return self._model

    def refresh(self):
        # todo: collect current selected items
        self._model.refresh()
        self._view.expandToDepth(1)

    def on_right_click(self, position):
        index = self._view.indexAt(position)

        if not index.isValid():
            # Clicked outside any item
            return

        menu = QtWidgets.QMenu(self)

        manipulate = QtWidgets.QAction("Manipulate", menu)
        select_marker = QtWidgets.QAction("Select Marker", menu)
        select_target = QtWidgets.QAction("Select Target", menu)
        append_target = QtWidgets.QAction("Add Target From Selection", menu)

        menu.addAction(manipulate)
        menu.addSeparator()
        menu.addAction(select_marker)
        menu.addAction(select_target)
        menu.addSeparator()
        menu.addAction(append_target)

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
                    selection.append(node)
            cmds.select(selection)

        def on_manipulate():
            _select_node(0)
            cmds.setToolTo("ShowManips")

        def on_select_marker():
            _select_node(0)

        def on_select_target():
            _select_node(1)

        def on_append_target():
            valid_target_list = [
                node
                for node in cmdx.selection()
                if node.isA(cmdx.kDagNode)
            ]

            for i in self._view.selectedIndexes():
                i = self._proxy.mapToSource(i)
                if not i.parent().isValid() or i.column() != 0:
                    continue
                marker_node = i.data(MarkerTreeModel.NodeRole)
                for target_node in valid_target_list:
                    self._model.append_target(marker_node, target_node)

        manipulate.triggered.connect(on_manipulate)
        select_marker.triggered.connect(on_select_marker)
        select_target.triggered.connect(on_select_target)
        append_target.triggered.connect(on_append_target)

        menu.move(QtGui.QCursor.pos())
        menu.show()

    def on_target_toggled(self, marker_node, target_node, checked):
        if checked:
            opts = {"append": True}
            commands.retarget_marker(marker_node, target_node, opts)
        else:
            targets = [
                plug.input() for plug in marker_node["destinationTransforms"]
                if plug.input() is not None and plug.input() != target_node
            ]
            commands.untarget_marker(marker_node)
            opts = {"append": True}
            for transform in targets:
                commands.retarget_marker(marker_node, transform, opts)

    def set_sort_by_name(self, ascending):
        self._delegate.set_enabled(False)
        self._proxy.setSortRole(MarkerTreeModel.NameSortingRole)
        self._view.set_sort_by_name(ascending)

    def set_sort_by_hierarchy(self):
        self._delegate.set_enabled(True)
        self._proxy.setSortRole(MarkerTreeModel.NaturalSortingRole)
        self._view.set_sort_by_hierarchy()


class RetargetWindow2(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(RetargetWindow2, self).__init__(parent=parent)
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
            "SearchType": QtWidgets.QPushButton(),
            "SearchCase": QtWidgets.QPushButton(),
            "MarkerView": MarkerTreeWidget(),
            "Cleanup": QtWidgets.QPushButton(),
            "SortNameAZ": QtWidgets.QPushButton(),
            "SortNameZA": QtWidgets.QPushButton(),
            "SortHierarchy": QtWidgets.QPushButton(),
        }

        widgets["SearchBar"].setClearButtonEnabled(True)
        widgets["Cleanup"].setObjectName("CleanupButton")

        def set_toggle(w):
            widgets[w].setObjectName(w + "Button")
            widgets[w].setCheckable(True)

        panels["SideBar"].setObjectName("ButtonGroup")

        set_toggle("SearchType")
        set_toggle("SearchCase")
        set_toggle("SortNameAZ")
        set_toggle("SortNameZA")
        set_toggle("SortHierarchy")
        # sort marker by name A -> Z as default
        widgets["SortNameAZ"].setChecked(True)
        # filtering with case sensitive enabled by default
        widgets["SearchCase"].setChecked(True)

        layout = QtWidgets.QVBoxLayout(panels["SideBar"])
        layout.setContentsMargins(4, 2, 4, 0)
        layout.setSpacing(4)
        layout.addWidget(widgets["SortNameAZ"])
        layout.addWidget(widgets["SortNameZA"])
        layout.addWidget(widgets["SortHierarchy"])
        layout.addStretch(1)
        layout.addWidget(widgets["Cleanup"])

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

        widgets["SortNameAZ"].toggled.connect(self.on_sorting_toggled)
        widgets["SortNameZA"].toggled.connect(self.on_sorting_toggled)
        widgets["SortHierarchy"].toggled.connect(self.on_sorting_toggled)
        widgets["SortNameAZ"].toggled.connect(self.on_sort_marker_by_name_az)
        widgets["SortNameZA"].toggled.connect(self.on_sort_marker_by_name_za)
        widgets["SortHierarchy"].toggled.connect(self.on_sort_marker_by_hierarchy)
        widgets["SearchCase"].toggled.connect(self.on_search_case_toggled)
        widgets["SearchType"].toggled.connect(self.on_search_type_toggled)
        widgets["SearchBar"].textChanged.connect(self.on_searched)
        widgets["Cleanup"].clicked.connect(self.on_cleanup_clicked)

        self._panels = panels
        self._widgets = widgets

        self.setCentralWidget(panels["Central"])
        self.setStyleSheet(_treeview_style_sheet + _sidebar_style_sheet)
        self.setMinimumSize(QtCore.QSize(600, 500))

        self.on_search_type_toggled(False)
        self._widgets["MarkerView"].refresh()
        self._widgets["MarkerView"].set_sort_by_name(ascending=True)

    def on_cleanup_clicked(self):
        self._widgets["MarkerView"].model.remove_unchecked()

    def on_sorting_toggled(self, _):
        sender = self.sender()
        buttons = [
            self._widgets["SortNameAZ"],
            self._widgets["SortNameZA"],
            self._widgets["SortHierarchy"],
        ]
        for btn in buttons:
            btn.blockSignals(True)
            btn.setChecked(btn == sender)
            btn.blockSignals(False)

    def on_sort_marker_by_name_az(self, _):
        self._widgets["MarkerView"].set_sort_by_name(ascending=True)

    def on_sort_marker_by_name_za(self, _):
        self._widgets["MarkerView"].set_sort_by_name(ascending=False)

    def on_sort_marker_by_hierarchy(self, _):
        self._widgets["MarkerView"].set_sort_by_hierarchy()

    def on_search_case_toggled(self, state):
        proxy = self._widgets["MarkerView"].proxy
        if state:
            proxy.setFilterCaseSensitivity(QtCore.Qt.CaseSensitive)
        else:
            proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def on_search_type_toggled(self, state):
        if state:
            self._widgets["SearchBar"].setPlaceholderText("Search targets..")
            pass  # todo: search on targets, also change first column
        else:
            self._widgets["SearchBar"].setPlaceholderText("Search markers..")
            pass  # todo: search on markers, also change first column

    def on_searched(self, text):
        proxy = self._widgets["MarkerView"].proxy
        proxy.setFilterRegExp(text)

    def enterEvent(self, event):
        super(RetargetWindow2, self).enterEvent(event)
        current_dump = json.loads(cmds.ragdollDump())
        current_dump.pop("info")  # we don't compare with timestamp

        if self._widgets["MarkerView"].model.dump != current_dump:
            self._widgets["MarkerView"].refresh()


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
    padding: {padding};
    padding-left: {padding_left};
    padding-right: {padding_right};
    border: 0px;
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

QTreeView::item:!first {{
    padding-left: {item_padding_left}px;
}}
QTreeView::indicator {{
    right: {indicator_right}px;
}}
QTreeView::indicator:unchecked {{
    image: url({indicator_unchecked});
}}
QTreeView::indicator:checked {{
    image: url({indicator_checked});
}}

""".format(
    padding="%dpx" % px(3),
    padding_left="%dpx" % px(1),
    padding_right="%dpx" % px(10),
    primary="#9be7ff",
    secondary="#64b5f6",
    on_primary="#000000",
    on_secondary="#000000",
    background="#2B2B2B",
    background_alt="#323232",
    branch_down=_resource("ui", "caret-down-fill.svg"),
    branch_down_on=_resource("ui", "caret-down-fill-on.svg"),
    branch_right=_resource("ui", "caret-right-fill.svg"),
    branch_right_on=_resource("ui", "caret-right-fill-on.svg"),
    item_padding_left=px(12),
    indicator_right=px(10),
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

#ButtonGroup QPushButton:!pressed:!hover:checked {{
    background: rgba(255,255,255,20);
}}

#CleanupButton {{
    icon: url({cleanup});
}}

#SearchTypeButton:checked {{
    icon: url({search_type_on});
}}
#SearchTypeButton:!checked {{
    icon: url({search_type_off});
}}

#SearchCaseButton:checked {{
    icon: url({search_case_on});
}}
#SearchCaseButton:!checked {{
    icon: url({search_case_off});
}}

#SortNameAZButton:checked {{
    icon: url({sort_name_az_on});
}}
#SortNameAZButton:!checked {{
    icon: url({sort_name_az_off});
}}

#SortNameZAButton:checked {{
    icon: url({sort_name_za_on});
}}
#SortNameZAButton:!checked {{
    icon: url({sort_name_za_off});
}}

#SortHierarchyButton:checked {{
    icon: url({sort_hierarchy_on});
}}
#SortHierarchyButton:!checked {{
    icon: url({sort_hierarchy_off});
}}
""".format(
    radius=px(2),
    size=px(22),
    cleanup=_resource("ui", "stars.svg"),
    search_type_on=_resource("icons", "children.png"),
    search_type_off=_resource("icons", "parent.png"),
    search_case_on=_resource("ui", "alpha-case.svg"),
    search_case_off=_resource("ui", "alpha-case-opac.svg"),
    sort_name_az_on=_resource("ui", "sort-alpha-down.svg"),
    sort_name_az_off=_resource("ui", "sort-alpha-down-opac.svg"),
    sort_name_za_on=_resource("ui", "sort-alpha-down-alt.svg"),
    sort_name_za_off=_resource("ui", "sort-alpha-down-alt-opac.svg"),
    sort_hierarchy_on=_resource("ui", "list-nested.svg"),
    sort_hierarchy_off=_resource("ui", "list-nested-opac.svg"),
)


class RetargetWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(RetargetWindow, self).__init__(parent=parent)
        self.setWindowTitle("Marker Retargeting Tool")

        views = {
            "solvers": QtWidgets.QComboBox(),
            "markers": QtWidgets.QTreeWidget(),
            "targets": MayaOutliner(),
        }

        widgets = {
            "manipulator": QtWidgets.QPushButton(),
            "refresh": QtWidgets.QPushButton(),
            "treeToggle": QtWidgets.QPushButton(),
            "listToggle": QtWidgets.QPushButton(),
            "linkSelection": QtWidgets.QCheckBox(),
            "appendTargets": QtWidgets.QPushButton(),
            "removeTargets": QtWidgets.QPushButton(),
        }

        containers = {
            "head": QtWidgets.QWidget(),
            "center": QtWidgets.QWidget(),
            "targets": QtWidgets.QWidget(),
        }

        views["markers"].setColumnCount(1)
        views["markers"].setHeaderHidden(True)

        widgets["listToggle"].setObjectName("ToggleButton")
        widgets["treeToggle"].setObjectName("ToggleButton")
        widgets["listToggle"].setCheckable(True)
        widgets["treeToggle"].setCheckable(True)
        widgets["treeToggle"].setChecked(True)  # hierarchical view as default

        def set_icon(w, icon):
            _icon = QtGui.QIcon(_resource("icons", icon))
            widgets[w].setIcon(_icon)

        set_icon("manipulator", "manipulator.png")
        set_icon("refresh", "reset.png")
        set_icon("treeToggle", "hierarchy.png")
        set_icon("listToggle", "attributes.png")
        set_icon("appendTargets", "retarget.png")
        set_icon("removeTargets", "untarget.png")

        widgets["linkSelection"].setText("Link Selection")

        layout = QtWidgets.QHBoxLayout(containers["head"])
        layout.addWidget(widgets["refresh"])
        layout.addWidget(views["solvers"], stretch=1)
        layout.addWidget(widgets["manipulator"])

        layout = QtWidgets.QHBoxLayout(containers["targets"])
        layout.addWidget(widgets["appendTargets"])
        layout.addWidget(widgets["removeTargets"])

        layout = QtWidgets.QHBoxLayout(containers["center"])
        layout.setContentsMargins(8, 0, 0, 0)
        layout.addWidget(widgets["treeToggle"])
        layout.addWidget(widgets["listToggle"])
        layout.addSpacing(12)
        layout.addWidget(widgets["linkSelection"], stretch=1)
        layout.addWidget(containers["targets"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(containers["head"])
        layout.addWidget(views["markers"], stretch=5)
        layout.addWidget(containers["center"])
        layout.addWidget(views["targets"], stretch=3)

        # signals
        views["solvers"].currentIndexChanged.connect(self._on_solver_changed)
        views["markers"].currentItemChanged.connect(self._on_marker_changed)
        widgets["refresh"].clicked.connect(self._on_refresh_clicked)
        widgets["manipulator"].clicked.connect(self._on_manipulate_clicked)
        widgets["treeToggle"].toggled.connect(self._on_marker_tree_toggled)
        widgets["listToggle"].toggled.connect(self._on_marker_list_toggled)
        widgets["linkSelection"].stateChanged.connect(self._on_link_sel_checked)
        widgets["appendTargets"].clicked.connect(self._on_target_append_clicked)
        widgets["removeTargets"].clicked.connect(self._on_target_remove_clicked)
        self.destroyed.connect(self.on_destroyed)  # todo: seems not triggered

        self.setStyleSheet("""
        QPushButton {
            background: transparent;
            border: none;
            border-radius: %dpx;
            width: %dpx;
            height: %dpx;
        }
        QPushButton:hover,
        #ToggleButton:hover:checked,
        #ToggleButton:hover:!checked {
            background: rgba(255,255,255,60);
        }
        #ToggleButton:checked {
            background: rgba(255,255,255,30);
        }
        """ % (px(2), px(22), px(22)))

        self._views = views
        self._widgets = widgets
        self._solvers = None
        self._registry = None
        self.__job_id = None

    def on_destroyed(self):
        self._teardown_script_job()

    def _on_solver_changed(self, index):
        solver = self._solvers[index]
        self.set_current(solver)

    def _on_marker_changed(self, item):
        marker = cmdx.encode(item.text(0))
        self._list_targets(marker)
        self._setup_script_job(marker)

    def _on_marker_tree_toggled(self, state):
        self._widgets["listToggle"].setChecked(not state)
        solver = self.current_solver()
        if solver is not None:
            self._list_markers(solver, hierarchical=state)

    def _on_marker_list_toggled(self, state):
        self._widgets["treeToggle"].setChecked(not state)
        solver = self.current_solver()
        if solver is not None:
            self._list_markers(solver, hierarchical=not state)

    def _on_link_sel_checked(self, state):
        pass

    def _on_refresh_clicked(self):
        self.refresh()  # todo: add a delay

    def _on_manipulate_clicked(self):
        pass

    def _on_target_append_clicked(self):
        self._append_targets()

    def _on_target_remove_clicked(self):
        self._remove_targets()

    def _setup_script_job(self, marker):
        self._teardown_script_job()
        attr = marker["destinationTransforms"].path()
        self.__job_id = cmds.scriptJob(
            connectionChange=[attr, self._list_targets],
        )

    def _teardown_script_job(self):
        if self.__job_id is not None and cmds.scriptJob(exists=self.__job_id):
            cmds.scriptJob(kill=self.__job_id, force=True)

    def _get_registry(self):
        if self._registry is None:
            self._registry = dump.Registry(json.loads(cmds.ragdollDump()))
        return self._registry

    def refresh(self, solver_or_marker=None):
        self._solvers = None
        self._registry = None
        solver_view = self._views["solvers"]
        solver_view.blockSignals(True)
        solver_view.clear()

        registry = self._get_registry()
        solver_sizes = _get_all_solver_size(registry)
        # todo: what happen if marker exceeds the non-commercial limit ?

        solvers = cmdx.ls(type="rdSolver")
        self._solvers = solvers
        if not solvers:
            return

        _icon = QtGui.QIcon(_resource("icons", "solver.png"))
        for i, solver in enumerate(solvers):
            solver_name = _solver_ui_name_by_sizes(solver_sizes, solver)
            solver_size = solver_sizes[int(solver["ragdollId"])]

            item_name = "[%d] %s" % (solver_size, solver_name)
            solver_view.addItem(_icon, item_name)
        solver_view.blockSignals(False)

        solver_or_marker = solver_or_marker or solvers[0]
        self.set_current(solver_or_marker)

    def set_current(self, solver_or_marker):
        assert isinstance(solver_or_marker, cmdx.DagNode)

        node = solver_or_marker
        node_type = node.type()
        hierarchical = self._widgets["treeToggle"].isChecked()

        if node_type == "rdSolver":
            solver = node
            marker = None

        elif node_type == "rdMarker":
            marker = node

            other = marker["startState"].output()
            if not other:
                raise Exception("Marker node %r as no solver." % marker)

            if other.isA("rdSolver"):
                solver = other

            elif other.isA("rdGroup"):
                other = other["startState"].output(type="rdSolver")
                if not other:
                    raise Exception("Marker node %r as no solver." % marker)
                solver = other

            else:
                raise Exception("Unknown connection.")
        else:
            raise Exception("Must be rdSolver or rdMarker type.")

        self._list_markers(solver, marker, hierarchical)

    def current_solver(self):
        index = self._views["solvers"].currentIndex()
        if index >= 0:
            return self._solvers[index]

    def current_marker(self):
        item = self._views["markers"].currentItem()
        return cmdx.encode(item.text(0))

    def _list_markers(self, solver, current=None, hierarchical=True):
        marker_view = self._views["markers"]
        marker_view.clear()

        registry = self._get_registry()
        solver_id = int(solver["ragdollId"])

        marker_names = []
        for entity in registry.view():
            scene_comp = registry.get(entity, "SceneComponent")
            is_marker = registry.has(entity, "MarkerUIComponent")
            if not is_marker or scene_comp["entity"] != solver_id:
                continue

            marker_name = registry.get(entity, "NameComponent")["value"]
            marker_names.append(marker_name)

        markers = cmdx.ls(marker_names)

        if hierarchical:
            # tree view
            marker_by_id = {int(m["ragdollId"]): m for m in markers}

            def iter_children(parent_id):
                for entity_ in marker_by_id.keys():
                    rigid = registry.get(entity_, "RigidComponent")
                    if rigid["parentRigid"] == parent_id:
                        yield marker_by_id[entity_]

            def walk_hierarchy(parent_id, parent_item=None):
                for c_marker in iter_children(parent_id):
                    item_ = QtWidgets.QTreeWidgetItem([c_marker.name()])
                    if parent_item is None:
                        marker_view.addTopLevelItem(item_)
                    else:
                        parent_item.addChild(item_)

                    _parent_id = int(c_marker["ragdollId"])
                    walk_hierarchy(_parent_id, item_)

            walk_hierarchy(0)

        else:
            # flat list

            items = []
            for marker in markers:
                item = QtWidgets.QTreeWidgetItem([marker.name()])
                items.append(item)
            marker_view.addTopLevelItems(items)

        if current:
            text = current.name()
            found = marker_view.findItems(text, QtCore.Qt.MatchExactly)
            if found:
                marker_view.setCurrentItem(found[0])

    def _list_targets(self, marker=None):
        target_view = self._views["targets"]
        target_view.clear()
        marker = marker or self.current_marker()
        if marker is None:
            return

        node_paths = []
        for plug in marker["destinationTransforms"]:
            p_input = plug.input()
            if p_input is not None:
                node_paths.append(p_input.shortest_path())

        target_view.set_items(node_paths)

    def _append_targets(self):
        marker = self.current_marker()
        opts = {"append": True}
        for transform in cmdx.ls(sl=True, type="transform"):
            commands.retarget_marker(marker, transform, opts)

    def _remove_targets(self):
        target_view = self._views["targets"]
        to_removed = target_view.active_items()
        targets = [
            cmdx.encode(path)
            for path in target_view.items()
            if path not in to_removed
        ]

        marker = self.current_marker()
        commands.untarget_marker(marker)

        opts = {"append": True}
        for transform in targets:
            commands.retarget_marker(marker, transform, opts)
