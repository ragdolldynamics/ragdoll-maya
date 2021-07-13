from .. import commands
from ..tools import create_character, create_chain
from ..vendor import cmdx
from . import _new, _play

import math
from nose.tools import (
    assert_equals,
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
    result = create_character(root, scene, copy=False)

    # After 100 frames, the simulation has come to a rest
    _play(result, 1, 101)

    # The chain should now be lying down, which means
    # the Y-position should end up being the capsule radius

    assert_equals(math.trunc(result["tx"].read() * 10), -28)
    assert_equals(math.trunc(result["ty"].read() * 10), 10)
    assert_equals(math.trunc(result["tz"].read() * 10), -84)


def test_scale_chain():
    _new()

    with cmdx.DagModifier() as mod:
        nodes = []
        parent = None

        for link in range(3):
            cube = mod.create_node("transform", parent=parent)
            cube["translateX"] = 2
            nodes += [cube]
            parent = cube

        nodes[0]["translateY"] = 2
        nodes[0]["scale"] = (2, 2, 2)

    scene = commands.create_scene()
    rigids = create_chain(nodes, scene, opts={"passiveRoot": False})

    # Ignore any automatically computed radius
    for rigid in rigids:
        if rigid.type() != "rdRigid":
            continue

        rigid["shapeRadius"] = 0.5

    _play(rigids[0], start=1, end=10)

    # It should be lying down by now, 1 unit from the ground given
    # it was scaled at the root, which should scale all of them.
    def t(node):
        return node.translation(cmdx.sWorld)

    assert_almost_equals(t(nodes[0]).y, 1.0, 2)
    assert_almost_equals(t(nodes[1]).y, 1.0, 2)
    assert_almost_equals(t(nodes[2]).y, 1.0, 2)


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
