from nose.tools import assert_almost_equals
from ragdoll.vendor import cmdx
from ragdoll.tools import markers_tool as markers
from ragdoll import interactive as ri
from maya import cmds
from . import _new


def test_uniform_scale():
    _new()

    with cmdx.DagModifier() as mod:
        a = mod.create_node("transform", name="a")
        b = mod.create_node("transform", name="b", parent=a)
        c = mod.create_node("transform", name="c", parent=b)

        mod.set_attr(a["scale"], 2.0)
        mod.set_attr(a["ty"], 3.0)
        mod.set_attr(b["tx"], 1.0)
        mod.set_attr(c["tx"], 1.0)

    cmds.select(str(a), str(b), str(c))
    ri.assign_group()

    solver = cmdx.ls(type="rdSolver")[0]
    solver["gravity"] = 0

    ri.record_markers()

    # Any motion is bad
    assert_almost_equals(a["ty"].read(), 3.0, 4)
    assert_almost_equals(b["tx"].read(), 1.0, 4)
    assert_almost_equals(b["ty"].read(), 0.0, 4)
    assert_almost_equals(c["tx"].read(), 1.0, 4)
    assert_almost_equals(c["ty"].read(), 0.0, 4)


def test_non_uniform_scale():
    _new()

    with cmdx.DagModifier() as mod:
        a = mod.create_node("transform", name="a")
        b = mod.create_node("transform", name="b", parent=a)
        c = mod.create_node("transform", name="c", parent=b)

        mod.set_attr(a["scale"], 2.0)
        mod.set_attr(a["ty"], 3.0)
        mod.set_attr(b["tx"], 1.0)
        mod.set_attr(b["scaleX"], 2.0)
        mod.set_attr(c["tx"], 1.0)

    cmds.select(str(a), str(b), str(c))
    ri.assign_group()

    solver = cmdx.ls(type="rdSolver")[0]
    solver["gravity"] = 0

    ri.record_markers()

    assert_almost_equals(a["ty"].read(), 3.0, 4)
    assert_almost_equals(b["tx"].read(), 1.0, 4)
    assert_almost_equals(b["ty"].read(), 0.0, 4)
    assert_almost_equals(c["tx"].read(), 1.0, 4)
    assert_almost_equals(c["ty"].read(), 0.0, 4)

    # Because C is a child of B that has been scaled,
    # it would be further along X than its local sum
    c_tm = c["worldMatrix"][0].as_matrix()
    c_tm = cmdx.Tm(c_tm)
    c_pos = c_tm.translation()
    assert_almost_equals(c_pos.x, 6.0, 4)


def test_rotate_pivot():
    _new()

    with cmdx.DagModifier() as mod:
        a = mod.create_node("transform", name="a")
        b = mod.create_node("transform", name="b", parent=a)
        c = mod.create_node("transform", name="c", parent=b)

        mod.set_attr(a["ty"], 3.0)
        mod.set_attr(b["tx"], 1.0)
        mod.set_attr(c["tx"], 1.0)

    cmds.select(str(a), str(b), str(c))
    ri.assign_group()

    # Give them some droop
    group = cmdx.ls(type="rdGroup")[0]
    group["driveStiffness"] = 0.01

    ri.record_markers()

    # We've got a dick-like shape
    #
    # a
    # .----. b
    #       \
    #        . c
    #        |
    #        |
    #
    assert_almost_equals(b["rz"].read(
        time=cmdx.max_time()), cmdx.radians(-50.0), 1
    )


def test_rotate_axis():
    _new()

    with cmdx.DagModifier() as mod:
        a = mod.create_node("transform", name="a")
        b = mod.create_node("transform", name="b", parent=a)
        c = mod.create_node("transform", name="c", parent=b)

        mod.set_attr(a["rotateAxisZ"], cmdx.radians(45))
        mod.set_attr(b["rotateAxisZ"], cmdx.radians(-45))
        mod.set_attr(c["rotateAxisZ"], cmdx.radians(-45))
        mod.set_attr(a["ty"], 3.0)
        mod.set_attr(b["tx"], 1.0)
        mod.set_attr(c["tx"], 1.0)

    cmds.select(str(a), str(b), str(c))
    ri.assign_group()

    # Give them some droop
    group = cmdx.ls(type="rdGroup")[0]
    group["driveStiffness"] = 0.01

    # We've got a bridge-like shape
    #
    #   b      c
    #   .-----.
    #  /       \
    # . a       \
    #
    cmdx.min_time(1)
    cmdx.max_time(50)
    ri.record_markers()

    assert_almost_equals(b["rz"].read(time=50), cmdx.radians(-48.0), 1)


def test_joint_orient():
    _new()

    with cmdx.DagModifier() as mod:
        a = mod.create_node("joint", name="a")
        b = mod.create_node("joint", name="b", parent=a)
        c = mod.create_node("joint", name="c", parent=b)
        tip = mod.create_node("joint", name="tip", parent=c)

        mod.set_attr(a["jointOrientZ"], cmdx.radians(45))
        mod.set_attr(b["jointOrientZ"], cmdx.radians(-45))
        mod.set_attr(c["jointOrientZ"], cmdx.radians(-45))
        mod.set_attr(a["ty"], 3.0)
        mod.set_attr(b["tx"], 5.0)
        mod.set_attr(c["tx"], 5.0)
        mod.set_attr(tip["tx"], 5.0)

    cmds.select(str(a), str(b), str(c))
    ri.assign_group()

    # Give them some droop
    group = cmdx.ls(type="rdGroup")[0]
    group["driveStiffness"] = 0.01

    # We've got a bridge-like shape
    #
    #   b      c
    #   .-----.
    #  /       \
    # . a       \
    #
    cmdx.min_time(1)
    cmdx.max_time(25)
    ri.record_markers(**{"markersIgnoreJoints": False})

    assert_almost_equals(b["rz"].read(time=25), cmdx.radians(-13.0), 1)
