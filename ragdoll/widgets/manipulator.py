
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


def get_outliner_color(node):
    # type: (cmdx.DagNode) -> str or None
    parent = node.parent()
    if parent and parent["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*parent["outlinerColor"]).name()
    elif node["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*node["outlinerColor"]).name()


class SolverButton(QtWidgets.QPushButton):
    tip_shown = QtCore.Signal(str)

    def __init__(self, registry, solver=None, parent=None):
        # type: (Registry, cmdx.DagNode, QtWidgets.QWidget) -> None
        super(SolverButton, self).__init__(parent=parent)

        body = QtWidgets.QWidget()
        info = QtWidgets.QWidget()

        _icon_img = _resource("icons", "solver.png")
        _pixmap = QtGui.QIcon(_icon_img).pixmap(px(48)).scaledToWidth(px(48))
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
        layout.addWidget(info, stretch=True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body, alignment=QtCore.Qt.AlignCenter)

        key_name.tip_shown.connect(self.tip_shown)
        key_size.tip_shown.connect(self.tip_shown)

        self._registry = registry
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
        solver_name = elide(solver.name(), length=60)
        solver_size = compute_solver_size(self._registry, solver)
        solver_color = get_outliner_color(solver) or ""

        self._name.setText(solver_name)
        self._size.setText(str(solver_size))

        if solver_color:
            self._name.setStyleSheet("QLabel {color: %s}" % solver_color)
        else:
            self._name.setStyleSheet(self.__default_style)

        self._dag_path = solver.shortest_path()


class SolverSelectorDialog(FramelessDialog):
    solver_picked = QtCore.Signal(str)

    # todo:
    #   * button
    #       - solver name
    #       - solver size
    #       - solver namespace if any and the sizes are the same
    #       - one of root marker if needed
    #   * tool-tip
    #       - show additional info when button hovered
    #           (but not suitable for explaining per entry on button because
    #            those are being rendered as one image)
    #   * find a place to display solver size
    #       (an overall scene state UI, able to embed into viewport as HUD)
    #

    # todo: guidance image
    #   Hint: When a Marker is selected, Ragdoll will manipulate the solver
    #   it belongs to

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
        # todo: check ragdollDump schema version ?

        main = QtWidgets.QWidget()
        body = QtWidgets.QWidget()
        title = QtWidgets.QLabel("Pick Solver")

        if len(solvers) > 3:
            view = self._init_full(registry, solvers, best_guess)
        else:
            view = self._init_slim(registry, solvers)

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

        layout = QtWidgets.QVBoxLayout(self)
        layout.setMargin(32)
        layout.addWidget(main)

        main.setObjectName("Frameless")
        main.setStyleSheet("#Frameless {background: #333}")

        fx = QtWidgets.QGraphicsDropShadowEffect(self)
        fx.setBlurRadius(32)
        fx.setOffset(0)
        fx.setColor("black")
        self.setGraphicsEffect(fx)

    def _init_slim(self, registry, solvers):
        # type: (Registry, list[cmdx.DagNode]) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(registry, s) for s in solvers]

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

    def _init_full(self, registry, solvers, best_guess=None):
        # type: (Registry, list[cmdx.DagNode], cmdx.DagNode) -> QtWidgets.QWidget
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(registry)]

        combo = QtWidgets.QComboBox()
        _icon = QtGui.QIcon(_resource("icons", "solver.png"))
        for i, s in enumerate(solvers):
            combo.addItem(_icon, s.shortest_path(), s)
            c = get_outliner_color(s)
            if c:
                combo.setItemData(i, QtGui.QColor(c), QtCore.Qt.TextColorRole)

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.addWidget(solver_bar)
        layout.addWidget(combo)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)
        combo.currentIndexChanged.connect(self.on_solver_changed)

        self._solvers = solver_btn_row
        self._combo = combo

        # init
        if best_guess is None:
            self.on_solver_changed(0)
        else:
            combo.setCurrentText(best_guess.shortest_path())
            if combo.currentIndex() == 0:
                self.on_solver_changed(0)

        return view

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()

    def on_solver_changed(self, index):
        solver = self._combo.itemData(index)
        self._solvers[-1].set_solver(solver)
