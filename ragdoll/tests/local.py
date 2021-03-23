# Tests meant to be run non-headless, in an interactive Maya session

from .. import commands, interactive
from ..tools import chain_tool
from ..vendor import cmdx
from maya import cmds


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

ITERATIONS = 20


def _create_joint_arm():
    joints = []

    parent = None

    for translate, orient in zip(*JOINT_3CHAIN):
        joint = cmdx.create_node("joint", parent=parent)
        joint["translate"] = translate
        joint["jointOrient"] = orient

        parent = joint

        joints += [joint]

    return joints


def _create_ik_joint_arm():
    joints = _create_joint_arm()
    cmds.select(joints[0].path(), joints[-1].path())
    cmds.ikHandle()
    return joints


def _new():
    cmds.file(new=True, force=True)


def _refresh(transform=None):
    t0 = cmds.currentTime(query=True)

    for i in range(2):
        cmds.currentTime(t0 + i, update=True)

        if transform:
            transform["ty"].read()

        cmds.refresh()

    cmds.currentTime(t0, update=True)


def test_chain_stability_1():
    """Joints does not crash Maya"""

    def run():
        _new()
        _refresh()

        scene = commands.create_scene()
        joints = _create_joint_arm()
        _refresh()
        op = chain_tool.Chain(joints)
        op.do_it(scene)
        _refresh(joints[-1])

    for i in range(ITERATIONS):
        run()


def test_chain_stability_2_ik():
    """Joints with IK does not crash Maya"""

    def run():
        _new()
        _refresh()

        scene = commands.create_scene()
        joints = _create_ik_joint_arm()
        _refresh()
        chain_tool.Chain(joints).do_it(scene)
        _refresh(joints[-1])

    for i in range(ITERATIONS):
        run()


def test_tiger():
    links = [
        "_:ctrlIK_Hips_",
        "_:ctrlFK_Tail_1_",
        "_:ctrlFK_Tail_2_",
        "_:ctrlFK_Tail_3_",
        "_:ctrlFK_Tail_4_",
        "_:ctrlFK_Tail_5_",
    ]

    for i in range(10):
        cmds.select(links)
        interactive.create_active_chain()
        _refresh()
        cmds.select(deselect=True)
        interactive.delete_physics()
        _refresh()


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
        try:
            test()
        except Exception as e:
            import traceback
            traceback.print_exc()
            errors += [e]

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
