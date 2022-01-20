"""Every command is undoable and redoable"""

import os
from maya import cmds
from ..vendor import cmdx
from .. import commands, dump, api
from . import __, _new, _save, _load


from nose.tools import (
    assert_equals,
)


def setup():
    pass


def _export(fname=None):
    fname = cmds.file(fname, expandName=True, query=True)
    dump.export(fname)
    print("Wrote %s" % fname.replace("/", os.sep))
    return True


def _reinterpret(fname=None):
    fname = cmds.file(fname, expandName=True, query=True)
    print("Read %s" % fname.replace("/", os.sep))
    return dump.reinterpret(fname)


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

    _export("simplest_case.rag")
    _new()
    _load()

    assert_equals(len(cmds.ls(type="rdMarker")), 0)

    _reinterpret("simplest_case.rag")
    assert_equals(len(cmds.ls(type="rdMarker")), 1)


def test_export_import_order():
    pass
