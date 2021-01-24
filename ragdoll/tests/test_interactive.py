from maya import cmds
from .. import interactive, commands, options
from ..vendor import cmdx

from nose.tools import (
    assert_equals,
    assert_true,
)

__ = type("internal", (object,), {})()
__.fname = "test.ma"

# A simple arm
#
# o     o----o
#  \   /
#   \ /
#    o
#
JOINT_3CHAIN = (
    # translation
    [
        [-6.21, 9.98, 0.08],
        [7.62, 0.0, 0.00],
        [7.21, 0.0, 0.00],
        [3.80, 0.0, 0.00]
    ],
    # orientation
    [
        [1.57, -0.0, -0.66],
        [0.0, 1.33, 0.0],
        [0.0, -0.58, 0.0],
        [0.0, -0.09, 0.0]
    ],
)


def setup():
    options.reset()


def create_arm():
    joints = []

    parent = None

    for translate, orient in zip(*JOINT_3CHAIN):
        joint = cmdx.create_node("joint", parent=parent)
        joint["translate"] = translate
        joint["jointOrient"] = orient

        parent = joint

        joints += [joint]

    return joints


def new():
    cmds.file(new=True, force=True)


def save():
    __.fname = cmds.file("test.ma", rename=True)
    cmds.file(save=True, force=True)


def load():
    cmds.file(__.fname, open=True, force=True)


def test_create_rigid():
    new()

    cube, _ = cmds.polyCube()
    cmds.select(cube)
    assert_true(interactive.create_active_rigid())

    assert_equals(len(cmds.ls(type="rdRigid")), 1)
    assert_equals(len(cmds.ls(type="rdScene")), 1)


def test_create_muscle():
    new()

    arm = create_arm()
    a = cmdx.create_node("joint", parent=arm[0])
    b = cmdx.create_node("joint", parent=arm[1])

    a["translateY"] = 2
    b["translateY"] = 2

    cmds.select(str(a), str(b))
    assert_true(interactive.create_muscle())

    # Two colliders, one muscle
    assert_equals(len(cmds.ls(type="rdRigid")), 3)
    assert_equals(len(cmds.ls(type="rdScene")), 1)

    # One per anchor
    assert_equals(len(cmds.ls(type="rdConstraint")), 2)


def test_create_passive():
    new()

    # Nothing needs to be selected
    assert_true(interactive.create_passive_rigid())

    # Two colliders, one muscle
    assert_equals(len(cmds.ls(type="rdRigid")), 1)
    assert_equals(len(cmds.ls(type="rdScene")), 1)

    # Channels are unlocked/unconnected
    rigid = cmdx.ls(type="rdRigid")[0]
    tm = rigid.parent()

    assert_true(tm["translateX"].editable)
    assert_true(tm["rotateX"].editable)


def test_create_constraint():
    new()

    cube1, _ = map(cmdx.encode, cmds.polyCube())
    sphere1, _ = map(cmdx.encode, cmds.polySphere())

    cube1["translate"] = (1, 2, 0)
    sphere1["translate"] = (1, 4, 0)

    # Use commands, in case the interactive function is failing
    scene = commands.create_scene()
    commands.create_rigid(cube1, scene)
    commands.create_rigid(sphere1, scene)

    cmds.select(str(cube1), str(sphere1))
    opts = {"constraintSelect": False}
    assert_true(interactive.create_point_constraint(**opts))
    assert_true(interactive.create_orient_constraint(**opts))
    assert_true(interactive.create_parent_constraint(**opts))
    assert_true(interactive.create_hinge_constraint(**opts))
    assert_true(interactive.create_socket_constraint(**opts))

    assert_equals(len(cmds.ls(type="rdRigid")), 2)
    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdConstraint")), 5)


def test_create_kinematic_control():
    new()

    cube1, _ = map(cmdx.encode, cmds.polyCube())
    cube1["translate"] = (1, 2, 0)

    # Use commands, in case the interactive function is failing
    scene = commands.create_scene()
    commands.create_rigid(cube1, scene)

    cmds.select(str(cube1))
    assert_true(interactive.create_kinematic_control())

    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdRigid")), 1)
    assert_equals(len(cmds.ls(type="rdConstraint")), 0)  # No constraint here
    assert_equals(len(cmds.ls(type="rdControl")), 1)

    control = cmdx.ls(type="rdControl")[0]
    assert "kinematic" in control


def test_create_driven_control():
    new()

    cube1, _ = map(cmdx.encode, cmds.polyCube())
    cube1["translate"] = (1, 2, 0)

    # Use commands, in case the interactive function is failing
    scene = commands.create_scene()
    commands.create_rigid(cube1, scene)

    cmds.select(str(cube1))
    assert_true(interactive.create_driven_control())

    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdRigid")), 1)
    assert_equals(len(cmds.ls(type="rdConstraint")), 1)
    assert_equals(len(cmds.ls(type="rdControl")), 1)


def test_create_force():
    new()

    cube1, _ = map(cmdx.encode, cmds.polyCube())
    cube1["translate"] = (1, 2, 0)

    # Use commands, in case the interactive function is failing
    scene = commands.create_scene()
    commands.create_rigid(cube1, scene)

    cmds.select(deselect=True)
    assert_true(interactive.create_push_force())
    cmds.select(deselect=True)
    assert_true(interactive.create_pull_force())
    cmds.select(deselect=True)
    assert_true(interactive.create_uniform_force())
    cmds.select(deselect=True)
    assert_true(interactive.create_turbulence_force())
    cmds.select(deselect=True)

    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdRigid")), 1)
    assert_equals(len(cmds.ls(type="rdConstraint")), 0)
    assert_equals(len(cmds.ls(type="rdForce")), 4)


def test_create_character():
    new()

    hierarchy = create_arm()
    root = hierarchy[0]

    cmds.select(root.path())
    assert_true(interactive.create_character())

    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdRigid")), 3)
    assert_equals(len(cmds.ls(type="rdControl")), 3)

    # Two sockets, and one absolute for the root
    assert_equals(len(cmds.ls(type="rdConstraint")), 3)


def test_dynamic_control():
    new()

    hierarchy = create_arm()
    a, b, c = map(str, hierarchy[:3])
    cmds.select(a, b, c)
    assert_true(interactive.create_dynamic_control())

    assert_equals(len(cmds.ls(type="rdScene")), 1)
    assert_equals(len(cmds.ls(type="rdRigid")), 3)

    # Two local and two worldspace guides
    assert_equals(len(cmds.ls(type="rdConstraint")), 4)


def test_save():
    test_dynamic_control()
    save()
    load()

    rigid = cmdx.ls(type="rdRigid")[0]
    transform = rigid.parent()

    assert_true(transform["translateY"] != 0)

    for frame in range(1, 30):
        transform["ty"].read()  # Trigger evaluation
        cmds.currentTime(frame)


def test_normalise_shapes():
    new()

    hierarchy = create_arm()
    cmds.select(hierarchy[0].path())
    interactive.normalise_shapes()


def manual():
    import time
    t0 = time.time()

    tests = (
        test_create_rigid,
        test_create_muscle,
        test_create_passive,
        test_create_constraint,
        test_create_kinematic_control,
        test_create_driven_control,
        test_create_force,
        test_create_character,
        test_dynamic_control,
        test_save,
        test_normalise_shapes,
    )

    setup()

    errors = []
    for test in tests:
        test()

    # Cleanup
    new()
    t1 = time.time()
    duration = t1 - t0

    if not errors:
        print("Successfully ran %d tests in %.2fs" % (len(tests), duration))
    else:
        print("Ran %d tests with %d errors in %.2fs" % (
            len(tests), len(errors), duration)
        )
