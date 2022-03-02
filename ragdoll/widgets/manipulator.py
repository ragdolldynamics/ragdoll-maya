
from PySide2 import QtCore, QtWidgets, QtGui
from ..ui import DuckArgParser

# State
__ = type("internal", (object,), {})
__.remember = False
__.preferred_solver = None


def get_current_solver():
    s = __.preferred_solver
    if not __.remember:
        __.preferred_solver = None
    return s


def set_current_solver(solver_shape):
    # todo: type check
    __.preferred_solver = solver_shape


class SlimSolverSelector(DuckArgParser):

    def __init__(self, solvers, parent=None):
        super(SlimSolverSelector, self).__init__(parent=parent)
        # todo:
        #   1. a simple btn bar, with solver node's outliner color
        #   2. remember the decision for following operations when "apply" btn
        #      hit.

        solver_bar = QtWidgets.QWidget()
        solver_btn = [QtWidgets.QPushButton(str(s)) for s in solvers]
        for btn in solver_btn:
            btn.setCheckable(True)
        solver_btn[0].setChecked(True)  # default

        memorize = QtWidgets.QCheckBox("Remember for this session")

        layout = QtWidgets.QHBoxLayout(solver_bar)
        for btn in solver_btn:
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)
        layout.addWidget(memorize)
        layout.addStretch(True)

        for btn in solver_btn:
            btn.toggled.connect(self.on_solver_toggled)

        self._solver_btn = solver_btn
        self._memorize = memorize

    def on_solver_toggled(self, checked):
        clicked = self.sender()

        def check(b, state):
            b.blockSignals(True)
            b.setChecked(state)
            b.blockSignals(False)

        unchecked = []
        for btn in self._solver_btn:
            if btn is not clicked:
                check(btn, False)
                unchecked.append(btn)

        if not checked:
            check(unchecked[0], True)

    def on_accepted(self):
        selected = next(b for b in self._solver_btn if b.isChecked())
        selected = selected.text()
        set_current_solver(selected)
        __.remember = self._memorize.isChecked()


class FullSolverSelector(DuckArgParser):
    def __init__(self, solvers, parent=None):
        super(FullSolverSelector, self).__init__(parent=parent)
        # todo:
        #   1. get best guess from view and set as default option
        #   2. remember the decision for following operations when "apply" btn
        #      hit.

        combo = QtWidgets.QComboBox()
        combo.addItems([str(s) for s in solvers])
        memorize = QtWidgets.QCheckBox("Remember for this session")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(combo)
        layout.addWidget(memorize)
        layout.addStretch(True)

        self._combo = combo
        self._memorize = memorize

    def on_accepted(self):
        selected = self._combo.currentText()
        set_current_solver(selected)
        __.remember = self._memorize.isChecked()
