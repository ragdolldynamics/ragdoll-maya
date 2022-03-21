import os
import json
import shiboken2
from maya import cmds, OpenMayaUI
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from . import px
from .. import dump, commands

# Unused, for type hint in IDEs
__ = cmdx

try:
    long  # noqa
except NameError:
    # Python 3 compatibility
    long = int


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


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
            ignoreDagHierarchy=False,
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
