from maya import cmds
from .. import commands
from ..vendor import cmdx
from ..tools import chain_tool

from nose.tools import (
    assert_equals,
    assert_almost_equals,
)


def new():
    cmds.file(new=True, force=True)
    cmds.playbackOptions(minTime=1, maxTime=120)
    cmds.playbackOptions(animationStartTime=1, animationEndTime=120)
    cmds.currentTime(1)


def make_rigid():
    transform = cmdx.createNode("transform")
    transform["ty"] = 5.0

    scene = commands.create_scene()
    return commands.create_rigid(transform, scene)


def test_defaults():
    new()

    cube, _ = cmds.polyCube()
    cube = cmdx.encode(cube)  # Convert to cmdx
    cube["translateY"] = 10
    cube["rotate", cmdx.Degrees] = (35, 50, 30)

    cmds.currentTime(1)

    scene = commands.create_scene()
    commands.create_rigid(cube, scene)

    for frame in range(1, 30):
        cube["ty"].read()  # Trigger evaluation
        cmds.currentTime(frame)

    # It'll be resting on the ground at this point
    assert_almost_equals(cube["ty"].read(), 0.500, 3)


def test_delete_all():
    new()

    a = cmdx.createNode("transform")
    b = cmdx.createNode("transform", parent=a)
    c = cmdx.createNode("transform", parent=b)
    d = cmdx.createNode("transform", parent=c)

    a["ty"] = 5.0
    b["tx"] = 5.0
    c["tx"] = 5.0
    d["tx"] = 5.0

    scene = commands.create_scene()

    operator = chain_tool.Chain([a, b, c, d], scene)
    assert operator.pre_flight()
    operator.do_it()
    assert_equals(len(cmds.ls(type="rdRigid")), 4)

    result = commands.delete_physics([scene, a, b, c, d])

    # 1 scene, 4 rigids, 3 constraints, 1 multiplier
    assert_equals(result["deletedRagdollNodeCount"], 9)

    # Scene node transform
    assert_equals(result["deletedExclusiveNodeCount"], 1)

    assert_equals(len(cmds.ls(type="rdRigid")), 0)

    cmds.undo()

    assert_equals(len(cmds.ls(type="rdRigid")), 4)

    commands.delete_physics([a, b, c, d])
    assert_equals(len(cmds.ls(type="rdRigid")), 0)


def test_convert_constraint():
    pass


def test_convert_rigid():
    # Passive -> Active
    # Active -> Passive
    pass


def manual():
    import sys
    import time

    t0 = time.time()

    mod = sys.modules[__name__]
    tests = list(
        func
        for name, func in mod.__dict__.items()
        if name.startswith("test_")
    )

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


def test_chain_tree_tiger():
    # "simulated" attribute only appears on tree root
    # multiplier applies to
    pass


def test_save_load_tiger():
    # Animation/initial pose should not be affected by saving/loading
    pass
