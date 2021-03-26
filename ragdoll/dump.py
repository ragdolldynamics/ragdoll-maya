"""Recreate Maya scene from Ragdoll dump

# Usage Example
import json
dump = cmds.ragdollDump()
dump = json.loads(dump)
dedump(dump)

"""

import json
import logging

from maya import cmds
from .vendor import cmdx
from . import commands

log = logging.getLogger("ragdoll")

# Python 2 backwards compatibility
try:
    string_types = basestring,
except NameError:
    string_types = str,


class Component(dict):
    """Simplified access to component members"""

    def __getattr__(self, key):
        value = super(Component, self).__getitem__("members")[key]

        if not isinstance(value, dict):
            return value

        if value["type"] == "Vector3":
            return cmdx.Vector(value["values"])

        elif value["type"] == "Color4":
            return cmdx.Color(value["values"])

        elif value["type"] == "Matrix44":
            return cmdx.Matrix4(value["values"])

        elif value["type"] == "Quaternion":
            return cmdx.Quaternion(*value["values"])

        else:
            raise TypeError("Unsupported type: %s" % value)

    def __getitem__(self, key):
        try:
            return self.__getattr__(key)
        except KeyError:
            return super(Component, self).__getitem__(key)


def dedump(dump):
    """Recreate Maya scene from `dump`"""

    with cmdx.DagModifier() as mod:
        root = mod.createNode("transform", name="dump")

    for entity, data in dump["entities"].items():
        comps = data["components"]

        if "RigidComponent" not in comps:
            continue

        name = Component(comps["NameComponent"])

        if not name.path:
            # Bad export
            continue

        joint = name.path.rsplit("|", 3)[-2]

        scale = Component(comps["ScaleComponent"])
        rest = Component(comps["RestComponent"])
        desc = Component(comps["GeometryDescriptionComponent"])

        # Establish rigid transformation
        tm = cmdx.TransformationMatrix(rest.matrix)

        # Establish shape
        if desc.type in ("Cylinder", "Capsule"):
            radius = desc.radius * scale.absolute.x
            length = desc.length * scale.absolute.y
            geo, _ = cmds.polyCylinder(axis=(1, 0, 0),
                                       radius=radius,
                                       height=length,
                                       roundCap=True,
                                       subdivisionsCaps=5)

        elif desc.type == "Box":
            extents = desc.extents
            extents.x *= scale.absolute.x
            extents.y *= scale.absolute.y
            extents.z *= scale.absolute.z
            geo, _ = cmds.polyCube(width=extents.x,
                                   height=extents.y,
                                   depth=extents.z)

        elif desc.type == "Sphere":
            radius = desc.radius * scale.absolute.x
            geo, _ = cmds.polySphere(radius=radius)

        else:
            print(
                "Unsupported shape type: %s.type=%s"
                % (name.path, desc.type)
            )
            continue

        with cmdx.DagModifier() as mod:
            transform = mod.createNode("transform", name=joint, parent=root)
            transform["translate"] = tm.translation()
            transform["rotate"] = tm.rotation()

        # Establish shape transformation
        offset = desc.offset
        offset.x *= scale.absolute.x
        offset.y *= scale.absolute.y
        offset.z *= scale.absolute.z

        geo = cmdx.encode(geo)
        geo["translate"] = offset
        geo["rotate"] = desc.rotation

        transform.addChild(geo)


def load(dump, scene_id=-1, parent=None, remap=None):
    """Apply JSON to existing nodes in the scene"""

    if isinstance(dump, string_types):
        dump = json.loads(dump)

    assert isinstance(dump, dict), "dump argument must be dict"
    assert "schema" in dump and dump["schema"] == "ragdoll-1.0", (
        "Dump not compatible with this version of Ragdoll"
    )

    transforms = {}
    scenes = {}
    rigids = {}
    constraints = {}

    def _match_transforms():
        """Find and associate a Maya transform with entities in this dump"""
        for entity, data in dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            # There won't be any solvers in here just yet
            if "SolverComponent" in comps:
                continue

            # The only animation controls we are able to influence
            # are those driven by a rigid.
            if "RigidComponent" not in comps:
                continue

            name = Component(comps["NameComponent"])

            if not name.path:
                # Bad export
                continue

            # Find original path, minus the rigid
            # E.g. |root_grp|upperArm_ctrl|rRigid4 -> |root_grp|upperArm_ctrl
            path = name.path.rsplit("|", 1)[0]

            try:
                transform = cmdx.encode(path)
            except cmdx.ExistError:
                log.warning("%s was not found in this scene" % path)
                continue

            transforms[entity] = transform

    def _scenes():
        # Generate scenes first
        for entity, data in dump["entities"].items():
            entity = int(entity)
            comps = data["components"]

            if "SolverComponent" not in comps:
                continue

            Solver = Component(comps["SolverComponent"])

            scene = commands.create_scene()
            scene["airDensity"] = Solver["airDensity"]
            scene["gravity"] = Solver["gravity"]

            scenes[entity] = scene

    def _rigids():
        for entity, data in dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "RigidComponent" not in comps:
                continue

            name = Component(comps["NameComponent"])

            if not name.path:
                # Bad export
                continue

            # These are guaranteed to be associated to any entity
            # with a `RigidComponent`
            Rest = Component(comps["RestComponent"])
            Desc = Component(comps["GeometryDescriptionComponent"])
            Rigid = Component(comps["RigidComponent"])
            Scene = Component(comps["SceneComponent"])
            Color = Component(comps["ColorComponent"])

            # Scenes have a rigid component too, but we've already created it
            if entity == Scene["entity"]:
                continue

            assert Scene["entity"] in scenes, (
                "The rigid '%s' belongs to a scene '%s' which was not "
                "found in this dump." % (name["path"], Scene["entity"])
            )

            try:
                transform = transforms[entity]
            except KeyError:
                continue

            scene = scenes[Scene["entity"]]
            rigid = commands.create_rigid(transform, scene)

            rigid["cachedRestMatrix"] = Rest["matrix"]
            rigid["mass"] = Rigid["mass"]
            rigid["friction"] = Rigid["friction"]
            rigid["shapeExtents"] = Desc["extents"]
            rigid["shapeLength"] = Desc["length"]
            rigid["shapeRadius"] = Desc["radius"]
            rigid["shapeOffset"] = Desc["offset"]
            rigid["shapeRotation"] = Desc["rotation"]
            rigid["color"] = Color["value"]

            # Establish shape
            if Desc["type"] in ("Cylinder", "Capsule"):
                rigid["shapeType"] = commands.CapsuleShape

            elif Desc["type"] == "Box":
                rigid["shapeType"] = commands.BoxShape

            elif Desc["type"] == "Sphere":
                rigid["shapeType"] = commands.SphereShape

            elif Desc["type"] == "ConvexHull":
                log.warning(
                    "%s.shapeType = convexHull not yet supported. :("
                    % name.path
                )

                rigid["shapeType"] = commands.BoxShape

            else:
                log.warning(
                    "Unsupported shape type: %s.type=%s"
                    % (name.path, Desc["type"])
                )
                continue

            rigids[entity] = rigid

    def _constraints():
        for entity, data in dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "JointComponent" not in comps:
                continue

            name = Component(comps["NameComponent"])

            if not name.path:
                # Bad export
                continue

            # These are guaranteed to be associated to any entity
            # with a `JointComponent`
            Joint = Component(comps["JointComponent"])
            Drive = Component(comps["DriveComponent"])
            Limit = Component(comps["LimitComponent"])
            LimitUi = Component(comps["LimitUIComponent"])
            DriveUi = Component(comps["DriveUIComponent"])

            parent_entity = Joint["parent"]
            child_entity = Joint["child"]

            assert parent_entity in rigids or parent_entity in scenes, (
                "%s.parentRigid=%r was not found in this dump"
                % (name.path, parent_entity)
            )

            assert child_entity in rigids, (
                "%s.childRigid=%r was not found in this dump"
                % (name.path, child_entity)
            )

            try:
                parent_rigid = rigids[parent_entity]
            except KeyError:
                parent_rigid = scenes[parent_entity]

            child_rigid = rigids[child_entity]

            con = commands.create_constraint(parent_rigid, child_rigid)

            con["parentFrame"] = Joint["parentFrame"]
            con["childFrame"] = Joint["childFrame"]
            con["disableCollision"] = Joint["disableCollision"]

            con["limitEnabled"] = Limit["enabled"]
            con["linearLimitX"] = Limit["x"]
            con["linearLimitY"] = Limit["y"]
            con["linearLimitZ"] = Limit["z"]
            con["angularLimitX"] = Limit["twist"]
            con["angularLimitY"] = Limit["swing1"]
            con["angularLimitZ"] = Limit["swing2"]
            con["limitStrength"] = LimitUi["strength"]
            con["linearLimitStiffness"] = LimitUi["linearStiffness"]
            con["linearLimitDamping"] = LimitUi["linearDamping"]
            con["angularLimitStiffness"] = LimitUi["angularStiffness"]
            con["angularLimitDamping"] = LimitUi["angularDamping"]

            con["driveEnabled"] = Drive["enabled"]
            con["driveStrength"] = DriveUi["strength"]
            con["linearDriveStiffness"] = DriveUi["linearStiffness"]
            con["linearDriveDamping"] = DriveUi["linearDamping"]
            con["angularDriveStiffness"] = DriveUi["angularStiffness"]
            con["angularDriveDamping"] = DriveUi["angularDamping"]
            con["driveMatrix"] = Drive["target"]

            # Restore it's name too
            with cmdx.DagModifier() as mod:
                mod.rename(con, name["value"])

            constraints[entity] = con

    _match_transforms()
    _scenes()
    _rigids()
    _constraints()

    return {
        "scenes": scenes,
        "rigids": rigids,
        "constraints": constraints
    }
