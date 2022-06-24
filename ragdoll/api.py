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
from functools import wraps as _wraps

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
    InputKinematic,
    InputDynamic,
    InputOff,
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

    # rdMarker.lod enums
    Lod0,
    Lod1,
    Lod2,
    LodCustom,

    MatchByName,
    MatchByHierarchy,
)

#
# cmds-compatible versions of commands
#


@_wraps(_commands.create_solver)
def create_solver(name=None, opts=None):
    return _return(_commands.create_solver(name=name, opts=opts))


@_wraps(_commands.assign_marker)
def assign_marker(transform, solver, opts=None):
    _assert_is_nodepath(transform)
    _assert_is_nodepath(solver)
    _assert_is_a(solver, ("rdSolver", "rdGroup"))

    transform = _cmdx.encode(transform)
    solver = _cmdx.encode(solver)
    return _return(
        _commands.assign_marker(
            transform,
            solver=solver,
            opts=opts
        )
    )


@_wraps(_commands.assign_markers)
def assign_markers(transforms, solver, opts=None):
    _assert_is_nodepaths(transforms)
    _assert_is_nodepath(solver)
    _assert_is_a(solver, ("rdSolver", "rdGroup"))

    solver = _cmdx.encode(solver)
    transforms = [_cmdx.encode(transform) for transform in transforms]

    return _return(
        _commands.assign_markers(
            transforms,
            solver=solver,
            opts=opts
        )
    )


@_wraps(_commands.create_group)
def create_group(solver, opts=None):
    _assert_is_nodepath(solver)
    _assert_is_a(solver, "rdSolver")

    solver = _cmdx.encode(solver)
    return _return(
        _commands.create_group(solver, opts)
    )


@_wraps(_commands.create_ground)
def create_ground(solver, opts=None):
    _assert_is_nodepath(solver)
    _assert_is_a(solver, "rdSolver")

    solver = _cmdx.encode(solver)
    return _return(
        _commands.create_ground(solver, opts)
    )


@_wraps(_commands.create_distance_constraint)
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


@_wraps(_commands.create_pin_constraint)
def create_pin_constraint(child, parent=None, opts=None):
    _assert_is_nodepath(child)
    _assert_is_a(child, "rdMarker")
    parent is None or _assert_is_nodepath(parent)
    parent is None or _assert_is_a(parent, "rdMarker")

    child = _cmdx.encode(child)
    return _return(
        _commands.create_pin_constraint(_child, parent, opts)
    )


@_wraps(_commands.create_fixed_constraint)
def create_fixed_constraint(parent, child, opts=None):
    _assert_is_nodepath(parent)
    _assert_is_nodepath(child)

    parent = _cmdx.encode(parent)
    child = _cmdx.encode(child)
    return _return(
        _commands.create_fixed_constraint(parent, child, opts)
    )


@_wraps(_commands.replace_mesh)
def replace_mesh(marker, mesh, opts=None):
    _assert_is_nodepath(marker)
    _assert_is_nodepath(mesh)
    _assert_is_a(marker, "rdMarker")

    marker = _cmdx.encode(marker)
    mesh = _cmdx.encode(mesh)
    _commands.replace_mesh(marker, mesh=mesh, opts=opts)


@_wraps(_commands.link_solver)
def link_solver(a, b, opts=None):
    _assert_is_nodepath(a)
    _assert_is_nodepath(b)
    _assert_is_a(a, "rdSolver")
    _assert_is_a(b, "rdSolver")

    a = _cmdx.encode(a)
    b = _cmdx.encode(b)
    _commands.link_solver(a, b, opts=opts)


@_wraps(_commands.unlink_solver)
def unlink_solver(solver, opts=None):
    _assert_is_nodepath(solver)
    _assert_is_a(solver, "rdSolver")

    solver = _cmdx.encode(solver)
    _commands.unlink_solver(solver, opts=opts)


@_wraps(_commands.retarget_marker)
def retarget_marker(marker, transform, opts=None):
    _assert_is_nodepath(marker)
    _assert_is_nodepath(transform)

    _assert_is_a(marker, "rdMarker")
    _assert_is_a(transform, _cmdx.kDagNode)

    marker = _cmdx.encode(marker)
    transform = _cmdx.encode(transform)
    _commands.retarget_marker(marker, transform, opts=opts)


@_wraps(_commands.unparent_marker)
def untarget_marker(marker, opts=None):
    _assert_is_a(marker, "rdMarker")

    marker = _cmdx.encode(marker)
    _commands.untarget_marker(marker, opts=opts)


@_wraps(_commands.reparent_marker)
def reparent_marker(child, parent, opts=None):
    _assert_is_nodepath(child)
    _assert_is_nodepath(parent)
    _assert_is_a(child, "rdMarker")
    _assert_is_a(parent, "rdMarker")

    child = _cmdx.encode(child)
    parent = _cmdx.encode(parent)
    _commands.reparent_marker(child, parent, opts=opts)


@_wraps(_commands.unparent_marker)
def unparent_marker(child, opts=None):
    _assert_is_a(child, "rdMarker")

    child = _cmdx.encode(child)
    _commands.unparent_marker(child, opts=opts)


@_wraps(_commands.delete_physics)
def delete_physics(nodes):
    assert isinstance(nodes, (list, tuple)), "First input must be a list"
    _assert_is_nodepaths(nodes)
    nodes = [_cmdx.encode(node) for node in nodes]
    _commands.delete_physics(nodes)


@_wraps(_commands.delete_all_physics)
def delete_all_physics():
    _commands.delete_all_physics()


@_wraps(_recording.record)
def record_physics(solver, opts=None):
    _assert_is_a(solver, "rdSolver")
    solver = _cmdx.encode(solver)
    _recording.record(solver, opts)


@_wraps(_dump.export)
def export_physics(fname=None, opts=None):
    return _dump.export(fname, opts)


@_wraps(_dump.reinterpret)
def reinterpret_physics(fname, opts=None):
    return _dump.reinterpret(fname, opts)


#
# Internals
#


def _assert_is_nodepath(value):
    assert (
        isinstance(value, _cmdx.string_types) and
        _cmdx.exists(value, strict=False)
    ), "%r must be the full path to a node." % value


def _assert_is_a(value, a):
    assert _cmdx.encode(value).isA(a), "%s was not a %s" % (value, a)


def _assert_is_nodepaths(values):
    for value in values:
        _assert_is_nodepath(value)


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
createGroup = create_group
assignMarker = assign_marker
assignMarkers = assign_markers
createGround = create_ground
createDistanceConstraint = create_distance_constraint
createPinConstraint = create_pin_constraint
createFixedConstraint = create_fixed_constraint
linkSolver = link_solver
unlinkSolver = unlink_solver
reparentMarker = reparent_marker
unparentMarker = unparent_marker
retargetMarker = retarget_marker
untargetMarker = untarget_marker
replaceMesh = replace_mesh
exportPhysics = export_physics
recordPhysics = record_physics
reinterpretPhysics = reinterpret_physics
deletePhysics = delete_physics
deleteAllPhysics = delete_all_physics


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
    "InputKinematic",
    "InputDynamic",
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
    "Lod0",
    "Lod1",
    "Lod2",
    "LodCustom",
    "MatchByName",
    "MatchByHierarchy",

    # Main
    "createSolver",
    "createGroup",
    "assignMarkers",
    "assignMarker",
    "createDistanceConstraint",
    "createPinConstraint",
    "createFixedConstraint",

    "linkSolver",
    "unlinkSolver",
    "retargetMarker",
    "untargetMarker",
    "reparentMarker",
    "unparentMarker",
    "replaceMesh",

    "exportPhysics",
    "recordPhysics",
    "reinterpretPhysics",

    "deletePhysics",
    "deleteAllPhysics",

    # Deprecated
    "InputOff",
    "InputGuide",
]
