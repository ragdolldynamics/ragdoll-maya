"""Functionality for scripting

These provide low-level access to node creation and scenegraph
manipulation and are meant for use in automation, pipeline and rigging.

These do not depend on scene selection, user preferences or Maya state.

"""

import re
import os
import sys
import random
import logging
import functools

from maya import cmds
from maya.api import OpenMayaAnim as oma
from .vendor import cmdx

log = logging.getLogger("ragdoll")

DEVELOPER = bool(os.getenv("RAGDOLL_DEVELOPER", None))

# Axes
Auto = "Auto"
X = "X"
Y = "Y"
Z = "Z"

# Shape types
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

ControlColor = (0.443, 0.705, 0.952)

Abort = 0
Overwrite = 1
Blend = 2

QuaternionInterpolation = 1

SteppedBlendMethod = 0
SmoothBlendMethod = 1

Epsilon = 0.001

# Python 2 backwards compatibility
try:
    string_types = basestring,
except NameError:
    string_types = str,


def to_cmds(name):
    """Convert cmdx instances to maya.cmds-compatible strings

    Two types of cmdx instances are returned natively, `Node` and `Plug`
    Any other return value remains unscathed.

    """

    func = getattr(sys.modules[__name__], name)

    @functools.wraps(func)
    def to_cmds_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, (tuple, list)):
            for index, entry in enumerate(result):
                if isinstance(entry, cmdx.Node):
                    result[index] = entry.shortestPath()

                if isinstance(entry, cmdx.Plug):
                    result[index] = entry.path()

        elif isinstance(result, cmdx.Node):
            result = result.shortestPath()

        elif isinstance(result, cmdx.Plug):
            result = result.path()

        return result

    return to_cmds_wrapper


def with_undo_chunk(func):
    """Consider the entire function one big giant undo chunk"""
    @functools.wraps(func)
    def _undo_chunk(*args, **kwargs):
        try:
            cmds.undoInfo(chunkName=func.__name__, openChunk=True)
            return func(*args, **kwargs)
        finally:
            cmds.undoInfo(chunkName=func.__name__, closeChunk=True)

    return _undo_chunk


class UserAttributes(object):
    """User attributes appear on the original controllers
     __________________
    |                  |
    |      leftArm_ctl |
    |                  |
    | Translate X  0.0 |
    | Translate Y  0.0 |
    | Translate Z  0.0 |
    |    Rotate X  0.0 |
    |    Rotate Y  0.0 |
    |    Rotate Z  0.0 |
    |                  |
    |          Ragdoll |
    |        Mass  0.0 |  <----- User Attributes
    |    Strength  0.0 |
    |__________________|

    Arguments:
        source (cmdx.DagNode): Original node, e.g. an rdRigid
        target (cmdx.DagNode): Typically the animation control

    """

    def __init__(self, source, target):
        self._source = source
        self._target = target
        self._added = []

    def do_it(self):
        if not self._added:
            pass

        added = []

        while self._added:
            attr = self._added.pop(0)

            if isinstance(attr, cmdx._AbstractAttribute):
                if self._target.has_attr(attr["name"]):
                    cmds.deleteAttr("%s.%s" % (self._target, attr["name"]))

                with cmdx.DagModifier() as mod:
                    mod.add_attr(self._target, attr)

                name = attr["name"]
                plug = self._target[attr["name"]]

            else:
                attr, long_name, nice_name = attr
                name = long_name or attr

                if self._target.has_attr(name):
                    cmds.deleteAttr("%s.%s" % (self._target, name))

                plug = self.proxy(attr, long_name, nice_name)

            added += [plug]

        with cmdx.DagModifier() as mod:
            for new_plug in added:
                index = self._source["userAttributes"].next_available_index()
                mod.connect(new_plug, self._source["userAttributes"][index])

                # Can't figure out the next available index until the
                # current index has been occupied. And we can't simply
                # linearly increment the index either, as indices are
                # logical, not physical.
                mod.do_it()

    def proxy(self, attr, long_name=None, nice_name=None):
        """Create a proxy attribute for `name` on `target`"""
        name = long_name or attr

        kwargs = {
            "longName": name,
        }

        if nice_name is not None:
            kwargs["niceName"] = nice_name

        kwargs["proxy"] = self._source[attr].path()
        cmds.addAttr(self._target.path(), **kwargs)

        return self._target[name]

    def proxy_2019(self, attr, long_name=None, nice_name=None):
        """Maya 2019 doesn't play well with proxy attributes"""

        name = long_name or attr
        default = cmds.getAttr("%s.%s" % (self._source, attr))

        kwargs = {
            "longName": name,
            "defaultValue": default,
            "keyable": True,
        }

        if nice_name is not None:
            kwargs["niceName"] = nice_name

        cmds.addAttr(self._target.path(), **kwargs)
        cmds.connectAttr("%s.%s" % (self._target, name),
                         "%s.%s" % (self._source, attr))

        return self._target[name]

    def add(self, attr, long_name=None, nice_name=None):
        assert isinstance(attr, string_types), "%s was not a string" % attr
        self._added.append((attr, long_name, nice_name))

    def add_divider(self, label):
        assert isinstance(label, string_types), "%s was not a string" % label
        self._added.append(cmdx.Divider(label))


def add_rigid(mod, rigid, scene):
    assert rigid.type() == "rdRigid", rigid
    assert scene.type() == "rdScene", scene
    assert rigid["startState"].connection() != scene, (
        "%s already a member of %s" % (rigid, scene)
    )

    time = cmdx.encode("time1")
    index = scene["outputObjects"].next_available_index()
    mod.connect(time["outTime"], rigid["currentTime"])
    mod.connect(scene["outputObjects"][index], rigid["nextState"])
    mod.connect(scene["startTime"], rigid["startTime"])
    mod.connect(rigid["startState"], scene["inputActiveStart"][index])
    mod.connect(rigid["currentState"], scene["inputActive"][index])

    # Record for backwards compatibility
    mod.set_attr(rigid["version"], _version())


def add_constraint(mod, con, scene):
    assert con["startState"].connection() != scene, (
        "%s already a member of %s" % (con, scene)
    )

    time = cmdx.encode("time1")
    index = scene["inputConstraintStart"].next_available_index()

    mod.connect(time["outTime"], con["currentTime"])
    mod.connect(con["startState"], scene["inputConstraintStart"][index])
    mod.connect(con["currentState"], scene["inputConstraint"][index])

    # Record for backwards compatibility
    mod.set_attr(con["version"], _version())


def add_force(mod, force, rigid):
    index = rigid["inputForce"].next_available_index()
    mod.connect(force["outputForce"], rigid["inputForce"][index])

    mod.set_attr(force["version"], _version())


def _unique_name(name):
    """Internal utility function"""
    if cmdx.exists(name):
        index = 1
        while cmdx.exists("%s%d" % (name, index)):
            index += 1
        name = "%s%d" % (name, index)

    return name


def _connect_passive(mod, rigid, transform):
    mod.set_attr(rigid["kinematic"], True)
    mod.connect(transform["worldMatrix"][0], rigid["inputMatrix"])


def _connect_active(mod, rigid, transform, existing=Overwrite):
    if existing == Overwrite:
        _connect_active_blend(mod, rigid, transform)

    elif existing == Blend:
        _connect_active_blend(mod, rigid, transform)

    else:  # Abort
        raise ValueError(
            "%s has incoming connections to translate and/or rotate"
            % rigid
        )

    return True


def _connect_active_blend(mod, rigid, transform):
    r"""Constrain rigid to original animation

     ______
    |\     \
    | \_____\                /
    | |     | . . . . . . - o -
    \ |     |              /
     \|_____|

    """

    with cmdx.DGModifier() as dgmod:
        pair_blend = dgmod.create_node("pairBlend", name="blendSimulation")
        dgmod.set_attr(pair_blend["rotInterpolation"], QuaternionInterpolation)
        dgmod.set_attr(pair_blend["isHistoricallyInteresting"], False)

        # Establish initial values, before keyframes
        # Use transform, rather than translate/rotate directly,
        # to account for e.g. jointOrient.
        tm = transform.transform()
        dgmod.set_attr(pair_blend["inTranslate1"], tm.translation())
        dgmod.set_attr(pair_blend["inRotate1"], tm.rotation())

    pair_blend["translateXMode"].hide()
    pair_blend["translateYMode"].hide()
    pair_blend["translateZMode"].hide()
    pair_blend["rotateMode"].hide()
    pair_blend["rotInterpolation"].hide()

    mod.connect(rigid["outputTranslateX"], pair_blend["inTranslateX2"])
    mod.connect(rigid["outputTranslateY"], pair_blend["inTranslateY2"])
    mod.connect(rigid["outputTranslateZ"], pair_blend["inTranslateZ2"])
    mod.connect(rigid["outputRotateX"], pair_blend["inRotateX2"])
    mod.connect(rigid["outputRotateY"], pair_blend["inRotateY2"])
    mod.connect(rigid["outputRotateZ"], pair_blend["inRotateZ2"])

    # Transfer existing animation/connections
    prior_to_pairblend = {
        "tx": "inTranslateX1",
        "ty": "inTranslateY1",
        "tz": "inTranslateZ1",
        "rx": "inRotateX1",
        "ry": "inRotateY1",
        "rz": "inRotateZ1",
    }

    for attr, plug in prior_to_pairblend.items():
        src = transform[attr].connection(destination=False, plug=True)

        if src is not None:
            pair_attr = prior_to_pairblend[attr]
            dst = pair_blend[pair_attr]
            mod.connect(src, dst)

    _connect_transform(mod, pair_blend, transform)

    mod.connect(rigid["drivenBySimulation"], pair_blend["weight"])

    # Pair blend directly feeds into the drive matrix
    with cmdx.DGModifier() as dgmod:
        compose = dgmod.create_node("composeMatrix", name="composePairBlend")

        # Account for node being potentially parented somewhere
        mult = dgmod.create_node("multMatrix", name="makeAbsolute")

    mod.connect(pair_blend["inTranslate1"], compose["inputTranslate"])
    mod.connect(pair_blend["inRotate1"], compose["inputRotate"])
    mod.connect(compose["outputMatrix"], mult["matrixIn"][0])

    # Reproduce a parent hierarchy, but don't connect it to avoid cycle
    mod.set_attr(mult["matrixIn"][1], transform["parentMatrix"][0].asMatrix())

    # Support hard manipulation
    # For e.g. transitioning between active and passive
    mod.connect(mult["matrixSum"], rigid["inputMatrix"])

    # Keep channel box clean
    mod.set_attr(compose["isHistoricallyInteresting"], False)
    mod.set_attr(mult["isHistoricallyInteresting"], False)

    return pair_blend


def _remove_pivots(mod, transform):
    # Remove unsupported additional transforms
    for channel in ("rotatePivot",
                    "rotatePivotTranslate",
                    "scalePivot",
                    "scalePivotTranslate",
                    "rotateAxis"):

        for axis in "XYZ":
            attr = transform[channel + axis]

            if attr.read() != 0:
                if attr.editable:
                    log.warning(
                        "Zeroing out non-zero channel %s.%s%s"
                        % (transform, channel, axis)
                    )
                    mod.set_attr(attr, 0.0)

                else:
                    log.warning(
                        "%s.%s%s was locked, results might look funny"
                        % (transform, channel, axis)
                    )

    if "jointOrient" in transform and any(transform["jointOrient"].read()):
        # Grab full transform, ahead of resetting the jointOrient
        # in case we reset it without connecting to `rotate`
        tm = transform.transform()

        if transform["jointOrient"].editable:
            mod.set_attr(transform["jointOrient"], (0.0, 0.0, 0.0))
            log.warning(
                "%s had a non-zero jointOrient, it was zeroed out"
                % transform
            )
        else:
            log.warning(
                "Tried resetting %s.jointOrient but could not. "
                "If you experience weird rotations, try resetting it to 0"
                % transform
            )

        # "Freeze" transformations if possible
        if transform["rotate"].editable:
            mod.set_attr(transform["rotate"], tm.rotation())


@with_undo_chunk
def create_scene(name=None, parent=None):
    time = cmdx.encode("time1")
    up = global_up_axis()
    name = name or _unique_name("rScene")

    with cmdx.DagModifier() as mod:
        if parent is None:
            parent = mod.create_node("transform", name=name)

            # Not yet supported
            mod.set_keyable(parent["scale"], False)
            mod.set_locked(parent["scale"])

        else:
            name = parent.name(namespace=False)

        scene = _rdscene(mod, _shape_name(name), parent=parent)
        mod.connect(parent["worldMatrix"][0], scene["inputMatrix"])
        mod.connect(time["outTime"], scene["currentTime"])
        mod.set_attr(scene["startTime"], oma.MAnimControl.minTime())
        mod.set_attr(scene["gravity"], up * -98.2)

        if up.y:
            mod.set_keyable(scene["gravityY"])
            mod.set_nice_name(scene["gravityY"], "Gravity")

        else:
            mod.set_keyable(scene["gravityZ"])
            mod.set_nice_name(scene["gravityZ"], "Gravity")
            mod.set_attr(parent["rotateX"], cmdx.radians(90))

        # Record for backwards compatibility
        mod.set_attr(scene["version"], _version())
        mod.connect(parent["message"], scene["exclusiveNodes"][0])

    return scene


@with_undo_chunk
# @contract(returns=("rdRigid", optional("rdConstraint")))
def create_rigid(node,
                 scene,
                 passive=False,
                 compute_mass=False,
                 existing=Overwrite,
                 defaults=None,
                 _cache=None):
    """Create a new rigid

    Create a new rigid from `node`, which may be a transform or
    shape. If transform, the first shape is queried for geometry.
    Otherwise, the shape itself is used for geometry.

    Arguments:
        node (DagNode): Maya transform or shape
        scene (DagNode): Ragdoll scene to which the new rigid is added
        compute_mass (bool): Whether to automatically compute the mass
            based on shape volume
        existing (int): What to do about existing connections to translate
            and rotate channels.
        defaults (dict, optional): Default attribute values for the
            newly created rigid
        _cache (AttributeCache, optional): Reach for attributes here first,
            to avoid triggering evaluations prematurely

    """

    cache = _cache or {}
    defaults = defaults or {}

    if isinstance(node, string_types):
        node = cmdx.encode(node)

    if isinstance(scene, string_types):
        scene = cmdx.encode(scene)

    assert isinstance(node, cmdx.DagNode), type(node)
    assert scene.type() == "rdScene", scene.type()

    assert not node.shape(type="rdRigid"), (
        "%s is already a rigid" % node
    )

    if node.isA(cmdx.kShape):
        transform = node.parent()
        shape = node

    else:
        # Supported shapes, in order of preference
        transform = node
        shape = node.shape(type=("mesh", "nurbsCurve", "nurbsSurface"))

    assert not transform.shape(type="rdRigid"), (
        "%s already had a rigid" % transform
    )

    rest = cache.get((node, "worldMatrix"))
    rest = rest or transform["worldMatrix"][0].asMatrix()

    with cmdx.DagModifier() as mod:
        rigid = _rdrigid(mod, "rRigid", parent=transform)

        # Copy current transformation
        mod.set_attr(rigid["cachedRestMatrix"], rest)
        mod.set_attr(rigid["inputMatrix"], rest)

        # Add to scene
        add_rigid(mod, rigid, scene)

    # Transfer geometry into rigid, if any
    #
    #     ______                ______
    #    /\    /|              /     /|
    #   /  \  /.|   ------>   /     / |
    #  /____\/  |            /____ /  |
    #  |\   | . |            |    |   |
    #  | \  |  /             |    |  /
    #  |  \ |./              |    | /
    #  |___\|/               |____|/
    #
    #
    with cmdx.DagModifier() as mod:
        if shape:
            _interpret_shape(mod, rigid, shape)
        else:
            _interpret_transform(mod, rigid, transform)

        if compute_mass:
            # Establish a sensible default mass, also taking into
            # consideration that joints must be comparable to meshes.
            # Mass unit is kg, whereas lengths are in centimeters
            mod.set_attr(rigid["mass"], (
                rigid["extentsX"].read() *
                rigid["extentsY"].read() *
                rigid["extentsZ"].read() *
                0.01
            ))

    uas = UserAttributes(rigid, transform)
    uas.add_divider("Ragdoll")
    uas.add("kinematic")
    uas.add("collide")
    uas.add("mass")
    uas.add("friction")
    uas.add("restitution")
    uas.do_it()

    # Make the connections
    with cmdx.DagModifier() as mod:
        if passive:
            _connect_passive(mod, rigid, transform)
        else:
            _remove_pivots(mod, transform)
            _connect_active(mod, rigid, transform, existing=existing)

        # Apply provided default attribute values
        for key, value in defaults.items():
            mod.set_attr(rigid[key], value)

    return rigid


def _anim_constraint(rigid, active=False):
    """Apply inputMatrix to a new constraint"""
    scene = rigid["nextState"].connection(type="rdScene")
    assert scene is not None, "%s was not connected to a scene" % rigid

    transform = rigid.parent()

    with cmdx.DagModifier() as mod:
        con = _rdconstraint(mod, "rAnimConstraint", parent=transform)

        mod.set_attr(con["limitEnabled"], False)
        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["drawScale"], _scale_from_rigid(rigid))

        # Follow animation, if any
        mod.set_attr(con["driveStrength"], 1.0 if active else 0.0)

        mod.connect(scene["ragdollId"], con["parentRigid"])
        mod.connect(rigid["ragdollId"], con["childRigid"])

        mod.do_it()

        # Support soft manipulation
        mod.connect(rigid["inputMatrix"], con["driveMatrix"])

        # Add to scene
        add_constraint(mod, con, scene)

    uas = UserAttributes(con, transform)
    uas.add("driveStrength")
    uas.do_it()

    return con


def create_active_rigid(node, scene, **kwargs):
    return create_rigid(node, scene, passive=False, **kwargs)


def create_passive_rigid(node, scene, **kwargs):
    return create_rigid(node, scene, passive=True, **kwargs)


def create_constraint(parent, child):
    assert child.type() == "rdRigid", child.type()
    assert parent.type() in ("rdRigid", "rdScene"), (
        "%s must be a rigid or scene" % parent.type()
    )

    if parent.type() == "rdScene":
        scene = parent
    else:
        scene = parent["nextState"].connection()
        assert scene and scene.type() == "rdScene", (
            "%s was not part of a scene" % parent
        )

    assert child["nextState"].connection() == scene, (
        "%s and %s was not part of the same scene" % (parent, child)
    )

    name = _unique_name("rConstraint")

    with cmdx.DagModifier() as mod:
        transform = child.parent()
        con = _rdconstraint(mod, name, parent=transform)

        draw_scale = _scale_from_rigid(child)
        mod.set_attr(con["drawScale"], draw_scale)

        mod.connect(parent["ragdollId"], con["parentRigid"])
        mod.connect(child["ragdollId"], con["childRigid"])

        _reset_constraint(mod, con)

        # Add to scene
        add_constraint(mod, con, scene)

    return con


@with_undo_chunk
def convert_to_point(con,
                     maintain_offset=True,
                     auto_orient=True,
                     standalone=False):

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod,
                          con,
                          maintain_offset=maintain_offset)

        node = con.parent() if standalone else con
        mod.rename(node, _unique_name("rPointConstraint"))
        mod.set_attr(con["type"], PointConstraint)
        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["limitStrength"], 1)
        mod.set_attr(con["linearLimitX"], -1)
        mod.set_attr(con["linearLimitY"], -1)
        mod.set_attr(con["linearLimitZ"], -1)
        mod.set_attr(con["angularLimitX"], 0)
        mod.set_attr(con["angularLimitY"], 0)
        mod.set_attr(con["angularLimitZ"], 0)

    return con


@with_undo_chunk
def convert_to_orient(con,
                      maintain_offset=True,
                      auto_orient=True,
                      standalone=False):

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod,
                          con,
                          maintain_offset=maintain_offset)

        node = con.parent() if standalone else con
        mod.rename(node, _unique_name("rOrientConstraint"))
        mod.set_attr(con["type"], OrientConstraint)
        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["limitStrength"], 1)
        mod.set_attr(con["linearLimitX"], 0)
        mod.set_attr(con["linearLimitY"], 0)
        mod.set_attr(con["linearLimitZ"], 0)
        mod.set_attr(con["angularLimitX"], cmdx.radians(-1))
        mod.set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.set_attr(con["angularLimitZ"], cmdx.radians(-1))

    return con


@with_undo_chunk
def convert_to_hinge(con,
                     maintain_offset=True,
                     auto_orient=True,
                     standalone=False):

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    """Convert `con` to Hinge Constraint

    Arguments:
        con (rdConstraint): Constraint to convert
        swing_axis (str): Aim swing in this direction. This should
            typically match your choice in the Maya "Orient Joints"
            dialog box.

    """

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod,
                          con,
                          maintain_offset=maintain_offset)

        node = con.parent() if standalone else con
        mod.rename(node, _unique_name("rHingeConstraint"))
        mod.set_attr(con["type"], HingeConstraint)
        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["limitStrength"], 1)
        mod.set_attr(con["linearLimitX"], -1)
        mod.set_attr(con["linearLimitY"], -1)
        mod.set_attr(con["linearLimitZ"], -1)
        mod.set_attr(con["angularLimitX"], cmdx.radians(45))
        mod.set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.set_attr(con["angularLimitZ"], cmdx.radians(-1))

    reorient(con)

    return con


@with_undo_chunk
def convert_to_socket(con,
                      maintain_offset=True,
                      auto_orient=True,
                      standalone=False):

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod,
                          con,
                          maintain_offset=maintain_offset)

        node = con.parent() if standalone else con
        mod.rename(node, _unique_name("rSocketConstraint"))
        mod.set_attr(con["type"], SocketConstraint)
        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["limitStrength"], 1)
        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1)
        mod.set_attr(con["linearDriveStiffness"], 0)
        mod.set_attr(con["linearDriveDamping"], 0)
        mod.set_attr(con["linearLimitX"], -1)
        mod.set_attr(con["linearLimitY"], -1)
        mod.set_attr(con["linearLimitZ"], -1)
        mod.set_attr(con["angularLimitX"], cmdx.radians(45))
        mod.set_attr(con["angularLimitY"], cmdx.radians(45))
        mod.set_attr(con["angularLimitZ"], cmdx.radians(45))

    return con


@with_undo_chunk
def convert_to_parent(con,
                      maintain_offset=True,
                      auto_orient=True,
                      standalone=False):
    """A constraint with no degrees of freedom"""

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod,
                          con,
                          maintain_offset=maintain_offset)

        node = con.parent() if standalone else con
        mod.rename(node, _unique_name("rParentConstraint"))
        mod.set_attr(con["type"], ParentConstraint)
        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["limitStrength"], 1)
        mod.set_attr(con["linearLimitX"], -1)
        mod.set_attr(con["linearLimitY"], -1)
        mod.set_attr(con["linearLimitZ"], -1)
        mod.set_attr(con["angularLimitX"], cmdx.radians(-1))
        mod.set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.set_attr(con["angularLimitZ"], cmdx.radians(-1))

    return con


def _make_constraint(convert_function):
    """Constraint factory function, less to type = happier developer"""

    @with_undo_chunk
    def make(parent,
             child,
             scene,
             maintain_offset=True,
             auto_orient=True,
             standalone=False):

        if isinstance(parent, string_types):
            parent = cmdx.encode(parent)

        if isinstance(child, string_types):
            child = cmdx.encode(parent)

        con = _attach_bodies(parent, child, scene, standalone)

        kwargs = {
            "maintain_offset": maintain_offset,
            "auto_orient": auto_orient,
            "standalone": standalone,
        }

        return convert_function(con, **kwargs)

    return make


point_constraint = _make_constraint(convert_to_point)
orient_constraint = _make_constraint(convert_to_orient)
parent_constraint = _make_constraint(convert_to_parent)
hinge_constraint = _make_constraint(convert_to_hinge)
socket_constraint = _make_constraint(convert_to_socket)


def _unscaled(mat):
    tm = cmdx.Tm(mat)
    tm.setScale((1, 1, 1))
    return tm.asMatrix()


def _reset_constraint(mod, con,
                      maintain_offset=True):
    """Reset a constraint

    Arguments:
        mod (cmdx.DagModifier): Current modifier in use
        con (rdConstraint): The constraint to reset
        auto_orient (bool): Use current axis, or compute one from hierarchy

    """

    assert con.type() == "rdConstraint", "%s must be an rdConstraint" % con

    def reset_attr(attr):
        if not attr.editable:
            return
        mod.reset_attr(attr)

    reset_attr(con["disableCollision"])
    reset_attr(con["limitEnabled"])
    reset_attr(con["limitStrength"])
    reset_attr(con["driveEnabled"])
    reset_attr(con["driveStrength"])
    reset_attr(con["linearLimitX"])
    reset_attr(con["linearLimitY"])
    reset_attr(con["linearLimitZ"])
    reset_attr(con["angularLimitX"])
    reset_attr(con["angularLimitY"])
    reset_attr(con["angularLimitZ"])

    # Initialise parent frame
    parent_rigid = con["parentRigid"].connection(type="rdRigid")
    child_rigid = con["childRigid"].connection(type="rdRigid")

    # Align constraint to whatever the local transformation is
    if maintain_offset and parent_rigid and child_rigid:
        child_matrix = child_rigid["cachedRestMatrix"].asMatrix()
        parent_matrix = parent_rigid["cachedRestMatrix"].asMatrix()
        parent_frame = child_matrix * parent_matrix.inverse()

        # Drive to where you currently are
        if con["driveMatrix"].writable:
            mod.set_attr(con["driveMatrix"], parent_frame)

        mod.set_attr(con["parentFrame"], parent_frame)
        mod.set_attr(con["childFrame"], cmdx.Mat4())


def _apply_scale(mat):
    tm = cmdx.Tm(mat)
    scale = tm.scale()
    translate = tm.translation()
    translate.x *= scale.x
    translate.y *= scale.y
    translate.z *= scale.z
    tm.setTranslation(translate)
    tm.setScale((1, 1, 1))
    return tm.asMatrix()


@with_undo_chunk
def orient(con, aim=None, up=None):
    """Orient a constraint

    Aim the constraint towards the child of its rigid, unless an `aim`
    and/or `up` is provided. For constraints with a non-hierarchical
    parent and/or child, such as the Dynamic Control where the selection
    determines hierarchy rather than Maya's physical hierarchy, the
    `aim` is mandatory.

    """

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    assert con.type() == "rdConstraint", "%s was not a rdConstraint" % con
    assert (aim is None) or isinstance(aim, cmdx.om.MVector), (
        "%r was not an aim position" % aim)
    assert (up is None) or isinstance(up, cmdx.om.MVector), (
        "%r was not an up position" % up)

    parent_rigid = con["parentRigid"].connection(type="rdRigid")
    child_rigid = con["childRigid"].connection(type="rdRigid")

    if not (parent_rigid and child_rigid):
        # This constraint isn't connected/used nor relevant,
        # the user won't be expecting anything out of it.
        return

    # Rather than ask the node for where it is, which could
    # trigger an evaluation, we fetch an input matrix that
    # isn't computed by Ragdoll
    child_matrix = child_rigid["cachedRestMatrix"].asMatrix()
    parent_matrix = parent_rigid["cachedRestMatrix"].asMatrix()

    child_tm = child_rigid.transform(cmdx.sWorld)

    # Try and aim towards the first child of the same type in the
    # hierarchy of the constraint. This assumes constraints are
    # themselves children of the transform they influence.
    #
    #  o parent
    #   \
    #    \ con
    #     o--------o first-child
    #
    if aim is None:
        transform = child_rigid.parent()

        # First child of same type, skipping over anything in between
        child = transform.descendent(type=transform.type())

        if not child:
            aim = cmdx.Tm(child_tm)
            aim.translateBy(cmdx.Vector(1, 0, 0), cmdx.sPreTransform)
            aim = aim.translation()
        else:
            aim = child.transform(cmdx.sWorld).translation()

    # The up direction should typically be the parent rigid, but
    # can be overridden too.
    #
    # o Up is here
    #  \
    #   \ con
    #    o---------o
    #
    if up is None:
        up = parent_rigid.transform(cmdx.sWorld).translation()

    origin = child_tm.translation()
    orient = orient_from_positions(origin, aim, up)
    mat = cmdx.Tm(translate=origin, rotate=orient).asMatrix()

    parent_frame = mat * parent_matrix.inverse()
    child_frame = mat * child_matrix.inverse()

    with cmdx.DagModifier() as mod:
        mod.set_attr(con["parentFrame"], parent_frame)
        mod.set_attr(con["childFrame"], child_frame)


@with_undo_chunk
def reorient(con):
    r"""Re-orient

                  /|
                 /| |
     o----------o\| |   .
                 \\|    .
                  \    .
                   \  v
                    o

    Flip the parent and child frames such that twist represents
    the major axis, e.g. bend of the elbow

    - X = twist
    - Y = break
    - Z = bend

    """

    if isinstance(con, string_types):
        con = cmdx.encode(con)

    parent = con["parentRigid"].connection()
    child = con["childRigid"].connection()

    if parent and child:
        assert parent.type() == "rdRigid", (
            "Bad parentRigid connection: %s" % parent
        )
        assert child.type() == "rdRigid", (
            "Bad childRigid connection: %s" % parent
        )

        rotation = cmdx.Quat(cmdx.radians(-90), cmdx.Vector(0, 0, 1))
        rotation *= cmdx.Quat(cmdx.radians(90), cmdx.Vector(1, 0, 0))

        parent_frame = cmdx.Tm(con["parentFrame"].asMatrix())
        parent_frame.rotateBy(rotation, cmdx.sPreTransform)
        parent_frame = parent_frame.asMatrix()

        child_frame = cmdx.Tm(con["childFrame"].asMatrix())
        child_frame.rotateBy(rotation, cmdx.sPreTransform)
        child_frame = child_frame.asMatrix()

        with cmdx.DagModifier() as mod:
            mod.set_attr(con["parentFrame"], parent_frame)
            mod.set_attr(con["childFrame"], child_frame)


def _connect_transform(mod, node, transform):
    assert transform.isA(cmdx.kTransform), "%s was not a transform" % transform
    attributes = {}

    if node.type() == "rdRigid":
        attributes = {
            "outputTranslateX": "translateX",
            "outputTranslateY": "translateY",
            "outputTranslateZ": "translateZ",
            "outputRotateX": "rotateX",
            "outputRotateY": "rotateY",
            "outputRotateZ": "rotateZ",
        }

    elif node.type() == "pairBlend":
        attributes = {
            "outTranslateX": "translateX",
            "outTranslateY": "translateY",
            "outTranslateZ": "translateZ",
            "outRotateX": "rotateX",
            "outRotateY": "rotateY",
            "outRotateZ": "rotateZ",
        }

    else:
        raise TypeError(
            "I don't know how to connect '%s' -> '%s"
            % (type(node), type(transform))
        )

    for src, dst in attributes.items():
        mod.try_connect(node[src], transform[dst])


@with_undo_chunk
def convert_rigid(rigid, passive=None):
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    transform = rigid.parent()

    if passive is None:
        passive = not rigid["kinematic"].read()

    with cmdx.DagModifier() as mod:
        #
        # Convert active --> passive
        #
        if not rigid["kinematic"] and passive:
            mod.disconnect(transform["translateX"])
            mod.disconnect(transform["translateY"])
            mod.disconnect(transform["translateZ"])
            mod.disconnect(transform["rotateX"])
            mod.disconnect(transform["rotateY"])
            mod.disconnect(transform["rotateZ"])

            mod.connect(transform["worldMatrix"][0], rigid["inputMatrix"])

            mod.set_attr(rigid["kinematic"], True)

        #
        # Convert passive --> active
        #
        elif not passive:
            mod.set_attr(rigid["kinematic"], False)

            # The user will expect a newly-turned active rigid to collide
            mod.set_attr(rigid["collide"], True)

            _remove_pivots(mod, transform)
            _connect_active_blend(mod, rigid, transform)
            _anim_constraint(rigid)

    return rigid


def _rdscene(mod, name, parent=None):
    name = _unique_name(name)
    scene = mod.create_node("rdScene", name=name, parent=parent)

    # Improve drive strength ranges
    mod.set_attr(scene["positionIterations"], 4)

    return scene


def _rdrigid(mod, name, parent):
    assert isinstance(parent, cmdx.DagNode) and parent.isA(cmdx.kTransform), (
        "%s was not a transform" % parent
    )

    name = _unique_name(name)
    rigid = mod.create_node("rdRigid", name=name, parent=parent)

    # Link relevant attributes
    # Keep up to date with initial world matrix
    mod.connect(parent["worldMatrix"][0], rigid["restMatrix"])

    # Compensate for any parents when outputting from the solver
    mod.connect(parent["parentInverseMatrix"][0],
                rigid["inputParentInverseMatrix"])

    mod.connect(parent["rotateOrder"], rigid["rotateOrder"])

    # Assign some random color, within some nice range
    mod.set_attr(rigid["color"], _random_color())

    return rigid


def _rdcontrol(mod, name, parent=None):
    name = _unique_name(name)
    ctrl = mod.create_node("rdControl", name=name, parent=parent)
    mod.set_attr(ctrl["color"], ControlColor)  # Default blue
    return ctrl


def _rdconstraint(mod, name, parent=None):
    name = _unique_name(name)
    node = mod.create_node("rdConstraint", name=name, parent=parent)
    return node


@with_undo_chunk
def create_absolute_control(rigid, reference=None):
    """Control a rigid body in worldspace

    Given a worldmatrix, attempt to guide a rigid body to match,
    with some stiffness and damping.

    This can be handy for transforming a rigid body as though it was
    kinematic, except with some response to forces and contacts.

    """

    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    tmat = rigid.transform(cmdx.sWorld)

    scene = rigid["nextState"].connection()
    assert scene and scene.type() == "rdScene", (
        "%s was not part of a scene" % rigid
    )

    with cmdx.DagModifier() as mod:
        if reference is None:
            name = _unique_name("rAbsoluteControl")
            reference = mod.create_node("transform", name=name)
            mod.set_attr(reference["translate"], tmat.translation())
            mod.set_attr(reference["rotate"], tmat.rotation())

            # Just mirror whatever the rigid is doing
            mod.connect(rigid["outputWorldScale"], reference["scale"])
            mod.set_keyable(reference["scale"], False)

        ctrl = _rdcontrol(mod, "rAbsoluteControl1", reference)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])

        con = mod.create_node("rdConstraint",
                              name="rAbsoluteConstraint1",
                              parent=reference)

        mod.connect(rigid["ragdollId"], con["childRigid"])

        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)
        mod.set_attr(con["disableCollision"], False)

        mod.set_attr(con["drawConnection"], False)
        mod.set_attr(con["drawScale"], _scale_from_rigid(rigid))

        mod.connect(scene["ragdollId"], con["parentRigid"])
        mod.connect(reference["worldMatrix"][0], con["driveMatrix"])

        # Add to scene
        add_constraint(mod, con, scene)

    forwarded = (
        "driveStrength",
        "linearDriveStiffness",
        "linearDriveDamping",
        "angularDriveStiffness",
        "angularDriveDamping"
    )

    reference_proxies = UserAttributes(con, reference)
    reference_proxies.add_divider("Ragdoll")

    for attr in forwarded:
        # Expose on constraint node itself
        reference_proxies.add(attr)

    reference_proxies.do_it()

    return reference, ctrl, con


@with_undo_chunk
def create_relative_control(rigid):
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    assert rigid.type() == "rdRigid", "%s was not a rdRigid" % rigid

    con = rigid.sibling(type="rdConstraint")
    assert con is not None, "Relative to what?"

    scene = rigid["nextState"].connection()
    assert scene and scene.type() == "rdScene", (
        "%s was not part of a scene" % rigid
    )

    parent_rigid = con["parentRigid"].connection()

    # Look for parent via constraint, rather than Maya hierarchy,
    # as there may be joints between two connected rigid bodies.
    assert parent_rigid and parent_rigid.type() == "rdRigid", (
        "Can't create relative control to world"
    )

    rigid_node = rigid.parent()
    tmat = rigid_node.transform()
    parent = parent_rigid.parent()

    with cmdx.DagModifier() as mod:
        tm = mod.create_node("joint", name="rRelativeControl1", parent=parent)
        ctrl = _rdcontrol(mod, "rAbsoluteControlShape1", tm)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])

        mod.set_attr(tm["radius"], 0)
        mod.set_attr(tm["translate"], tmat.translation())

        # Zero out the rotate part for a truly relative orientation
        parent_frame = con["parentFrame"].asMatrix()
        parent_frame = cmdx.TransformationMatrix(parent_frame)
        mod.set_attr(tm["jointOrient"], parent_frame.rotation())

        mod.connect(tm["matrix"], con["driveMatrix"])
        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)
        mod.set_attr(con["angularDriveStiffness"], 10000.0)
        mod.set_attr(con["angularDriveDamping"], 1000.0)

    # Cosmetics
    tm["translate"].lock_and_hide()
    tm["scale"].lock_and_hide()

    return con


@with_undo_chunk
def create_active_control(reference, rigid):
    """Control a rigid body using a reference transform

    Arguments:
        reference (transform): Follow this node
        rigid (rdRigid): Rigid which should follow `reference`

    """

    if isinstance(reference, string_types):
        reference = cmdx.encode(reference)

    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    assert reference.isA(cmdx.kTransform), "%s was not a transform" % reference
    assert rigid.type() == "rdRigid", "%s was not a rdRigid" % rigid

    scene = rigid["nextState"].connection()
    assert scene and scene.type() == "rdScene", (
        "%s was not part of a scene" % rigid
    )

    con = rigid.sibling(type="rdConstraint")
    assert con is not None, "Need an existing constraint"

    with cmdx.DagModifier() as mod:
        ctrl = _rdcontrol(mod, "rActiveControl1", reference)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])
        mod.connect(reference["matrix"], con["driveMatrix"])

        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)
        mod.set_attr(con["angularDriveStiffness"], 10000.0)
        mod.set_attr(con["angularDriveDamping"], 1000.0)

    forwarded = (
        "driveStrength",
        "linearDriveStiffness",
        "linearDriveDamping",
        "angularDriveStiffness",
        "angularDriveDamping"
    )

    reference_proxies = UserAttributes(con, reference)
    reference_proxies.add_divider("Ragdoll")

    for attr in forwarded:
        # Expose on constraint node itself
        reference_proxies.add(attr)

    reference_proxies.do_it()

    return ctrl


@with_undo_chunk
def create_kinematic_control(rigid, reference=None):
    if reference is not None and isinstance(reference, string_types):
        reference = cmdx.encode(reference)

    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    with cmdx.DagModifier() as mod:

        if reference is None:
            name = _unique_name("rPassive1")
            reference = mod.create_node("transform", name=name)

            tmat = rigid.transform(cmdx.sWorld)

            mod.set_attr(reference["translate"], tmat.translation())
            mod.set_attr(reference["rotate"], tmat.rotation())
            mod.set_attr(reference["scale"], tmat.scale())

            mod.set_locked(reference["scale"], True)
            mod.set_keyable(reference["scale"], False)

        ctrl = mod.create_node("rdControl",
                               name=_unique_name("rPassiveShape1"),
                               parent=reference)

        if rigid["kinematic"].connected:
            mod.disconnect(rigid["kinematic"], destination=False)
            mod.do_it()

        mod.set_attr(rigid["kinematic"], True)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])
        mod.connect(reference["worldMatrix"][0], rigid["inputMatrix"])

    forwarded = (
        "kinematic",
    )

    proxies = UserAttributes(rigid, ctrl)
    for attr in forwarded:
        proxies.add(attr)
    proxies.do_it()

    return reference


# Alias
create_passive_control = create_kinematic_control


def _shapeattributes_from_generator(mod, shape, rigid):
    """Look at `shape` history for a e.g. polyCube or polySphere"""

    gen = None

    if "inMesh" in shape and shape["inMesh"].connected:
        gen = shape["inMesh"].connection()

    elif "create" in shape and shape["create"].connected:
        gen = shape["create"].connection()

    else:
        return

    if gen.type() == "polyCube":
        mod.set_attr(rigid["shapeType"], BoxShape)
        mod.set_attr(rigid["shapeExtentsX"], gen["width"])
        mod.set_attr(rigid["shapeExtentsY"], gen["height"])
        mod.set_attr(rigid["shapeExtentsZ"], gen["depth"])

    elif gen.type() == "polySphere":
        mod.set_attr(rigid["shapeType"], SphereShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "polyCylinder" and gen["roundCap"]:
        mod.set_attr(rigid["shapeType"], CylinderShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["height"])

        # Align with Maya's cylinder/capsule axis
        # TODO: This doesn't account for partial values, like 0.5, 0.1, 1.0
        mod.set_attr(rigid["shapeRotation"], map(cmdx.radians, (
            (0, 0, 90) if gen["axisY"] else
            (0, 90, 0) if gen["axisZ"] else
            (0, 0, 0)
        )))

    elif gen.type() == "makeNurbCircle":
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "makeNurbSphere":
        mod.set_attr(rigid["shapeType"], SphereShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "makeNurbCone":
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["heightRatio"])

    elif gen.type() == "makeNurbCylinder":
        mod.set_attr(rigid["shapeType"], CylinderShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["heightRatio"])
        mod.set_attr(rigid["shapeRotation"], map(cmdx.radians, (
            (0, 0, 90) if gen["axisY"] else
            (0, 90, 0) if gen["axisZ"] else
            (0, 0, 0)
        )))


def _scale_from_rigid(rigid):
    rest_tm = cmdx.Tm(rigid["cachedRestMatrix"].asMatrix())

    scale = sum(rest_tm.scale()) / 3.0

    if rigid.parent().type() == "joint":
        return rigid["shapeLength"].read() * 0.25 * scale
    else:
        return sum(rigid["shapeExtents"].read()) / 3.0 * scale


def _attach_bodies(parent, child, scene, standalone):
    assert child.type() == "rdRigid", child.type()
    assert parent.type() in ("rdRigid", "rdScene"), (
        "%s must be a rigid or scene" % parent.type()
    )

    name = "rConstraint"
    excon = child["ragdollId"].connection(type="rdConstraint")

    with cmdx.DagModifier() as mod:

        if standalone:
            transform = mod.create_node("transform", name=name)
            mod.set_locked(transform["translate"])
            mod.set_locked(transform["rotate"])
            mod.set_locked(transform["scale"])
            con = _rdconstraint(mod, name + "Shape", parent=transform)

        else:
            transform = child.parent()
            con = _rdconstraint(mod, name, parent=transform)

        mod.set_attr(con["standalone"], standalone)
        mod.set_attr(con["disableCollision"], True)
        mod.set_attr(con["angularLimitX"], 0)  # Free
        mod.set_attr(con["angularLimitY"], 0)
        mod.set_attr(con["angularLimitZ"], 0)

        mod.set_attr(con["limitEnabled"], True)
        mod.set_attr(con["driveEnabled"], True)

        draw_scale = _scale_from_rigid(child)
        mod.set_attr(con["drawScale"], draw_scale)

        mod.connect(parent["ragdollId"], con["parentRigid"])
        mod.connect(child["ragdollId"], con["childRigid"])

        # Add to scene
        add_constraint(mod, con, scene)

        # Was there already a constraint here?
        # Does it have an input drive matrix?
        if excon:
            world_matrix = excon["driveMatrix"].connection(
                type="multMatrix", destination=False)

            if world_matrix is not None:
                local_matrix = world_matrix["matrixIn"][0].connection(
                    type="composeMatrix", destination=False)

                if local_matrix is not None:
                    mod.connect(local_matrix["outputMatrix"],
                                con["driveMatrix"])

                    # Take priority
                    mod.set_attr(excon["driveStrength"], 0.0)

    return con


def _is_locked(node, channels="tr"):
    attrs = [chan + ax for chan in channels for ax in "xyz"]
    return any(not node[a].editable for a in attrs)


@with_undo_chunk
def set_initial_state(rigids):
    assert isinstance(rigids, (tuple, list)), "%s was not a list" % rigids

    for index, rigid in enumerate(rigids):
        if isinstance(rigid, string_types):
            rigids[index] = cmdx.encode(rigid)

    assert all(r.type() == "rdRigid" for r in rigids), (
        "%s wasn't all rdRigid nodes" % str(rigids)
    )

    # Fetch matrices separately from modifying them, since they may
    # cause a re-evaluation that affect each other. Bad!
    rest_matrices = []
    for rigid in rigids:
        rest_matrices += [rigid.parent()["worldMatrix"][0].asMatrix()]

    with cmdx.DagModifier() as mod:
        for rigid, rest in zip(rigids, rest_matrices):
            if rigid["inputMatrix"].editable:
                mod.set_attr(rigid["inputMatrix"], rest)
            mod.set_attr(rigid["cachedRestMatrix"], rest)


def transfer_attributes(a, b, mirror=True):
    if isinstance(a, string_types):
        a = cmdx.encode(a)

    if isinstance(b, string_types):
        b = cmdx.encode(b)

    ra = a.shape(type="rdRigid")
    rb = b.shape(type="rdRigid")
    ca = a.shape(type="rdConstraint")
    cb = b.shape(type="rdConstraint")

    if ra and rb:
        transfer_rigid(ra, rb)

    if ca and cb:
        transfer_constraint(ca, cb, mirror)


def transfer_rigid(ra, rb):
    if isinstance(ra, string_types):
        ra = cmdx.encode(ra)

    if isinstance(rb, string_types):
        rb = cmdx.encode(rb)

    rigid_attributes = (
        "collide",
        "mass",
        "friction",
        "restitution",
        "shapeType",
        "shapeExtents",
        "shapeLength",
        "shapeRadius",
        "shapeOffset",
    )

    with cmdx.DagModifier() as mod:
        for attr in rigid_attributes:
            mod.set_attr(rb[attr], ra[attr])


def transfer_constraint(ca, cb, mirror=True):
    if isinstance(ca, string_types):
        ca = cmdx.encode(ca)

    if isinstance(cb, string_types):
        cb = cmdx.encode(cb)

    constraint_attributes = (
        "type",
        "limitStrength",
        "angularLimit",
        "drawScale",
    )

    with cmdx.DagModifier() as mod:
        for attr in constraint_attributes:
            mod.set_attr(cb[attr], ca[attr])

    # Mirror frames
    parent_frame = cmdx.Tm(ca["parentFrame"].asMatrix())
    child_frame = cmdx.Tm(ca["childFrame"].asMatrix())

    def _mirror(tm):
        t = tm.translation()
        r = tm.rotation()

        t.z *= -1
        r.x *= -1
        r.y *= -1

        tm.setTranslation(t)
        tm.setRotation(r)

    if mirror:
        _mirror(parent_frame)
        _mirror(child_frame)

    with cmdx.DagModifier() as mod:
        mod.set_attr(cb["parentFrame"], parent_frame.asMatrix())
        mod.set_attr(cb["childFrame"], child_frame.asMatrix())


@with_undo_chunk
def edit_constraint_frames(con):
    if isinstance(con, string_types):
        con = cmdx.encode(con)

    parent_rigid = con["parentRigid"].connection()
    child_rigid = con["childRigid"].connection()

    assert parent_rigid and child_rigid, "Unconnected constraint: %s" % con

    parent = parent_rigid.parent()
    child = child_rigid.parent()

    with cmdx.DagModifier() as mod:
        parent_frame = mod.create_node("transform",
                                       name="parentFrame",
                                       parent=parent)
        child_frame = mod.create_node("transform",
                                      name="childFrame",
                                      parent=child)

        for frame in (parent_frame, child_frame):
            mod.set_attr(frame["displayHandle"], True)
            mod.set_attr(frame["displayLocalAxis"], True)

        parent_frame_tm = cmdx.Tm(con["parentFrame"].asMatrix())
        child_frame_tm = cmdx.Tm(con["childFrame"].asMatrix())

        parent_translate = parent_frame_tm.translation()
        child_translate = child_frame_tm.translation()

        mod.set_attr(parent_frame["translate"], parent_translate)
        mod.set_attr(parent_frame["rotate"], parent_frame_tm.rotation())
        mod.set_attr(child_frame["translate"], child_translate)
        mod.set_attr(child_frame["rotate"], child_frame_tm.rotation())

        mod.connect(parent_frame["matrix"], con["parentFrame"])
        mod.connect(child_frame["matrix"], con["childFrame"])

    return parent_frame, child_frame


@with_undo_chunk
def edit_shape(rigid):
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    assert rigid and rigid.type() == "rdRigid", "%s was not a rigid" % rigid
    parent_transform = rigid.parent()

    with cmdx.DagModifier() as mod:
        shape = mod.create_node("transform",
                                name="shapeTransform",
                                parent=parent_transform)

        mod.set_attr(shape["displayHandle"], True)
        mod.set_attr(shape["displayLocalAxis"], True)

        # Transfer current values
        mod.set_attr(shape["translateX"], rigid["shapeOffsetX"])
        mod.set_attr(shape["translateY"], rigid["shapeOffsetY"])
        mod.set_attr(shape["translateZ"], rigid["shapeOffsetZ"])

        mod.set_attr(shape["rotateX"], rigid["shapeRotationX"])
        mod.set_attr(shape["rotateY"], rigid["shapeRotationY"])
        mod.set_attr(shape["rotateZ"], rigid["shapeRotationZ"])

        mod.connect(shape["translate"], rigid["shapeOffset"])
        mod.connect(shape["rotate"], rigid["shapeRotation"])

    return shape


@with_undo_chunk
def create_force(type, rigid, scene):
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    if isinstance(scene, string_types):
        scene = cmdx.encode(scene)

    enum = {
        PointForce: 0,
        PushForce: 0,
        PullForce: 0,
        UniformForce: 1,
        TurbulenceForce: 2,
    }

    with cmdx.DagModifier() as mod:
        tm = mod.create_node("transform", name="rForce1")
        force = mod.create_node("rdForce", name="rForceShape1", parent=tm)
        mod.connect(tm["worldMatrix"][0], force["inputMatrix"])
        mod.set_attr(force["type"], enum[type])

        if type == PointForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["minDistance"], 0)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, _unique_name("rPointForce"))
            mod.rename(force, _unique_name("rPointForceShape"))

        elif type == PushForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["minDistance"], 0)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, _unique_name("rPushForce"))
            mod.rename(force, _unique_name("rPushForceShape"))

        elif type == PullForce:
            mod.set_attr(force["magnitude"], -100)
            mod.set_attr(force["minDistance"], 1)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, _unique_name("rPullForce"))
            mod.rename(force, _unique_name("rPullForceShape"))

        elif type == UniformForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["direction"], (0, -1, 0))
            mod.rename(tm, _unique_name("rUniformForce"))
            mod.rename(force, _unique_name("rUniformForceShape"))

        elif type == TurbulenceForce:
            mod.set_attr(force["magnitude"], 200)
            mod.set_attr(tm["scale"], (5, 5, 5))
            mod.rename(tm, _unique_name("rTurbulence"))
            mod.rename(force, _unique_name("rTurbulence"))

        elif type == WindForce:
            pass

        mod.set_attr(tm["displayHandle"], True)
        mod.set_attr(tm["overrideEnabled"], True)
        mod.set_attr(tm["overrideRGBColors"], True)
        mod.set_attr(tm["overrideColorRGB"], (1.0, 0.63, 0.0))  # Yellowish

        add_force(mod, force, rigid)

    return force


@with_undo_chunk
def create_slice(scene):  # type: (cmdx.DagNode) -> cmdx.DagNode
    if isinstance(scene, string_types):
        scene = cmdx.encode(scene)

    with cmdx.DagModifier() as mod:
        tm = mod.create_node("transform", name="rSlice1")
        mod.set_attr(tm["translateY"], 5)
        mod.set_attr(tm["scale"], (5, 5, 5))

        slice = mod.create_node("rdSlice", name="rSliceShape1", parent=tm)
        mod.connect(tm["worldMatrix"][0], slice["inputMatrix"])

        # Add to scene
        index = scene["inputSliceStart"].next_available_index()
        mod.connect(slice["startState"], scene["inputSliceStart"][index])
        mod.connect(slice["currentState"], scene["inputSlice"][index])
        mod.connect(scene["outputChanged"], slice["nextState"])

    return slice


def assign_force(rigid, force):  # type: (cmdx.DagNode, cmdx.DagNode) -> bool
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    if isinstance(force, string_types):
        force = cmdx.encode(force)

    with cmdx.DagModifier() as mod:
        index = rigid["inputForce"].next_available_index()
        mod.connect(force["outputForce"], rigid["inputForce"][index])

    return True


@with_undo_chunk
def duplicate(rigid):
    if isinstance(rigid, string_types):
        rigid = cmdx.encode(rigid)

    assert rigid.type() == "rdRigid", "%s was not a rdRigid" % rigid

    scene = rigid["nextState"].connection()
    assert scene and scene.type() == "rdScene"

    parenttm = rigid.parent().transform(cmdx.sWorld)

    with cmdx.DagModifier() as mod:
        name = rigid.parent().name(namespace=False)
        duptm = mod.create_node("transform", name="%s1" % name)
        mod.set_attr(duptm["translate"], parenttm.translation())
        mod.set_attr(duptm["rotate"], parenttm.rotation())

    attrs = (
        "collide",
        "mass",
        "friction",
        "restitution",
        "shapeType",
        "shapeExtents",
        "shapeRadius",
        "shapeLength",
        "shapeOffset",
        "shapeRotation",
        "thickness",
        "kinematic",
    )

    if rigid["kinematic"]:
        dup = create_passive_rigid(duptm, scene)

    else:
        dup = create_active_rigid(duptm, scene)

    for attr in attrs:
        dup[attr] = rigid[attr].read()

    return dup


def add_to_set(node, name, mod=None):
    try:
        collection = cmdx.encode(name)
    except cmdx.ExistError:
        with cmdx.DGModifier() as mod:
            collection = mod.create_node(
                "objectSet", name=name
            )

    collection.add(node)
    return collection


def global_up_axis():
    try:
        # Supported since Maya 2019
        return cmdx.Vector(cmdx.om.MGlobal.upAxis())
    except AttributeError:
        return cmdx.Vector(0, 1, 0)


def orient_from_positions(a, b, c=None):
    aim = (b - a).normal()
    up = (c - a).normal() if c else global_up_axis()

    cross = aim ^ up  # Make axes perpendicular
    up = cross ^ aim

    orient = cmdx.Quaternion()
    orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
    orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

    return orient


def infer_geometry(root, parent=None, children=None):
    """Find length and orientation from `root`

    This function looks at the child and parent of
    any given root for clues as to how to orient it

    Length is simply the distance between `root`
    and its first child.

    Arguments:
        root (root): The root from which to derive length and orientation

    """

    class Geometry(object):
        __slots__ = [
            "orient",
            "extents",
            "length",
            "radius",
            "shape_offset",
            "shape_rotation",
        ]

        def __init__(self):
            self.orient = cmdx.Quaternion()
            self.extents = cmdx.Vector(1, 1, 1)
            self.length = 0.0
            self.radius = 0.0
            self.shape_offset = cmdx.Vector()
            self.shape_rotation = cmdx.Vector()

        def mass(self):
            return (
                self.extents.x *
                self.extents.y *
                self.extents.z *
                0.01
            )

        def copy(self):
            geo = Geometry()
            for slot in self.__slots__:
                setattr(geo, slot, getattr(self, slot))
            return geo

    geometry = Geometry()
    orient = cmdx.Quaternion()

    if children is None:
        # Better this than nothing
        children = list(root.children(type=root.type()))

    # Special case of not wanting to use childhood, but
    # rather share whatever geometry the parent has
    if children is False and parent is not None:
        if "_rdGeometry" in parent.data:
            parent_geometry = parent.data.get("_rdGeometry")
            return parent_geometry

    root_tm = root.transform(cmdx.sWorld)
    root_pos = root_tm.translation()
    root_scale = root_tm.scale()

    # There is a lot we can gather from the childhood
    if children:

        # Support multi-child scenarios
        #
        #         o
        #        /
        #  o----o--o
        #        \
        #         o
        #
        positions = []
        for child in children:
            positions += [child.transform(cmdx.sWorld).translation()]

        pos2 = cmdx.Vector()
        for pos in positions:
            pos2 += pos
        pos2 /= len(positions)

        # Find center joint if multiple children
        #
        # o o o  <-- Which is in the middle?
        #  \|/
        #   o
        #   |
        #
        distances = []
        for pos in positions + [root_pos]:
            distances += [(pos - pos2).length()]
        center_index = distances.index(min(distances))
        center_node = (children + [root])[center_index]

        # Roots typically get this, where e.g.
        #
        #      o
        #      |
        #      o  <-- Root
        #     / \
        #    o   o
        #
        if center_node != root:
            parent = parent or root.parent(type=root.type())

            if not parent:
                # Try using grand-child instead
                parent = center_node.child(type=root.type())

            if parent:
                up = parent.transform(cmdx.sWorld).translation()
                up = (up - root_pos).normal()
            else:
                up = global_up_axis()

            aim = (pos2 - root_pos).normal()
            cross = aim ^ up  # Make axes perpendicular
            up = cross ^ aim

            orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
            orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

            center_node_pos = center_node.transform(cmdx.sWorld).translation()
            length = (center_node_pos - root_pos).length()

            geometry.orient = orient
            geometry.length = length

    if geometry.length > 0.0:

        if geometry.radius:
            # Pre-populated somewhere above
            radius = geometry.radius

        # Joints for example ship with this attribute built-in, very convenient
        elif "radius" in root:
            radius = root["radius"].read()

        # If we don't have that, try and establish one from the bounding box
        else:
            shape = root.shape(type=("mesh", "nurbsCurve", "nurbsSurface"))

            if shape:
                bbox = shape.bounding_box

                # Bounding box is independent of global scale
                bbox = cmdx.Vector(bbox.width, bbox.height, bbox.depth)
                bbox.x *= root_scale.x
                bbox.y *= root_scale.y
                bbox.z *= root_scale.z

                radius = sorted([bbox.x, bbox.y, bbox.z])

                # A bounding box will be either flat or long
                # That means 2/3 axes will be similar, and one
                # either 0 or large.
                #  ___________________
                # /__________________/|
                # |__________________|/
                #
                radius = radius[1]  # Pick middle one
                radius /= 2  # Width to radius
                radius /= 2  # Controls are typically larger than the model

            else:
                # If there's no visible geometry what so ever, we have
                # very little to go on in terms of establishing a radius.
                radius = geometry.length * 0.1

        # Keep radius at minimum 10% of its length to avoid stick-figures
        radius = max(geometry.length * 0.1, radius)

        size = cmdx.Vector(geometry.length, radius, radius)
        offset = orient * cmdx.Vector(geometry.length / 2.0, 0, 0)

        geometry.extents = cmdx.Vector(geometry.length, radius * 2, radius * 2)
        geometry.radius = radius

    else:
        size, center = local_bounding_size(root)
        offset = center - root_pos

        geometry.length = size.x
        geometry.radius = min([size.y, size.z])
        geometry.extents = size

    # Compute final shape matrix with these ingredients
    shape_tm = cmdx.Tm(translate=root_pos, rotate=geometry.orient)
    shape_tm.translateBy(offset, cmdx.sPostTransform)
    shape_tm = cmdx.Tm(shape_tm.asMatrix() * root_tm.asMatrix().inverse())

    geometry.shape_offset = shape_tm.translation()
    geometry.shape_rotation = shape_tm.rotation()

    # Take root_scale into account
    if abs(root_scale.x) <= 0:
        geometry.radius = 0
        geometry.extents.x = 0

    if abs(root_scale.y) > 0:
        geometry.extents.x /= root_scale.x
        geometry.length /= root_scale.y
    else:
        geometry.length = 0
        geometry.extents.y = 0

    if abs(root_scale.z) <= 0:
        geometry.extents.z = 0

    # Store for subsequent accesses
    root.data["_rdGeometry"] = geometry

    return geometry


def _interpret_shape(mod, rigid, shape):
    """Translate `shape` into rigid shape attributes

    For example, if the shape is a `mesh`, we'll plug that in as
    a mesh for convex hull generation.

    """

    assert isinstance(rigid, cmdx.DagNode), "%s was not a cmdx.DagNode" % rigid
    assert isinstance(shape, cmdx.DagNode), "%s was not a cmdx.DagNode" % shape
    assert shape.isA(cmdx.kShape), "%s was not a shape" % shape
    assert rigid.type() == "rdRigid", "%s was not a rdRigid" % rigid

    bbox = shape.bounding_box
    extents = cmdx.Vector(bbox.width, bbox.height, bbox.depth)
    center = cmdx.Vector(bbox.center)

    mod.set_attr(rigid["shapeOffset"], center)
    mod.set_attr(rigid["shapeExtents"], extents)
    mod.set_attr(rigid["shapeRadius"], extents.x * 0.5)

    # Account for flat shapes, like a circle
    mod.set_attr(rigid["shapeLength"], max(extents.y, extents.x))

    if shape.type() == "mesh":
        mod.connect(shape["outMesh"], rigid["inputMesh"])
        mod.set_attr(rigid["shapeType"], MeshShape)

    elif shape.type() == "nurbsCurve":
        mod.connect(shape["local"], rigid["inputCurve"])
        mod.set_attr(rigid["shapeType"], MeshShape)

    elif shape.type() == "nurbsSurface":
        mod.connect(shape["local"], rigid["inputSurface"])
        mod.set_attr(rigid["shapeType"], MeshShape)

    # In case the shape is connected to a common
    # generator, like polyCube or polyCylinder
    _shapeattributes_from_generator(mod, shape, rigid)


def _interpret_transform(mod, rigid, transform):
    """Translate `transform` into rigid shape attributes

    Primarily joints, that have a radius and length.

    """

    if transform.isA(cmdx.kJoint):
        mod.set_attr(rigid["shapeType"], CapsuleShape)

        # Orient inner shape to wherever the joint is pointing
        # as opposed to whatever its jointOrient is facing
        geometry = infer_geometry(transform)

        mod.set_attr(rigid["shapeOffset"], geometry.shape_offset)
        mod.set_attr(rigid["shapeRotation"], geometry.shape_rotation)
        mod.set_attr(rigid["shapeLength"], geometry.length)
        mod.set_attr(rigid["shapeRadius"], geometry.radius)
        mod.set_attr(rigid["shapeExtents"], geometry.extents)


def local_bounding_size(root):
    """Bounding size taking immediate children into account

    DagNode.boundingBox on the other hand takes an entire
    hierarchy into account.

    """

    pos1 = root.transform(cmdx.sWorld).translation()
    positions = [pos1]

    # Start by figuring out a center point
    for child in root.children(type=root.type()):
        positions += [child.transform(cmdx.sWorld).translation()]

    center = cmdx.Vector()
    for pos in positions:
        center += pos
    center /= len(positions)

    # Then figure out a bounding box, relative this center
    min_ = cmdx.Vector()
    max_ = cmdx.Vector()

    for pos2 in positions:
        dist = pos2 - center

        min_.x = min(min_.x, dist.x)
        min_.y = min(min_.y, dist.y)
        min_.z = min(min_.z, dist.z)

        max_.x = max(max_.x, dist.x)
        max_.y = max(max_.y, dist.y)
        max_.z = max(max_.z, dist.z)

    size = cmdx.Vector(
        max_.x - min_.x,
        max_.y - min_.y,
        max_.z - min_.z,
    )

    # Keep smallest value within some sensible range
    minimum = list(size).index(min(size))
    size[minimum] = max(size) * 0.5

    return size, center


def _version():
    version = cmds.pluginInfo("ragdoll", query=True, version=True)
    version = "".join(version.split(".")[:3])

    try:
        return int(version.replace(".", ""))
    except ValueError:
        # No version during local or CI testing
        return 0


def _random_color():
    """Return a nice random color"""

    # Rather than any old color, limit colors to
    # the first 250 degress, out of 360 total
    # These all fall into a nice pastel-scheme
    # that fits with the overall look of Ragdoll
    hue = int(random.random() * 250)

    value = 0.7
    saturation = 0.7

    color = cmdx.ColorType()
    color.setColor((hue, value, saturation),
                   cmdx.ColorType.kHSV,
                   cmdx.ColorType.kFloat)

    return color


def global_scale():
    if cmds.optionVar(exists="ragdollScale"):
        return cmds.optionVar(query="ragdollScale")
    else:
        return 1.0


def edit_global_scale(scale):
    cmds.optionVar(floatValue=("ragdollScale", scale))

    affected_nodes = cmds.ls(type="rdConstraint")

    if affected_nodes:
        cmds.dgdirty(affected_nodes)


def delete_all_physics(include_attributes=False):
    """Nuke it from orbit

    Return to simpler days, days before physics, with this one command.

    """

    all_nodetypes = cmds.pluginInfo("ragdoll", query=True, dependNode=True)
    return delete_physics(cmdx.ls(type=all_nodetypes))


@with_undo_chunk
def delete_physics(nodes):
    """Delete Ragdoll from anything related to `nodes`

    This will delete anything related to Ragdoll from your scenes, including
    any attributes added (polluted) onto your animation controls.

    Arguments:
        nodes (list): Delete physics from these nodes

    """

    assert isinstance(nodes, (list, tuple)), "First input must be a list"

    result = {
        "deletedRagdollNodeCount": 0,
        "deletedExclusiveNodeCount": 0,
        "deletedUserAttributeCount": 0,
    }

    # Include shapes in supplied nodes
    shapes = []
    for node in nodes:

        # Don't bother with underworld shapes
        if node.isA(cmdx.kShape):
            continue

        shapes += node.shapes()

    shapes = filter(None, shapes)
    shapes = list(shapes) + nodes
    shapes = filter(lambda shape: shape.isA(cmdx.kShape), shapes)
    nodes = shapes

    # Filter by our types
    all_nodetypes = cmds.pluginInfo("ragdoll", query=True, dependNode=True)
    ragdoll_nodes = list(
        node for node in nodes
        if node.type() in all_nodetypes
    )

    # Nothing to do!
    if not ragdoll_nodes:
        return result

    # Delete transforms exclusively made for Ragdoll nodes.
    #  _____________________       ___________________
    # |                     |     |                   |
    # | Rigid               |     | Transform         |
    # |                     |     |                   |
    # |      exclusives [0] o<----o message           |
    # |_____________________|     |___________________|
    #
    #
    exclusives = list()
    for node in ragdoll_nodes:
        if "exclusiveNodes" not in node:
            continue

        for element in node["exclusiveNodes"]:
            other = element.connection(source=True, destination=False)

            if other is not None:
                assert isinstance(other, cmdx.Node), "This is a bug in cmdx"
                exclusives.append(other)

    # Delete attributes from Ragdoll interfaces,
    # such as on the original animation controls.
    #
    #  ______________________       ___________________
    # |                      |     |                   |
    # | Rigid                |     | Transform         |
    # |                      |     |                   |
    # |   userAttributes [0] o<----o mass              |
    # |                  [1] o<----o stiffness         |
    # |______________________|     |___________________|
    #
    #
    user_attributes = set()

    for node in ragdoll_nodes:
        if "userAttributes" not in node:
            continue

        for element in node["userAttributes"]:
            user_attribute = element.connection(plug=True,
                                                source=True,
                                                destination=False)
            if user_attribute is not None:
                user_attributes.add(user_attribute)

    result["deletedRagdollNodeCount"] = len(ragdoll_nodes)
    result["deletedExclusiveNodeCount"] = len(exclusives)
    result["deletedUserAttributeCount"] = len(user_attributes)

    # Ok, go ahead and start deleting stuff
    with cmdx.DagModifier() as mod:
        for attr in user_attributes:
            mod.delete_attr(attr)
            mod.do_it()

    for node in ragdoll_nodes + exclusives:
        try:
            # Use cmds rather than cmdx, as cmdx doesn't play nice
            # with the undo stack.. :(
            cmds.delete(node.path())
        except RuntimeError:
            # Already gone, good riddance
            pass

    return result


def normalise_shapes(root, max_delta=0.25):
    """Limit how greatly shapes can differ within a hierarchy

    Arguments:
        root (DagNode): Start of a hierarchy, must be a rigid
        max_delta (float): Percentage of how much a child rigid
            may differ from its parent. 25% is typically ok.

    """

    low = 1 - max_delta
    high = 1 + max_delta

    def get_radius(rigid):
        return max(0.1, rigid["shapeRadius"].read())

    root_rigid = root.shape(type="rdRigid")

    if not root_rigid:
        return

    last_radius = get_radius(root_rigid)
    hierarchy = list(root.descendents(type="rdRigid"))

    # This is our base
    hierarchy.remove(root_rigid)

    with cmdx.DagModifier() as mod:
        for rigid in hierarchy:
            radius = get_radius(rigid)

            ratio = radius / last_radius
            new_radius = radius

            if ratio < low:
                new_radius = last_radius * low

            if ratio > high:
                new_radius = last_radius * high

            # new_ratio = radius / new_radius
            new_extents = rigid["shapeExtents"].as_vector()
            new_extents.y = new_radius * 2
            new_extents.z = new_radius * 2

            mod.set_attr(rigid["shapeRadius"], new_radius)
            mod.set_attr(rigid["shapeExtents"], new_extents)


def _shape_name(transform_name):
    """Generate a suitable shape name from `transform_name`

    If a shape node has the name <transform>Shape<number>
    then Maya will keep that name updated as the transform
    name changes.

    """

    components = re.split(r"(\d+)$", transform_name, 1) + [""]
    return "Shape".join(components[:2])


def multiply_rigids(rigids, parent=None, channels=None):
    with cmdx.DagModifier() as mod:
        transform_name = _unique_name("rRigidMultiplier")
        shape_name = transform_name

        if parent is None:
            parent = mod.createNode("transform", name=transform_name)
            shape_name = _shape_name(transform_name)

        mult = mod.createNode("rdRigidMultiplier",
                              name=shape_name,
                              parent=parent)

        for rigid in rigids:
            mod.connect(mult["ragdollId"], rigid["multiplierNode"])

    if channels:
        channels = list(filter(None, [c for c in channels if c in mult]))

    if channels:
        for channel in channels:
            if channel not in mult:
                continue

            mult[channel].keyable = True

    else:
        # Default multipliers
        mult["airDensity"].keyable = True
        mult["linearDamping"].keyable = True
        mult["angularDamping"].keyable = True

    return mult


def multiply_constraints(constraints, parent=None, channels=None):
    with cmdx.DagModifier() as mod:
        transform_name = _unique_name("rConstraintMultiplier")
        shape_name = transform_name

        if parent is None:
            parent = mod.createNode("transform", name=transform_name)
            shape_name = _shape_name(transform_name)

        mult = mod.createNode("rdConstraintMultiplier",
                              name=shape_name,
                              parent=parent)

        for con in constraints:
            mod.connect(mult["ragdollId"], con["multiplierNode"])

    if channels:
        channels = list(filter(None, [c for c in channels if c in mult]))

    if channels:
        for channel in channels:
            if channel not in mult:
                continue

            mult[channel].keyable = True

    else:
        # Default multipliers
        mult["driveStrength"].keyable = True
        mult["linearDriveStiffness"].keyable = True
        mult["linearDriveDamping"].keyable = True
        mult["angularDriveStiffness"].keyable = True
        mult["angularDriveDamping"].keyable = True

    return mult


@with_undo_chunk
def convert_to_polygons(actor, worldspace=True):
    """Convert rigid or control to a polygonal surface

    Mostly intended for rendering and export of collision shapes

    Arguments:
        actor (rdRigid): Rigid which to generate a polygonal mesh from
        worldspace (bool): Move verticies to worldspace,
            or animate the translate/rotate channels

    """

    assert "outputMesh" in actor, (
        "%s did not have an .outputMesh attribute" % actor
    )

    with cmdx.DagModifier() as mod:
        tm = mod.create_node("transform", name=actor.name())
        mesh = mod.create_node("mesh", name=tm.name() + "Shape", parent=tm)
        mod.connect(actor["outputMesh"], mesh["inMesh"])
        mod.set_attr(mesh["displayColors"], True)
        mod.set_attr(mesh["displayColorChannel"], "Diffuse")

    # Transfer colors from our precious actor
    cmds.polyColorPerVertex(mesh.path(), rgb=actor["color"].read())

    if worldspace:
        with cmdx.DGModifier() as mod:
            dm = mod.create_node("decomposeMatrix")
            mod.connect(actor.parent()["worldMatrix"][0], dm["inputMatrix"])
            mod.connect(dm["outputTranslate"], tm["translate"])
            mod.connect(dm["outputRotate"], tm["rotate"])
            mod.connect(dm["outputScale"], tm["scale"])

    # Assign default shader
    lambert = cmdx.encode("initialShadingGroup")
    lambert.add(mesh)

    return mesh
