"""Public API

Ragdoll doesn't deal with nodes as strings, like maya.cmds does.
But it still needs to interoperate with it. So this module converts
string-based nodes you throw at it, along converting any output
that Ragdoll produces into strings such that the results can be
passed back to cmds, such as cmds.setAttr.

Everything exposed in this module is permanent and backwards
compatible with every version of Ragdoll for all time.

"""

# Internals, temporary
from .vendor import cmdx as _cmdx
from . import (
    commands as _commands,
    recording as _recording,
    dump as _dump,
)

# Inherit docstring from source command
import functools as _functools


# Constants
from .constants import (
    # rdSolver.frameskipMethod enums
    FrameskipPause,
    FrameskipIgnore,

    # rdMarker.displayType enums
    DisplayDefault,
    DisplayWire,
    DisplayConstant,
    DisplayShaded,
    DisplayMass,
    DisplayFriction,
    DisplayRestitution,
    DisplayVelocity,
    DisplayContacts,

    # rdMarker.inputType enums
    InputInherit,
    InputOff,
    InputKinematic,
    InputGuide,

    # rdSolver.type enums
    PGSSolverType,
    TGSSolverType,

    # rdMarker.shapeType enums
    BoxShape,
    SphereShape,
    CapsuleShape,
    MeshShape,
    ConvexHullShape,

    # rdMarker.densityType enums
    DensityOff,
    DensityCotton,
    DensityWood,
    DensityFlesh,
    DensityUranium,
    DensityBlackHole,
    DensityCustom,

    # rdSolver.startTime enums
    StartTimeRangeStart,
    StartTimeAnimationStart,
    StartTimeCustom,
)

#
# cmds-compatible versions of commands
#


@_functools.wraps(_commands.create_solver)
def create_solver(name=None, opts=None):
    return _return(_commands.create_solver(name=name, opts=opts))


@_functools.wraps(_commands.assign_marker)
def assign_marker(transform, solver, opts=None):
    _assert_is_nodepath(transform)
    _assert_is_nodepath(solver)

    transform = _cmdx.encode(transform)
    solver = _cmdx.encode(solver)
    return _return(
        _commands.assign_marker(transform, solver=solver, opts=opts)
    )


@_functools.wraps(_commands.assign_markers)
def assign_markers(transforms, solver, opts=None):
    _assert_is_nodepaths(transforms)
    _assert_is_nodepath(solver)
    _assert_is_a(solver, "rdSolver")

    solver = _cmdx.encode(solver)
    transforms = [_cmdx.encode(transform) for transform in transforms]

    return _return(
        _commands.assign_markers(transforms, solver=solver, opts=opts)
    )


@_functools.wraps(_commands.create_distance_constraint)
def create_distance_constraint(parent, child, opts=None):
    _assert_is_nodepath(parent)
    _assert_is_nodepath(child)
    _assert_is_a(parent, "rdMarker")
    _assert_is_a(child, "rdMarker")

    parent = _cmdx.encode(parent)
    child = _cmdx.encode(child)
    return _return(
        _commands.create_distance_constraint(parent, child, opts)
    )


@_functools.wraps(_commands.create_distance_constraint)
def create_pin_constraint(parent, child=None, opts=None):
    _assert_is_nodepath(parent)
    _assert_is_nodepath(child)
    _assert_is_a(parent, "rdMarker")
    _assert_is_a(child, "rdMarker")

    parent = _cmdx.encode(parent)
    return _return(
        _commands.create_pin_constraint(parent, opts)
    )


@_functools.wraps(_commands.create_distance_constraint)
def create_fixed_constraint(parent, child=None, opts=None):
    _assert_is_nodepath(parent)
    _assert_is_nodepath(child)

    parent = _cmdx.encode(parent)
    child = _cmdx.encode(child)
    return _return(
        _commands.create_fixed_constraint(parent, child, opts)
    )


@_functools.wraps(_commands.replace_mesh)
def replace_mesh(marker, mesh, opts=None):
    _assert_is_nodepath(marker)
    _assert_is_nodepath(mesh)
    _assert_is_a(marker, "rdMarker")

    marker = _cmdx.encode(marker)
    mesh = _cmdx.encode(mesh)
    return _return(
        _commands.replace_mesh(marker, mesh=mesh, opts=opts)
    )


@_functools.wraps(_recording.record)
def record(solver, opts=None):
    _assert_is_a(solver, "rdSolver")
    solver = _cmdx.encode(solver)
    _recording.record(solver, opts)


@_functools.wraps(_dump.export)
def export(fname, opts=None):
    return _dump.export(fname, opts)


@_functools.wraps(_dump.reinterpret)
def reinterpret(fname, opts=None):
    return _dump.reinterpret(fname, opts)


#
# Internals
#


def _assert_is_nodepath(value):
    assert (
        isinstance(value, _cmdx.string_types) and
        _cmdx.exists(value, strict=False)
    ), "%s must be the full path to a node." % value


def _assert_is_a(value, a):
    assert _cmdx.encode(value).isA(a)


def _assert_is_nodepaths(values):
    for value in values:
        _assert_is_nodepaths(value)


def _return(result):
    """Convert Ragdoll types to plain strings, for maya.cmds"""

    if isinstance(result, (tuple, list)):
        for index, value in enumerate(result):
            if isinstance(value, _cmdx.Node):
                result[index] = value.shortestPath()
            elif isinstance(value, _cmdx.Plug):
                result[index] = value.path()
            elif isinstance(result, _cmdx.string_types):
                pass
            else:
                raise TypeError("Unsupported return value '%s'" % value)
    else:
        if isinstance(result, _cmdx.Node):
            result = result.shortestPath()
        elif isinstance(result, _cmdx.Plug):
            result = result.path()
        elif isinstance(result, _cmdx.string_types):
            pass
        else:
            raise TypeError("Unsupported return value '%s'" % result)

    return result


#
# Camel-case alternative syntax
#
createSolver = create_solver
assignMarker = assign_marker
assignMarkers = assign_markers
createDistanceConstraint = create_distance_constraint
createPinConstraint = create_pin_constraint
createFixedConstraint = create_fixed_constraint


# Members are repeated here in __all__ for two reasons:
# 1. Linting picks up any member in here that isn't present above,
#    and can warn the author about it.
# 2. In the unlikely, and ill-advised event of a from ragdoll.api import *
#    these are the members that actually get imported. No private members.
__all__ = [

    # Constants

    "FrameskipPause",
    "FrameskipIgnore",
    "DisplayDefault",
    "DisplayWire",
    "DisplayConstant",
    "DisplayShaded",
    "DisplayMass",
    "DisplayFriction",
    "DisplayRestitution",
    "DisplayVelocity",
    "DisplayContacts",
    "InputInherit",
    "InputOff",
    "InputKinematic",
    "InputGuide",
    "PGSSolverType",
    "TGSSolverType",
    "BoxShape",
    "SphereShape",
    "CapsuleShape",
    "MeshShape",
    "ConvexHullShape",
    "DensityOff",
    "DensityCotton",
    "DensityWood",
    "DensityFlesh",
    "DensityUranium",
    "DensityBlackHole",
    "DensityCustom",
    "StartTimeRangeStart",
    "StartTimeAnimationStart",
    "StartTimeCustom",

    # Main

    "create_solver",
    "assign_marker",
    "assign_markers",
    "create_fixed_constraint",
    "create_distance_constraint",
    "create_pin_constraint",

    "record",
    "export",
    "reinterpret",

    # Camel case

    "createSolver",
    "assignMarker",
    "assignMarkers",
    "createDistanceConstraint",
    "createPinConstraint",
    "createFixedConstraint",
]
