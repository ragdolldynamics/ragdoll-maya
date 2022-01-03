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
from .vendor import cmdx
from . import (
    internal as i__,
    constants as c
)

log = logging.getLogger("ragdoll")


def _take_ownership(mod, rdnode, node):
    """Make `rdnode` the owner of `node`"""

    try:
        plug = rdnode["owner"]
    except cmdx.ExistError:
        try:
            plug = rdnode["exclusiveNodes"]
        except cmdx.ExistError:
            raise TypeError("%s not a Ragdoll node" % rdnode)

    # Ensure next_available_index is up-to-date
    mod.do_it()

    index = plug.next_available_index()
    mod.connect(node["message"], plug[index])



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


def infer_geometry(root, parent=None, children=None, geometry=None):
    """Find length and orientation from `root`

    This function looks at the child and parent of
    any given root for clues as to how to orient it

    Length is simply the distance between `root`
    and its first child.

    Arguments:
        root (root): The root from which to derive length and orientation

    """

    geometry = geometry or i__.Geometry()

    # Better this than nothing
    if not children:
        children = []

        # Consider cases where children have no distance from their parent,
        # common in offset groups without an actual offset in them. Such as
        # for organisational purposes
        #
        # | hip_grp
        # .-o offset_grp      <-- Some translation
        #   .-o hip_ctl
        #     .-o hip_loc   <-- Identity matrix
        #
        root_pos = root.translation(cmdx.sWorld)
        for child in root.children(type=root.type()):
            child_pos = child.translation(cmdx.sWorld)

            if not root_pos.is_equivalent(child_pos):
                children += [child]

    # Special case of a tip without children
    #
    # o        How long are you?
    #  \              |
    #   \             v
    #    o------------o
    #
    # In this case, reuse however long the parent is
    if not children and parent:
        children = [root]
        root = parent
        parent = None

    def position_incl_pivot(node, debug=False):
        """Return the final position of the translate and rotate handles

        That includes the rotate pivot, which isn't part
        of the worldspace matrix.

        """

        if node.type() == "joint":
            return node.translation(cmdx.sWorld)

        rotate_pivot = node.transformation().rotatePivot()

        world_tm = node.transform(cmdx.sWorld)
        world_tm.translateBy(rotate_pivot, cmdx.sPreTransform)

        pos = world_tm.translation()

        if debug:
            loc = cmdx.encode(cmds.spaceLocator(name=node.name())[0])
            loc["translate"] = pos

        return pos

    orient = cmdx.Quaternion()
    root_tm = root.transform(cmdx.sWorld)
    root_pos = position_incl_pivot(root)
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
            positions += [position_incl_pivot(child)]

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
                up = position_incl_pivot(parent)
                up = (up - root_pos).normal()
            else:
                up = cmdx.up_axis()

            aim = (pos2 - root_pos).normal()
            cross = aim ^ up  # Make axes perpendicular
            up = cross ^ aim

            orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
            orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

            center_node_pos = position_incl_pivot(center_node)
            length = (center_node_pos - root_pos).length()

            geometry.orient = orient
            geometry.length = length

    if geometry.length > 0.0:

        if geometry.radius:
            # Pre-populated somewhere above
            radius = geometry.radius

        # Joints for example ship with this attribute built-in, very convenient
        elif "radius" in root:
            joint_scale = cmds.jointDisplayScale(query=True)
            radius = root["radius"].read() * joint_scale

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
        tm = cmdx.Tm(root_tm)

        if all(axis == 0 for axis in size):
            geometry.length = 0
            geometry.radius = 1
            geometry.extents = cmdx.Vector(1, 1, 1)

        else:
            geometry.length = size.x
            geometry.radius = min([size.y, size.z])
            geometry.extents = size

            # Embed length
            tm.translateBy(cmdx.Vector(0, size.x * -0.5, 0))

        offset = center - tm.translation()

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

        if node.isA(cmdx.kDagNode):
            shapes += node.shapes()

    # Include DG nodes too
    dgnodes = []
    for node in nodes:
        dgnodes += list(
            node["message"].outputs(
                type=("rdGroup",
                      "rdMarker",
                      "rdDistanceConstraint",
                      "rdFixedConstraint")))

    shapes = filter(None, shapes)
    shapes = list(shapes) + nodes
    nodes = shapes + dgnodes

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


def _interpret_shape2(shape):
    """Translate `shape` into rigid shape attributes

    For example, if the shape is a `mesh`, we'll plug that in as
    a mesh for convex hull generation.

    """

    assert isinstance(shape, cmdx.DagNode), "%s was not a cmdx.DagNode" % shape
    assert shape.isA(cmdx.kShape), "%s was not a shape" % shape

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

    geo = i__.Geometry()
    geo.shape_offset = center
    geo.extents = extents
    geo.radius = radius * 0.5
    geo.length = length

    gen = None

    # Guilty until proven innocent
    geo.shape_type = c.MeshShape

    if "inMesh" in shape and shape["inMesh"].connected:
        gen = shape["inMesh"].connection()

    elif "create" in shape and shape["create"].connected:
        gen = shape["create"].connection()

    if gen:
        # In case the shape is connected to a common
        # generator, like polyCube or polyCylinder

        if gen.type() == "polyCube":
            geo.shape_type = c.BoxShape
            geo.extents.x = gen["width"].read()
            geo.extents.y = gen["height"].read()
            geo.extents.z = gen["depth"].read()

        elif gen.type() == "polySphere":
            geo.shape_type = c.SphereShape
            geo.radius = gen["radius"].read()

        elif gen.type() == "polyPlane":
            geo.shape_type = c.BoxShape
            geo.extents.x = gen["width"].read()
            geo.extents.z = gen["height"].read()

            # Align top of box with plane
            if gen["axisY"]:
                average_size = (geo.extents.x + geo.extents.y) / 2.0
                geo.extents.y = average_size / 40.0
                geo.shape_offset.y = -geo.extents.y / 2.0
            else:
                average_size = (geo.extents.x + geo.extents.y) / 2.0
                geo.extents.z = average_size / 40.0
                geo.shape_offset.z = -geo.extents.z / 2.0

        elif gen.type() == "polyCylinder" and gen["roundCap"]:
            geo.shape_type = c.CylinderShape
            geo.radius = gen["radius"].read()
            geo.length = gen["height"].read()

            # Align with Maya's cylinder/capsule axis
            # TODO: This doesn't account for partial values, like 0.5, 0.1, 1.0
            geo.shape_rotation = list(map(cmdx.radians, (
                (0, 0, 90) if gen["axisY"] else
                (0, 90, 0) if gen["axisZ"] else
                (0, 0, 0)
            )))

        elif gen.type() == "makeNurbCircle":
            geo.radius = gen["radius"]

        elif gen.type() == "makeNurbSphere":
            geo.shape_type = c.SphereShape
            geo.radius = gen["radius"]

        elif gen.type() == "makeNurbCone":
            geo.radius = gen["radius"]
            geo.length = gen["heightRatio"]

        elif gen.type() == "makeNurbCylinder":
            geo.shape_type = c.CylinderShape
            geo.radius = gen["radius"]
            geo.length = gen["heightRatio"]
            geo.shape_rotation = list(map(cmdx.radians, (
                (0, 0, 90) if gen["axisY"] else
                (0, 90, 0) if gen["axisZ"] else
                (0, 0, 0)
            )))

    return geo


def _interpret_transform2(mod, transform):
    """Translate `transform` into rigid shape attributes

    Primarily joints, that have a radius and length.

    """

    geo = infer_geometry(transform)

    return geo


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


def _apply_scale(mat):
    tm = cmdx.Tm(mat)
    scale = tm.scale()
    translate = tm.translation()
    translate.x *= scale.x
    translate.y *= scale.y
    translate.z *= scale.z
    tm.setTranslation(translate)
    tm.setScale((1, 1, 1))
    return tm.as_matrix()


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

            if pos2.is_equivalent(pos1, i__.tolerance):
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
            # No size
            cmdx.Vector(0, 0, 0),

            # Original center
            pos1
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
