
import os
import json
from maya import cmds
from PySide2 import QtCore, QtWidgets, QtGui
from ._base import FramelessDialog, TippedLabel
from ..vendor.qargparse import px
from ..vendor import cmdx
from ..dump import Registry


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def elide(string, length=120):
    string = str(string)
    placeholder = "..."
    length -= len(placeholder)

    if len(string) <= length:
        return string

    half = int(length / 2)
    return string[:half] + placeholder + string[-half:]


def compute_solver_size(registry, solver):
    # note: maybe we could lru_cache this
    solver_size = 0
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        if scene_comp["entity"] == solver["ragdollId"]:
            solver_size += 1
    return solver_size


def get_all_solver_size(registry):
    solvers = list(registry.view("SolverComponent"))
    solver_size = dict.fromkeys(solvers, 0)
    for entity in registry.view():
        scene_comp = registry.get(entity, "SceneComponent")
        solver_size[scene_comp["entity"]] += 1
    return solver_size


def solver_ui_name_by_sizes(solver_sizes, solver):
    solver_id = int(solver["ragdollId"])
    solver_size = solver_sizes[solver_id]

    has_same_size = any(
        _id != solver_id and size == solver_size
        for _id, size in solver_sizes.items()
    )
    transform = solver.parent()
    return transform.shortest_path() if has_same_size else transform.name()


def get_outliner_color(node):
    # type: (cmdx.DagNode) -> str or None
    parent = node.parent()
    if parent and parent["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*parent["outlinerColor"]).name()
    elif node["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*node["outlinerColor"]).name()


class SolverButton(QtWidgets.QPushButton):
    tip_shown = QtCore.Signal(str)

    def __init__(self, solver_sizes, solver=None, parent=None):
        # type: (dict, cmdx.DagNode, QtWidgets.QWidget) -> None
        super(SolverButton, self).__init__(parent=parent)

        body = QtWidgets.QWidget()
        info = QtWidgets.QWidget()

        _icon_img = _resource("icons", "solver.png")
        _pixmap = QtGui.QIcon(_icon_img).pixmap(px(32))
        _pixmap = _pixmap.scaledToWidth(px(32), QtCore.Qt.SmoothTransformation)
        icon = QtWidgets.QLabel()
        icon.setPixmap(_pixmap)

        key_name = TippedLabel("name:")
        val_name = QtWidgets.QLabel()

        key_size = TippedLabel("size:")
        val_size = QtWidgets.QLabel()

        key_name.setStyleSheet("QLabel {color: rgba(240,240,240,125)}")
        key_size.setStyleSheet("QLabel {color: rgba(240,240,240,125)}")

        layout = QtWidgets.QGridLayout(info)
        layout.setSpacing(4)
        layout.addWidget(key_name, 0, 0, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(val_name, 0, 1, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(key_size, 1, 0, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(val_size, 1, 1, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QHBoxLayout(body)
        layout.addWidget(icon)
        layout.addSpacing(4)
        layout.addWidget(info, stretch=True, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body, alignment=QtCore.Qt.AlignLeft)

        key_name.tip_shown.connect(self.tip_shown)
        key_size.tip_shown.connect(self.tip_shown)

        self._solver_sizes = solver_sizes
        self._name = val_name
        self._size = val_size
        self._dag_path = None
        self.__default_style = val_name.styleSheet()

        if solver is not None:
            self.set_solver(solver)

    def sizeHint(self):
        # type: () -> QtCore.QSize
        size = QtCore.QSize()
        for child in self.children():
            if isinstance(child, QtWidgets.QLayout):
                size += child.sizeHint()
        # expand a bit
        size += QtCore.QSize(4, 4)
        return size

    @property
    def dag_path(self):
        return self._dag_path

    def set_solver(self, solver):
        solver_name = solver_ui_name_by_sizes(self._solver_sizes, solver)
        solver_color = get_outliner_color(solver) or ""
        solver_size = self._solver_sizes[int(solver["ragdollId"])]

        self._name.setText(solver_name)
        self._size.setText(str(solver_size))

        if solver_color:
            self._name.setStyleSheet("QLabel {color: %s}" % solver_color)
        else:
            self._name.setStyleSheet(self.__default_style)

        self._dag_path = solver.shortest_path()


class SolverComboBox(QtWidgets.QComboBox):

    def __init__(self, solver_sizes, solvers=None, parent=None):
        # type: (dict, list[cmdx.DagNode], QtWidgets.QWidget) -> None
        super(SolverComboBox, self).__init__(parent=parent)

        _icon = QtGui.QIcon(_resource("icons", "solver.png"))
        for i, solver in enumerate(solvers):
            solver_name = solver_ui_name_by_sizes(solver_sizes, solver)
            solver_size = solver_sizes[int(solver["ragdollId"])]

            item_name = "[%d] %s" % (solver_size, solver_name)
            self.addItem(_icon, item_name, solver)

            solver_color = get_outliner_color(solver)
            if solver_color:
                q_solver_color = QtGui.QColor(solver_color)
                self.setItemData(i, q_solver_color, QtCore.Qt.TextColorRole)


class SolverSelectorDialog(FramelessDialog):
    solver_picked = QtCore.Signal(str)

    def __init__(self, solvers, best_guess=None, parent=None):
        """
        Args:
            solvers (list[cmdx.DagNode]):
            best_guess (cmdx.DagNode or None):
            parent (QtWidgets.QWidget or None):
        """
        super(SolverSelectorDialog, self).__init__(parent=parent)

        dump = json.loads(cmds.ragdollDump())
        registry = Registry(dump)
        solver_sizes = get_all_solver_size(registry)
        # todo: check ragdollDump schema version ?

        main = QtWidgets.QWidget()
        body = QtWidgets.QWidget()
        title = QtWidgets.QLabel("Pick Solver")

        if len(solvers) > 3:
            view = self._init_full(solver_sizes, solvers, best_guess)
        else:
            view = self._init_slim(solver_sizes, solvers)

        # note: this dialog has fixed width by the banner
        pixmap = QtGui.QPixmap(_resource("ui", "option_header.png"))
        pixmap = pixmap.scaledToWidth(px(570), QtCore.Qt.SmoothTransformation)
        footer = QtWidgets.QLabel()
        footer.setPixmap(pixmap)
        footer.setFixedHeight(px(75))
        footer.setFixedWidth(px(570))

        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(20, 14, 20, 8)
        layout.addWidget(title)
        layout.addWidget(view)

        layout = QtWidgets.QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body)
        layout.addWidget(footer)

        # for the drop-shadow
        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(32)
        layout.addWidget(main)

        main.setObjectName("Frameless")
        main.setStyleSheet("#Frameless {background: #444}")

        fx = QtWidgets.QGraphicsDropShadowEffect(self)
        fx.setBlurRadius(32)
        fx.setOffset(0)
        fx.setColor(QtGui.QColor("black"))
        self.setGraphicsEffect(fx)

    def _init_slim(self, solver_sizes, solvers):
        # type: (dict, list[cmdx.DagNode]) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(solver_sizes, s) for s in solvers]

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.addWidget(solver_bar)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)

        self._solvers = solver_btn_row
        self._combo = None

        return view

    def _init_full(self, solver_sizes, solvers, best_guess=None):
        # type: (dict, list[cmdx.DagNode], cmdx.DagNode) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(solver_sizes)]
        solver_combo = SolverComboBox(solver_sizes, solvers)
        # todo: set max width on combobox ?

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.addWidget(solver_bar)
        layout.addWidget(solver_combo)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)
        solver_combo.currentIndexChanged.connect(self.on_solver_changed)

        self._solvers = solver_btn_row
        self._combo = solver_combo

        # init
        if best_guess is None:
            self.on_solver_changed(0)
        else:
            assert best_guess in solvers
            solver_combo.setCurrentIndex(solvers.index(best_guess))
            if solver_combo.currentIndex() == 0:
                self.on_solver_changed(0)

        return view

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()

    def on_solver_changed(self, index):
        solver = self._combo.itemData(index)
        self._solvers[-1].set_solver(solver)
