"""Recreate Maya scene from Ragdoll dump

# Usage Example
import json
dump = cmds.ragdollDump()
dump = json.loads(dump)
dedump(dump)

"""

import json
import copy
import logging

from collections import OrderedDict as odict

from maya import cmds
from .vendor import cmdx
from . import (
    commands,
    tools,
    constants,
    internal
)

from .tools import markers_tool as markers_

log = logging.getLogger("ragdoll")


class Entity(int):
    pass


def Component(comp):
    """Simplified access to component members"""

    data = {}

    for key, value in comp["members"].items():
        if not isinstance(value, dict):
            pass

        elif value["type"] == "Entity":
            value = Entity(value["value"])

        elif value["type"] == "Vector3":
            value = cmdx.Vector(value["values"])

        elif value["type"] == "Color4":
            value = cmdx.Color(value["values"])

        elif value["type"] == "Matrix44":
            value = cmdx.Matrix4(value["values"])

        elif value["type"] == "Path":
            value = value["value"]

        elif value["type"] == "Quaternion":
            value = cmdx.Quaternion(*value["values"])

        else:
            raise TypeError("Unsupported type: %s" % value)

        data[key] = value

    return data


class Registry(object):
    def __init__(self, dump):
        dump = copy.deepcopy(dump)
        dump["entities"] = {

            # Original JSON stores keys as strings, but the original
            # keys are integers; i.e. entity IDs
            Entity(entity): value
            for entity, value in dump["entities"].items()
        }

        self._dump = dump

    def view(self, *components):
        """Iterate over every entity that has all of `components`"""
        for entity in self._dump["entities"]:
            if all(self.has(entity, comp) for comp in components):
                yield entity

    def has(self, entity, component):
        """Return whether `entity` has `component`"""
        assert isinstance(entity, int), "entity must be int"
        assert isinstance(component, cmdx.string_types), (
            "component must be string")
        return component in self._dump["entities"][entity]["components"]

    def get(self, entity, component):
        """Return `component` for `entity`

        Returns:
            dict: The component

        Raises:
            KeyError: if `entity` does not have `component`

        Example:
            >>> s = {}
            >>> dump = cmds.ragdollDump()
            >>> dump["entities"][1] = {"components": {"SceneComponent": s}}
            >>> loader = Loader(dump)
            >>> assert s == loader.component(1, "SceneComponent")

        """

        try:
            return Component(
                self._dump["entities"][entity]["components"][component]
            )

        except KeyError:
            Name = self._dump["entities"][entity]
            Name = Name["components"]["NameComponent"]
            Name = Component(Name)
            raise KeyError("%s did not have %s" % (Name["path"], component))

    def components(self, entity):
        """Return *all* components for `entity`"""
        return self._dump["entities"][entity]["components"]


def _name(Name, level=-1):
    return Name["path"].rsplit("|", 1)[level]


def DefaultDump():
    return {
        "schema": Loader.SupportedSchema,
        "entities": {},
        "info": {}
    }


def DefaultState():
    return {

        # Series of solver entities
        "solvers": [],

        # Series of group entities
        "groups": [],

        # Series of markers entities
        "markers": [],

        # Transforms that are already assigned
        "occupied": [],

        # Map entity -> active Maya transform node
        "entityToTransform": {},
    }


def _smart_try_setattr(mod, plug, value):
    try:
        # In the simplest case, the plug is free
        mod.set_attr(plug, value)

    except cmdx.LockedError:

        try:
            # In other cases, it might be connected to a user attributes
            mod.smart_set_attr(plug, value)

        except cmdx.LockedError:
            # Connected plug may also be locked or uneditable
            return False

    except Exception:
        # Worst case, there's nothing we can do
        return False

    return True


class Loader(object):
    """Reconstruct physics from a Ragdoll dump

    A "dump" is the internal data of the Ragdoll plug-in.

    This loader reconstructs a Maya scene such that the results
    are the same as when the dump was originally created.

    Arguments:
        roots (list): Path(s) that the original path must match
        replace (list): Search/replace pairs of strings to find and replace
            in each original path

    """

    SupportedSchema = "ragdoll-1.1"

    def __init__(self, opts=None):
        opts = opts or {}
        opts = dict(opts, **{
            "roots": [],
            "replace": [],
            "namespace": None,
            "preserveControls": False,
            "preserveAttributes": True,
        })

        self._opts = opts

        # Do we need to re-analyse before use?
        self._dirty = True

        # Is the data valid, e.g. no null-entities?
        self._invalid_reasons = []

        # Transient data, updated on changes to fname and filtering
        self._state = DefaultState()

        self._registry = None

    @property
    def registry(self):
        return self._registry

    def read(self, fname):
        self._invalid_reasons[:] = []

        dump = DefaultDump()

        if isinstance(fname, dict):
            # Developer-mode, bypass everything and use as-is
            dump = fname

        else:
            try:
                with open(fname) as f:
                    dump = json.load(f)

            except Exception as e:
                error = (
                    "An exception was thrown when attempting to read %s\n%s"
                    % (fname, str(e))
                )

                self._invalid_reasons += [error]

        assert "schema" in dump and dump["schema"] == self.SupportedSchema, (
            "Dump not compatible with this version of Ragdoll"
        )

        self._registry = Registry(dump)
        self._dirty = True

    def set_roots(self, roots):
        self._opts["roots"][:] = roots
        self._dirty = True

    def set_replace(self, replace):
        assert isinstance(replace, (tuple, list))
        assert all(isinstance(i, tuple) for i in replace)
        self._opts["replace"][:] = replace
        self._dirty = True

    def set_namespace(self, namespace=None):
        # Support passing namespace with or without suffix ":"
        if namespace is not None:
            namespace = namespace.rstrip(":") + ":"

        self._opts["namespace"] = namespace
        self._dirty = True

    def set_preserve_attributes(self, preserve):
        self._opts["preserveAttributes"] = preserve
        self._dirty = True

    def set_preserve_control(self, preserve):
        self._opts["preserveControls"] = preserve
        self._dirty = True

    def is_valid(self):
        return len(self._invalid_reasons) == 0

    def invalid_reasons(self):
        """Return reasons for failure, useful for reporting"""
        return self._invalid_reasons[:]

    def analyse(self):
        """Fill internal state from dump with something we can use"""

        # No need for needless work
        if not self._dirty:
            return self._state

        self._find_solvers()
        self._find_groups()
        self._find_markers()

        self.validate()

        self._dirty = False
        return self._state

    def validate(self):
        reasons = []
        self._invalid_reasons[:] = reasons

    def report(self):
        if self._dirty:
            self.analyse()

        def _name(entity):
            Name = self._registry.get(entity, "NameComponent")
            return Name["value"]

        solvers = self._state["solvers"]
        groups = self._state["groups"]
        transforms = self._state["entityToTransform"]

        if transforms:
            log.info("Solvers:")
            for entity, transform in transforms.items():
                log.info("  %s -> %s.." % (_name(entity), transform))

            log.info("Markers:")
            for entity, transform in transforms.items():
                log.info("  %s -> %s.." % (_name(entity), transform))

            log.info("Markers:")
            for entity, transform in transforms.items():
                log.info("  %s -> %s.." % (_name(entity), transform))

        if not any([transforms]):
            log.debug("Dump was empty")

    @internal.with_undo_chunk
    def reinterpret(self, dry_run=False):
        """Interpret dump back into the UI-commands used to create them.

        For example, if two chains were created using the `Active Chain`
        command, then this function will attempt to figure this out and
        call `Active Chain` on the original controls.

        Unlike `load` this method reproduces what the artist did in order
        to author the rigids and constraints. The advantage is closer
        resemblance to newly authored chains and rigids, at the cost of
        less accurately capturing custom constraints and connections.

        Caveat:
            Imports are made using the current version of Ragdoll and its
            tools. Meaning that if a tool - e.g. create_chain - has been
            updated since the export was made, then the newly imported
            physics will be up-to-date but not necessarily the same as
            when it got exported.

        """

        # In case the user forgot or didn't know
        if self._dirty:
            self.analyse()

        if dry_run:
            return self.report()

        if not self.is_valid():
            return log.error("Dump not valid")

        rdsolvers = self._create_solvers()
        rdgroups = self._create_groups(rdsolvers)
        rdmarkers = self._create_markers(rdgroups, rdsolvers)

        self._dirty = True
        log.info("Done")

        return {
            "solvers": rdsolvers.values(),
            "groups": rdgroups.values(),
            "markers": rdmarkers.values(),
        }

    def _create_solvers(self):
        log.info("Creating solver(s)..")

        unoccupied_markers = list(self._state["markers"])
        for marker in self._state["occupied"]:
            unoccupied_markers.remove(marker)

        for marker in unoccupied_markers:
            if marker not in self._state["entityToTransform"]:
                unoccupied_markers.remove(marker)

        rdsolvers = {}

        for entity in self._state["solvers"]:

            # Ensure there is at least 1 marker in it
            is_empty = True
            for marker in unoccupied_markers:
                Scene = self._registry.get(marker, "SceneComponent")
                if Scene["entity"] == entity:
                    is_empty = False
                    break

            if is_empty:
                continue

            Name = self._registry.get(entity, "NameComponent")
            transform_name = Name["path"].rsplit("|", 1)[-1]
            rdsolver = markers_.create_solver(transform_name)
            rdsolvers[entity] = rdsolver

        if self._opts["preserveAttributes"]:
            with cmdx.DagModifier() as mod:
                for entity, rdsolver in rdsolvers.items():
                    self._apply_solver(mod, entity, rdsolver)

        return rdsolvers

    def _create_groups(self, rdsolvers):
        log.info("Creating group(s)..")

        unoccupied_markers = list(self._state["markers"])
        for marker in self._state["occupied"]:
            unoccupied_markers.remove(marker)

        for marker in unoccupied_markers:
            if marker not in self._state["entityToTransform"]:
                unoccupied_markers.remove(marker)

        rdgroups = {}

        for entity in self._state["groups"]:
            Scene = self._registry.get(entity, "SceneComponent")
            rdsolver = rdsolvers.get(Scene["entity"])

            if not rdsolver:
                # Exported group wasn't part of an exported solver
                # This would be exceedingly rare.
                continue

            # Ensure there is at least 1 marker in it
            is_empty = True
            for marker in unoccupied_markers:
                Group = self._registry.get(marker, "GroupComponent")
                if Group["entity"] == entity:
                    is_empty = False
                    break

            if is_empty:
                continue

            Name = self._registry.get(entity, "NameComponent")

            # E.g. |someCtl_rGroup
            transform_name = Name["path"].rsplit("|", 1)[-1]
            rdgroup = markers_.create_group(transform_name, rdsolver)
            rdgroups[entity] = rdgroup

        if self._opts["preserveAttributes"]:
            with cmdx.DagModifier() as mod:
                for entity, rdgroup in rdgroups.items():
                    self._apply_group(mod, entity, rdgroup)

        return rdgroups

    def _create_markers(self, rdgroups, rdsolvers):
        log.info("Creating marker(s)..")
        rdmarkers = {}

        unoccupied_markers = list(self._state["markers"])

        for marker in self._state["occupied"]:
            unoccupied_markers.remove(marker)

        for entity in unoccupied_markers:
            transform = self._state["entityToTransform"].get(entity)

            if not transform:
                continue

            Scene = self._registry.get(entity, "SceneComponent")
            rdsolver = rdsolvers.get(Scene["entity"])

            if not rdsolver:
                # Exported marker wasn't part of an exported solver
                continue

            rdmarker = markers_.assign([transform], rdsolver)
            rdmarkers[entity] = rdmarker[0]

        if self._opts["preserveAttributes"]:
            with cmdx.DagModifier() as mod:
                for entity, rdmarker in rdmarkers.items():
                    self._apply_marker(mod, entity, rdmarker)

        with cmdx.DagModifier() as mod:
            log.info("Adding to group(s)..")
            for entity, rdmarker in rdmarkers.items():
                Group = self._registry.get(entity, "GroupComponent")
                rdgroup = rdgroups.get(Group["entity"])

                if rdgroup is not None:
                    markers_.add_to_group(mod, rdmarker, rdgroup)
                    mod.do_it()  # Commit to group

            log.info("Reconstructing hierarchy..")
            for entity, rdmarker in rdmarkers.items():
                Subs = self._registry.get(entity, "SubEntitiesComponent")
                JointComponent = self._registry.get(Subs["relative"], "JointComponent")
                parent_entity = JointComponent["parent"]

                if parent_entity:
                    parent_rdmarker = rdmarkers[parent_entity]
                    mod.connect(parent_rdmarker["ragdollId"], rdmarker["parentMarker"])

        return rdmarkers

    def _find_solvers(self):
        solvers = self._state["solvers"]
        solvers[:] = []

        for entity in self._registry.view("SolverComponent"):
            solvers.append(entity)

    def _find_groups(self):
        groups = self._state["groups"]
        groups[:] = []

        for entity in self._registry.view("GroupUIComponent"):
            groups.append(entity)

    def _find_markers(self):
        """Find and associate each entity with a Maya transform"""
        entity_to_transform = self._state["entityToTransform"]
        markers = self._state["markers"]
        occupied = self._state["occupied"]

        entity_to_transform.clear()
        markers[:] = []
        occupied[:] = []

        for entity in self._registry.view("MarkerUIComponent"):
            MarkerUI = self._registry.get(entity, "MarkerUIComponent")

            # Find original path, minus the rigid
            # E.g. |rMarker_upperArm_ctl -> |root_grp|upperArm_ctrl
            path = MarkerUI["sourceTransform"]

            for search, replace in self._opts["replace"]:
                path = path.replace(search, replace)

            if self._opts["namespace"]:
                # Find all namespaces for the original node
                # E.g. |myNamespace:root_grp|myNamespace:controls_grp
                namespaces = path.split("|")
                namespaces = [
                    node.rsplit(":", 1)[0]
                    for node in namespaces
                    if ":" in node
                ]
                namespaces = filter(None, namespaces)  # Remove `None`
                namespaces = tuple(set(namespaces))  # Remove duplicates

                # Let them know
                if len(namespaces) > 1:
                    log.debug(
                        "%s had multiple namespaces, using first: %s"
                        % (path, ", ".join(namespaces))
                    )

                if len(namespaces) > 0:
                    namespace = namespaces[0]
                    namespace = namespace.rstrip(":") + ":"
                    path = path.replace(namespace, self._opts["namespace"])

            # Exclude anything not starting with any of these
            roots = self._opts["roots"]
            if roots and not any(path.startswith(root) for root in roots):
                continue

            markers.append(entity)

            try:
                transform = cmdx.encode(path)

            except cmdx.ExistError:
                # Transform wasn't found in this scene, that's OK.
                # It just means it can't actually be loaded onto anything.
                continue

            entity_to_transform[entity] = transform

            # Avoid assigning to already assigned transforms
            if transform["message"].output(type="rdMarker"):
                occupied.append(entity)

        # Re-establish creation order
        def sort(entity):
            order = self._registry.get(entity, "OrderComponent")
            return order["value"]

        markers[:] = sorted(markers, key=sort)

    def _apply_solver(self, mod, entity, solver):
        Solver = self._registry.get(entity, "SolverComponent")
        SolverUi = self._registry.get(entity, "SolverUIComponent")

        cache_method = {
            "Off": 0,
            "Static": 1,
            "Dynamic": 2,
        }.get(Solver["cacheMethod"], 0)

        frameskip_method = {
            "Pause": 0,
            "Ignore": 1,
        }.get(Solver["frameskipMethod"], 0)

        solver_type = {
            "PGS": 0,
            "TGS": 1,
        }.get(Solver["type"], 1)

        collision_type = {
            "SAT": 0,
            "PCM": 1,
        }.get(Solver["collisionDetectionType"], 1)

        mod.smart_set_attr(solver["solverType"], solver_type)
        mod.smart_set_attr(solver["cache"], cache_method)
        mod.smart_set_attr(solver["frameskipMethod"], frameskip_method)
        mod.smart_set_attr(solver["collisionDetectionType"], collision_type)
        mod.smart_set_attr(solver["enabled"], Solver["enabled"])
        mod.smart_set_attr(solver["airDensity"], Solver["airDensity"])
        mod.smart_set_attr(solver["gravity"], Solver["gravity"])
        mod.smart_set_attr(solver["substeps"], Solver["substeps"])
        mod.smart_set_attr(solver["timeMultiplier"], Solver["timeMultiplier"])
        mod.smart_set_attr(solver["spaceMultiplier"], Solver["spaceMultiplier"])
        mod.smart_set_attr(solver["positionIterations"], Solver["positionIterations"])
        mod.smart_set_attr(solver["velocityIterations"], Solver["velocityIterations"])

        mod.smart_set_attr(solver["linearLimitStiffness"], SolverUi["linearLimitStiffness"])
        mod.smart_set_attr(solver["linearLimitDamping"], SolverUi["linearLimitDamping"])
        mod.smart_set_attr(solver["angularLimitStiffness"], SolverUi["angularLimitStiffness"])
        mod.smart_set_attr(solver["angularLimitDamping"], SolverUi["angularLimitDamping"])
        mod.smart_set_attr(solver["linearConstraintStiffness"], SolverUi["linearConstraintStiffness"])
        mod.smart_set_attr(solver["linearConstraintDamping"], SolverUi["linearConstraintDamping"])
        mod.smart_set_attr(solver["angularConstraintStiffness"], SolverUi["angularConstraintStiffness"])
        mod.smart_set_attr(solver["angularConstraintDamping"], SolverUi["angularConstraintDamping"])
        mod.smart_set_attr(solver["linearDriveStiffness"], SolverUi["linearDriveStiffness"])
        mod.smart_set_attr(solver["linearDriveDamping"], SolverUi["linearDriveDamping"])
        mod.smart_set_attr(solver["angularDriveStiffness"], SolverUi["angularDriveStiffness"])
        mod.smart_set_attr(solver["angularDriveDamping"], SolverUi["angularDriveDamping"])

    def _apply_group(self, mod, entity, group):
        GroupUi = self._registry.get(entity, "GroupUIComponent")

        input_type = {
            "Inherit": 0,
            "Off": 1,
            "Kinematic": 2,
            "Drive": 3
        }.get(GroupUi["inputType"], 3)

        drive_space = {
            "Relative": 1,
            "Absolute": 2,
            "Custom": 3
        }.get(GroupUi["driveSpace"], 1)

        mod.smart_set_attr(group["inputType"], input_type)
        mod.smart_set_attr(group["driveSpace"], drive_space)
        mod.smart_set_attr(group["enabled"], GroupUi["enabled"])
        mod.smart_set_attr(group["selfCollide"], GroupUi["selfCollide"])
        mod.smart_set_attr(group["driveStiffness"], GroupUi["stiffness"])
        mod.smart_set_attr(group["driveDampingRatio"], GroupUi["dampingRatio"])
        mod.smart_set_attr(group["driveSpaceCustom"], GroupUi["driveSpaceCustom"])

    def _apply_marker(self, mod, entity, marker):
        Desc = self._registry.get(entity, "GeometryDescriptionComponent")
        Color = self._registry.get(entity, "ColorComponent")
        Rigid = self._registry.get(entity, "RigidComponent")
        MarkerUi = self._registry.get(entity, "MarkerUIComponent")

        input_type = {
            "Inherit": 0,
            "Off": 1,
            "Kinematic": 2,
            "Drive": 3
        }.get(MarkerUi["inputType"], 0)

        drive_space = {
            "Inherit": 0,
            "Relative": 1,
            "Absolute": 2,
            "Custom": 3
        }.get(MarkerUi["driveSpace"], 0)

        mod.smart_set_attr(marker["mass"], MarkerUi["mass"])
        mod.smart_set_attr(marker["inputType"], input_type)
        mod.smart_set_attr(marker["driveSpace"], drive_space)
        mod.smart_set_attr(marker["driveSpaceCustom"], MarkerUi["driveSpaceCustom"])
        mod.smart_set_attr(marker["driveStiffness"], MarkerUi["driveStiffness"])
        mod.smart_set_attr(marker["driveDampingRatio"], MarkerUi["driveDampingRatio"])
        mod.smart_set_attr(marker["driveAbsoluteLinear"], MarkerUi["driveAbsoluteLinear"])
        mod.smart_set_attr(marker["driveAbsoluteAngular"], MarkerUi["driveAbsoluteAngular"])
        mod.smart_set_attr(marker["limitStiffness"], MarkerUi["limitStiffness"])
        mod.smart_set_attr(marker["limitDampingRatio"], MarkerUi["limitDampingRatio"])
        mod.smart_set_attr(marker["collisionGroup"], MarkerUi["collisionGroup"])
        mod.smart_set_attr(marker["friction"], Rigid["friction"])
        mod.smart_set_attr(marker["restitution"], Rigid["restitution"])
        mod.smart_set_attr(marker["collide"], Rigid["collide"])
        mod.smart_set_attr(marker["linearDamping"], Rigid["linearDamping"])
        mod.smart_set_attr(marker["angularDamping"], Rigid["angularDamping"])
        mod.smart_set_attr(marker["positionIterations"],
                           Rigid["positionIterations"])
        mod.smart_set_attr(marker["velocityIterations"],
                           Rigid["velocityIterations"])
        mod.smart_set_attr(marker["maxContactImpulse"],
                           Rigid["maxContactImpulse"])
        mod.smart_set_attr(marker["maxDepenetrationVelocity"],
                           Rigid["maxDepenetrationVelocity"])
        # mod.smart_set_attr(marker["enableCCD"], Rigid["enableCCD"])
        mod.smart_set_attr(marker["angularMass"], Rigid["angularMass"])
        mod.smart_set_attr(marker["centerOfMass"], Rigid["centerOfMass"])

        mod.smart_set_attr(marker["shapeExtents"], Desc["extents"])
        mod.smart_set_attr(marker["shapeLength"], Desc["length"])
        mod.smart_set_attr(marker["shapeRadius"], Desc["radius"])
        mod.smart_set_attr(marker["shapeOffset"], Desc["offset"])

        # These are exported as Quaternion
        rotation = Desc["rotation"].asEulerRotation()
        mod.smart_set_attr(marker["shapeRotation"], rotation)

        mod.smart_set_attr(marker["color"], Color["value"])
        # mod.smart_set_attr(marker["drawShaded"], MarkerUi["shaded"])

        # Establish shape
        if Desc["type"] in ("Cylinder", "Capsule"):
            mod.smart_set_attr(marker["shapeType"], constants.CapsuleShape)

        elif Desc["type"] == "Box":
            mod.smart_set_attr(marker["shapeType"], constants.BoxShape)

        elif Desc["type"] == "Sphere":
            mod.smart_set_attr(marker["shapeType"], constants.SphereShape)

        elif Desc["type"] == "ConvexHull":
            mod.smart_set_attr(marker["shapeType"], constants.MeshShape)

        else:
            Name = self._registry.get(entity, "NameComponent")
            log.debug(
                "Unsupported shape type: %s.type=%s"
                % (Name["name"], Desc["type"])
            )


def load(fname, roots=None):
    loader = Loader(roots)
    loader.read(fname)
    return loader.load()


def reinterpret(fname, roots=None):
    loader = Loader(roots)
    loader.read(fname)
    return loader.reinterpret()


def export(fname, data=None):
    import json
    data = data or json.loads(cmds.ragdollDump())

    # Validate a few things
    registry = Registry(data)
    for entity in registry.view("SceneComponent", "NameComponent"):
        Name = registry.get(entity, "NameComponent")
        Scene = registry.get(entity, "SceneComponent")

        # This would be an invalid, non-exising scene
        assert Scene["entity"] != 0, "%s has no scene" % Name["shortestPath"]

    with open(fname, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

    return True
