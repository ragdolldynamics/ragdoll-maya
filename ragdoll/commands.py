"""Functionality for scripting

These provide low-level access to node creation and scenegraph
manipulation and are meant for use in automation, pipeline and rigging.

These do not depend on scene selection, user preferences or Maya state.

NOTE: Every function in here MUST be undoable as-one.

"""

import sys
import logging
import functools

from maya import cmds
from maya.api import OpenMayaAnim as oma
from .vendor import cmdx
from . import (
    internal as i__,
    constants as c
)

log = logging.getLogger("ragdoll")


@i__.with_contract(kwargs={"name": (cmdx.string_types, None),
                           "parent": (cmdx.DagNode, None)},
                   returns=(cmdx.DagNode,))
@i__.with_undo_chunk
def create_scene(name=None, parent=None):
    """Create a new Ragdoll scene

    Arguments:
        name (str, optional): Override defaut name
        parent (DagNode, optional): Do not create a new transform, use this

    """

    time = cmdx.encode("time1")
    up = cmdx.up_axis()
    name = name or i__.unique_name("rScene")

    with cmdx.DagModifier() as mod:
        if parent is None:
            parent = mod.create_node("transform", name=name)

            # Not yet supported
            mod.set_keyable(parent["scale"], False)
            mod.set_locked(parent["scale"])

        else:
            name = parent.name(namespace=False)

        scene = _rdscene(mod, i__.shape_name(name), parent=parent)
        mod.connect(parent["worldMatrix"][0], scene["inputMatrix"])
        mod.connect(time["outTime"], scene["currentTime"])
        mod.set_attr(scene["startTime"], oma.MAnimControl.minTime())
        mod.set_attr(scene["gravity"], up * -982)
        mod.set_attr(scene["spaceMultiplier"], 0.1)

        # The ground is really really bouncy since 2021.04.28
        mod.set_attr(scene["groundFriction"], 0.1)
        mod.set_attr(scene["groundRestitution"], 0.01)

        if up.y:
            mod.set_keyable(scene["gravityY"])
            mod.set_nice_name(scene["gravityY"], "Gravity")

        else:
            mod.set_keyable(scene["gravityZ"])
            mod.set_nice_name(scene["gravityZ"], "Gravity")
            mod.set_attr(parent["rotateX"], cmdx.radians(90))

        mod.connect(parent["message"], scene["exclusiveNodes"][0])

    return scene


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,),
                   opts=("rigidAddUserAttributes",
                         "computeMass",
                         "createRigidType",
                         "rigidDefaults"))
def create_rigid(node, scene, opts=None, _cache=None):
    """Create a new rigid

    Create a new rigid from `node`, which may be a transform or
    shape. If transform, the first shape is queried for geometry.
    Otherwise, the shape itself is used for geometry.

    Arguments:
        node (DagNode): Maya transform or shape
        scene (DagNode): Ragdoll scene to which the new rigid is added
        defaults (dict, optional): Default attribute values for the
            newly created rigid
        _cache (AttributeCache, optional): Reach for attributes here first,
            to avoid triggering evaluations prematurely

    """

    if isinstance(node, i__.string_types):
        node = cmdx.encode(node)

    if isinstance(scene, i__.string_types):
        scene = cmdx.encode(scene)

    assert isinstance(node, cmdx.DagNode), type(node)
    assert isinstance(scene, cmdx.DagNode), type(scene)
    assert scene.type() == "rdScene", scene.type()

    assert not node.shape(type="rdRigid"), (
        "%s is already a rigid" % node
    )

    opts = opts or {}
    cache = _cache or {}
    defaults = opts.get("defaults", {})

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
        mod.set_attr(rigid["kinematic"], opts.get("passive", False))

        # Avoid contacts getting too excited
        mod.set_attr(rigid["maxDepenetrationVelocity"], 20.0)

        # Add to scene
        _add_rigid(mod, rigid, scene)

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

        if opts.get("computeMass"):
            # Establish a sensible default mass, also taking into
            # consideration that joints must be comparable to meshes.
            # Mass unit is kg, whereas lengths are in centimeters
            mod.set_attr(rigid["mass"], (
                rigid["shapeExtentsX"].read() *
                rigid["shapeExtentsY"].read() *
                rigid["shapeExtentsZ"].read() *
                0.01
            ))

    if opts.get("addUserAttributes"):
        uas = i__.UserAttributes(rigid, transform)
        uas.add_divider("Ragdoll")
        uas.add("collide")
        uas.add("mass")
        uas.add("friction")
        uas.add("restitution")
        uas.do_it()

    # Make the connections
    with cmdx.DagModifier() as mod:
        if opts.get("passive"):
            _connect_passive(mod, rigid, transform)
        else:
            _connect_active(mod, rigid, transform,
                            existing=opts.get("existing"))

        # Apply provided default attribute values
        for key, value in defaults.items():
            mod.set_attr(rigid[key], value)

    return rigid


def create_active_rigid(node, scene, **kwargs):
    return create_rigid(node, scene, opts={"passive": False}, **kwargs)


def create_passive_rigid(node, scene, **kwargs):
    return create_rigid(node, scene, opts={"passive": True}, **kwargs)


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_rigid(rigid, opts=None):
    if isinstance(rigid, i__.string_types):
        rigid = cmdx.encode(rigid)

    opts = opts or {}
    opts = dict({"passive": True}, **opts)

    transform = rigid.parent()

    # Toggle between active and passive
    if opts["passive"] is None:
        opts["passive"] = not rigid["kinematic"].read()

    with cmdx.DagModifier() as mod:
        #
        # Convert active --> passive
        #
        if not rigid["kinematic"] and opts["passive"]:
            mod.disconnect(transform["translateX"])
            mod.disconnect(transform["translateY"])
            mod.disconnect(transform["translateZ"])
            mod.disconnect(transform["rotateX"])
            mod.disconnect(transform["rotateY"])
            mod.disconnect(transform["rotateZ"])

            mod.connect(transform["worldMatrix"][0], rigid["inputMatrix"])

            # May be connected
            mod.force_set_attr(rigid["kinematic"], True)

            # This rigid can no longer be affected by constraints
            constraints = rigid["ragdollId"].connections(type="rdConstraint",
                                                         source=False,
                                                         plugs=True)
            for plug in constraints:
                if plug.name() == "childRigid":
                    mod.delete(plug.node())

        #
        # Convert passive --> active
        #
        elif not opts["passive"]:
            mod.force_set_attr(rigid["kinematic"], False)

            # The user will expect a newly-turned active rigid to collide
            mod.smart_set_attr(rigid["collide"], True)

            _connect_active(mod, rigid, transform)

    return rigid


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"transform": (cmdx.DagNode, None),
                           "opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def create_constraint(parent, child, transform=None, opts=None):
    assert child.type() == "rdRigid", child.type()
    assert parent.type() in ("rdRigid", "rdScene"), (
        "%s must be a rigid or scene" % parent.type()
    )

    opts = dict({
        "name": "rConstraint",
        "outlinerStyle": c.RagdollStyle,
    }, **(opts or {}))

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

    name = i__.unique_name(opts["name"])

    with cmdx.DagModifier() as mod:
        if not transform and opts["outlinerStyle"] != c.RagdollStyle:
            if opts["outlinerStyle"] == c.MayaConstraintStyle:
                transform = mod.create_node("transform",
                                            name=name,
                                            parent=child.parent())

            if opts["outlinerStyle"] == c.nConstraintStyle:
                transform = mod.create_node("transform", name=name)

            name = i__.shape_name(name)

        transform = transform or child.parent()
        con = _rdconstraint(mod, name, parent=transform)

        draw_scale = _scale_from_rigid(child)
        mod.set_attr(con["drawScale"], draw_scale)

        mod.connect(parent["ragdollId"], con["parentRigid"])
        mod.connect(child["ragdollId"], con["childRigid"])

        _reset_constraint(mod, con)

        # Add to scene
        _add_constraint(mod, con, scene)

    return con


@i__.with_undo_chunk
def animation_constraint(rigid, opts=None):
    """A special-purpose constraint for converting animation into a guide

    Animation is converted into a matrix which is then used by a newly
    created guide constraint.

    Arguments:
        rigid (cmdx.Node): Rigid which to constrain to animation

    Options:
        name (str): Name given to the constraint
        parent (cmdx.Node): Parent rigid, animation is assumed relative
            to this rigid. Default is the scene, i.e. worldspace

    """

    assert opts is None or isinstance(opts, dict), "opts must be of type dict"

    opts = dict({
        "name": "rAnimConstraint",
        "parent": None,
        "defaults": {"driveStrength": 1.0},
    }, **(opts or {}))

    scene = rigid["nextState"].connection(type="rdScene")
    assert scene is not None, "%s was not connected to a scene" % rigid

    transform = rigid.parent()
    parent_transform = transform.parent()

    parent = opts["parent"] or scene
    worldspace = True

    # Special case of the immediate parent already being a dynamic rigid body
    if parent_transform and parent_transform.shape(type="rdRigid"):
        parent = parent_transform.shape(type="rdRigid")
        worldspace = False

    assert "ragdollId" in parent, (
        "%s was not a suitable scene or rigid" % parent
    )

    # Without a pairBlend, the constraint is but the dream of a mad man
    pair_blend = rigid["outputTranslateX"].connection(type="pairBlend",
                                                      source=False)

    assert pair_blend, "%s must be passing through a pairBlend" % rigid

    # Pair blend directly feeds into the drive matrix
    with cmdx.DGModifier(interesting=False) as dgmod:
        compose = dgmod.create_node("composeMatrix", name="animToMatrix")

        if worldspace:
            # Account for node being potentially parented somewhere
            absolute = dgmod.create_node("multMatrix", name="makeAbsolute")

    with cmdx.DagModifier() as mod:
        name = opts["name"]
        name = i__.unique_name(name)

        # Compute *before* assigning constraint, to get the rigid
        # bounding box as opposed to the box for both
        scale = _scale_from_rigid(rigid)

        con = _rdconstraint(mod, name, parent=transform)

        mod.set_attr(con["limitEnabled"], False)
        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["drawScale"], scale)

        for key, value in opts["defaults"].items():
            mod.set_attr(con[key], value)

        mod.connect(parent["ragdollId"], con["parentRigid"])
        mod.connect(rigid["ragdollId"], con["childRigid"])

        mod.connect(pair_blend["inTranslate1"], compose["inputTranslate"])
        mod.connect(pair_blend["inRotate1"], compose["inputRotate"])
        mod.connect(transform["rotateOrder"], compose["inputRotateOrder"])

        if worldspace:
            mod.connect(compose["outputMatrix"], absolute["matrixIn"][0])

            if parent_transform and i__.is_dynamic(parent_transform, scene):
                # Because the parent transform is dynamic, we can't connect
                # directly to it as that would mean a cycle
                mod.set_attr(absolute["matrixIn"][1],
                             transform["parentMatrix"][0].asMatrix())

            else:
                mod.connect(transform["parentMatrix"][0],
                            absolute["matrixIn"][1])

            mod.connect(absolute["matrixSum"], con["driveMatrix"])

        else:
            mod.connect(compose["outputMatrix"], con["driveMatrix"])

        # Add to scene
        _add_constraint(mod, con, scene)

    uas = i__.UserAttributes(con, transform)
    uas.add("driveStrength",
            long_name="animStrength",
            nice_name="Anim Strength")
    uas.do_it()

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def ignore_contacts_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    name = parent.parent().name(namespace=False)
    opts = dict({
        "name": "rIgnore_%s" % name,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_ignore_contacts(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def point_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "name": "rPointConstraint",
        "maintainOffset": True,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_point(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def orient_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "name": "rOrientConstraint",
        "maintainOffset": True,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_orient(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def parent_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "name": "rParentConstraint",
        "maintainOffset": True,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_parent(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def hinge_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "name": "rHingeConstraint",
        "maintainOffset": True,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_hinge(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def socket_constraint(parent, child, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "name": "rSocketConstraint",
        "maintainOffset": True,
        "outlinerStyle": c.RagdollStyle,
    }, **opts)

    con = create_constraint(parent, child, opts=opts)
    convert_to_socket(con, opts=opts)
    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_ignore_contacts(con, opts=None):
    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        mod.smart_set_attr(con["disableCollision"], True)
        mod.smart_set_attr(con["limitEnabled"], False)
        mod.smart_set_attr(con["driveEnabled"], False)

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_point(con, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod, con, opts=opts)

        mod.smart_set_attr(con["type"], c.PointConstraint)
        mod.smart_set_attr(con["limitEnabled"], True)
        mod.smart_set_attr(con["limitStrength"], 1)
        mod.smart_set_attr(con["angularLimitX"], 0)
        mod.smart_set_attr(con["angularLimitY"], 0)
        mod.smart_set_attr(con["angularLimitZ"], 0)

        if opts["maintainOffset"]:
            # Hard
            mod.smart_set_attr(con["linearLimitX"], -1)
            mod.smart_set_attr(con["linearLimitY"], -1)
            mod.smart_set_attr(con["linearLimitZ"], -1)
        else:
            # Soft
            mod.smart_set_attr(con["disableCollision"], False)
            mod.smart_set_attr(con["limitStrength"], 0.01)
            mod.smart_set_attr(con["linearLimitX"], 0.001)
            mod.smart_set_attr(con["linearLimitY"], 0.001)
            mod.smart_set_attr(con["linearLimitZ"], 0.001)

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_orient(con, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod, con, opts=opts)

        mod.smart_set_attr(con["type"], c.OrientConstraint)
        mod.smart_set_attr(con["limitEnabled"], True)
        mod.smart_set_attr(con["limitStrength"], 1)
        mod.smart_set_attr(con["linearLimitX"], 0)
        mod.smart_set_attr(con["linearLimitY"], 0)
        mod.smart_set_attr(con["linearLimitZ"], 0)
        mod.smart_set_attr(con["angularLimitX"], cmdx.radians(-1))
        mod.smart_set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.smart_set_attr(con["angularLimitZ"], cmdx.radians(-1))

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_hinge(con, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    """Convert `con` to Hinge Constraint

    Arguments:
        con (rdConstraint): Constraint to convert
        swing_axis (str): Aim swing in this direction. This should
            typically match your choice in the Maya "Orient Joints"
            dialog box.

    """

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod, con, opts=opts)

        mod.smart_set_attr(con["type"], c.HingeConstraint)
        mod.smart_set_attr(con["limitEnabled"], True)
        mod.smart_set_attr(con["limitStrength"], 1)
        mod.smart_set_attr(con["angularLimitX"], cmdx.radians(45))
        mod.smart_set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.smart_set_attr(con["angularLimitZ"], cmdx.radians(-1))

        if opts["maintainOffset"]:
            # Hard
            mod.smart_set_attr(con["linearLimitX"], -1)
            mod.smart_set_attr(con["linearLimitY"], -1)
            mod.smart_set_attr(con["linearLimitZ"], -1)
        else:
            # Soft
            mod.smart_set_attr(con["disableCollision"], False)
            mod.smart_set_attr(con["limitStrength"], 0.01)
            mod.smart_set_attr(con["linearLimitX"], 0.001)
            mod.smart_set_attr(con["linearLimitY"], 0.001)
            mod.smart_set_attr(con["linearLimitZ"], 0.001)

    reorient(con)

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_socket(con, opts=None):
    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod, con, opts=opts)

        mod.smart_set_attr(con["type"], c.SocketConstraint)
        mod.smart_set_attr(con["limitEnabled"], True)
        mod.smart_set_attr(con["limitStrength"], 1)
        mod.smart_set_attr(con["driveEnabled"], True)
        mod.smart_set_attr(con["driveStrength"], 1)
        mod.smart_set_attr(con["linearDriveStiffness"], 0)
        mod.smart_set_attr(con["linearDriveDamping"], 0)
        mod.smart_set_attr(con["angularLimitX"], cmdx.radians(45))
        mod.smart_set_attr(con["angularLimitY"], cmdx.radians(45))
        mod.smart_set_attr(con["angularLimitZ"], cmdx.radians(45))

        if opts["maintainOffset"]:
            # Hard
            mod.smart_set_attr(con["linearLimitX"], -1)
            mod.smart_set_attr(con["linearLimitY"], -1)
            mod.smart_set_attr(con["linearLimitZ"], -1)
        else:
            # Soft
            mod.smart_set_attr(con["disableCollision"], False)
            mod.smart_set_attr(con["limitStrength"], 0.01)
            mod.smart_set_attr(con["linearLimitX"], 0.001)
            mod.smart_set_attr(con["linearLimitY"], 0.001)
            mod.smart_set_attr(con["linearLimitZ"], 0.001)

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode,))
def convert_to_parent(con, opts=None):
    """A constraint with no degrees of freedom, a.k.a. Fixed Constraint"""

    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    if isinstance(con, i__.string_types):
        con = cmdx.encode(con)

    with cmdx.DagModifier() as mod:
        _reset_constraint(mod, con, opts=opts)

        mod.smart_set_attr(con["type"], c.ParentConstraint)
        mod.smart_set_attr(con["limitEnabled"], True)
        mod.smart_set_attr(con["limitStrength"], 1)
        mod.smart_set_attr(con["angularLimitX"], cmdx.radians(-1))
        mod.smart_set_attr(con["angularLimitY"], cmdx.radians(-1))
        mod.smart_set_attr(con["angularLimitZ"], cmdx.radians(-1))

        if opts["maintainOffset"]:
            # Hard
            mod.smart_set_attr(con["linearLimitX"], -1)
            mod.smart_set_attr(con["linearLimitY"], -1)
            mod.smart_set_attr(con["linearLimitZ"], -1)
        else:
            # Soft
            mod.smart_set_attr(con["disableCollision"], False)
            mod.smart_set_attr(con["limitStrength"], 0.01)
            mod.smart_set_attr(con["linearLimitX"], 0.001)
            mod.smart_set_attr(con["linearLimitY"], 0.001)
            mod.smart_set_attr(con["linearLimitZ"], 0.001)

    return con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"aim": (cmdx.Vector, None),
                           "opts": (dict, None)},
                   returns=None)
def orient(con, aim=None, up=None):
    """Orient a constraint

    Aim the constraint towards the child of its rigid, unless an `aim`
    and/or `up` is provided. For constraints with a non-hierarchical
    parent and/or child, such as the Dynamic Control where the selection
    determines hierarchy rather than Maya's physical hierarchy, the
    `aim` is mandatory.

    """

    if isinstance(con, i__.string_types):
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

    def orient_from_positions(a, b, c=None):
        """Look at `a` from `b`, with an optional up-vector `c`

                a
                o
               /|
              / |
             /  |
            /   |
         c o____o b

        """

        assert isinstance(a, cmdx.Vector)
        assert isinstance(b, cmdx.Vector)
        assert c is None or isinstance(c, cmdx.Vector)

        aim = (b - a).normal()
        up = (c - a).normal() if c else cmdx.up_axis()

        cross = aim ^ up  # Make axes perpendicular
        up = cross ^ aim

        orient = cmdx.Quaternion()
        orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
        orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

        return orient

    origin = child_tm.translation()
    orient = orient_from_positions(origin, aim, up)
    mat = cmdx.Tm(translate=origin, rotate=orient).asMatrix()

    parent_frame = mat * parent_matrix.inverse()
    child_frame = mat * child_matrix.inverse()

    with cmdx.DagModifier() as mod:
        mod.set_attr(con["parentFrame"], parent_frame)
        mod.set_attr(con["childFrame"], child_frame)


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs=None,
                   returns=None)
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

    if isinstance(con, i__.string_types):
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


def _take_ownership(mod, rdnode, node):
    """Make `rdnode` the owner of `node`"""
    assert "exclusiveNodes" in rdnode, "%s not a Ragdoll node" % rdnode

    # Ensure next_available_index is up-to-date
    mod.do_it()

    index = rdnode["exclusiveNodes"].next_available_index()
    mod.connect(node["message"], rdnode["exclusiveNodes"][index])


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"reference": (cmdx.DagNode, None),
                           "opts": (dict, None)},
                   returns=(cmdx.DagNode,
                            cmdx.DagNode,
                            cmdx.DagNode))
def create_absolute_control(rigid, reference=None, opts=None):
    """Control a rigid body in worldspace

    Given a worldmatrix, attempt to guide a rigid body to match,
    with some stiffness and damping.

    This can be handy for transforming a rigid body as though it was
    kinematic, except with some response to forces and contacts.

    """

    if isinstance(rigid, i__.string_types):
        rigid = cmdx.encode(rigid)

    tmat = rigid.transform(cmdx.sWorld)

    scene = rigid["nextState"].connection()
    assert scene and scene.type() == "rdScene", (
        "%s was not part of a scene" % rigid
    )

    opts = dict({
        "name": "rSoftPin",
        "defaults": {},
        "addUserAttributes": True,
    }, **(opts or {}))

    with cmdx.DagModifier() as mod:
        name = opts["name"]
        shape_name = name
        ctrl = None

        if reference is None:
            name = i__.unique_name(name)
            reference = mod.create_node("transform", name=name)
            mod.set_attr(reference["translate"], tmat.translation())
            mod.set_attr(reference["rotate"], tmat.rotation())

            # Just mirror whatever the rigid is doing
            mod.set_attr(reference["scale"],
                         rigid["outputWorldScale"].as_vector())
            mod.set_keyable(reference["scale"], False)

            shape_name = i__.shape_name(name)

        ctrl = reference.shape(type="rdControl")

        if not ctrl:
            shape_name = i__.shape_name(reference.name(namespace=False))
            ctrl = _rdcontrol(mod, shape_name, reference, rigid)
            _take_ownership(mod, ctrl, reference)

        shape_name = i__.unique_name(name)
        con = _rdconstraint(mod, shape_name, reference)

        mod.connect(rigid["ragdollId"], con["childRigid"])

        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)
        mod.set_attr(con["disableCollision"], False)

        mod.set_attr(con["drawConnection"], False)
        mod.set_attr(con["drawScale"], _scale_from_rigid(rigid))

        for key, value in opts["defaults"].items():
            mod.set_attr(con[key], value)

        mod.connect(scene["ragdollId"], con["parentRigid"])
        mod.connect(reference["worldMatrix"][0], con["driveMatrix"])

        # Add to scene
        _add_constraint(mod, con, scene)

    if opts["addUserAttributes"]:
        forwarded = (
            "driveStrength",
            "linearDriveStiffness",
            "linearDriveDamping",
            "angularDriveStiffness",
            "angularDriveDamping"
        )

        reference_proxies = i__.UserAttributes(con, reference)
        reference_proxies.add_divider("Ragdoll")

        for attr in forwarded:
            # Expose on constraint node itself
            reference_proxies.add(attr)

        reference_proxies.do_it()

    return reference, ctrl, con


def is_a(node, typ):
    return node.type() == typ


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,
                         cmdx.DagNode,
                         cmdx.DagNode),
                   kwargs={"opts": (dict, None)},
                   returns=(cmdx.DagNode, cmdx.DagNode))
def create_relative_control(child_rigid, parent_rigid, reference, opts=None):
    """Control `child_rigid` relative to `parent_rigid` with `reference`

    Arguments:
        reference (transform): Follow this node
        child_rigid (rdRigid): Rigid which should follow `reference`

    Returns:
        New nodes (list): rdControl, rdConstraint

    """

    assert reference.isA(cmdx.kTransform), "%s was not a transform" % reference
    assert is_a(child_rigid, "rdRigid"), "%s was not a rdRigid" % child_rigid
    assert is_a(parent_rigid, "rdRigid"), "%s was not a rdRigid" % parent_rigid
    scene = child_rigid["nextState"].connection()
    assert scene and is_a(scene, "rdScene"), (
        "%s was not part of a scene" % child_rigid)
    scene = parent_rigid["nextState"].connection()
    assert scene and is_a(scene, "rdScene"), (
        "%s was not part of a scene" % parent_rigid)

    opts = dict({
        "name": "rSoftPin",
        "addUserAttributes": True,
        "defaults": {},
    }, **(opts or {}))

    with cmdx.DGModifier(interesting=False) as mod:
        mult = mod.create_node("multMatrix")

    with cmdx.DagModifier() as mod:
        shape_name = opts["name"]

        # Just mirror whatever the child_rigid is doing
        mod.set_attr(reference["scale"],
                     child_rigid["outputScale"].as_vector())
        mod.set_keyable(reference["scale"], False)

        ctrl = reference.shape(type="rdControl")

        if not ctrl:
            shape_name = i__.shape_name(reference.name(namespace=False))
            ctrl = _rdcontrol(mod, shape_name, reference, child_rigid)
            _take_ownership(mod, ctrl, reference)

        con = create_constraint(
            parent_rigid, child_rigid, transform=reference, opts={
                "name": opts["name"]
            })

        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)
        mod.set_attr(con["linearDriveStiffness"], 0)
        mod.set_attr(con["linearDriveDamping"], 0)

        for key, value in opts["defaults"].items():
            mod.set_attr(con[key], value)

        def bake_joint_orient(mat, orient):
            """Bake jointOrient values

            Such that keyframes can be made without
            taking those into account. E.g. a joint with 0 rotate
            but 45 degrees of jointOrient should only require a key
            with 0 degrees.

            """

            assert isinstance(mat, cmdx.om.MMatrix)
            assert isinstance(orient, cmdx.om.MQuaternion)

            mat_tm = cmdx.om.MTransformationMatrix(mat)
            new_quat = mat_tm.rotation(asQuaternion=True) * orient
            mat_tm.setRotation(new_quat)

            return mat_tm.asMatrix()

        # From this space..
        parent_matrix = child_rigid["inputParentInverseMatrix"].asMatrix()
        parent_matrix = parent_matrix.inverse()

        # To this space..
        parent_rigid_matrix = parent_rigid["cachedRestMatrix"].asMatrix()
        parent_rigid_matrix = parent_rigid_matrix.inverse()

        total_matrix = parent_matrix * parent_rigid_matrix

        if "jointOrient" in reference:
            joint_orient = reference["jointOrient"].as_quaternion()
            total_matrix = bake_joint_orient(total_matrix, joint_orient)

        # The drive operates relative the parent rigid. But the parent
        # rigid may not be the same as the Maya parent transform.
        # So, generate a realtive matrix, taking offset parent matrix
        # pivots and what not into account.
        mod.connect(reference["worldMatrix"][0], mult["matrixIn"][0])

        reference_parent = reference.parent()
        if reference_parent is not None:
            # You might think "hey, what about parentInverseMatrix!?"
            # And you'd be surprised to find out that offsetParentParent
            # is *excluded* from that matrix, so we need to physically
            # reach out onto the actual parent to find its inverse matrix.
            # Sigh..
            mod.connect(reference_parent["worldInverseMatrix"][0],
                        mult["matrixIn"][1])

        # mod.set_attr(mult["matrixIn"][2], total_matrix)
        mod.connect(mult["matrixSum"], con["driveMatrix"])

    if opts["addUserAttributes"]:
        forwarded = (
            "driveStrength",
            "linearDriveStiffness",
            "linearDriveDamping",
            "angularDriveStiffness",
            "angularDriveDamping"
        )

        reference_proxies = i__.UserAttributes(con, reference)
        reference_proxies.add_divider("Ragdoll")

        for attr in forwarded:
            # Expose on constraint node itself
            reference_proxies.add(attr)

        reference_proxies.do_it()

    return ctrl, con


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode, cmdx.DagNode),
                   kwargs=None,
                   returns=(cmdx.DagNode,))
def create_active_control(reference, rigid):
    """Control a rigid body using a reference transform

    Arguments:
        reference (transform): Follow this node
        rigid (rdRigid): Rigid which should follow `reference`

    """

    if isinstance(reference, i__.string_types):
        reference = cmdx.encode(reference)

    if isinstance(rigid, i__.string_types):
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
        ctrl = _rdcontrol(mod, "rActiveControl1", reference, rigid)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])
        mod.connect(reference["matrix"], con["driveMatrix"])

        mod.set_attr(con["driveEnabled"], True)
        mod.set_attr(con["driveStrength"], 1.0)

    forwarded = (
        "driveStrength",
        "linearDriveStiffness",
        "linearDriveDamping",
        "angularDriveStiffness",
        "angularDriveDamping"
    )

    reference_proxies = i__.UserAttributes(con, reference)
    reference_proxies.add_divider("Ragdoll")

    for attr in forwarded:
        # Expose on constraint node itself
        reference_proxies.add(attr)

    reference_proxies.do_it()

    return ctrl


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={"reference": (cmdx.DagNode, None)},
                   returns=(cmdx.DagNode,))
def create_kinematic_control(rigid, reference=None):
    if reference is not None and isinstance(reference, i__.string_types):
        reference = cmdx.encode(reference)

    if isinstance(rigid, i__.string_types):
        rigid = cmdx.encode(rigid)

    with cmdx.DagModifier() as mod:
        name = "rHardPin"
        shape_name = name

        if reference is None:
            name = i__.unique_name(name)
            reference = mod.create_node("transform", name=name)

            tmat = rigid.transform(cmdx.sWorld)

            mod.set_attr(reference["translate"], tmat.translation())
            mod.set_attr(reference["rotate"], tmat.rotation())
            mod.set_attr(reference["scale"], tmat.scale())

            mod.set_locked(reference["scale"])
            mod.set_keyable(reference["scale"], False)

            shape_name = i__.shape_name(name)

        ctrl = mod.create_node("rdControl", name=shape_name, parent=reference)

        if rigid["kinematic"].connected:
            mod.disconnect(rigid["kinematic"], destination=False)
            mod.do_it()

        mod.set_attr(rigid["kinematic"], True)
        mod.connect(rigid["ragdollId"], ctrl["rigid"])
        mod.connect(reference["worldMatrix"][0], rigid["inputMatrix"])

    forwarded = (
        "kinematic",
    )

    proxies = i__.UserAttributes(rigid, ctrl)
    for attr in forwarded:
        proxies.add(attr)
    proxies.do_it()

    return reference


# Alias
create_passive_control = create_kinematic_control


def _list_children(rigid):
    """Find all rigids considered to be 'children' of `rigid`"""
    plugs = rigid["ragdollId"].connections(source=False,
                                           plugs=True,
                                           type="rdRigid")

    # `rigid` could be the parent of multiple children
    for plug in plugs:
        if plug.name() != "parentRigid":
            continue

        yield plug.node()


def _list_influencers(rigid):
    """Find all constraints related to `rigid`"""
    for plug in rigid["ragdollId"].connections(type="rdConstraint",
                                               plugs=True):

        # Only consider rigids that are "children" of this
        # constraint as ones being actually influenced by it
        if plug.name() != "childRigid":
            continue

        yield plug.node()


@i__.with_undo_chunk
def create_mimic(root, opts=None):
    """Mimic an external control hierarchy"""

    if root.isA(cmdx.kTransform):
        root = root.shape(type="rdRigid")

    assert root and root.type() == "rdRigid", "%s was not a rigid" % root

    opts = dict({

        # Disable all other constraints, take exclusive control
        "exclusive": True,

        # Add local and world multipliers
        "addMultiplier": True,

        # Transforms for simplicity, joints for flexibility and IK
        "nodeType": c.Transform,

        # Add user attributes
        "addUserAttributes": True,

        "addSoftPin": True,
        "addHardPin": True,

        "cleanChannelBox": True,

        # Should current rotate/translate values be zeroed out?
        # I.e. store offset in a parent group
        "freezeTransform": True,

    }, **(opts or {}))

    def make_name(name):
        first = name[0]
        rest = name[1:]

        # Special case.
        # Account for existing one-letter prefix
        # e.g. pCube -> rCube
        # But watch out for the existing prefix also being `r`
        # e.g. rCube -> rrCube
        # But watch out for the first *two* characters being upper-case
        # e.g. FKHand -> rFKHand
        if all([len(name) > 1,
                name[1] != "r",
                name[1].isupper(),
                not name[2].isupper()]):
            first = name[1]
            rest = name[2:]

        name = "r" + first.upper() + rest
        name = i__.unique_name(name)

        return name

    def freeze_transform(tm, transform):
        with cmdx.DagModifier() as mod:
            if cmdx.__maya_version__ >= 2020:
                mod.set_attr(transform["offsetParentMatrix"],
                             tm.as_matrix())

            else:
                name = transform.name() + "Offset"
                offset = mod.create_node("transform", name=name)
                mod.set_attr(offset["translate"], tm.translation())
                mod.set_attr(offset["rotate"], tm.rotation())
                mod.set_attr(transform["translate"], 0)
                mod.set_attr(transform["rotate"], 0)
                mod.parent(transform, offset)

                parent = transform.parent()
                if parent is not None:
                    mod.parent(offset, parent)

    passive_root = root["kinematic"].read()

    if passive_root:
        convert_rigid(root, opts={"passive": False})

    with cmdx.DagModifier() as mod:
        tm = root.transform(cmdx.sWorld)
        transform = root.parent()
        name = make_name(transform.name())
        root_reference = mod.create_node("transform", name=name)
        mod.set_keyable(root_reference["scale"], False)

        if opts["freezeTransform"] and opts["nodeType"] != c.Joint:
            freeze_transform(tm, root_reference)
        else:
            mod.set_attr(root_reference["translate"], tm.translation())
            mod.set_attr(root_reference["rotate"], tm.rotation())

    root_reference, root_ctrl, root_con = create_absolute_control(
        root,
        reference=root_reference,

        # Disable per default
        opts={
            "name": "rSoftPinConstraint",
            "addUserAttributes": False,
            "defaults": {
                "driveStrength": 1.0 if opts["addMultiplier"] else 0.0
            }
        }
    )

    ctrls = [root_ctrl]
    local_cons = []
    world_cons = [root_con]
    multipliers = []

    # As we generate the mimic hierarchy, keep track
    # of which reference is associated to each rigid,
    # so as to facilitate one reference with multiple
    # children, like two legs connecting to one hip.
    rigid_to_reference = {root: root_reference}

    pose_attributes = (
        ("driveStrength", "poseStrength", "Strength"),
        ("angularDriveStiffness", "poseStiffness", "Stiffness"),
        ("angularDriveDamping", "poseDamping", "Damping"),
    )

    pin_attributes = (
        ("driveStrength", "pinStrength", "Strength"),
        ("linearDriveStiffness", "pinTranslateStiffness",
         "Translate Stiffness"),
        ("linearDriveDamping", "pinTranslateDamping", "Translate Damping"),
        ("angularDriveStiffness", "pinRotateStiffness", "Rotate Stiffness"),
        ("angularDriveDamping", "pinRotateDamping", "Rotate Damping"),
    )

    if opts["addUserAttributes"]:
        proxies = i__.UserAttributes(root_con, root_reference)
        proxies.add_divider("Soft Pin")

        for attr, name, nice in pin_attributes:
            proxies.add(attr, long_name=name, nice_name=nice)

        proxies.do_it()

    # Recursively walk from root throughout the connected rigid hierarchy
    #
    #         o
    #         |
    #       o-o-o
    #      /  |  \
    #     o   o   o
    #    /    |    \
    #   o   o-o-o   o
    #  /    |   |    \
    #       |   |
    #       |   |
    #       o   o
    #       |   |
    #       |   |
    #       |   |
    #     --o   o--
    #
    def walk(root, parent_reference=None):
        for child in _list_children(root):
            # Take exclusive control
            if opts["exclusive"]:
                with cmdx.DagModifier() as mod:
                    for con in _list_influencers(child):
                        try:
                            mod.smart_set_attr(con["driveEnabled"], False)
                        except cmdx.LockedError:
                            log.debug(
                                "Puppet could not take exclusive control "
                                "over %s, it was locked" % con
                            )

            try:
                # We've already created a reference to this rigid
                reference = rigid_to_reference[child]

            except KeyError:
                # Let's make a new reference
                transform = child.parent()

                # We can't assume the original rigid bodies are
                # parented or that there aren't transforms inbetween
                # each rigid. So let's compute a new local matrix.
                tm = cmdx.Tm(
                    child["worldMatrix"][0].as_matrix() *
                    root["worldInverseMatrix"][0].as_matrix()
                )

                with cmdx.DagModifier() as mod:
                    name = make_name(transform.name())
                    reference = mod.create_node("transform",
                                                name=name,
                                                parent=parent_reference)

                    if opts["freezeTransform"] and opts["nodeType"] != c.Joint:
                        freeze_transform(tm, reference)
                    else:
                        mod.set_attr(reference["translate"], tm.translation())
                        mod.set_attr(reference["rotate"], tm.rotation())

                rigid_to_reference[child] = reference

            ctrl, con = create_relative_control(
                child, root, reference, opts={
                    "name": "rPoseConstraint",
                    "addUserAttributes": False
                })

            if parent_reference is not None:
                parent_ctrl = parent_reference.shape(type="rdControl")
            else:
                parent_ctrl = root_ctrl

            # Forwards compatibility
            with cmdx.DagModifier() as mod:
                mod.connect(parent_ctrl["ragdollId"],
                            ctrl["parentControl"])

            if opts["addUserAttributes"]:
                proxies = i__.UserAttributes(con, reference)
                proxies.add_divider("Pose")

                for attr, name, nice in pose_attributes:
                    proxies.add(attr, long_name=name, nice_name=nice)

                proxies.do_it()

            ctrls.append(ctrl)
            local_cons.append(con)

            if opts["addSoftPin"]:
                _, ctrl, con = create_absolute_control(
                    child, reference=reference,
                    opts={
                        "name": "rSoftPinConstraint",
                        "addUserAttributes": False,
                        "defaults": {

                            # Let the user enable this on a per-rigid basis
                            "driveStrength": 0.0
                        }
                    }
                )

                if opts["addUserAttributes"]:
                    proxies = i__.UserAttributes(con, reference)
                    proxies.add_divider("Soft Pin")

                    for attr, name, nice in pin_attributes:
                        proxies.add(attr, long_name=name, nice_name=nice)

                    proxies.do_it()

            ctrls.append(ctrl)
            world_cons.append(con)

            walk(child, reference)
    walk(root, root_reference)

    if opts["addHardPin"]:
        attr = cmdx.Enum("hardPin", fields=["Inherit", "Off", "On"])

        # Ensure this attribute appears ahead of other attributes
        with cmdx.DGModifier() as mod:
            mod.add_attr(root_reference, attr)
            mod.do_it()

            index = root["userAttributes"].next_available_index()
            mod.connect(root_reference["hardPin"],
                        root["userAttributes"][index])
            mod.do_it()

            # Preserve this
            if passive_root:
                mod.set_attr(root_reference["hardPin"], 2)

        proxies = i__.UserAttributes(root, root_reference)
        proxies.add_divider("Globals")
        proxies.add("kinematic",
                    long_name="globalHardPin",
                    nice_name="Global Hard Pin")
        proxies.do_it()

        with cmdx.DGModifier(interesting=False) as mod:
            for rigid, reference in rigid_to_reference.items():
                mod.connect(reference["worldMatrix"][0],
                            rigid["inputMatrix"])

                if rigid != root:
                    mod.add_attr(reference, attr)
                    mod.do_it()

                    # Clean this up along with the rest
                    index = rigid["userAttributes"].next_available_index()
                    mod.connect(reference["hardPin"],
                                rigid["userAttributes"][index])
                    mod.do_it()

                choice = mod.create_node("choice", "hardPinChoice")
                mod.connect(root_reference["globalHardPin"],
                            choice["input"][0])
                mod.set_attr(choice["input"][1], False)
                mod.set_attr(choice["input"][2], True)

                mod.connect(reference["hardPin"], choice["selector"])
                mod.connect(choice["output"], rigid["kinematic"])
                _take_ownership(mod, rigid, choice)

    if opts["addMultiplier"]:
        pose_mult = multiply_constraints(
            local_cons, parent=root_reference, opts={
                "name": "rGlobalPose",
            })

        multipliers.append(pose_mult)

        if opts["addSoftPin"]:
            soft_mult = multiply_constraints(
                world_cons, parent=root_reference, opts={
                    "name": "rGlobalSoftPin",
                    "defaults": {"driveStrength": 1.0}
                })

            multipliers.append(soft_mult)

        if opts["addUserAttributes"]:
            proxies = i__.UserAttributes(pose_mult, root_reference)
            proxies.add("driveStrength",
                        long_name="globalPoseStrength",
                        nice_name=False)
            proxies.do_it()

            if opts["addSoftPin"]:
                proxies = i__.UserAttributes(soft_mult, root_reference)
                proxies.add("driveStrength",
                            long_name="globalPinStrength",
                            nice_name=False)
                proxies.do_it()

    if opts["cleanChannelBox"] and opts["addUserAttributes"]:
        with cmdx.DagModifier() as mod:
            for mult in multipliers:
                mod.set_attr(mult["isHistoricallyInteresting"], False)

            for con in world_cons + local_cons:
                mod.set_attr(con["isHistoricallyInteresting"], False)

    if opts["nodeType"] == c.Joint:
        rigid_to_joint = {}
        joint_to_reference = {}
        reference_to_joint = {}

        # Convert hierarchy into a well-oriented joint chain,
        # something suitable for IK.
        with cmdx.DagModifier() as mod:
            for rigid, reference in rigid_to_reference.items():
                name = reference.name(namespace=False)
                joint = mod.create_node("joint", name=name)
                rigid_to_joint[rigid] = joint
                joint_to_reference[joint] = (rigid, reference)
                reference_to_joint[reference] = joint

        # Establish position and orientation
        with cmdx.DagModifier() as mod:
            for joint, (rigid, reference) in joint_to_reference.items():
                parent = reference.parent(type="transform")
                child = reference.child(type="transform")

                base = reference.translation(cmdx.sWorld)
                aim = base + cmdx.Vector(1, 0, 0)
                up = base + cmdx.Vector(0, 1, 0)

                if child:
                    aim = child.translation(cmdx.sWorld)

                else:
                    aim = cmdx.Vector(
                        rigid["shapeOffset"].as_point() *
                        reference["worldMatrix"][0].asMatrix()
                    )

                if parent:
                    up = parent.translation(cmdx.sWorld)

                orient = orient_from_positions(base, aim, up)

                mod.set_attr(joint["translate"], base)
                mod.set_attr(joint["rotate"], orient)

        # Joint Hierarchy
        for joint, (rigid, reference) in joint_to_reference.items():
            parent = reference.parent()

            try:
                joint_parent = reference_to_joint[parent]

            except KeyError:
                # Root joint
                pass

            else:
                # Let Maya figure out rotate and jointOrient
                cmds.parent(str(joint), str(joint_parent))

            joint["jointOrient"] = joint.rotation()
            joint["rotate"] = (0, 0, 0)

        # Extend tip joints, for IK
        with cmdx.DagModifier() as mod:
            for joint, (rigid, reference) in joint_to_reference.items():
                if reference.child(type="transform") is None:
                    length = rigid["shapeLength"].read()
                    name = joint.name(namespace=False) + "Tip"
                    tip = mod.create_node("joint", name=name, parent=joint)
                    tip["translateX"] = length
                    tip["rotate"] = joint.rotation()

        # Reference Hierarchy
        for joint, (rigid, reference) in joint_to_reference.items():
            cmds.parent(str(reference), str(joint))

            if joint.parent(type="joint") is None:
                root_reference = joint

    return root_reference


def orient_from_positions(a, b, c=None):
    """Look at `a` from `b`, with an optional up-vector `c`

            a
            o
           /|
          / |
         /  |
        /   |
     c o____o b

    """

    assert isinstance(a, cmdx.om.MVector), type(a)
    assert isinstance(b, cmdx.om.MVector), type(b)
    assert c is None or isinstance(c, cmdx.om.MVector), type(c)

    aim = (b - a).normal()
    up = (c - a).normal() if c else cmdx.up_axis()

    cross = aim ^ up  # Make axes perpendicular
    up = cross ^ aim

    orient = cmdx.Quaternion()
    orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
    orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

    return orient


@i__.with_undo_chunk
def clear_initial_state(rigids):
    assert isinstance(rigids, (tuple, list)), "%s was not a list" % rigids
    assert all(r.type() == "rdRigid" for r in rigids), (
        "%s wasn't all rdRigid nodes" % str(rigids)
    )

    with cmdx.DagModifier() as mod:
        for rigid in rigids:
            mod.set_attr(rigid["cachedRestMatrix"],
                         rigid["creationMatrix"].asMatrix())

    # Refresh current values
    for rigid in rigids:
        rigid["worldMatrix"][0].pull()


@i__.with_undo_chunk
def set_initial_state(rigids):
    """Use current world transformation as initial state for `rigids"""

    assert isinstance(rigids, (tuple, list)), "%s was not a list" % rigids
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


@i__.with_undo_chunk
def transfer_attributes(a, b, opts=None):
    if isinstance(a, i__.string_types):
        a = cmdx.encode(a)

    if isinstance(b, i__.string_types):
        b = cmdx.encode(b)

    opts = opts or {}
    opts = dict({"mirror": True}, **opts)

    def translate(node, typ):
        if node.type() == typ:
            return node
        elif node.isA(cmdx.kTransform):
            return node.shape(type=typ)

    ra = translate(a, "rdRigid")
    rb = translate(b, "rdRigid")
    ca = translate(a, "rdConstraint")
    cb = translate(b, "rdConstraint")

    if ra and rb:
        transfer_rigid(ra, rb)

    if ca and cb:
        transfer_constraint(ca, cb, opts=opts)


@i__.with_undo_chunk
def transfer_rigid(ra, rb):
    if isinstance(ra, i__.string_types):
        ra = cmdx.encode(ra)

    if isinstance(rb, i__.string_types):
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
        "shapeRotation",
    )

    with cmdx.DagModifier() as mod:
        for attr in rigid_attributes:

            # Account for locked attributes
            try:
                # Account for user attributes
                mod.smart_set_attr(rb[attr], ra[attr].read())
            except cmdx.LockedError:
                log.warning(
                    "%s was locked and wasn't changed" % rb[attr].path()
                )


@i__.with_undo_chunk
def transfer_constraint(ca, cb, opts=None):
    if isinstance(ca, i__.string_types):
        ca = cmdx.encode(ca)

    if isinstance(cb, i__.string_types):
        cb = cmdx.encode(cb)

    opts = opts or {}
    opts = dict({"mirror": True}, **opts)

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

    if opts["mirror"]:
        _mirror(parent_frame)
        _mirror(child_frame)

    with cmdx.DagModifier() as mod:
        mod.set_attr(cb["parentFrame"], parent_frame.asMatrix())
        mod.set_attr(cb["childFrame"], child_frame.asMatrix())


@i__.with_undo_chunk
@i__.with_contract(args=(cmdx.DagNode,),
                   kwargs={},
                   returns=(cmdx.DagNode, cmdx.DagNode),
                   opts=("constraintAddUserAttributes"))
def edit_constraint_frames(con, opts=None):
    opts = dict({
        "addUserAttributes": False,
    }, **(opts or {}))

    if isinstance(con, i__.string_types):
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

        # Have these deleted alongside the constraint
        index = con["exclusiveNodes"].next_available_index()
        mod.connect(parent_frame["message"], con["exclusiveNodes"][index])
        mod.connect(child_frame["message"], con["exclusiveNodes"][index + 1])

    if opts["addUserAttributes"]:
        proxies = i__.UserAttributes(con, child_frame)

        proxies.add_divider("Limit")
        proxies.add("limitEnabled")
        proxies.add("limitStrength")
        proxies.add("linearLimitX")
        proxies.add("linearLimitY")
        proxies.add("linearLimitZ")
        proxies.add("angularLimitX")
        proxies.add("angularLimitY")
        proxies.add("angularLimitZ")
        proxies.add("linearLimitStiffness")
        proxies.add("linearLimitDamping")
        proxies.add("angularLimitStiffness")
        proxies.add("angularLimitDamping")

        proxies.add_divider("Drive")
        proxies.add("driveEnabled")
        proxies.add("driveStrength")
        proxies.add("linearDriveStiffness")
        proxies.add("linearDriveDamping")
        proxies.add("angularDriveStiffness")
        proxies.add("angularDriveDamping")

        proxies.do_it()

    return parent_frame, child_frame


@i__.with_undo_chunk
def edit_shape(rigid):
    if isinstance(rigid, i__.string_types):
        rigid = cmdx.encode(rigid)

    assert rigid and rigid.type() == "rdRigid", "%s was not a rigid" % rigid
    parent_transform = rigid.parent()

    with cmdx.DagModifier() as mod:
        shape = mod.create_node("transform",
                                name="shapeTransform",
                                parent=parent_transform)

        mod.set_attr(shape["displayHandle"], True)
        mod.set_attr(shape["displayLocalAxis"], True)

        mod.add_attr(shape, cmdx.Enum(
            "shapeType", fields=[(c.BoxShape, "Box"),
                                 (c.SphereShape, "Sphere"),
                                 (c.CapsuleShape, "Capsule"),
                                 (c.MeshShape, "Mesh")]))

        mod.do_it()

        # Transfer current values
        mod.set_attr(shape["translateX"], rigid["shapeOffsetX"])
        mod.set_attr(shape["translateY"], rigid["shapeOffsetY"])
        mod.set_attr(shape["translateZ"], rigid["shapeOffsetZ"])

        mod.set_attr(shape["rotateX"], rigid["shapeRotationX"])
        mod.set_attr(shape["rotateY"], rigid["shapeRotationY"])
        mod.set_attr(shape["rotateZ"], rigid["shapeRotationZ"])

        mod.set_attr(shape["shapeType"], rigid["shapeType"])

        if rigid["shapeType"] in (c.BoxShape, c.MeshShape):
            mod.set_attr(shape["scale"], rigid["shapeExtents"])
        else:
            mod.set_attr(shape["scaleX"], rigid["shapeLength"])
            mod.set_attr(shape["scaleY"], rigid["shapeRadius"])

        mod.connect(shape["translate"], rigid["shapeOffset"])
        mod.connect(shape["rotate"], rigid["shapeRotation"])
        mod.connect(shape["scale"], rigid["shapeExtents"])
        mod.connect(shape["scaleX"], rigid["shapeLength"])
        mod.connect(shape["scaleY"], rigid["shapeRadius"])
        mod.connect(shape["shapeType"], rigid["shapeType"])

        # Have this deleted alongside the constraint
        index = rigid["exclusiveNodes"].next_available_index()
        mod.connect(shape["message"], rigid["exclusiveNodes"][index])

    return shape


@i__.with_undo_chunk
def create_force(type, scene):
    """Create a new force of `type`"""

    if isinstance(scene, i__.string_types):
        scene = cmdx.encode(scene)

    enum = {
        c.PointForce: 0,
        c.PushForce: 0,
        c.PullForce: 0,
        c.UniformForce: 1,
        c.TurbulenceForce: 2,
    }

    with cmdx.DagModifier() as mod:
        tm = mod.create_node("transform", name="rForce1")
        force = _rdforce(mod, "rForceShape1", parent=tm)
        mod.connect(tm["worldMatrix"][0], force["inputMatrix"])
        mod.set_attr(force["type"], enum[type])

        if type == c.PointForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["minDistance"], 0)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, i__.unique_name("rPointForce"))
            mod.rename(force, i__.unique_name("rPointForceShape"))

        elif type == c.PushForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["minDistance"], 0)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, i__.unique_name("rPushForce"))
            mod.rename(force, i__.unique_name("rPushForceShape"))

        elif type == c.PullForce:
            mod.set_attr(force["magnitude"], -100)
            mod.set_attr(force["minDistance"], 1)
            mod.set_attr(force["maxDistance"], 20)
            mod.rename(tm, i__.unique_name("rPullForce"))
            mod.rename(force, i__.unique_name("rPullForceShape"))

        elif type == c.UniformForce:
            mod.set_attr(force["magnitude"], 100)
            mod.set_attr(force["direction"], (0, -1, 0))
            mod.rename(tm, i__.unique_name("rUniformForce"))
            mod.rename(force, i__.unique_name("rUniformForceShape"))

        elif type == c.TurbulenceForce:
            mod.set_attr(force["magnitude"], 200)
            mod.set_attr(tm["scale"], (5, 5, 5))
            mod.rename(tm, i__.unique_name("rTurbulence"))
            mod.rename(force, i__.unique_name("rTurbulence"))

        elif type == c.WindForce:
            pass

        mod.set_attr(tm["displayHandle"], True)
        mod.set_attr(tm["overrideEnabled"], True)
        mod.set_attr(tm["overrideRGBColors"], True)
        mod.set_attr(tm["overrideColorRGB"], (1.0, 0.63, 0.0))  # Yellowish

    return force


@i__.with_undo_chunk
def create_slice(scene):  # type: (cmdx.DagNode) -> cmdx.DagNode
    if isinstance(scene, i__.string_types):
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


@i__.with_undo_chunk
def assign_force(rigid, force):  # type: (cmdx.DagNode, cmdx.DagNode) -> bool
    if isinstance(rigid, i__.string_types):
        rigid = cmdx.encode(rigid)

    if isinstance(force, i__.string_types):
        force = cmdx.encode(force)

    with cmdx.DagModifier() as mod:
        index = rigid["inputForce"].next_available_index()
        mod.connect(force["outputForce"], rigid["inputForce"][index])

    return True


@i__.with_undo_chunk
def duplicate(rigid):
    if isinstance(rigid, i__.string_types):
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


def infer_geometry(root, parent=None, children=None):
    """Find length and orientation from `root`

    This function looks at the child and parent of
    any given root for clues as to how to orient it

    Length is simply the distance between `root`
    and its first child.

    Arguments:
        root (root): The root from which to derive length and orientation

    """

    geometry = i__.Geometry()

    if children is None:
        # Better this than nothing
        children = list(root.children(type=root.type()))

    orient = cmdx.Quaternion()
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
                up = cmdx.up_axis()

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
                bbox = cmdx.Vector(bbox.width, bbox.height, bbox.depth)

                radius = sorted([bbox.x, bbox.y, bbox.z])

                # A bounding box will be either flat or long
                # That means 2/3 axes will be similar, and one
                # either 0 or large.
                #  ___________________
                # /__________________/|
                # |__________________|/
                #
                radius = radius[1]  # Pick middle one
                radius *= 0.5  # Width to radius
                radius *= 0.5  # Controls are typically larger than the model

            else:
                # If there's no visible geometry what so ever, we have
                # very little to go on in terms of establishing a radius.
                radius = geometry.length * 0.1

        size = cmdx.Vector(geometry.length, radius, radius)
        offset = orient * cmdx.Vector(geometry.length / 2.0, 0, 0)

        geometry.extents = cmdx.Vector(geometry.length, radius * 2, radius * 2)
        geometry.radius = radius

    else:
        size, center = _hierarchy_bounding_size(root)
        offset = center - root_pos

        geometry.length = size.x
        geometry.radius = min([size.y, size.z])
        geometry.extents = size

    # Compute final shape matrix with these ingredients
    shape_tm = cmdx.Tm(translate=root_pos,
                       rotate=geometry.orient)
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

    # Keep radius at minimum 10% of its length to avoid stick-figures
    geometry.radius = max(geometry.length * 0.1, geometry.radius)

    return geometry


@i__.with_refresh_suspended
@i__.with_timing
@i__.with_undo_chunk
def delete_physics(nodes, dry_run=False):
    """Delete Ragdoll from anything related to `nodes`

    This will delete anything related to Ragdoll from your scenes, including
    any attributes added (polluted) onto your animation controls.

    Arguments:
        nodes (list): Delete physics from these nodes
        dry_run (bool, optional): Do not actually delete anything,
            but still run through the process and throw exceptions
            if any, and still return the results of what *would*
            have been deleted if it wasn't dry.

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

    # See whether any of the nodes are referenced, in which
    # case we don't have permission to delete those.
    for node in ragdoll_nodes[:]:
        if node.is_referenced():
            ragdoll_nodes.remove(node)
            raise i__.UserWarning(
                "Cannot Delete Referenced Nodes",
                "I can't do that.\n\n%s is referenced "
                "and **cannot** be deleted." % node.shortest_path()
            )

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
    user_attributes = dict()
    for node in ragdoll_nodes:
        if "userAttributes" not in node:
            continue

        for element in node["userAttributes"]:
            user_attribute = element.connection(plug=True,
                                                source=True,
                                                destination=False)
            if user_attribute is None:
                continue

            other = user_attribute.node()

            # These will be deleted anyway
            if other in exclusives:
                continue

            if other not in user_attributes:
                user_attributes[other] = {}

            key = user_attribute.name(long=False)
            user_attributes[other][key] = user_attribute

    # Reorder attributes by the order they appear in the parent node
    #  _____________
    # |             |
    # |    Friction o -> 126
    # |        Mass o -> 127
    # |     Color R o -> 128
    # |     Color G o -> 129
    # |     Color B o -> 130
    # |             |
    # |_____________|
    #
    plug_to_index = {}
    for node, plugs in user_attributes.items():
        for index in range(node._fn.attributeCount()):
            attr = node._fn.attribute(index)
            fn = cmdx.om.MFnAttribute(attr)

            try:
                plug = plugs[fn.shortName]
            except KeyError:
                continue
            else:
                plug_to_index[plug] = index

    # TODO: This only works reliably when all ragdoll_nodes
    # are involved. When deleting only a subset of nodes, like
    # mimic controls which do not carry their associated rigid
    # for example, then rigid attributes will appear scrambled

    user_attributes = sorted(plug_to_index.items(), key=lambda i: i[1])
    user_attributes = [r[0] for r in user_attributes]

    result["deletedRagdollNodeCount"] = len(ragdoll_nodes)
    result["deletedExclusiveNodeCount"] = len(exclusives)
    result["deletedUserAttributeCount"] = len(user_attributes)

    # It was just a joke, relax
    if dry_run:
        return result

    # Delete attributes first, as they may otherwise
    # disappear along with their node.
    with cmdx.DagModifier() as mod:

        # Attributes are recreated in the reverse order
        # during undo, so to preserve their original order
        # we'll need to delete them in reverse.
        for attr in reversed(user_attributes):
            mod.delete_attr(attr)
        mod.do_it()

        for node in ragdoll_nodes + exclusives:
            try:
                mod.delete(node)
                mod.do_it()

            except cmdx.ExistError:
                # Deleting a shape whose parent transform has no other shape
                # automatically deletes the transform. This is shit behavior
                # that can be corrected in Maya 2022 onwards,
                # via includeParents=False
                pass

    return result


def delete_all_physics(dry_run=False):
    """Nuke it from orbit

    Return to simpler days, days before physics, with this one command.

    """

    all_nodetypes = cmds.pluginInfo("ragdoll", query=True, dependNode=True)
    all_nodes = cmdx.ls(type=all_nodetypes)
    return delete_physics(all_nodes, dry_run=dry_run)


@i__.with_undo_chunk
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


@i__.with_undo_chunk
def multiply_rigids(rigids, parent=None, channels=None):
    with cmdx.DagModifier() as mod:
        transform_name = i__.unique_name("rRigidMultiplier")
        shape_name = transform_name

        if parent is None:
            parent = mod.createNode("transform", name=transform_name)
            shape_name = i__.shape_name(transform_name)

        mult = _rdrigidmultiplier(mod, shape_name, parent)

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
        # Default channels
        mult["airDensity"].keyable = True
        mult["linearDamping"].keyable = True
        mult["angularDamping"].keyable = True

    return mult


@i__.with_undo_chunk
def multiply_constraints(constraints, parent=None, channels=None, opts=None):
    opts = dict({
        "name": "rConstraintMultiplier",
        "defaults": {},
    }, **(opts or {}))

    with cmdx.DagModifier() as mod:
        transform_name = i__.unique_name(opts["name"])
        shape_name = transform_name

        if parent is None:
            parent = mod.createNode("transform", name=transform_name)
            shape_name = i__.shape_name(transform_name)

        mult = _rdconstraintmultiplier(mod, name=shape_name, parent=parent)

        for key, value in opts["defaults"].items():
            mod.set_attr(mult[key], value)

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
        # Default channels
        mult["driveStrength"].keyable = True
        mult["linearDriveStiffness"].keyable = True
        mult["linearDriveDamping"].keyable = True
        mult["angularDriveStiffness"].keyable = True
        mult["angularDriveDamping"].keyable = True

    return mult


@i__.with_undo_chunk
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
        with cmdx.DGModifier(interesting=False) as mod:
            dm = mod.create_node("decomposeMatrix")
            mod.connect(actor.parent()["worldMatrix"][0], dm["inputMatrix"])
            mod.connect(dm["outputTranslate"], tm["translate"])
            mod.connect(dm["outputRotate"], tm["rotate"])
            mod.connect(dm["outputScale"], tm["scale"])

    # Assign default shader
    lambert = cmdx.encode("initialShadingGroup")
    lambert.add(mesh)

    return mesh


@i__.with_undo_chunk
def bake_simulation(rigids=None, opts=None):
    """Bake transforms associated with `rigids` with `opts`

    Arguments:
        rigids (list, optional): List of rigids to bake, or bake everything
        opts (dict, optional): Optional options

    Returns:
        transforms (list): Baked transforms, excluding
            those associated with passive and static rigids

    """

    assert rigids is None or isinstance(rigids, (tuple, list)), (
        "rigids must be list")
    assert opts is None or isinstance(opts, dict), "opts must be dict"

    opts = dict({
        "startTime": cmdx.oma.MAnimControl.minTime(),
        "endTime": cmdx.oma.MAnimControl.maxTime(),
        "attributes": ("tx", "ty", "tz", "rx", "ry", "rz"),
        "includeStatic": False,
        "bakeToLayer": False,
        "deletePhysics": True,
        "unrollRotation": True,
    }, **(opts or {}))

    # Make sure we're actually allowed to delete physics
    # E.g. the character(s) could be referenced.
    if opts["deletePhysics"]:
        try:
            delete_all_physics(dry_run=True)
        except i__.UserWarning:
            raise i__.UserWarning(
                "Cannot Delete Referenced Nodes",
                "Some nodes are referenced, I cannot delete those "
                "after baking.\n\n"
                "Untick the 'Delete Physics' option to preserve "
                "physics after baking, or import the referenced physics."
            )

    rigids = rigids or cmdx.ls(type="rdRigid")

    rigid_to_transform = {}
    for rigid in rigids:
        if not opts["includeStatic"]:
            # No need to bake something that is unaffected by physics
            if rigid["kinematic"] and not rigid["kinematic"].animated():
                continue

        rigid_to_transform[rigid] = rigid.parent()

    if not rigid_to_transform:
        raise UserWarning("Nothing to bake")

    time = tuple(t.value for t in (opts["startTime"], opts["endTime"]))

    args = [str(rigid) for rigid in rigid_to_transform.values()]
    kwargs = {
        "attribute": opts["attributes"],
        "simulation": True,
        "time": time,
        "sampleBy": 1,
        "oversamplingRate": 1,
        "disableImplicitControl": True,
        "preserveOutsideKeys": False,
        "sparseAnimCurveBake": False,
        "removeBakedAttributeFromLayer": False,
        "removeBakedAnimFromLayer": False,
        "bakeOnOverrideLayer": opts["bakeToLayer"],
        "minimizeRotation": False,
    }

    cmds.bakeResults(*args, **kwargs)

    if opts["unrollRotation"]:
        rotate_channels = ["%s.rx" % t for t in rigid_to_transform.values()]
        rotate_channels += ["%s.ry" % t for t in rigid_to_transform.values()]
        rotate_channels += ["%s.rz" % t for t in rigid_to_transform.values()]
        cmds.rotationInterpolation(rotate_channels, c="quaternionSlerp")
        cmds.rotationInterpolation(rotate_channels, c="none")

    def reconnect_physics():
        attributes = {
            "translateX": ("animCurveTL", "inTranslateX1", "outTranslateX"),
            "translateY": ("animCurveTL", "inTranslateY1", "outTranslateY"),
            "translateZ": ("animCurveTL", "inTranslateZ1", "outTranslateZ"),
            "rotateX": ("animCurveTA", "inRotateX1", "outRotateX"),
            "rotateY": ("animCurveTA", "inRotateY1", "outRotateY"),
            "rotateZ": ("animCurveTA", "inRotateZ1", "outRotateZ"),
        }

        outputs = (
            "outputTranslateX",
            "outputTranslateY",
            "outputTranslateZ",
            "outputRotateX",
            "outputRotateY",
            "outputRotateZ"
        )

        with cmdx.DagModifier() as mod:
            for rigid, transform in rigid_to_transform.items():

                # Handle cases of some outputs not reaching the pairblend
                # E.g. the user manually disconnected one or more.
                for output in outputs:
                    #
                    #   ___________       ___________
                    #  |           |     |           |
                    #  | pairBlend |     | transform |
                    #  |           o---->o           |
                    #  |           o     |___________|
                    #  |           o
                    #  |           |
                    #  |___________|
                    #
                    #
                    pairblend = rigid[output].connection(type="pairBlend",
                                                         source=False)

                    # They'll all reach the same pairblend
                    if pairblend:
                        break

                # In the rare case of no pairblend actually being there
                if not pairblend:
                    continue

                #  ___________                      ___________
                # |           |            /       |           |
                # | bakedAnim o-.- - - - -/      .-o transform |
                # |___________| |        /       | |___________|
                #               |  ___________   |
                #               | |           |  |
                #               .-o pairBlend o--`
                #                 |           |
                #                 |           |
                #                 |___________|
                #
                # 1. Find bakedAnim
                # 2. Plug bakedAnim -> pairBlend
                # 3. Swap bakedAnim for pairBlend
                #
                for a, (typ, inp, out) in attributes.items():
                    baked = transform[a].connection(type=typ,
                                                    destination=False,
                                                    plug=True)

                    if baked is None:
                        # Channel could have been locked, and thus won't bake
                        continue

                    mod.connect(baked, pairblend[inp])
                    mod.connect(pairblend[out], transform[a])

                if "simulation" not in transform:
                    proxy = i__.UserAttributes(pairblend,
                                               transform,
                                               owner=rigid)
                    proxy.add_divider("Baked")
                    proxy.add("weight",
                              long_name="simulation",
                              nice_name="Simulation")
                    proxy.do_it()

                mod.set_attr(transform["simulation"], 0.0)

    if opts["deletePhysics"]:
        delete_all_physics()
    else:
        # Baking automatically breaks the connection
        # between rigid and transform.
        reconnect_physics()

    return list(rigid_to_transform.values())


@i__.with_undo_chunk
def extract_from_scene(rigids,
                       scene=None,
                       include_connected_rigids=False,
                       discard_empty_scenes=True):
    """Extract `rigids` from `scene`

    Arguments:
        rigids (tuple): Rigids to be extracted from `scene`
        scene (cmdx.DagNode, optional): Scene to extract rigids into,
            defaults to creating a new scene.
        include_connected_rigids (bool, optional): Include rigids connected
            via constraints.
        discard_empty_scenes (bool, optional): Automatically delete
            old scenes that no longer have any rigids in them.

    """

    assert isinstance(rigids, (tuple, list)), "rigids must be tuple"
    assert len(rigids) > 0, "no rigids passed"
    assert isinstance(rigids[0], cmdx.DagNode), "rigid was node a cmdx type"
    assert all(rigid.type() == "rdRigid" for rigid in rigids), (
        "%s were not of type rdRigid" % ", ".join(rigids)
    )
    assert scene is None or isinstance(scene, cmdx.DagNode), (
        "rigid was node a cmdx type"
    )

    assert include_connected_rigids is False, (
        "include_connected_rigids Not yet implemeneted"
    )

    def walk_constraints():
        """Walk the constraint graph to include any connected rigids"""
        connected_rigids = set()
        for rigid in rigids:
            for plug in rigid["ragdollId"].connections(type="rdConstraint",
                                                       plugs=True):
                # A constraint connects to two rigids, a parent and child
                # We're only interested in those of which this rigid
                # is a child.
                if plug.name() != "childRigid":
                    continue

                con = plug.node()
                parent = con["parentRigid"].connection(
                    type="rdRigid", source=False)
                child = con["childRigid"].connection(
                    type="rdRigid", source=False)
                connected_rigids.add(parent)
                connected_rigids.add(child)

                # Todo

    new = scene or create_scene(name=i__.unique_name("rSceneExtracted"))
    old_scenes = set()

    with cmdx.DagModifier() as mod:
        for rigid in rigids:
            old = rigid["currentState"].connection(type="rdScene")
            old_scenes.add(old)

            if old:
                _remove_rigid(mod, rigid, old)
            else:
                log.warning("%s wasn't part of a scene?" % rigid)

            _add_rigid(mod, rigid, new)

            for plug in rigid["ragdollId"].connections(type="rdConstraint",
                                                       plugs=True):
                # A constraint connects to two rigids, a parent and child
                # We're only interested in those of which this rigid
                # is a child.
                if plug.name() != "childRigid":
                    continue

                con = plug.node()
                _remove_constraint(mod, con, old)
                _add_constraint(mod, con, new)

    # Automatically delete empty scenes
    if discard_empty_scenes:
        with cmdx.DagModifier() as mod:
            for scene in old_scenes:

                # Can't use `.count` or `evaluateNumElements` for some reason.
                # So let's check whether they are physically connected or not.
                if not any(el.connection() for el in scene["outputObjects"]):
                    mod.delete(scene)

    return new


def move_to_scene(rigids, scene):
    return extract_from_scene(rigids, scene)


def combine_scenes(scenes):
    assert len(scenes) > 1, "Cannot combine anything less than 2 scenes"

    master = scenes[0]
    for scene in scenes[1:]:
        rigids = filter(None, [
            el.connection(type="rdRigid")
            for el in scene["outputObjects"]
        ])

        move_to_scene(rigids, master)

    return master


"""

Internal helper functions

These things just help readability for the above functions,
and aren't meant for use outside of this module.

"""


def _shapeattributes_from_generator(mod, shape, rigid):
    """Look at `shape` history for a e.g. polyCube or polySphere

    This function interprets a simple shape, like a box, as a box
    rather than treat it like an arbitrary convex hull. That enables
    us to leverage the simpler shape types for improved
    performance, editability and visibility.

    """

    gen = None

    if "inMesh" in shape and shape["inMesh"].connected:
        gen = shape["inMesh"].connection()

    elif "create" in shape and shape["create"].connected:
        gen = shape["create"].connection()

    else:
        return

    if gen.type() == "polyCube":
        mod.set_attr(rigid["shapeType"], c.BoxShape)
        mod.set_attr(rigid["shapeExtentsX"], gen["width"])
        mod.set_attr(rigid["shapeExtentsY"], gen["height"])
        mod.set_attr(rigid["shapeExtentsZ"], gen["depth"])

    elif gen.type() == "polySphere":
        mod.set_attr(rigid["shapeType"], c.SphereShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "polyCylinder" and gen["roundCap"]:
        mod.set_attr(rigid["shapeType"], c.CylinderShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["height"])

        # Align with Maya's cylinder/capsule axis
        # TODO: This doesn't account for partial values, like 0.5, 0.1, 1.0
        mod.set_attr(rigid["shapeRotation"], list(map(cmdx.radians, (
            (0, 0, 90) if gen["axisY"] else
            (0, 90, 0) if gen["axisZ"] else
            (0, 0, 0)
        ))))

    elif gen.type() == "makeNurbCircle":
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "makeNurbSphere":
        mod.set_attr(rigid["shapeType"], c.SphereShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])

    elif gen.type() == "makeNurbCone":
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["heightRatio"])

    elif gen.type() == "makeNurbCylinder":
        mod.set_attr(rigid["shapeType"], c.CylinderShape)
        mod.set_attr(rigid["shapeRadius"], gen["radius"])
        mod.set_attr(rigid["shapeLength"], gen["heightRatio"])
        mod.set_attr(rigid["shapeRotation"], list(map(cmdx.radians, (
            (0, 0, 90) if gen["axisY"] else
            (0, 90, 0) if gen["axisZ"] else
            (0, 0, 0)
        ))))


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

    # Account for flat shapes, like a circle
    radius = extents.x
    length = max(extents.y, extents.x)

    # Account for X not necessarily being
    # represented by the width of the bounding box.
    if radius < i__.tolerance:
        radius = length * 0.5

    mod.set_attr(rigid["shapeOffset"], center)
    mod.set_attr(rigid["shapeExtents"], extents)
    mod.set_attr(rigid["shapeRadius"], radius * 0.5)
    mod.set_attr(rigid["shapeLength"], length)

    if shape.type() == "mesh":
        mod.connect(shape["outMesh"], rigid["inputMesh"])
        mod.set_attr(rigid["shapeType"], c.MeshShape)

    elif shape.type() == "nurbsCurve":
        mod.connect(shape["local"], rigid["inputCurve"])
        mod.set_attr(rigid["shapeType"], c.MeshShape)

    elif shape.type() == "nurbsSurface":
        mod.connect(shape["local"], rigid["inputSurface"])
        mod.set_attr(rigid["shapeType"], c.MeshShape)

    # In case the shape is connected to a common
    # generator, like polyCube or polyCylinder
    _shapeattributes_from_generator(mod, shape, rigid)


def _interpret_transform(mod, rigid, transform):
    """Translate `transform` into rigid shape attributes

    Primarily joints, that have a radius and length.

    """

    if transform.isA(cmdx.kJoint):
        mod.set_attr(rigid["shapeType"], c.CapsuleShape)

        # Orient inner shape to wherever the joint is pointing
        # as opposed to whatever its jointOrient is facing
        geometry = infer_geometry(transform)

        mod.set_attr(rigid["shapeOffset"], geometry.shape_offset)
        mod.set_attr(rigid["shapeRotation"], geometry.shape_rotation)
        mod.set_attr(rigid["shapeLength"], geometry.length)
        mod.set_attr(rigid["shapeRadius"], geometry.radius)
        mod.set_attr(rigid["shapeExtents"], geometry.extents)


def _to_cmds(name):
    """Convert cmdx instances to maya.cmds-compatible strings

    Two types of cmdx instances are returned natively, `Node` and `Plug`
    Any other return value remains unscathed.

    """

    func = getattr(sys.modules[__name__], name)

    contract = getattr(func, "contract", {})

    @functools.wraps(func)
    def to_cmds_wrapper(*args, **kwargs):

        # Convert cmdx arguments to string
        #
        # ---> cmdx --> string ---> func()
        #
        for index in range(len(args)):
            arg = args[index]
            _arg = contract["args"][index]

            if issubclass(_arg, cmdx.Node):
                # It's supposed to be string, and may already be
                if isinstance(arg, cmdx.string_types):
                    continue

                args[index] = arg.shortestPath()

            if issubclass(_arg, cmdx.Plug):
                # It's supposed to be string, and may already be
                if isinstance(arg, cmdx.string_types):
                    continue

                args[index] = arg.shortestPath()

        for key, value in kwargs.items():
            kwarg = contract["kwargs"][key]

            if issubclass(kwarg, cmdx.Node):
                # It's supposed to be string, and may already be
                if isinstance(value, cmdx.string_types):
                    continue

                kwargs[key] = value.shortestPath()

            if issubclass(kwarg, cmdx.Plug):
                # It's supposed to be string, and may already be
                if isinstance(value, cmdx.string_types):
                    continue

                kwargs[key] = value.path()

        result = func(*args, **kwargs)

        # Convert cmdx return values to string
        #
        # ----> cmdx ---> string
        #
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


def _rdscene(mod, name, parent=None):
    name = i__.unique_name(name)
    node = mod.create_node("rdScene", name=name, parent=parent)

    # Improve drive strength ranges
    mod.set_attr(node["positionIterations"], 4)
    mod.set_attr(node["version"], i__.version())

    return node


def _rdrigid(mod, name, parent):
    """Create a new rdRigid node"""
    assert isinstance(parent, cmdx.DagNode) and parent.isA(cmdx.kTransform), (
        "%s was not a transform" % parent
    )

    name = i__.unique_name(name)
    node = mod.create_node("rdRigid", name=name, parent=parent)

    # Link relevant attributes
    # Keep up to date with initial world matrix
    mod.connect(parent["worldMatrix"][0], node["restMatrix"])

    mod.set_attr(node["creationMatrix"], parent["worldMatrix"][0].as_matrix())

    # Compensate for any parents when outputting from the solver
    mod.connect(parent["parentInverseMatrix"][0],
                node["inputParentInverseMatrix"])

    mod.connect(parent["rotateOrder"], node["rotateOrder"])
    mod.connect(parent["rotateAxis"], node["rotateAxis"])
    mod.connect(parent["rotatePivot"], node["rotatePivot"])
    mod.connect(parent["rotatePivotTranslate"], node["rotatePivotTranslate"])
    mod.connect(parent["scalePivot"], node["scalePivot"])
    mod.connect(parent["scalePivotTranslate"], node["scalePivotTranslate"])

    if "jointOrient" in parent:
        mod.connect(parent["jointOrient"], node["jointOrient"])

    # Assign some random color, within some nice range
    mod.set_attr(node["color"], i__.random_color())
    mod.set_attr(node["version"], i__.version())

    return node


def _rdcontrol(mod, name, parent, rigid):
    """Create a new rdControl node"""
    name = i__.unique_name(name)
    node = mod.create_node("rdControl", name=name, parent=parent)
    mod.set_attr(node["color"], c.ControlColor)  # Default blue
    mod.set_attr(node["version"], i__.version())
    mod.set_attr(node["hiddenInOutliner"], True)
    mod.connect(rigid["ragdollId"], node["rigid"])
    mod.connect(rigid["geometryChanging"], node["inputGeometry"])

    # There's never anything to tweak on these, they are visual only
    mod.set_attr(node["isHistoricallyInteresting"], False)

    return node


def _rdconstraint(mod, name, parent):
    """Create a new rdConstraint node"""
    name = i__.unique_name(name)
    node = mod.create_node("rdConstraint", name=name, parent=parent)
    mod.set_attr(node["version"], i__.version())
    return node


def _rdconstraintmultiplier(mod, name, parent):
    """Create a new rdConstraint node"""
    name = i__.unique_name(name)
    node = mod.create_node("rdConstraintMultiplier", name=name, parent=parent)
    mod.set_attr(node["version"], i__.version())
    return node


def _rdrigidmultiplier(mod, name, parent):
    """Create a new rdConstraint node"""
    name = i__.unique_name(name)
    node = mod.create_node("rdRigidMultiplier", name=name, parent=parent)
    mod.set_attr(node["version"], i__.version())
    return node


def _rdforce(mod, name, parent):
    """Create a new rdForce node"""
    name = i__.unique_name(name)
    node = mod.create_node("rdForce", name=name, parent=parent)
    mod.set_attr(node["version"], i__.version())
    return node


def _add_rigid(mod, rigid, scene):
    """Add `rigid` to `scene`"""
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
    mod.set_attr(rigid["version"], i__.version())

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def _remove_rigid(mod, rigid, scene):
    assert rigid.type() == "rdRigid", rigid
    assert scene.type() == "rdScene", scene

    attributes = (
        ("outputObjects", "nextState"),
        ("startTime", "startTime"),
        ("currentTime", "currentTime"),
        ("inputActiveStart", "startState"),
        ("inputActive", "currentState"),
    )

    for a, b in attributes:
        if scene[a].isArray:
            other = rigid[b].connection(type="rdScene", plug=True)
            index = other._mplug.logicalIndex()
            mod.disconnect(scene[a][index], rigid[b])

        else:
            mod.disconnect(scene[a], rigid[b])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def _add_constraint(mod, con, scene):
    assert con["startState"].connection() != scene, (
        "%s already a member of %s" % (con, scene)
    )

    time = cmdx.encode("time1")
    index = scene["inputConstraintStart"].next_available_index()

    mod.connect(time["outTime"], con["currentTime"])
    mod.connect(con["startState"], scene["inputConstraintStart"][index])
    mod.connect(con["currentState"], scene["inputConstraint"][index])
    mod.set_attr(con["version"], i__.version())

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def _remove_constraint(mod, con, scene):
    assert con.type() == "rdConstraint", con
    assert scene.type() == "rdScene", scene

    attributes = (
        ("inputConstraintStart", "startState"),
        ("inputConstraint", "currentState"),
    )

    for a, b in attributes:
        if scene[a].isArray:
            other = con[b].connection(type="rdScene", plug=True)
            index = other._mplug.logicalIndex()
            mod.disconnect(scene[a][index], con[b])

        else:
            mod.disconnect(scene[a], con[b])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


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


def _connect_passive(mod, rigid, transform):
    mod.smart_set_attr(rigid["kinematic"], True)
    mod.connect(transform["worldMatrix"][0], rigid["inputMatrix"])


def _connect_active(mod, rigid, transform, existing=None):
    r"""Connect `rigid` to `transform` via `pairBlend`

     ______
    |\     \
    | \_____\                /
    | |     | . . . . . . - o -
    \ |     |              /
     \|_____|

    """

    with cmdx.DGModifier() as dgmod:
        pair_blend = dgmod.create_node("pairBlend", name="blendSimulation")
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

    # Pair blend directly feeds into the drive matrix
    with cmdx.DGModifier(interesting=False) as dgmod:
        compose = dgmod.create_node("composeMatrix", name="composePairBlend")

        # Account for node being potentially parented somewhere
        absolute = dgmod.create_node("multMatrix", name="makeAbsolute")

        _take_ownership(mod, rigid, compose)
        _take_ownership(mod, rigid, absolute)

    mod.connect(pair_blend["inTranslate1"], compose["inputTranslate"])
    mod.connect(pair_blend["inRotate1"], compose["inputRotate"])
    mod.connect(transform["rotateOrder"], compose["inputRotateOrder"])
    mod.connect(compose["outputMatrix"], absolute["matrixIn"][0])

    # Reproduce a parent hierarchy, but don't connect it to avoid cycle
    mod.set_attr(absolute["matrixIn"][1],
                 transform["parentMatrix"][0].asMatrix())

    # Support hard manipulation
    # For e.g. transitioning between active and passive
    mod.connect(absolute["matrixSum"], rigid["inputMatrix"])

    return pair_blend


def _reset_constraint(mod, con, opts=None):
    """Reset a constraint

    Arguments:
        mod (cmdx.DagModifier): Current modifier in use
        con (rdConstraint): The constraint to reset
        auto_orient (bool): Use current axis, or compute one from hierarchy

    """

    assert con.type() == "rdConstraint", "%s must be an rdConstraint" % con

    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
        "useRotatePivot": True,
    }, **opts)

    def reset_attr(attr):
        if not attr.editable:
            return
        mod.reset_attr(attr)

    reset_attr(con["limitEnabled"])
    reset_attr(con["limitStrength"])
    reset_attr(con["linearLimitX"])
    reset_attr(con["linearLimitY"])
    reset_attr(con["linearLimitZ"])
    reset_attr(con["angularLimitX"])
    reset_attr(con["angularLimitY"])
    reset_attr(con["angularLimitZ"])

    # This is normally what you'd expect
    mod.set_attr(con["disableCollision"], True)

    # Initialise parent frame
    parent_rigid = con["parentRigid"].connection(type="rdRigid")
    child_rigid = con["childRigid"].connection(type="rdRigid")

    # Align constraint to whatever the local transformation is
    if opts["maintainOffset"] and parent_rigid and child_rigid:
        child_matrix = child_rigid["cachedRestMatrix"].asMatrix()
        parent_matrix = parent_rigid["cachedRestMatrix"].asMatrix()
        child_frame = cmdx.Matrix4()

        if opts["useRotatePivot"]:
            # Use rotate pivot as an offset to the native parent/child frames
            rotate_pivot = child_rigid["rotatePivot"].as_vector()
            offset_tm = cmdx.Tm(child_matrix)
            offset_tm.translate_by(rotate_pivot)
            offset_matrix = offset_tm.as_matrix()

            child_frame = offset_matrix * child_matrix.inverse()
            child_matrix = offset_matrix

        parent_frame = child_matrix * parent_matrix.inverse()

        # Drive to where you currently are
        if con["driveMatrix"].writable:
            mod.set_attr(con["driveMatrix"], parent_frame)

        mod.set_attr(con["parentFrame"], parent_frame)
        mod.set_attr(con["childFrame"], child_frame)


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


def _scale_from_rigid(rigid):
    if rigid.parent().type() == "joint":
        return rigid["shapeLength"].read() * 0.25
    else:
        return sum(rigid["shapeExtents"].read()) / 3.0


def _hierarchy_bounding_size(root):
    """Bounding size taking immediate children into account

            _________
         o |    a    |
    ---o-|-o----o----o--
         | |_________|
         |      |
        o-o    bbox of a
        | |
        | |
        o o
        | |
        | |
       -o o-

    DagNode.boundingBox on the other hand takes an entire
    hierarchy into account.

    """

    pos1 = root.translation(cmdx.sWorld)
    positions = [pos1]

    # Start by figuring out a center point
    for child in root.children(type=root.type()):
        positions += [child.translation(cmdx.sWorld)]

    # There were no children, consider the parent instead
    if len(positions) < 2:

        # It's possible the immediate parent is an empty
        # group without translation. We can't use that, so
        # instead walk the hierarchy until you find the first
        # parent with some usable translation to it.
        for parent in root.lineage():
            pos2 = parent.translation(cmdx.sWorld)

            if pos2.isEquivalent(pos1, i__.tolerance):
                continue

            # The parent will be facing in the opposite direction
            # of what we want, so let's invert that.
            pos2 -= pos1
            pos2 *= -1
            pos2 += pos1

            positions += [pos2]

            break

    # There were neither parent nor children,
    # we don't have a lot of options here.
    if len(positions) < 2:
        return (
            # Default size
            cmdx.Vector(1, 1, 1),

            # Default center
            cmdx.Vector(0, 0, 0)
        )

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
