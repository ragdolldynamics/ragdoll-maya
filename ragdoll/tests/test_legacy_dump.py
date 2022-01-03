"""Every command is undoable and redoable"""

from maya import cmds
from ..vendor import cmdx
from ..legacy.tools import chain_tool
from ..legacy import commands, dump
from . import __, _new, _save, _load


from nose.tools import (
    assert_equals,
)


def setup():
    pass


def _export():
    data = cmds.ragdollDump()

    with open(__.export, "w") as f:
        f.write(data)

    return True


def _reinterpret():
    return dump.reinterpret(__.export)


def test_simplest_of_cases():
    # Just a box
    _new()

    cube, _ = map(cmdx.encode, cmds.polyCube())
    cmds.move(0, 5, 0)
    _save()

    scene = commands.create_scene(name="myScene")
    commands.create_rigid(cube, scene)

    cube["tx"].read()  # Trigger evaluation

    assert_equals(len(cmds.ls(type="rdRigid")), 1)

    _export()
    _new()
    _load()

    assert_equals(len(cmds.ls(type="rdRigid")), 0)

    _reinterpret()
    assert_equals(len(cmds.ls(type="rdRigid")), 1)


def test_chain():
    _new()

    links = []
    parent = None
    for link in range(5):
        name = "_LINK_%d" % link  # Something distinguishable
        parent = cmdx.createNode("transform", name=name, parent=parent)

        if link == 0:
            parent["ty"] = 5
        else:
            parent["tx"] = 5

        links += [parent]

    _save()

    for link in cmdx.ls("_LINK_*"):
        shapes = link.shapes(type="rdRigid")
        assert_equals(len(list(shapes)), 0)

    scene = commands.create_scene()
    chain_tool.create(links, scene)

    links[-1]["tx"].read()  # Evaluate

    for link in cmdx.ls("_LINK_*"):
        shapes = link.shapes(type="rdRigid")
        assert_equals(len(list(shapes)), 1)

    _export()
    _new()
    _load()

    for link in cmdx.ls("_LINK_*"):
        shapes = link.shapes(type="rdRigid")
        assert_equals(len(list(shapes)), 0)

    _reinterpret()

    for link in cmdx.ls("_LINK_*"):
        shapes = link.shapes(type="rdRigid")
        assert_equals(len(list(shapes)), 1)


def test_hydra():
    """Dump is able to load chains with only 1 child link"""

    # It used to fault here (2021.04.11), let's never let that happen again
    _new()

    body = cmdx.create_node("transform")
    head1 = cmdx.create_node("transform", parent=body)
    head2 = cmdx.create_node("transform", parent=body)

    body["ty"] = 5.0
    head1["t"] = (5, 5, 0)
    head2["t"] = (-5, 5, 0)

    _save()

    scene = commands.create_scene(name="myScene")

    # A two-headed hydra
    chain_tool.create([body, head1], scene)
    chain_tool.create([body, head2], scene)

    assert_equals(len(cmds.ls(type="rdRigid")), 3)

    _export()
    _new()
    _load()

    _reinterpret()
    assert_equals(len(cmds.ls(type="rdRigid")), 3)


def test_rigid_passive_vs_active():
    """Dump accuratey captures the `kinematic` state of each rigid"""

    # It used to fault here (2021.04.11), let's never let that happen again
    _new()

    passive = cmdx.create_node("transform")
    active1 = cmdx.create_node("transform", parent=passive)
    active2 = cmdx.create_node("transform", parent=passive)

    passive["ty"] = 5.0
    active1["t"] = (5, 5, 0)
    active2["t"] = (-5, 5, 0)

    _save()

    scene = commands.create_scene(name="myScene")

    # A two-headed hydra
    commands.create_rigid(passive, scene, opts={"passive": True})
    commands.create_rigid(active1, scene)
    commands.create_rigid(active2, scene)

    active2.transform(cmdx.sWorld)  # Trigger evaluation

    rigids = list(cmdx.ls(type="rdRigid"))
    assert_equals(len(rigids), 3)
    assert_equals(len([n for n in rigids if n["kinematic"].read()]), 1)
    assert_equals(len([n for n in rigids if not n["kinematic"].read()]), 2)

    _export()
    _new()
    _load()

    _reinterpret()

    rigids = cmdx.ls(type="rdRigid")
    assert_equals(len(rigids), 3)
    assert_equals(len([n for n in rigids if n["kinematic"].read()]), 1)
    assert_equals(len([n for n in rigids if not n["kinematic"].read()]), 2)
