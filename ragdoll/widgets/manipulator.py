
import os
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor.qargparse import px
from ..vendor import cmdx


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


def get_outliner_color(node):
    # type: (cmdx.DagNode) -> QtGui.QColor or None
    parent = node.parent()
    if parent and parent["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*parent["outlinerColor"])
    elif node["useOutlinerColor"]:
        return QtGui.QColor.fromRgbF(*node["outlinerColor"])


class SolverButton(QtWidgets.QPushButton):
    _icon = QtGui.QIcon(_resource("icons", "solver.png"))

    def __init__(self, solver, parent=None):
        # type: (cmdx.DagNode, QtWidgets.QWidget) -> None
        super(SolverButton, self).__init__(parent=parent)
        self.setIcon(self._icon)
        self.setIconSize(QtCore.QSize(px(64), px(64)))
        self.setText(elide(solver.shortest_path(), length=60))

        text_color = get_outliner_color(solver)
        text_style = ("color: %s;" % text_color.name()) if text_color else ""

        self.setStyleSheet("""
        * {
            %s
        }
        """ % text_style)

        self._dag_path = solver.shortest_path()

    @property
    def dag_path(self):
        return self._dag_path


class SlimSolverSelector(QtWidgets.QDialog):
    solver_picked = QtCore.Signal(str)

    def __init__(self, solvers, hints, parent=None):
        """
        :type solvers: list[cmdx.DagNode]
        :type hints: list[cmdx.DagNode or None]
        :type parent: QtWidgets.QWidget or None
        """
        super(SlimSolverSelector, self).__init__(parent=parent)
        self.setWindowTitle("Which Solver ?")

        solver_bar = QtWidgets.QWidget()
        solver_btn = [SolverButton(solver) for solver in solvers]
        hint_label = [
            QtWidgets.QLabel(hint.shortest_path() if hint else "")
            for hint in hints
        ]

        layout = QtWidgets.QGridLayout(solver_bar)
        for i, btn in enumerate(solver_btn):
            layout.addWidget(btn, 0, i)
        for i, lab in enumerate(hint_label):
            layout.addWidget(lab, 1, i)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)
        # todo: guidance image
        #   Hint: When a Marker is selected, Ragdoll will manipulate the solver
        #   it belongs to

        for btn in solver_btn:
            btn.clicked.connect(self.on_solver_clicked)

        self._solver_btn = solver_btn

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()


class FullSolverSelector(QtWidgets.QDialog):
    solver_picked = QtCore.Signal(str)

    def __init__(self, solvers, best_guesses, best_hints, parent=None):
        """
        :type solvers: list[cmdx.DagNode]
        :type best_guesses: list[cmdx.DagNode]
        :type best_hints: list[cmdx.DagNode or None]
        :type parent: QtWidgets.QWidget or None
        """
        super(FullSolverSelector, self).__init__(parent=parent)
        self.setWindowTitle("Which Solver ?")

        solver_bar = QtWidgets.QWidget()
        solver_btn = [SolverButton(s) for s in best_guesses]
        hint_label = [
            QtWidgets.QLabel(hint.shortest_path() if hint else "")
            for hint in best_hints
        ]

        layout = QtWidgets.QGridLayout(solver_bar)
        for i, btn in enumerate(solver_btn):
            layout.addWidget(btn, 0, i)
        for i, lab in enumerate(hint_label):
            layout.addWidget(lab, 1, i)

        combo = QtWidgets.QComboBox()
        combo.addItems([solver.shortest_path() for solver in solvers])

        confirm = QtWidgets.QPushButton("Pick")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)
        layout.addWidget(combo)
        layout.addWidget(confirm)
        # todo: guidance image

        confirm.clicked.connect(self.on_solver_picked)
        for btn in solver_btn:
            btn.clicked.connect(self.on_solver_clicked)

        self._solver_btn = solver_btn
        self._combo = combo

    def on_solver_picked(self):
        self.solver_picked.emit(self._combo.currentText())
        self.close()

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()
