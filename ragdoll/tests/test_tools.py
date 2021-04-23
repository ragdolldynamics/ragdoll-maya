import os
from maya import cmds
from .. import commands
from ..tools import character_tool
from ..vendor import cmdx
from . import _new, _play

from nose.tools import (
    assert_almost_equals,
)


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


def test_character():
    _new()

    joints = []

    with cmdx.DagModifier() as mod:
        parent = None

        for translate, orient in zip(*JOINT_3CHAIN):
            joint = mod.create_node("joint", parent=parent)
            joint["translate"] = translate
            joint["jointOrient"] = orient

            parent = joint

            joints += [joint]

    # Create with root
    root = joints[0]
    scene = commands.create_scene()
    result = character_tool.create(root, scene, copy=False)

    # After 100 frames, the simulation has come to a rest
    _play(result, 1, 101)

    # The chain should now be lying down, which means
    # the Y-position should end up being the capsule radius

    # Account for compiler differences
    if os.name == "posix":
        assert_almost_equals(result["tx"].read(), -2.37, 2)
        assert_almost_equals(result["ty"].read(), 1.00, 2)
        assert_almost_equals(result["tz"].read(), -8.44, 2)
    else:
        assert_almost_equals(result["tx"].read(), -2.38, 2)
        assert_almost_equals(result["ty"].read(), 1.00, 2)
        assert_almost_equals(result["tz"].read(), -8.44, 2)


def manual():
    import time
    t0 = time.time()

    tests = (
        test_character,
    )

    errors = []
    for test in tests:
        test()

    # Cleanup
    _new()
    t1 = time.time()
    duration = t1 - t0

    if not errors:
        print("Successfully ran %d tests in %.2fs" % (len(tests), duration))
    else:
        print("Ran %d tests with %d errors in %.2fs" % (
            len(tests), len(errors), duration)
        )
