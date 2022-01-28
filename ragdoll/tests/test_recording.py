"""The API takes and returns native Maya paths as strings"""

from maya import cmds
from ragdoll import api
from ragdoll.vendor import cmdx

from . import _new, _save

from nose.tools import (
    assert_equals,
    assert_not_equals,
)


def test_record_ik():
    # Recording IK involves retargeting and untargeting

    _new()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    joint3 = cmds.joint()  # tip
    cmds.move(10, 5, 0)

    handle, eff = cmds.ikHandle(joint1, joint2)
    pole = cmds.spaceLocator()[0]
    cmds.poleVectorConstraint(pole, handle)[0]

    # o---o---o
    # 1   2   3

    solver = api.createSolver()
    markers = api.assignMarkers([joint1, joint2, joint3], solver)
    api.untarget_marker(markers[0])
    api.retarget_marker(markers[1], pole)
    api.retarget_marker(markers[2], handle)

    cmdx.min_time(1)
    cmdx.max_time(5)  # Won't need many frames
    api.recordPhysics(solver)

    joint1 = cmdx.encode(joint1)
    joint2 = cmdx.encode(joint2)
    handle = cmdx.encode(handle)

    assert not joint1["tx"].connected, "%s was connected" % joint1["tx"].path()
    assert not joint2["tx"].connected, "%s was connected" % joint2["tx"].path()
    assert handle["tx"].connected, "%s was not connected" % handle["tx"].path()


def test_record_constrained_controls():
    # Existing constraints should be preserved

    _new()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    joint3 = cmds.joint()  # tip
    cmds.move(10, 5, 0)

    ctrl = cmds.createNode("transform", name="control")
    con = cmds.parentConstraint(ctrl, joint1)[0]

    # o---o---o
    # 1   2   3

    solver = api.createSolver()
    api.assignMarkers([joint1, joint2, joint3], solver)

    cmdx.min_time(1)
    cmdx.max_time(5)  # Won't need many frames
    api.recordPhysics(solver)

    # The joint was kinematic, and is still connected
    joint1 = cmdx.encode(joint1)
    con = cmdx.encode(con)
    assert_equals(joint1["tx"].input(type="parentConstraint"), con)


def test_animated_controls():
    # Existing animation should be kept and ignored,
    # new animation ending up on a layer

    _new()
    joint1 = cmds.joint()
    cmds.move(0, 5, 0)
    joint2 = cmds.joint()
    cmds.move(5, 5, 0)
    joint3 = cmds.joint()  # tip
    cmds.move(10, 5, 0)

    joint = cmdx.encode(joint2)
    joint["rz"] = {1: 0.0, 10: 1.0, 20: 0.0}  # Some animation

    solver = api.createSolver()
    api.assignMarkers([joint1, joint2, joint3], solver)

    cmdx.min_time(1)
    cmdx.max_time(15)
    api.recordPhysics(solver)

    # It must have changed by now
    value = joint["rz"].read(time=cmdx.time(10))
    assert_not_equals("%.1f" % value, "1.0")

    # Deleting the animation layer restores the original animation
    cmds.delete(cmds.ls(type="container"))

    value = joint["rz"].read(time=cmdx.time(10))
    assert_equals("%.1f" % value, "1.0")
