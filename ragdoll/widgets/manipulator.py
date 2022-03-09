
import os
import json
from maya import cmds
from PySide2 import QtCore, QtWidgets, QtGui
from ._base import FramelessDialog, HTMLSkinnedButton
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


class SolverButton(HTMLSkinnedButton):
    _icon_path = _resource("icons", "solver.png")

    def __init__(self, registry, solver=None, parent=None):
        # type: (Registry, cmdx.DagNode, QtWidgets.QWidget) -> None
        super(SolverButton, self).__init__(html="", parent=parent)
        self._registry = registry
        self._dag_path = None

        if solver is not None:
            self.set_solver(solver)

    @property
    def dag_path(self):
        return self._dag_path

    def set_solver(self, solver):
        solver_dag_path = solver.shortest_path()

        solver_name = elide(solver_dag_path, length=60)
        solver_size = compute_solver_size(self._registry, solver)
        solver_color = get_outliner_color(solver) or ""

        html = "<table cellpadding=2 cellspacing=4>"
        html += """
        <tr>
            <td rowspan=4 align="left" valign="top">{icon}</td>
            <td align="right" valign="middle">{key}</td>
            <td align="left" valign="middle">{value}</td>
        </tr>
        """.format(
            icon='<img src="%s" width=64 height=64 />' % self._icon_path,
            key='<strong>Node:</strong>',
            value='<font color="%s">%s</font>' % (solver_color, solver_name),
        )
        html += """
        <tr>
            <td align="right" valign="middle">{key}</td>
            <td align="left" valign="middle">{value}</td>
        </tr>
        """.format(
            key='<strong>Size:</strong>',
            value=solver_size,
        )
        html += "</table>"

        self.draw_skin(html)
        self._dag_path = solver_dag_path


class SolverSelectorDialog(FramelessDialog):
    solver_picked = QtCore.Signal(str)

    # todo:
    #   * button
    #       - solver name
    #       - solver size
    #       - solver namespace if any and the sizes are the same
    #       - one of root marker if needed
    #   * combo-box
    #       - update button
    #   * tool-tip
    #       - show additional info when button hovered
    #           (but not suitable for explaining per entry on button because
    #            those are being rendered as one image)
    #   * re-size handle (?)
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

        if len(solvers) > 3:
            self._init_full(registry, solvers, best_guess)
        else:
            self._init_slim(registry, solvers)

    def _init_slim(self, registry, solvers):
        # type: (Registry, list[cmdx.DagNode]) -> None

        objection = QtWidgets.QLabel("Pick Solver")

        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(registry, s) for s in solvers]

        layout = QtWidgets.QHBoxLayout(solver_bar)
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 28, 20, 20)
        layout.addWidget(objection)
        layout.addWidget(solver_bar)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)

        self._solvers = solver_btn_row
        self._combo = None

    def _init_full(self, registry, solvers, best_guess=None):
        # type: (Registry, list[cmdx.DagNode], cmdx.DagNode) -> None

        objection = QtWidgets.QLabel("Pick Solver")

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
        for btn in solver_btn_row:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 28, 20, 20)
        layout.addWidget(objection)
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

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()

    def on_solver_changed(self, index):
        solver = self._combo.itemData(index)
        self._solvers[-1].set_solver(solver)
