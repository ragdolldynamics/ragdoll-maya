"""

A personal licence is unable to..

1. Record more than 100 frames
2. Export more than 10 markers

"""

from nose.tools import (
    assert_equals,
    assert_less,
)

from maya import cmds
from ragdoll import api, dump
from ragdoll.vendor import cmdx

from . import _new


def test_export_10():
    # The user can only ever export 10 markers from a Personal licence
    _new()
    solver = api.createSolver()

    for cube in range(15):
        cube1, _ = cmds.polyCube()
        api.assignMarker(cube1, solver)

    # Only 10 markers will be exported
    data = api.exportPhysics()
    registry = dump.Registry(data)

    print("Entities:")
    for entity in registry.view("MarkerUIComponent"):
        print("  - %s" % registry.get(entity, "NameComponent")["value"])

    assert_equals(registry.count("MarkerUIComponent"), 10)


def test_record_100():
    # Non-commercial users can only record up to 100 frames
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    api.assignMarker(cube1, solver)

    # The cube will fall and fall, long past 100 frames
    cmdx.min_time(0)
    cmdx.max_time(120)
    api.recordPhysics(solver)

    value_at_100 = cmds.getAttr(cube1 + ".ty", time=100)
    value_at_110 = cmds.getAttr(cube1 + ".ty", time=110)

    # It'll have fallen far beyond minus 10
    assert_less(value_at_100, -10)

    # Since recording stops at 100, any frame after that will be the same
    assert_equals(value_at_110, value_at_100)
