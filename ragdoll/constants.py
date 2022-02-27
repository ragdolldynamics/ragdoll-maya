import os

# Environment variables
RAGDOLL_DEVELOPER = bool(os.getenv("RAGDOLL_DEVELOPER"))
RAGDOLL_PLUGIN = os.getenv("RAGDOLL_PLUGIN", "ragdoll")
RAGDOLL_PLUGIN_NAME = os.path.basename(RAGDOLL_PLUGIN)
RAGDOLL_NO_STARTUP_DIALOG = bool(os.getenv("RAGDOLL_NO_STARTUP_DIALOG"))
RAGDOLL_AUTO_SERIAL = os.getenv("RAGDOLL_AUTO_SERIAL")
RAGDOLL_NO_TELEMETRY = bool(os.getenv("RAGDOLL_NO_TELEMETRY"))
RAGDOLL_FLOATING = bool(os.getenv("RAGDOLL_FLOATING"))
RAGDOLL_TELEMETRY = bool(os.getenv("RAGDOLL_TELEMETRY"))

CREATE_NEW_SOLVER = 0

# Shape types
BoxShape = 0
SphereShape = 1
CapsuleShape = 2
CylinderShape = 2
ConvexHullShape = 4
MeshShape = 4  # Alias

PGSSolverType = 0
TGSSolverType = 1

# Markers
InputInherit = 0
InputKinematic = 2
InputDynamic = 3

DisplayDefault = 0
DisplayWire = 1
DisplayConstant = 2
DisplayShaded = 3
DisplayMass = 4
DisplayFriction = 5
DisplayRestitution = 6
DisplayVelocity = 7
DisplayContacts = 8

# Record
Off = 0
FromRetargeting = 1
FromStart = 2

# Cache
StaticCache = 1
DynamicCache = 2

DensityOff = 0
DensityCotton = 1
DensityWood = 2
DensityFlesh = 3
DensityUranium = 4
DensityBlackHole = 5
DensityCustom = 6

FrameskipPause = 0
FrameskipIgnore = 1

ImportLoad = "Load"
ImportReinterpret = "Reinterpret"
ImportSolverFromFile = 0
ImportSolverFromScene = 1

ImportNamespaceOff = " "
ImportNamespaceFromFile = ""

StartTimeRangeStart = 0
StartTimeAnimationStart = 1
StartTimeCustom = 2

Lod0 = 0
Lod1 = 1
Lod2 = 2
LodCustom = 3

LodLessThan = 0
GreaterThan = 1
LodEqual = 2
LodNotEqual = 3

MatchByName = 0
MatchByHierarchy = 1

RecordFastAndLoose = 0
RecordNiceAndSteady = 1

ComCentroid = 0
VolumetricCentroids = 1

MotionInherit = -1
MotionLocked = 0
MotionLimited = 1
MotionFree = 2

DecompositionOff = 0
DecompositionIslands = 1
DecompositionAutomatic = 2

# cacheMedia enum indices
Off = 0
On = 1
All = 2


#
# Deprecated
#

InputGuide = 3
InputOff = 3
X = "X"
Y = "Y"
Z = "Z"
OrientToNeighbour = 0
OrientToJoint = 1
QuaternionInterpolation = 1
SteppedBlendMethod = 0
SmoothBlendMethod = 1
Epsilon = 0.001
Transform = "transform"
Joint = "joint"
nConstraintStyle = 0
MayaConstraintStyle = 1
RagdollStyle = 2
BakeAll = 0
BakeSelected = 1
AutoShape = 0
ControlColor = (0.443, 0.705, 0.952)
WhiteIndex = 17
YellowIndex = 17
InitialShapeAuto = 0
InitialShapeBox = 1
InitialShapeSphere = 2
InitialShapeCapsule = 3
InitialShapeMesh = 4
CreateActive = 0
CreatePassive = 1
ConvertActive = 0
ConvertPassive = 1
ExistingIgnore = 0
ExistingFollow = 1
Abort = 0
Overwrite = 1
Blend = 2
PointForce = 0
UniformForce = 1
TurbulenceForce = 2
PushForce = 3
PullForce = 4
WindForce = 5
Off = 0
On = 1
Kinematic = 1
Passive = 1
Driven = 2
PointConstraint = 0
OrientConstraint = 1
ParentConstraint = 2
HingeConstraint = 3
SocketConstraint = 4
IgnoreContactsConstraint = 5
NoLimit = -1
CustomPreset = 0
HingePreset = 1
RagdollPreset = 2
SuspensionPreset = 3
GuideInherit = 0
GuideRelative = 1
GuideAbsolute = 2
GuideCustom = 3
GuideLocal = GuideCustom
GuideWorld = GuideAbsolute
Both = 0
Parent = 1
Child = 2
WaterDensity = 1
WoodDensity = 2
FeatherDensity = 3
AirDensity = 4
