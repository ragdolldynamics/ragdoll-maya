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
    markers = commands.assign_markers([a, b, c], group)

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
    markers = commands.assign_markers([a, b, c], group)

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
    commands.assign_markers([a, b, c], group)

    cmdx.delete(group)

    assert_equals(len(cmdx.ls(type="rdMarker")), 0)


def test_group_with_existing():
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    group = commands.create_group(solver)
    commands.assign_markers([a, b], group)

    marker = commands.assign_marker(c, group)

    assert_equals(marker["startState"].output(), group)


def test_merge_solvers():
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver1 = commands.create_solver()
    solver2 = commands.create_solver()
    commands.assign_markers([a, b], solver1)
    c_marker = commands.assign_marker(c, solver2)

    commands.merge_solvers(solver1, solver2)
    assert not solver1.exists, "%s should not have existed anymore" % solver1
    assert c_marker["startState"].output(type="rdSolver") is solver2


def test_move_to_solver():
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver1 = commands.create_solver()
    solver2 = commands.create_solver()
    commands.assign_markers([a, b], solver1)
    c_marker = commands.assign_marker(c, solver2)

    commands.move_to_solver(c_marker, solver1)
    assert not solver2.exists, "%s should not have existed anymore" % solver2
    assert c_marker["startState"].output(type="rdSolver") is solver1


def test_extract_from_solver():
    _new()

    a = cmdx.create_node("transform", name="a")
    b = cmdx.create_node("transform", name="b", parent=a)
    c = cmdx.create_node("transform", name="c", parent=b)

    solver = commands.create_solver()
    markers = commands.assign_markers([a, b, c], solver)

    new_solver = commands.extract_from_solver(markers[:1])
    assert new_solver and new_solver.isA("rdSolver")
    assert solver.exists, "The original solver vanished"
    assert markers[0]["startState"].output(type="rdSolver") is new_solver
