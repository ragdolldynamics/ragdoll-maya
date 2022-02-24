"""The API takes and returns native Maya paths as strings"""

from maya import cmds
from ragdoll import api
from ragdoll.vendor import cmdx

from . import _new

from nose.tools import (
    assert_almost_equals,
)


def test_basics():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    cube2, _ = cmds.polyCube()
    marker1 = api.assignMarker(cube1, solver)
    marker2 = api.assignMarker(cube2, solver)
    api.createDistanceConstraint(marker1, marker2)


def test_create_group():
    _new()
    solver = api.createSolver()
    group = api.createGroup(solver)

    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    cmds.joint()  # tip
    cmds.move(10, 5, 0)

    markers = api.assignMarkers([joint1, joint2], group)

    # Check the results
    marker = cmdx.encode(markers[0])
    group = marker["startState"].output(type="rdGroup")
    group["driveStiffness"] = 0.001
    cmdx.min_time(1)
    cmdx.max_time(50)
    api.recordPhysics(solver)

    joint2 = cmdx.encode(joint2)
    assert_almost_equals(
        joint2["rz", cmdx.Degrees].read(time=cmdx.time(50)), -32, 0
    )


def test_assign_and_connect():
    _new()
    solver = api.createSolver()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    cmds.joint()  # tip
    cmds.move(10, 5, 0)
    markers = api.assignMarkers([joint1, joint2], solver)

    # Check the results
    for marker in markers:
        marker = cmdx.encode(marker)
        marker["driveStiffness"] = 0.001

    cmdx.min_time(1)
    cmdx.max_time(50)
    api.recordPhysics(solver)

    joint2 = cmdx.encode(joint2)
    assert_almost_equals(
        joint2["rz", cmdx.Degrees].read(time=cmdx.time(50)), -32, 0
    )


def test_retarget():
    _new()
    solver = api.createSolver()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    cmds.joint()  # tip
    cmds.move(10, 5, 0)
    markers = api.assignMarkers([joint1, joint2], solver)

    # Retarget to this box
    box, _ = cmds.polyCube()
    api.retargetMarker(markers[1], box)

    # The box should now get recorded, not the joint
    cmdx.min_time(1)
    cmdx.max_time(50)
    api.recordPhysics(solver)

    joint2 = cmdx.encode(joint2)
    box = cmdx.encode(box)

    assert not joint2["tx"].input(), "%s was connected" % joint2["tx"].path()
    assert box["tx"].input(), "%s was not connected" % box["tx"].path()


def test_reparent():
    _new()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    joint3 = cmds.joint()  # tip
    cmds.move(10, 5, 0)
    joint4 = cmds.joint()
    cmds.move(5, 10, 0)

    #       o  <-- reparent to b
    #        \
    # o---o---o
    # a   b

    solver = api.createSolver()
    markers = api.assignMarkers([joint1, joint2, joint3, joint4], solver)
    api.reparentMarker(markers[3], markers[1])

    # Check it
    child = cmdx.encode(markers[3])
    parent = cmdx.encode(markers[1])
    assert child["parentMarker"].input() is parent, "%s != %s" % (
        child["parentMarker"].input(), parent)


def test_unparent():
    _new()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    joint3 = cmds.joint()  # tip
    cmds.move(10, 5, 0)
    joint4 = cmds.joint()
    cmds.move(5, 10, 0)

    #       o  <-- unparent
    #        \
    # o---o---o
    # a   b

    solver = api.createSolver()
    markers = api.assignMarkers([joint1, joint2, joint3, joint4], solver)
    api.unparentMarker(markers[3])

    # Check it
    child = cmdx.encode(markers[3])
    old_parent = cmdx.encode(markers[2])
    assert child["parentMarker"].input() is None, "%s == %s" % (
        child["parentMarker"].input(), old_parent)


def test_link_solver():
    _new()
    cube1, _ = cmds.polyCube(height=1)
    cmds.move(0, 5, 0)
    cube2, _ = cmds.polyCube(height=1)
    cmds.move(0, 10, 0)

    solver1 = api.createSolver()
    solver2 = api.createSolver()
    api.createGround(solver1)
    api.createGround(solver2)

    api.assignMarker(cube1, solver1)
    api.assignMarker(cube2, solver2)

    api.linkSolver(solver1, solver2)

    api.recordPhysics(solver2, opts={"startTime": 1, "endTime": 20})

    # box2 is now stacked on top of box1
    cube2 = cmdx.encode(cube2)

    # The center of the cube on top of the other cube
    # both of which are 1 unit high.
    #   ____
    #  /   /|
    # /___/ | <--- 1.5 units
    # |   | /
    # |___|/|
    # |   | /
    # |___|/
    #
    assert_almost_equals(cmds.getAttr("pCube2.ty", time=20), 1.5, 1)


def test_unlink_solver():
    test_link_solver()

    solver1 = "rSolverShape"
    solver2 = "rSolverShape1"

    api.unlinkSolver(solver1)

    # Delete old record
    cmds.delete(cmds.ls(type="container"))

    # The box should now intersect the other, landing at ty=0.5
    api.recordPhysics(solver2, opts={"startTime": 1, "endTime": 20})

    # box2 is no longer stacked on top of box1
    assert_almost_equals(cmds.getAttr("pCube2.ty", time=20), 0.5, 1)


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
    api.record_physics(solver)

    cube1 = cmdx.encode(cube1)
    assert cube1["tx"].connected, (
        "%s should have been recorded" % cube1["tx"].path())

    # Baking to layer per default, which means the curve type is
    curve_type = "animBlendNodeAdditiveDL"
    assert cube1["tx"].input().isA(curve_type), (
        "%s.%s should have been an '%s'"
        % (cube1["tx"].input(),
           cube1["tx"].input().type_name,
           curve_type)
    )


def test_record_nokinematic():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    marker = api.assignMarker(cube1, solver)
    cmds.setAttr(marker + ".inputType", api.InputKinematic)
    api.recordPhysics(solver, opts={"includeKinematic": False})

    cube1 = cmdx.encode(cube1)
    assert not cube1["tx"].connected, (
        "%s was kinematic, it should not have been recorded"
        % cube1["tx"].path()
    )


def test_delete_physics():
    _new()
    solver = api.createSolver()
    cube1, _ = cmds.polyCube()
    api.assignMarker(cube1, solver)
    api.deletePhysics([cube1])
    assert not cmds.ls(type="rdMarker"), cmds.ls(type="rdMarker")


def test_delete_all_physics():
    _new()
    solver1 = api.createSolver()
    solver2 = api.createSolver()
    cube1, _ = cmds.polyCube()
    cube2, _ = cmds.polyCube()
    api.assignMarker(cube1, solver1)
    api.assignMarker(cube2, solver2)
    api.deleteAllPhysics()
    assert not cmds.ls(type="rdSolver"), cmds.ls(type="rdSolver")


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
    api.record_physics(solver, opts={
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
