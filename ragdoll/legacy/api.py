"""Public API

These members differ from ragdoll.commands and friends
in that they take and return native Maya strings as
is typical of the maya.cmds module.

Everything exposed in this module is permanent and backwards
compatible with every version of Ragdoll for all time.

"""

# Internals, temporary
from . import commands as _commands
from .tools import chain_tool
from ..vendor import cmdx as _cmdx

# Inherit docstring from source command
import functools as _functools


# Constants
from ..constants import (
    BoxShape,
    SphereShape,
    CapsuleShape,
    MeshShape,
    ConvexHullShape,
)

#
# cmds-compatible versions of _commands
#


@_functools.wraps(_commands.create_scene)
def createScene(name=None, parent=None):
    parent = _converted(parent)
    return _output(_commands.create_scene(name=name, parent=parent))


@_functools.wraps(_commands.create_rigid)
def createRigid(node, scene, opts=None):
    node = _converted(node)
    scene = _converted(scene)
    return _output(_commands.create_rigid(node, scene, opts=opts))


@_functools.wraps(chain_tool.create)
def createChain(links, scene, opts=None):
    assert isinstance(links, (tuple, list)), "links must be list"
    links = [_converted(link) for link in links]
    scene = _converted(scene)
    return _output(chain_tool.create(links, scene, opts=opts))


@_functools.wraps(_commands.create_active_rigid)
def createActiveRigid(node, scene, opts=None):
    return createRigid(node, scene, opts=dict({"passive": False}, **opts))


@_functools.wraps(_commands.create_passive_rigid)
def createPassiveRigid(node, scene, opts=None):
    return createRigid(node, scene, opts=dict({"passive": True}, **opts))


@_functools.wraps(_commands.create_constraint)
def createConstraint(parent, child):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.create_constraint(parent, child))


@_functools.wraps(_commands.point_constraint)
def pointConstraint(parent, child, opts=None):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.point_constraint(parent, child, opts=opts))


@_functools.wraps(_commands.orient_constraint)
def orientConstraint(parent, child, opts=None):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.orient_constraint(parent, child, opts=opts))


@_functools.wraps(_commands.hinge_constraint)
def hingeConstraint(parent, child, opts=None):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.hinge_constraint(parent, child, opts=opts))


@_functools.wraps(_commands.socket_constraint)
def socketConstraint(parent, child, opts=None):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.socket_constraint(parent, child, opts=opts))


@_functools.wraps(_commands.parent_constraint)
def parentConstraint(parent, child, opts=None):
    parent = _converted(parent)
    child = _converted(child)
    return _output(_commands.parent_constraint(parent, child, opts=opts))


@_functools.wraps(_commands.animation_constraint)
def animationConstraint(rigid, opts=None):
    rigid = _converted(rigid)
    return _output(_commands.animation_constraint(rigid, opts=opts))


@_functools.wraps(_commands.convert_rigid)
def convertRigid(rigid, opts=None):
    rigid = _converted(rigid)
    return _output(_commands.convert_rigid(rigid, opts=opts))


@_functools.wraps(_commands.convert_to_point)
def convertToPoint(constraint, opts=None):
    constraint = _converted(constraint)
    return _output(_commands.convert_to_point(constraint, opts=opts))


@_functools.wraps(_commands.convert_to_orient)
def convertToOrient(constraint, opts=None):
    constraint = _converted(constraint)
    return _output(_commands.convert_to_orient(constraint, opts=opts))


@_functools.wraps(_commands.convert_to_hinge)
def convertToHinge(constraint, opts=None):
    constraint = _converted(constraint)
    return _output(_commands.convert_to_hinge(constraint, opts=opts))


@_functools.wraps(_commands.convert_to_socket)
def convertToSocket(constraint, opts=None):
    constraint = _converted(constraint)
    return _output(_commands.convert_to_socket(constraint, opts=opts))


@_functools.wraps(_commands.convert_to_parent)
def convertToParent(constraint, opts=None):
    constraint = _converted(constraint)
    return _output(_commands.convert_to_parent(constraint, opts=opts))


@_functools.wraps(_commands.set_initial_state)
def setInitialState(rigids):
    rigids = _converted(rigids)
    return _output(_commands.set_initial_state(rigids))


@_functools.wraps(_commands.set_initial_state)
def clearInitialState(rigids):
    rigids = _converted(rigids)
    return _output(_commands.clear_initial_state(rigids))


@_functools.wraps(_commands.transfer_attributes)
def transferAttributes(a, b, opts=None):
    a = _converted(a)
    b = _converted(b)
    return _output(_commands.transfer_attributes(a, b, opts=opts))


@_functools.wraps(_commands.edit_constraint_frames)
def editConstraintFrames(constraint):
    constraint = _converted(constraint)
    return _output(_commands.edit_constraint_frames(constraint))


@_functools.wraps(_commands.create_force)
def createForce(type, scene):
    scene = _converted(scene)
    return _output(_commands.create_force(type, scene))


@_functools.wraps(_commands.assign_force)
def assignForce(rigid, force):
    rigid = _converted(rigid)
    force = _converted(force)
    return _output(_commands.assign_force(rigid, force))


@_functools.wraps(_commands.create_slice)
def createSlice(scene):
    scene = _converted(scene)
    return _output(_commands.create_slice(scene))


def _converted(node):
    if isinstance(node, _cmdx.string_types):
        node = _cmdx.encode(node)
    return node


def _output(result):
    if isinstance(result, (tuple, list)):
        for index, value in enumerate(result):
            if isinstance(value, _cmdx.Node):
                result[index] = value.shortestPath()
            if isinstance(value, _cmdx.Plug):
                result[index] = value.path()
    else:
        if isinstance(result, _cmdx.Node):
            result = result.shortestPath()
        if isinstance(result, _cmdx.Plug):
            result = result.path()

    return result


__all__ = [
    "BoxShape",
    "SphereShape",
    "CapsuleShape",
    "MeshShape",
    "ConvexHullShape",

    # Camel case
    "createScene",
    "createRigid",
    "createChain",
    "pointConstraint",
    "orientConstraint",
    "hingeConstraint",
    "socketConstraint",
    "parentConstraint",
    "convertRigid",
    "convertToPoint",
    "convertToOrient",
    "convertToHinge",
    "convertToSocket",
    "convertToParent",
    "transferAttributes",
    "editConstraintFrames",
    "createForce",
    "createSlice",
    "assignForce",
]
