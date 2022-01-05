"""Every command is undoable and redoable"""

from maya import cmds
from ..vendor import cmdx
from .. import commands, dump
from . import __, _new, _save, _load


from nose.tools import (
    assert_equals,
)


def setup():
    pass


def _export():
    data = cmds.ragdollDump()

    with open(__.export, "w") as f:
        f.write(data)

    return True


def _reinterpret():
    return dump.reinterpret(__.export)


def test_simplest_of_cases():
    # Just a box
    _new()

    cube, _ = map(cmdx.encode, cmds.polyCube())
    cmds.move(0, 5, 0)
    _save()

    solver = commands.create_solver()
    commands.assign_marker(cube, solver)

    solver["startState"].read()  # Trigger evaluation

    assert_equals(len(cmds.ls(type="rdMarker")), 1)

    _export()
    _new()
    _load()

    assert_equals(len(cmds.ls(type="rdMarker")), 0)

    _reinterpret()
    assert_equals(len(cmds.ls(type="rdMarker")), 1)


def test_export_import_order():
    pass
