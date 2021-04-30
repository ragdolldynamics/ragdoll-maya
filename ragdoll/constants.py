import os

# Environment variables
RAGDOLL_DEVELOPER = bool(os.getenv("RAGDOLL_DEVELOPER"))
RAGDOLL_PLUGIN = os.getenv("RAGDOLL_PLUGIN", "ragdoll")
RAGDOLL_PLUGIN_NAME = os.path.basename(RAGDOLL_PLUGIN)
RAGDOLL_NO_STARTUP_DIALOG = bool(os.getenv("RAGDOLL_NO_STARTUP_DIALOG"))
RAGDOLL_AUTO_SERIAL = os.getenv("RAGDOLL_AUTO_SERIAL")

CREATE_NEW_SOLVER = 0

# Axes
X = "X"
Y = "Y"
Z = "Z"

# Shape types
AutoShape = 0
BoxShape = 0
SphereShape = 1
CapsuleShape = 2
CylinderShape = 2
ConvexHullShape = 4
MeshShape = 4  # Alias

# Dynamic states
Off = 0
On = 1
Kinematic = 1
Passive = 1
Driven = 2

# Constraint types
PointConstraint = 0
OrientConstraint = 1
ParentConstraint = 2
HingeConstraint = 3
SocketConstraint = 4

# cacheMedia enum indices
Off = 0
On = 1
All = 2

OrientToNeighbour = 0
OrientToJoint = 1

PointForce = 0
UniformForce = 1
TurbulenceForce = 2
PushForce = 3
PullForce = 4
WindForce = 5

PGSSolverType = 0
TGSSolverType = 1

ControlColor = (0.443, 0.705, 0.952)  # Blue

# Enums
InitialShapeAuto = 0
InitialShapeBox = 1
InitialShapeSphere = 2
InitialShapeCapsule = 3
InitialShapeMesh = 4

CreateActive = 0
CreatePassive = 1
ConvertOpposite = 0
ConvertActive = 1
ConvertPassive = 2
ExistingIgnore = 0
ExistingFollow = 1

Abort = 0
Overwrite = 1
Blend = 2

QuaternionInterpolation = 1

SteppedBlendMethod = 0
SmoothBlendMethod = 1

Epsilon = 0.001
