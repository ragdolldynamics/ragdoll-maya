"""Every command is undoable and redoable"""

from maya import cmds
from ..vendor import cmdx
from .. import commands, tools, dump
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
    tools.create_chain(links, scene)

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
