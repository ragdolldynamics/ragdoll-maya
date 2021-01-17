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
from .commands import to_cmds
createScene = to_cmds("create_scene")
createRigid = to_cmds("create_rigid")
createActiveRigid = to_cmds("create_active_rigid")
createPassiveRigid = to_cmds("create_passive_rigid")
createCollider = to_cmds("create_passive_rigid")
pointConstraint = to_cmds("point_constraint")
orientConstraint = to_cmds("orient_constraint")
hingeConstraint = to_cmds("hinge_constraint")
socketConstraint = to_cmds("socket_constraint")
parentConstraint = to_cmds("parent_constraint")
convertRigid = to_cmds("convert_rigid")
convertToPoint = to_cmds("convert_to_point")
convertToOrient = to_cmds("convert_to_orient")
convertToHinge = to_cmds("convert_to_hinge")
convertToSocket = to_cmds("convert_to_socket")
convertToParent = to_cmds("convert_to_parent")
createAbsoluteControl = to_cmds("create_absolute_control")
createRelativeControl = to_cmds("create_relative_control")
createActiveControl = to_cmds("create_active_control")
createKinematicControl = to_cmds("create_kinematic_control")
transferAttributes = to_cmds("transfer_attributes")
transferRigid = to_cmds("transfer_rigid")
transferConstraint = to_cmds("transfer_constraint")
editConstraintFrames = to_cmds("edit_constraint_frames")
createForce = to_cmds("create_force")
createSlice = to_cmds("create_slice")
assignForce = to_cmds("assign_force")

# Backwards compatibility
createCollider = to_cmds("create_passive_rigid")
del to_cmds


__all__ = [
    "BoxShape",
    "SphereShape",
    "CapsuleShape",
    "ConvexHullShape",

    # Camel case
    "createScene",
    "createRigid",
    "createActiveRigid",
    "createPassiveRigid",
    "createCollider",
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
]
