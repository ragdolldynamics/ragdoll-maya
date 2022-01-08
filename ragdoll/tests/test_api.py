"""The API takes and returns native Maya paths as strings"""

from maya import cmds
from ragdoll import api
from ragdoll.vendor import cmdx

from . import _new


def test_basics():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    cube2, _ = cmds.polyCube()
    marker1 = api.assignMarker(cube1, solver)
    marker2 = api.assignMarker(cube2, solver)
    api.createDistanceConstraint(marker1, marker2)


def test_assign_group():
    pass


def test_attribute_set():
    # Attributes are set like any other Maya node with cmds

    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    marker1 = api.assignMarker(cube1, solver)

    cmds.setAttr(solver + ".gravityY", -982)
    cmds.setAttr(marker1 + ".shapeType", api.SphereShape)


def test_marker_options():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    marker1 = api.assignMarker(cube1, solver, opts={
        "density": api.DensityWood,
    })

    marker1 = cmdx.encode(marker1)
    assert marker1["densityType"] == api.DensityWood, (
        "Density '%d' should have been '%d'" % (
            marker1["densityType"], api.DensityWood)
    )


def test_record():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    api.assignMarker(cube1, solver)
    api.record(solver)

    cube1 = cmdx.encode(cube1)
    assert cube1["tx"].connected, (
        "%s should have been recorded" % cube1["tx"])

    # Baking to layer per default, which means the curve type is
    curve_type = "animBlendNodeAdditiveDL"
    assert cube1["tx"].input().isA(curve_type), (
        "%s.%s should have been an '%s'"
        % (cube1["tx"].input(),
           cube1["tx"].input().type_name,
           curve_type)
    )


def test_record_options():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    cmds.move(0, 100)

    cmds.setAttr(solver + ".startTime", api.StartTimeCustom)
    cmds.setAttr(solver + ".startTimeCustom", 10)
    api.assignMarker(cube1, solver)

    start = cmdx.time(10)
    end = cmdx.time(15)
    api.record(solver, opts={
        "startTime": start,
        "endTime": end,
        "toLayer": False,
    })

    # Should still be at a Y-value of 100 here
    cube1 = cmdx.encode(cube1)
    assert cube1["ty"].read(time=start) > 99, (
        "%s was not 100" % cube1["ty"].read(time=start)
    )

    assert cube1["ty"].read(time=end) < 99, (
        "Should have fallen more than %s" % cube1["ty"].read(time=end)
    )

    # Not baking to a layer
    curve_type = "animCurveTL"
    assert cube1["ty"].input().isA(curve_type), (
        "%s.%s should have been an '%s'"
        % (cube1["ty"].input(),
           cube1["ty"].input().type_name,
           curve_type)
    )
