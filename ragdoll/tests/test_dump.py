"""Every command is undoable and redoable"""

import os
from maya import cmds
from ..vendor import cmdx
from .. import commands, dump, api, constants
from . import __, _new, _save, _load


from nose.tools import (
    assert_equals,
)


def setup():
    pass


def _export(fname=None):
    fname = cmds.file(fname, expandName=True, query=True)
    dump.export(fname)
    print("Wrote %s" % fname.replace("/", os.sep))
    return True


def _reinterpret(fname=None, opts=None):
    fname = cmds.file(fname, expandName=True, query=True)
    print("Read %s" % fname.replace("/", os.sep))
    return dump.reinterpret(fname, opts=opts)


def test_simplest_of_cases():
    # Just a box
    _new()

    cube, _ = map(cmdx.encode, cmds.polyCube())
    cmds.move(0, 5, 0)
    _save()

    solver = commands.create_solver()
    commands.assign_marker(cube, solver)

    solver["startState"].read()  # Trigger evaluation

    assert_equals(len(cmds.ls(type="rdMarker")), 1)

    _export("simplest_case.rag")
    _new()
    _load()

    assert_equals(len(cmds.ls(type="rdMarker")), 0)

    _reinterpret("simplest_case.rag")
    assert_equals(len(cmds.ls(type="rdMarker")), 1)


def test_export_import_order():
    pass


def test_import_match_hierarchy():
    # Even though names are all the same, match by hierarchy solves that
    _new()

    joint1 = cmdx.createNode(type="joint", name="joint1")
    cmds.select(str(joint1))
    cmds.move(0, 5, 0)
    joint2 = cmdx.createNode(type="joint", name="joint1", parent=joint1)
    cmds.select(str(joint2))
    cmds.move(5, 5, 0)
    joint3 = cmdx.createNode(type="joint", name="joint1", parent=joint2)
    cmds.select(str(joint3))
    cmds.move(10, 5, 0)
    joint4 = cmdx.createNode(type="joint", name="joint1", parent=joint3)
    cmds.select(str(joint4))
    cmds.move(5, 10, 0)

    #       o
    #        \
    # o---o---o
    # a   b

    _save()

    solver = commands.create_solver()
    markers = commands.assign_markers([joint1, joint2, joint3, joint4], solver)

    # This will be assigned to the last joint, even though name is clashing
    last = markers[-1]
    cmdx.rename(last, "LastMarker")

    _export("match_hierarchy.rag")
    _new()
    _load()

    _reinterpret("match_hierarchy.rag", opts={
        "matchBy": constants.MatchByHierarchy
    })

    last = cmdx.find("LastMarker")
    joint4 = last["src"].input(type="joint")
    assert_equals(len(list(joint4.lineage())), 3)


def test_import_match_name():
    # Even though hierarchies are all different, match by name solves that
    _new()

    joint1 = cmdx.createNode(type="joint")
    cmds.select(str(joint1))
    cmds.move(0, 5, 0)
    joint2 = cmdx.createNode(type="joint", parent=joint1)
    cmds.select(str(joint2))
    cmds.move(5, 5, 0)
    joint3 = cmdx.createNode(type="joint", parent=joint2)
    cmds.select(str(joint3))
    cmds.move(10, 5, 0)
    joint4 = cmdx.createNode(type="joint", parent=joint3)
    cmds.select(str(joint4))
    cmds.move(5, 10, 0)

    #       o
    #        \
    # o---o---o
    # a   b

    solver = commands.create_solver()
    commands.assign_markers([joint1, joint2, joint3, joint4], solver)

    _export("match_name.rag")
    _new()

    group = cmdx.createNode("transform", name="aGroup")
    joint1 = cmdx.createNode(type="joint", parent=group)
    cmds.select(str(joint1))
    cmds.move(0, 5, 0)
    joint2 = cmdx.createNode(type="joint", parent=joint1)
    cmds.select(str(joint2))
    cmds.move(5, 5, 0)
    joint3 = cmdx.createNode(type="joint", parent=joint2)
    cmds.select(str(joint3))
    cmds.move(10, 5, 0)
    joint4 = cmdx.createNode(type="joint", parent=joint3)
    cmds.select(str(joint4))
    cmds.move(5, 10, 0)

    # Hierarchy won't work here, it's different!
    _reinterpret("match_name.rag", opts={
        "matchBy": constants.MatchByHierarchy
    })

    assert_equals(len(cmdx.ls(type="rdMarker")), 0)

    # But the names are the same
    _reinterpret("match_name.rag", opts={
        "matchBy": constants.MatchByName
    })

    assert_equals(len(cmdx.ls(type="rdMarker")), 4)


def test_import_match_name_clash():
    # 2 or more destinations with the same name
    # results in none of them having that name.
    #
    # - joint1 -> |joint1
    # - joint1 -> |joint1|joint1
    # - joint3 -> joint3
    #

    _new()

    joint1 = cmdx.createNode(type="joint", name="joint1")
    cmds.select(str(joint1))
    cmds.move(0, 5, 0)
    joint2 = cmdx.createNode(type="joint", name="joint1", parent=joint1)
    cmds.select(str(joint2))
    cmds.move(5, 5, 0)
    joint3 = cmdx.createNode(type="joint", name="joint3", parent=joint2)
    cmds.select(str(joint3))
    cmds.move(10, 5, 0)

    _save()

    #
    # o---o---o
    # a   b

    solver = commands.create_solver()
    commands.assign_markers([joint1, joint2, joint3], solver)

    _export("match_name_clash.rag")
    _new()
    _load()

    # Only one of the joints get a match
    _reinterpret("match_name_clash.rag", opts={
        "matchBy": constants.MatchByName
    })

    assert_equals(len(cmdx.ls(type="rdMarker")), 1)
