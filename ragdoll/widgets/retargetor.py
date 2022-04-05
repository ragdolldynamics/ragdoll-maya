import os
import json
import typing
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

    def flags(self, index):
        base_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.parent().isValid():
            base_flags |= QtCore.Qt.ItemIsEditable
        if index.column() == 1:
            return base_flags | QtCore.Qt.ItemIsUserCheckable
        return base_flags

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        # type: (QtCore.QModelIndex, typing.Any, int) -> bool
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            return True
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

    def updateEditorGeometry(self, editor, option, index):
        """
        Args:
            editor (QtWidgets.QWidget):
            option (QtWidgets.QStyleOptionViewItem):
            index (QtCore.QModelIndex):
        """
        editor.setReadOnly(True)  # yes, should be an instance of QLineEdit

        if self._enabled and index.column() == 0:
            depth = index.data(MarkerTreeModel.DepthRole)
            if depth:
                self.initStyleOption(option, index)
                style = option.widget.style()
                geom = style.subElementRect(
                    QtWidgets.QStyle.SE_ItemViewItemText,
                    option,
                    option.widget
                )

                offset = self._indent * depth
                geom.adjust(offset, 0, 0, 0)
                editor.setGeometry(geom)
                return
        super(MarkerIndentDelegate, self
              ).updateEditorGeometry(editor, option, index)

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
        super(RetargetWindow, self).enterEvent(event)
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
