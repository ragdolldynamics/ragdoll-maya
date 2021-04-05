"""Public API

These members differ from ragdoll.commands and friends
in that they take and return native Maya strings as
is typical of the maya.cmds module.

Everything exposed in this module is permanent
and backwards compatible with every version of
Ragdoll for all time.

"""

# Constants
from .commands import (
    BoxShape,
    SphereShape,
    CapsuleShape,
    ConvexHullShape,
)

# cmds-compatible versions of commands
# Note that these still exist in commands.py, the difference being
# the return-type; api -> strings and commands -> cmdx instances
from .commands import _to_cmds
createScene = _to_cmds("create_scene")
createRigid = _to_cmds("create_rigid")
createActiveRigid = _to_cmds("create_active_rigid")
createPassiveRigid = _to_cmds("create_passive_rigid")
createCollider = _to_cmds("create_passive_rigid")
pointConstraint = _to_cmds("point_constraint")
orientConstraint = _to_cmds("orient_constraint")
hingeConstraint = _to_cmds("hinge_constraint")
socketConstraint = _to_cmds("socket_constraint")
parentConstraint = _to_cmds("parent_constraint")
convertRigid = _to_cmds("convert_rigid")
convertToPoint = _to_cmds("convert_to_point")
convertToOrient = _to_cmds("convert_to_orient")
convertToHinge = _to_cmds("convert_to_hinge")
convertToSocket = _to_cmds("convert_to_socket")
convertToParent = _to_cmds("convert_to_parent")
createAbsoluteControl = _to_cmds("create_absolute_control")
createRelativeControl = _to_cmds("create_relative_control")
createActiveControl = _to_cmds("create_active_control")
createKinematicControl = _to_cmds("create_kinematic_control")
transferAttributes = _to_cmds("transfer_attributes")
transferRigid = _to_cmds("transfer_rigid")
transferConstraint = _to_cmds("transfer_constraint")
editConstraintFrames = _to_cmds("edit_constraint_frames")
createForce = _to_cmds("create_force")
createSlice = _to_cmds("create_slice")
assignForce = _to_cmds("assign_force")

from .tools import _to_cmds
createChain = _to_cmds("create_chain")
createMuscle = _to_cmds("create_muscle")
createCharacter = _to_cmds("create_character")

# Backwards compatibility
createCollider = _to_cmds("create_passive_rigid")
del _to_cmds


__all__ = [
    "BoxShape",
    "SphereShape",
    "CapsuleShape",
    "ConvexHullShape",

    # Camel case
    "createScene",
    "createRigid",
    "createChain",
    "createAbsoluteControl",
    "createRelativeControl",
    "createActiveControl",
    "createKinematicControl",
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
    "transferRigid",
    "transferAttributes",
    "transferConstraint",
    "editConstraintFrames",
    "createForce",
    "createSlice",
    "assignForce",

    # Backwards compatibility
    "createCollider",
    "createActiveRigid",
    "createPassiveRigid",
]
