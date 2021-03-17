from maya import cmds
from .. import commands, chain
from ..vendor import cmdx

from nose.tools import (
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

    b["tx"] = 5.0
    c["tx"] = 5.0

    scene = commands.create_scene()
    rigid = commands.create_chain(transform, scene)

    commands.delete_physics([rigid], include_attributes=False)
    assert transform.has_attr("mass")

    commands.delete_physics([rigid], include_attributes=True)
    assert not transform.has_attr("mass")

    new()

    transform = cmdx.createNode("transform")
    scene = commands.create_scene()
    rigid = commands.create_rigid(transform, scene)

    commands.delete_all_physics(include_attributes=True)

    assert not transform.has_attr("mass")


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
