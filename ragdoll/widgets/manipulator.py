
from ..ui import DuckArgParser

# State
__ = type("internal", (object,), {})
__.preferred_solver = None


def get_current_solver():
    return __.preferred_solver


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


class FullSolverSelector(DuckArgParser):
    def __init__(self, solvers, parent=None):
        super(FullSolverSelector, self).__init__(parent=parent)
        # todo:
        #   1. get best guess from view and set as default option
        #   2. remember the decision for following operations when "apply" btn
        #      hit.
