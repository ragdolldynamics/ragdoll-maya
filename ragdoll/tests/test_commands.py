from ragdoll import commands
from ragdoll.vendor import cmdx

from . import _new

from nose.tools import (
    assert_equals,
)


def test_assign_with_group():
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    group = commands.create_group(solver)
    markers = commands.assign_markers([a, b, c], solver, group)

    for marker in markers:
        assert_equals(marker["startState"].output(type="rdGroup"), group)


def test_group():
    # Grouping and ungrouping
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    markers = commands.assign_markers([a, b, c], solver)

    group = commands.group_markers(markers)

    for marker in markers:
        assert_equals(marker["startState"].output(type="rdGroup"), group)


def test_ungroup_delete_empty():
    # Ungrouping all markers from a group automatically deletes that group
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    group = commands.create_group(solver)
    markers = commands.assign_markers([a, b, c], solver, group)

    commands.ungroup_markers(markers)

    assert_equals(len(cmdx.ls(type="rdGroup")), 0)


def test_delete_group_deletes_markers():
    # Deleting the group automatically deletes any associated markers
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    group = commands.create_group(solver)
    commands.assign_markers([a, b, c], solver, group)

    cmdx.delete(group)

    assert_equals(len(cmdx.ls(type="rdMarker")), 0)
