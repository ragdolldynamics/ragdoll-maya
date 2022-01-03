import logging

from ...vendor import cmdx
from ... import constants, internal
from .. import commands

from maya import cmds
from maya.api import OpenMaya as om

log = logging.getLogger(__name__)


class PivotEditorTool(object):
    instance = None

    def __init__(self):
        self._constraints = []
        self._window = None
        self._modifier = None
        self._mirror = False
        self._selection_callback = None

        if PivotEditorTool.instance is not None:
            PivotEditorTool.instance.cleanup()

        PivotEditorTool.instance = self

    def spin_add(self, axis):
        self._rotate(-90, axis)

    def spin_sub(self, axis):
        self._rotate(90, axis)

    @internal.with_undo_chunk
    def swap(self):
        self._rotate(-90, (0, 0, 1))
        self._rotate(180, (0, 1, 0))

    def tune_started(self, mirror=False):
        log.debug("Opening")
        self._mirror = mirror
        self._modifier = cmdx.DagModifier()

    def tune(self, amount, axis):
        log.debug("Tuning %s around %s" % (amount, str(axis)))
        self._rotate(amount, axis, frames=constants.Parent, mod=self._modifier)
        self._modifier.do_it()

    def tune_finished(self):
        log.debug("Closing")
        self._mirror = False
        cmdx.commit(self._modifier.undoIt, self._modifier.doIt)

    def _on_selection_changed(self, data=None):
        try:
            self.on_selection_changed()

        except Exception:
            log.warning("Bad Pivot Editor Window, cleaning up")
            self.cleanup()

    def on_selection_changed(self, selection=None):
        constraints = []
        for node in selection or cmdx.selection():
            con = node

            if con.isA(cmdx.kTransform):
                cons = list(node.shapes(type="rdConstraint"))

                if cons:
                    # Last created constraint
                    con = cons[-1]

            if not (con and con.type() == "rdConstraint"):
                continue

            constraints += [{
                "node": con,

                # Store initial frames, for `reset()`
                "parentFrame": con["parentFrame"].as_matrix(),
                "childFrame": con["childFrame"].as_matrix(),
            }]

        self._constraints = constraints

        try:
            self._window.update_selection(constraints)

        except Exception:
            log.warning("Bad Pivot Editor Window, cleaning up")
            self.cleanup()

    def show(self, window):
        self._selection_callback = om.MModelMessage.addCallback(
            om.MModelMessage.kActiveListModified,
            self._on_selection_changed
        )

        window.spin_add_pressed.connect(self.spin_add)
        window.spin_sub_pressed.connect(self.spin_sub)
        window.swap_pressed.connect(self.swap)
        window.tune_pressed.connect(self.tune_started)
        window.tune_dragged.connect(self.tune)
        window.tune_released.connect(self.tune_finished)
        window.reset_pressed.connect(self.reset)
        window.undo_pressed.connect(cmds.undo)
        window.redo_pressed.connect(cmds.redo)
        window.hard_reset_pressed.connect(self.hard_reset)
        window.finished.connect(self.tune_finished)
        window.exited.connect(self.cleanup)

        window.show()

        self._window = window
        self.on_selection_changed()

    def cleanup(self):
        if not self._selection_callback:
            return

        try:
            log.debug("Removing callback")
            om.MMessage.removeCallback(self._selection_callback)
        except RuntimeError:
            log.info("Could not remove callback, probably already removed")
            pass

    def window(self):
        return self._window

    def reset(self):
        with cmdx.DagModifier() as mod:
            for con in self._constraints:
                node = con["node"]
                mod.set_attr(node["childFrame"], con["childFrame"])
                mod.set_attr(node["parentFrame"], con["parentFrame"])

    @internal.with_undo_chunk
    def hard_reset(self):
        for con in self._constraints:
            commands.reset_constraint_frames(con["node"])

    def _rotate(self, degrees, axis, frames=constants.Both, mod=None):
        for index, con in enumerate(self._constraints):
            node = con["node"]
            deg = degrees

            if self._mirror:
                is_even = index % 2 == 0
                deg *= -1 if is_even else +1

            commands.rotate_constraint(
                node, degrees=deg, axis=axis,
                frames=frames,

                # Consolidate undo to here
                _mod=mod
            )


def show(window):
    tool = PivotEditorTool()
    tool.show(window)
    return tool
