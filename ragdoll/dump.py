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


def Component(comp):
    """Simplified access to component members"""

    data = {}

    for key, value in comp["members"].items():
        if not isinstance(value, dict):
            pass

        elif value["type"] == "Vector3":
            value = cmdx.Vector(value["values"])

        elif value["type"] == "Color4":
            value = cmdx.Color(value["values"])

        elif value["type"] == "Matrix44":
            value = cmdx.Matrix4(value["values"])

        elif value["type"] == "Quaternion":
            value = cmdx.Quaternion(*value["values"])

        else:
            raise TypeError("Unsupported type: %s" % value)

        data[key] = value

    return data


def dedump(dump):
    """Recreate Maya scene from `dump`"""

    with cmdx.DagModifier() as mod:
        root = mod.createNode("transform", name="dump")

    for entity, data in dump["entities"].items():
        comps = data["components"]

        if "RigidComponent" not in comps:
            continue

        Name = Component(comps["NameComponent"])

        if not Name["path"]:
            # Bad export
            continue

        Scale = Component(comps["ScaleComponent"])
        Rest = Component(comps["RestComponent"])
        Desc = Component(comps["GeometryDescriptionComponent"])

        # Establish rigid transformation
        tm = cmdx.TransformationMatrix(Rest["matrix"])

        # Establish shape
        if Desc["type"] in ("Cylinder", "Capsule"):
            radius = Desc["radius"] * Scale["absolute"].x
            length = Desc["length"] * Scale["absolute"].y
            geo, _ = cmds.polyCylinder(axis=(1, 0, 0),
                                       radius=radius,
                                       height=length,
                                       roundCap=True,
                                       subdivisionsCaps=5)

        elif Desc["type"] == "Box":
            extents = Desc["extents"]
            extents.x *= Scale["absolute"].x
            extents.y *= Scale["absolute"].y
            extents.z *= Scale["absolute"].z
            geo, _ = cmds.polyCube(width=extents.x,
                                   height=extents.y,
                                   depth=extents.z)

        elif Desc["type"] == "Sphere":
            radius = Desc["radius"] * Scale["absolute"].x
            geo, _ = cmds.polySphere(radius=radius)

        else:
            print(
                "Unsupported shape type: %s.type=%s"
                % (Name["path"], Desc["type"])
            )
            continue

        with cmdx.DagModifier() as mod:
            name = Name["path"].rsplit("|", 3)[-2]
            transform = mod.createNode("transform", name=name, parent=root)
            transform["translate"] = tm.translation()
            transform["rotate"] = tm.rotation()

        # Establish shape transformation
        offset = Desc["offset"]
        offset.x *= Scale["absolute"].x
        offset.y *= Scale["absolute"].y
        offset.z *= Scale["absolute"].z

        geo = cmdx.encode(geo)
        geo["translate"] = offset
        geo["rotate"] = Desc["rotation"]

        transform.addChild(geo)


def _name(Name, level=-1):
    return Name["path"].rsplit("|", 1)[level]


class Loader(object):
    """Reconstruct physics from a Ragdoll dump"""

    def __init__(self, dump):
        if isinstance(dump, string_types):
            dump = json.loads(dump)

        assert isinstance(dump, dict), "dump argument must be dict"
        assert "schema" in dump and dump["schema"] == "ragdoll-1.0", (
            "Dump not compatible with this version of Ragdoll"
        )

        self._dump = dump

    def load(self):
        """Apply JSON to existing nodes in the scene"""

        transforms = self._match_transforms()

        rigid_multipliers = self._load_rigid_multipliers(transforms)
        constraint_multipliers = self._load_constraint_multipliers(transforms)

        scenes = self._load_scenes()
        rigids = self._load_rigids(scenes, transforms, rigid_multipliers)
        constraints = self._load_constraints(
            scenes, rigids, constraint_multipliers)

        return {
            "scenes": scenes,
            "rigids": rigids,
            "constraints": constraints,
            "constraint_multipliers": constraint_multipliers,
            "rigid_multipliers": rigid_multipliers,
        }

    def _match_transforms(self):
        """Find and associate each entity with a Maya transform"""
        transforms = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            # There won't be any solvers in here just yet
            if "SolverComponent" in comps:
                continue

            Name = Component(comps["NameComponent"])

            # Find original path, minus the rigid
            # E.g. |root_grp|upperArm_ctrl|rRigid4 -> |root_grp|upperArm_ctrl
            path = Name["path"].rsplit("|", 1)[0]

            try:
                transform = cmdx.encode(path)

            except cmdx.ExistError:
                standalones = (
                    "RigidMultiplierUIComponent",
                    "ConstraintMultiplierUIComponent",
                )

                if any(c in comps for c in standalones):
                    # This is an entity that can carry its own transform
                    pass

                else:
                    log.warning("%s was not found in this scene" % path)

                continue

            transforms[entity] = transform

        return transforms

    def _load_scenes(self):
        # Generate scenes first
        scenes = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)
            comps = data["components"]

            if "SolverComponent" not in comps:
                continue

            Solver = Component(comps["SolverComponent"])

            scene = commands.create_scene()
            scene["airDensity"] = Solver["airDensity"]
            scene["gravity"] = Solver["gravity"]

            scenes[entity] = scene

        return scenes

    def _load_rigid_multipliers(self, transforms):
        rigid_multipliers = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "RigidMultiplierUIComponent" not in comps:
                continue

            Name = Component(comps["NameComponent"])
            Mult = Component(comps["RigidMultiplierUIComponent"])

            with cmdx.DagModifier() as mod:
                transform_name = _name(Name, -2)
                shape_name = transform_name

                try:
                    transform = transforms[entity]
                except KeyError:
                    # These may have their own transform
                    transform = mod.create_node("transform", transform_name)
                    shape_name = commands._shape_name(transform_name)

                node = mod.create_node("rdRigidMultiplier",
                                       name=shape_name,
                                       parent=transform)
                mod.set_attr(node["airDensity"], Mult["airDensity"])
                mod.set_attr(node["linearDamping"], Mult["linearDamping"])
                mod.set_attr(node["angularDamping"], Mult["angularDamping"])

            rigid_multipliers[entity] = node

        return rigid_multipliers

    def _load_rigids(self, scenes, transforms, multipliers):
        rigids = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "RigidComponent" not in comps:
                continue

            # The scene has a rigid too
            if "SolverComponent" in comps:
                continue

            # These are guaranteed to be associated to any entity
            # with a `RigidComponent`
            Name = Component(comps["NameComponent"])
            Rest = Component(comps["RestComponent"])
            Desc = Component(comps["GeometryDescriptionComponent"])
            Rigid = Component(comps["RigidComponent"])
            RigidUi = Component(comps["RigidUIComponent"])
            Scene = Component(comps["SceneComponent"])
            Color = Component(comps["ColorComponent"])

            # Scenes have a rigid component too, but we've already created it
            if entity == Scene["entity"]:
                continue

            assert Scene["entity"] in scenes, (
                "The rigid '%s' belongs to a scene '%s' which was not "
                "found in this dump." % (Name["path"], Scene["entity"])
            )

            try:
                transform = transforms[entity]
            except KeyError:
                log.warning(
                    "Could not find transform for %s" % Name["path"]
                )
                continue

            scene = scenes[Scene["entity"]]
            rigid = commands.create_rigid(transform, scene)

            with cmdx.DagModifier() as mod:
                mod.set_attr(rigid["cachedRestMatrix"], Rest["matrix"])
                mod.set_attr(rigid["mass"], Rigid["mass"])
                mod.set_attr(rigid["friction"], Rigid["friction"])
                mod.set_attr(rigid["collide"], Rigid["collide"])
                mod.set_attr(rigid["kinematic"], Rigid["kinematic"])
                mod.set_attr(rigid["linearDamping"], Rigid["linearDamping"])
                mod.set_attr(rigid["angularDamping"], Rigid["angularDamping"])
                mod.set_attr(rigid["positionIterations"],
                             Rigid["positionIterations"])
                mod.set_attr(rigid["velocityIterations"],
                             Rigid["velocityIterations"])
                mod.set_attr(rigid["maxContactImpulse"],
                             Rigid["maxContactImpulse"])
                mod.set_attr(rigid["maxDepenetrationVelocity"],
                             Rigid["maxDepenetrationVelocity"])
                mod.set_attr(rigid["enableCCD"], Rigid["enableCCD"])
                mod.set_attr(rigid["angularMass"], Rigid["angularMass"])
                mod.set_attr(rigid["centerOfMass"], Rigid["centerOfMass"])

                mod.set_attr(rigid["shapeExtents"], Desc["extents"])
                mod.set_attr(rigid["shapeLength"], Desc["length"])
                mod.set_attr(rigid["shapeRadius"], Desc["radius"])
                mod.set_attr(rigid["shapeOffset"], Desc["offset"])

                # These are exported as Quaternion
                rotation = Desc["rotation"].asEulerRotation()
                mod.set_attr(rigid["shapeRotation"], rotation)

                mod.set_attr(rigid["color"], Color["value"])
                mod.set_attr(rigid["drawShaded"], RigidUi["shaded"])

                # Establish shape
                if Desc["type"] in ("Cylinder", "Capsule"):
                    mod.set_attr(rigid["shapeType"], commands.CapsuleShape)

                elif Desc["type"] == "Box":
                    mod.set_attr(rigid["shapeType"], commands.BoxShape)

                elif Desc["type"] == "Sphere":
                    mod.set_attr(rigid["shapeType"], commands.SphereShape)

                elif Desc["type"] == "ConvexHull":
                    log.warning(
                        "%s.shapeType = convexHull not yet supported. :("
                        % Name["path"]
                    )

                    rigid["shapeType"] = commands.BoxShape

                else:
                    log.warning(
                        "Unsupported shape type: %s.type=%s"
                        % (Name["path"], Desc["type"])
                    )

                # Restore it's name too
                mod.rename(rigid, _name(Name))

                if RigidUi["multiplierEntity"] in multipliers:
                    multiplier = multipliers[RigidUi["multiplierEntity"]]
                    mod.connect(multiplier["ragdollId"],
                                rigid["multiplierNode"])

            rigids[entity] = rigid

        return rigids

    def _load_constraint_multipliers(self, transforms):
        rigid_multipliers = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "ConstraintMultiplierUIComponent" not in comps:
                continue

            Name = Component(comps["NameComponent"])
            Mult = Component(comps["ConstraintMultiplierUIComponent"])

            with cmdx.DagModifier() as mod:
                try:
                    transform = transforms[entity]
                except KeyError:
                    # These may have their own transform
                    transform = mod.create_node("transform", _name(Name))

                node = mod.create_node("rdConstraintMultiplier",
                                       name=_name(Name),
                                       parent=transform)

                mod.set_attr(node["limitStrength"],
                             Mult["limitStrength"])
                mod.set_attr(node["linearLimitStiffness"],
                             Mult["linearLimitStiffness"])
                mod.set_attr(node["linearLimitDamping"],
                             Mult["linearLimitDamping"])
                mod.set_attr(node["angularLimitStiffness"],
                             Mult["angularLimitStiffness"])
                mod.set_attr(node["angularLimitDamping"],
                             Mult["angularLimitDamping"])
                mod.set_attr(node["driveStrength"],
                             Mult["driveStrength"])
                mod.set_attr(node["linearDriveStiffness"],
                             Mult["linearDriveStiffness"])
                mod.set_attr(node["linearDriveDamping"],
                             Mult["linearDriveDamping"])
                mod.set_attr(node["angularDriveStiffness"],
                             Mult["angularDriveStiffness"])
                mod.set_attr(node["angularDriveDamping"],
                             Mult["angularDriveDamping"])

                rigid_multipliers[entity] = node

        return rigid_multipliers

    def _load_constraints(self, scenes, rigids, multipliers):
        constraints = {}

        for entity, data in self._dump["entities"].items():
            entity = int(entity)

            comps = data["components"]

            if "JointComponent" not in comps:
                continue

            # These are guaranteed to be associated to any entity
            # with a `JointComponent`
            Name = Component(comps["NameComponent"])
            Joint = Component(comps["JointComponent"])
            Drive = Component(comps["DriveComponent"])
            Limit = Component(comps["LimitComponent"])
            LimitUi = Component(comps["LimitUIComponent"])
            DriveUi = Component(comps["DriveUIComponent"])
            ConstraintUi = Component(comps["ConstraintUIComponent"])

            parent_entity = Joint["parent"]
            child_entity = Joint["child"]

            assert parent_entity in rigids or parent_entity in scenes, (
                "%s.parentRigid=%r was not found in this dump"
                % (Name["path"], parent_entity)
            )

            assert child_entity in rigids, (
                "%s.childRigid=%r was not found in this dump"
                % (Name["path"], child_entity)
            )

            try:
                parent_rigid = rigids[parent_entity]
            except KeyError:
                parent_rigid = scenes[parent_entity]

            child_rigid = rigids[child_entity]

            con = commands.create_constraint(parent_rigid, child_rigid)

            with cmdx.DagModifier() as mod:
                mod.set_attr(con["parentFrame"], Joint["parentFrame"])
                mod.set_attr(con["childFrame"], Joint["childFrame"])
                mod.set_attr(con["disableCollision"],
                             Joint["disableCollision"])

                mod.set_attr(con["limitEnabled"], Limit["enabled"])
                mod.set_attr(con["linearLimitX"], Limit["x"])
                mod.set_attr(con["linearLimitY"], Limit["y"])
                mod.set_attr(con["linearLimitZ"], Limit["z"])
                mod.set_attr(con["angularLimitX"], Limit["twist"])
                mod.set_attr(con["angularLimitY"], Limit["swing1"])
                mod.set_attr(con["angularLimitZ"], Limit["swing2"])
                mod.set_attr(con["limitStrength"], LimitUi["strength"])
                mod.set_attr(con["linearLimitStiffness"],
                             LimitUi["linearStiffness"])
                mod.set_attr(con["linearLimitDamping"],
                             LimitUi["linearDamping"])
                mod.set_attr(con["angularLimitStiffness"],
                             LimitUi["angularStiffness"])
                mod.set_attr(con["angularLimitDamping"],
                             LimitUi["angularDamping"])

                mod.set_attr(con["driveEnabled"], Drive["enabled"])
                mod.set_attr(con["driveStrength"], DriveUi["strength"])
                mod.set_attr(con["linearDriveStiffness"],
                             DriveUi["linearStiffness"])
                mod.set_attr(con["linearDriveDamping"],
                             DriveUi["linearDamping"])
                mod.set_attr(con["angularDriveStiffness"],
                             DriveUi["angularStiffness"])
                mod.set_attr(con["angularDriveDamping"],
                             DriveUi["angularDamping"])
                mod.set_attr(con["driveMatrix"], Drive["target"])

                # Restore it's name too
                mod.rename(con, _name(Name))

                if ConstraintUi["multiplierEntity"] in multipliers:
                    multiplier = multipliers[ConstraintUi["multiplierEntity"]]
                    mod.connect(multiplier["ragdollId"],
                                con["multiplierNode"])

            constraints[entity] = con

        return constraints


def load(dump):
    loader = Loader(dump)
    return loader.load()
