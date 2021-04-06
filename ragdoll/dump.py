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
from . import commands, tools, internal as i__

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

        elif value["type"] == "Quaternion":
            value = cmdx.Quaternion(*value["values"])

        else:
            raise TypeError("Unsupported type: %s" % value)

        data[key] = value

    return data


class Registry(object):
    def __init__(self, dump):
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
        assert isinstance(component, i__.string_types), (
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
            name = Name["path"].rsplit("|", 2)[1]
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
    """Reconstruct physics from a Ragdoll dump

    Overview
    --------

    Hi and welcome to the Ragdoll Dump Loader!

    The Loader takes each entity in a given dump and generates a Maya
    scene graph from it. Sort of like how the "Mother Box" from the DC
    universe is able to turn the ash of a burnt house back into a house.

    It works on "transforms", which is the Maya `transform` node type
    and the type most often used to represent Ragdoll rigid bodies.
    Transforms can either be created from scratch or "merged" with existing
    nodes in the currently open scene. Either based on their name, or name
    plus some namespace.

    Merging
    -------

    An animator will typically have a hierarchy of nodes in the scene to
    which they would like physics applied. Physics was usually authored
    separately and exported into a `.rag` file; a.k.a. a Ragdoll "dump"

    In that case, references to transforms in this dump are associated
    with transforms in the Maya scene, typically under the root node
    an animator has got selected at the time of loading.

    Arguments:
        roots (list): Path(s) that the original path must match
        replace (list): Search/replace pairs of strings to find and replace
            in each original path

    """

    SupportedSchema = "ragdoll-1.0"

    def __init__(self, roots=None, replace=None):
        self._dump = {"entities": {}}
        self._roots = roots or []
        self._replace = replace or []

        # Do we need to re-analyse before use?
        self._up_to_date = False

        # Transient data, updated on changes to fname and filtering
        self._state = {

            # Map entity -> active Maya transform node
            "transforms": {},

            # Series of Scenes
            # {
            #    "entity": 1,
            #
            #    "options": {}
            # }
            "scenes": [],

            # Series of Rigids
            # {
            #    "entity": 10,
            #
            #    "options": {}
            # }
            "rigids": [],

            # Series of chains
            # {
            #    "rigids": [10, 11, 12, 13],
            #    "constraints": [14, 15, 16]
            #    "constraintMultipliers": [17],
            #
            #    "options": {},
            # }
            "chains": [],

            # Individual constraint
            # {
            #    "entity": 18,
            #    "options": {}
            # }
            "constraints": [],

            # Individual constraint multiplier
            # {
            #    "entity": 19,
            #    "options": {}
            # }
            "constraintMultipliers": [],

            # Individual rigid multiplier
            # {
            #    "entity": 20,
            #    "options": {}
            # }
            "rigidMultipliers": [],
        }

    def read(self, fname):
        self._dump = {"entities": {}}

        if isinstance(fname, dict):
            dump = fname

        else:
            with open(fname) as f:
                dump = json.load(f)

        assert "schema" in dump and dump["schema"] == self.SupportedSchema, (
            "Dump not compatible with this version of Ragdoll"
        )

        dump["entities"] = {

            # Original JSON stores keys as strings, but the original
            # keys are integers; i.e. entity IDs
            Entity(entity): value
            for entity, value in dump["entities"].items()
        }

        self._dump = dump
        self._up_to_date = False

    def set_roots(self, roots):
        self._roots[:] = roots
        self._up_to_date = False

    def set_replace(self, replace):
        self._replace[:] = replace
        self._up_to_date = False

    def analyse(self):
        """Fill internal state from dump with something we can use"""

        transforms = self._find_transforms()
        chains = self._find_chains()
        rigids = self._find_rigids()

        # Only create a scene if it's related to an interesting rigid
        rigid_entities = [r["entity"] for r in rigids]
        scenes = self._find_scenes(rigid_entities)

        for chain in chains:
            scenes += self._find_scenes(chain["rigids"])

        # Remove duplicates
        scenes = list({s["entity"]: s for s in scenes}.values())
        assert scenes, "No scenes would get made!"  # Could have been filtered

        # What got created on-top of rigids and chains? These are our leftovers
        visited = set()
        visited.update(s["entity"] for s in scenes)
        visited.update(r["entity"] for r in rigids)

        for chain in chains:
            visited.update(chain["rigids"])
            visited.update(chain["constraints"])
            visited.update(chain["constraintMultipliers"])

        leftovers = self._find_leftovers(visited)

        self._state.update({
            "transforms": transforms,
            "scenes": scenes,
            "rigids": rigids,
            "chains": chains,
            "constraints": leftovers["constraints"],
            "constraintMultipliers": leftovers["constraintMultipliers"],
        })

        self._up_to_date = True

        return self._state

    def ls(self):
        """Return current analysis"""
        if not self._up_to_date:
            self.analyse()

        return self._state.copy()

    def report(self):
        if not self._up_to_date:
            self.analyse()

        def _name(entity):
            Name = self.component(entity, "NameComponent")
            name = Name["path"].rsplit("|", 2)[1]
            return name

        scenes = self._state["scenes"]
        rigids = self._state["rigids"]
        constraints = self._state["constraints"]
        chains = self._state["chains"]
        constraint_multipliers = self._state["constraintMultipliers"]
        rigid_multipliers = self._state["rigidMultipliers"]

        if scenes:
            log.info("Scenes:")
            for scene in scenes:
                log.info("  %s.." % _name(scene["entity"]))

        if rigids:
            log.info("Rigids:")
            for rigid in rigids:
                log.info("  %s.." % _name(rigid["entity"]))

        if chains:
            log.info("Chains:")
            for chain in chains:
                log.info("  %s.." % _name(chain["rigids"][0]))

                for entity in chain["rigids"][1:]:
                    log.info("    -o %s.." % _name(entity))

        if constraints:
            log.info("Constraints:")
            for constraint in constraints:
                log.info("  %s.." % _name(constraint["entity"]))

        if constraint_multipliers:
            log.info("Constraint Multipliers:")
            for mult in constraint_multipliers:
                log.info("  %s.." % _name(mult["entity"]))

        if rigid_multipliers:
            log.info("Rigig Multipliers:")
            for mult in rigid_multipliers:
                log.info("  %s.." % _name(mult["entity"]))

        if not any([scenes,
                    rigids,
                    constraints,
                    chains,
                    constraint_multipliers,
                    rigid_multipliers]):
            log.warning("Dump was empty")

    @i__.with_undo_chunk
    def load(self, merge=True):
        """Apply JSON to existing nodes in the scene

        This will accurately reflect each and every rigid body from the
        exported file, at the expense of not being able to reproduce
        surronding, unrelated physics nodes like `pairBlend` and various
        matrix multiplication operations found in UI-level controls such
        as Active Rigid and Active Chain.

        It's also able to generate a scene from scratch, with no existing
        nodes present. A so called non-merge. This can be useful for
        debugging and "cleaning" a scene from any and all Maya-specific
        customisations or "hacks".

        Arguments:
            merge (bool): Apply dump to existing controls in the scene,
                otherwise generate new controls to go with the physics
                found in this dump.

        """

        if not self._up_to_date:
            self.analyse()

        if merge:
            transforms = self._find_transforms()
        else:
            transforms = self._make_transforms()

        rigid_multipliers = self._load_rigid_multipliers(transforms)
        constraint_multipliers = self._load_constraint_multipliers(transforms)

        scenes = self._load_scenes(transforms)
        rigids = self._load_rigids(scenes, transforms, rigid_multipliers)
        constraints = self._load_constraints(
            scenes, rigids, constraint_multipliers)

        self._up_to_date = False

        return {
            "transforms": transforms,
            "scenes": scenes,
            "rigids": rigids,
            "constraints": constraints,
            "constraint_multipliers": constraint_multipliers,
            "rigid_multipliers": rigid_multipliers,
        }

    @i__.with_undo_chunk
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
        if not self._up_to_date:
            self.analyse()

        if dry_run:
            self.report()
            return

        scenes = self._state["scenes"]
        rigids = self._state["rigids"]
        chains = self._state["chains"]
        constraints = self._state["constraints"]
        transforms = self._state["transforms"]

        rdscenes = self._create_scenes(scenes, transforms)
        rdrigids = self._create_rigids(rigids, rdscenes, transforms)

        rdchains = []
        for chain in chains:
            rdchain = self._create_chain(chain, rdscenes, transforms)
            rdchains += [rdchain]

        # Anything added on-top of new rigids and new chains, like
        # custom constraints or multipliers, are yet to be created
        rdconstraints = {}
        rdmultipliers = {}
        for chain, rdchain in zip(chains, rdchains):
            rdrigids.update(zip(chain["rigids"],
                                rdchain["rigids"]))
            rdconstraints.update(zip(chain["constraints"],
                                     rdchain["constraints"]))
            rdmultipliers.update(zip(chain["constraintMultipliers"],
                                     rdchain["constraintMultipliers"]))

        rdconstraints.update(
            self._create_constraints(
                constraints,
                rdscenes,
                rdrigids,
                rdmultipliers,
                transforms
            )
        )

        self._up_to_date = False

        return {
            "scenes": rdscenes,
            "rigids": rdrigids,
            "constraints": rdconstraints,
            "constraintMultipliers": rdmultipliers,
        }

    def view(self, *components):
        """Iterate over every entity that has all of `components`"""
        for entity in self._dump["entities"]:
            if all(self.has(entity, comp) for comp in components):
                yield entity

    def has(self, entity, component):
        """Return whether `entity` has `component`"""
        assert isinstance(entity, int), "entity must be int"
        assert isinstance(component, i__.string_types), (
            "component must be string")
        return component in self._dump["entities"][entity]["components"]

    def component(self, entity, component):
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

    def siblings(self, entity):
        """Yield siblings of entity

        -o root_grp
          -o spine1_ctl
             -o rRigid1
             -o rConstraintMultiplier
             -o rConstraint1    <--- `entity`

        The siblings of this entity is `rRigid1` and `rConstrintMultiplier`

        """

        Name = self.component(entity, "NameComponent")
        parent_path = Name["path"].rsplit("|", 1)[0]

        for entity in self._dump["entities"]:
            Name = self.component(entity, "NameComponent")
            sibling_parent_path = Name["path"].rsplit("|", 1)[0]

            if parent_path == sibling_parent_path:
                yield entity

    def _find_path(self, entity):
        Name = self.component(entity, "NameComponent")

        # Find original path, minus the rigid
        # E.g. |root_grp|upperArm_ctrl|rRigid4 -> |root_grp|upperArm_ctrl
        path = Name["path"]

        for search, replace in self._replace:
            path = path.replace(search, replace)

        return path

    def _make_transforms(self):
        transforms = {}

        for entity in self.view("RigidComponent"):

            # Scenes will make their own transform
            if self.has(entity, "SolverComponent"):
                continue

            Name = self.component(entity, "NameComponent")
            Rest = self.component(entity, "RestComponent")

            # Find name transform name, minus the rigid
            # E.g. |root_grp|upperArm_ctrl|rRigid4 -> upperArm_ctrl
            name = Name["path"].rsplit("|", 2)[1]

            with cmdx.DagModifier() as mod:
                transform = mod.create_node("transform", name=name)

                tm = cmdx.Tm(Rest["matrix"])
                mod.set_attr(transform["translate"], tm.translation())
                mod.set_attr(transform["rotate"], tm.rotation())

            transforms[entity] = transform

        if not transforms:
            raise RuntimeError("No transforms created")

        return transforms

    def _find_transforms(self):
        """Find and associate each entity with a Maya transform"""
        transforms = {}

        for entity in self.view():
            Name = self.component(entity, "NameComponent")

            # Find original path, minus the rigid
            # E.g. |root_grp|upperArm_ctrl|rRigid4 -> |root_grp|upperArm_ctrl
            path = Name["path"]

            for search, replace in self._replace:
                path = path.replace(search, replace)

            # Only filter non-scenes, as we'd like to reuse these
            if self._roots and not self.has(entity, "SolverComponent"):
                if not any(path.startswith(root) for root in self._roots):
                    continue

            try:
                transform = cmdx.encode(path)

            except cmdx.ExistError:
                # Transform wasn't found in this scene, that's OK.
                # It just means it can't actually be loaded onto anything.
                continue

            # Avoid the fate of double-assigning a rigid
            # NOTE: We might want to support import of constraints
            # onto existing rigid bodies.. but let's cross that bridge
            if transform.shape(type="rdRigid"):
                continue

            transforms[entity] = transform

        return transforms

    def _find_scenes(self, rigids):
        """Find and associate each entity with a Maya transform"""

        scenes = set()
        for rigid in rigids:
            Scene = self.component(rigid, "SceneComponent")
            scenes.add(Scene["entity"])

        scenes = [
            {
                "entity": scene,
                "options": {}
            }
            for scene in scenes
        ]

        return scenes

    def _find_rigids(self):
        """Identify lone rigids"""

        parents = set()
        for rigid in self.view("RigidUIComponent"):
            Rigid = self.component(rigid, "RigidComponent")

            if Rigid["parentRigid"]:
                parents.add(Rigid["parentRigid"])

        rigids = list()
        for rigid in self.view("RigidUIComponent"):
            Rigid = self.component(rigid, "RigidComponent")

            # Ignore chains
            if Rigid["parentRigid"]:
                continue

            # Root of chains don't have a parent,
            # but they are still chains.
            if rigid in parents:
                continue

            rigids.append(rigid)

        rigids = [
            {
                "entity": rigid,
                "options": {}
            }
            for rigid in rigids

        ]

        # Figure out options
        for rigid in rigids:
            rigid["options"].update({
                "passive": Rigid["kinematic"],
            })

        return rigids

    def _find_chains(self):
        r"""Identify chains amongst rigids

         o                   .                   .
          \          .        .          o        .          .
           \        .          .        /          .        .
            o . . .             o------o            . . . .o
            |       .           .       .           .       \
            |        . . .      .        . . .      .        o---o
            o                   .                   .


            Chain 1               Chain 2               Chain 3

        Rigids created as chains carry a `.parentRigid` attribute
        that identifies the intended "parent" for the rigid in the chain.

        Walk that attribute and find each chain in the resulting hierarchy.

        Based on https://www.educative.io/edpresso
                        /how-to-implement-depth-first-search-in-python

        """

        def _rigids():
            for rigid in self.view("RigidUIComponent"):
                yield rigid

        # Create a vertex for each rigid
        #
        #  o
        #              o
        #
        #     o      o
        #
        #              o   o
        #     o
        #
        graph = {}  # A.k.a. adjencency list

        for entity in _rigids():
            graph[entity] = []

        for entity in self.view("SolverComponent"):
            graph[entity] = []

        # Connect vertices based on the `.parentRigid` attribute
        #
        #  o
        #   \          o
        #    \        /
        #     o------o
        #     |       \
        #     |        o---o
        #     o
        #
        for entity in _rigids():
            Rigid = self.component(entity, "RigidComponent")
            Scene = self.component(entity, "SceneComponent")

            parent = Rigid["parentRigid"] or Scene["entity"]
            graph[parent].append(entity)

        # Identify chains
        #
        #  o                   .                   .
        #   \          .        .          o        .          .
        #    \        .          .        /          .        .
        #     o . . .             o------o            . . . .o
        #     |       .           .       .           .       \
        #     |        . . .      .        . . .      .        o---o
        #     o                   .                   .
        #
        #
        #  Chain 1               Chain 2               Chain 3
        #
        chains = []

        def walk(graph, entity, chain=None):
            """Depth-first search of `graph`, starting at `entity`"""
            chain = chain or []
            chain.append(entity)

            # End of chain, let's start anew
            if not graph[entity]:
                chains.append(list(chain))
                chain[:] = []

            for neighbour in graph[entity]:
                walk(graph, neighbour, chain)

        for scene in self.view("SolverComponent"):
            # Chains start at the scene, but let's not *include* the scene
            for neighbour in graph[scene]:
                walk(graph, neighbour)

        # Separate chains from individual rigids
        rigids = []
        for chain in chains[:]:
            if len(chain) == 1:
                rigids += chain
                chains.remove(chain)

        # Consider each chain its own object, with unique constraints
        chains = [
            {
                "rigids": chain,
                "constraints": [],
                "constraintMultipliers": [],

                # Figure out what the options were at the time
                # of creating this chain.
                "options": {},

                # If part of a tree, indicate whether this particular
                # chain is the root of that tree.
                "partOfTree": True,
            }
            for chain in chains
        ]

        # The root of this chain may or may not have a parent
        # If it doesn't, then this is the root of a tree
        #
        #    o   o
        #     \ /
        #  o   o  <-- root of chain
        #   \ /
        #    o
        #    |
        #    o  <-- root of tree
        #
        for chain in chains:
            Rigid = self.component(chain["rigids"][0], "RigidComponent")

            if Rigid["parentRigid"]:
                chain["rigids"].insert(0, Rigid["parentRigid"])
            else:
                chain["partOfTree"] = False

        # Find constraints associated to links in each chain
        #
        #  o link0       <-- Root, no constraint
        #   \
        #    \
        #     \
        #      \
        #       o link1  <-- con0
        #       |
        #       |
        #       |
        #       |
        #       o link2  <-- con1
        #
        for chain in chains:
            rigid_to_constraints = {}

            for rigid in chain["rigids"][1:]:
                for entity in self.siblings(rigid):

                    if not self.has(entity, "JointComponent"):
                        continue

                    Joint = self.component(entity, "JointComponent")

                    # There may be more than one constraint to a given
                    # rigid, if the user made a chain and *then* constrained
                    # it some more. It is however unlikely to be two
                    # constraints between the same two rigids. An edgecase
                    # is having two or more constraints for independent
                    # control of their limits and strengths.
                    if Joint["child"] != rigid:
                        continue

                    Rigid = self.component(rigid, "RigidComponent")

                    # It's guaranteed to have the same parent as the
                    # rigid itself; it's what makes it a chain.
                    if Joint["parent"] != Rigid["parentRigid"]:
                        continue

                    if rigid not in rigid_to_constraints:
                        rigid_to_constraints[rigid] = []

                    rigid_to_constraints[rigid].append(entity)

            # In case there are two constraints between the same
            # two links, we'll pick the one first in the Maya outliner
            # hierarchy. That'll be the one created when the transform
            # is first turned into a chain, the rest being added afterwards.
            for rigid in chain["rigids"][1:]:
                constraints = rigid_to_constraints[rigid]
                assert len(constraints) > 0

                # This will be the common case
                if len(constraints) == 1:
                    chain["constraints"] += constraints

                else:
                    indices = []
                    for constraint in constraints:
                        ConstraintUi = self.component(constraint,
                                                      "ConstraintUIComponent")
                        index = ConstraintUi["childIndex"]
                        indices.append((index, constraint))

                    chain["constraints"] += sorted(
                        indices, key=lambda i: i[0]
                    )[:1]

            # The root *may* have a multiplier, it's optional and only
            # occurs at the root of a tree.
            if not chain["partOfTree"]:
                root = chain["rigids"][0]
                for entity in self.siblings(root):
                    if self.has(entity, "ConstraintMultiplierUIComponent"):
                        chain["constraintMultipliers"].append(entity)

        # Figure out what options to use to recreate this chain
        #
        #  _______________________________________
        # |______________________________________x|
        # |                                       |
        # |   o   - - - - - - -                   |
        # |    \  __________________              |
        # |     o ---------------                 |
        # |        ______                         |
        # |   --- |______|                        |
        # |    -- o                               |
        # |  ---- o__________                     |
        # |   --- |__________|                    |
        # |                                       |
        # |_______________________________________|
        # |            |             |            |
        # |____________|_____________|____________|
        # |_______________________________________|
        #
        #
        for chain in chains:
            root = chain["rigids"][0]

            RootRigid = self.component(root, "RigidComponent")
            RootRigidUi = self.component(root, "RigidUIComponent")

            chain["options"].update({
                "passiveRoot": RootRigid["kinematic"],
                "drawShaded": RootRigidUi["shaded"],
                "autoMultiplier": chain["constraintMultipliers"] != [],
            })

        # Sanity checks
        for chain in chains:

            # Just warn. It'll still work, in fact it will
            # be *repaired* by creating each link using the
            # scene from the first link. It just might not
            # be what the user expects.
            self._validate_same_scene(chain["rigids"])
            self._validate_same_scene(chain["constraints"])

        return chains

    def _load_scenes(self, transforms):
        scenes = {}

        for entity in self.view("SolverComponent"):
            Name = self.component(entity, "NameComponent")

            # Support loading a dump multiple times,
            # whilst only creating one instance of
            # a contained scene
            try:
                transform = transforms[entity]
                scene = transform.shape(type="rdScene")

                if scene:
                    scenes[entity] = scene
                    continue

            except KeyError:
                # There wasn't a transform for this scene, that's OK
                pass

            name = _name(Name, -2)
            scene = commands.create_scene(name=name)

            with cmdx.DagModifier() as mod:
                self._apply_scene(mod, entity, scene)

            scenes[entity] = scene

        return scenes

    def _create_scenes(self, scenes, transforms):
        rdscenes = {}

        for scene in scenes:
            Name = self.component(scene["entity"], "NameComponent")

            # Support loading a dump multiple times,
            # whilst only creating one instance of
            # a contained scene
            try:
                transform = transforms[scene["entity"]]
                rdscene = transform.shape(type="rdScene")

                if rdscene:
                    rdscenes[scene["entity"]] = rdscene
                    continue

            except KeyError:
                # There wasn't a transform for this scene, that's OK
                pass

            name = _name(Name, -2)
            rdscene = commands.create_scene(name=name)

            with cmdx.DagModifier() as mod:
                self._apply_scene(mod, scene["entity"], rdscene)

            rdscenes[scene["entity"]] = rdscene

        return rdscenes

    def _create_constraints(self,
                            constraints,
                            scenes,
                            rigids,
                            multipliers,
                            transforms):
        entity_to_constraint = {}

        for constraint in constraints:
            entity = constraint["entity"]

            if entity not in transforms:
                continue

            # These are guaranteed to be associated to any entity
            # with a `JointComponent`
            Name = self.component(entity, "NameComponent")
            Joint = self.component(entity, "JointComponent")
            ConstraintUi = self.component(entity, "ConstraintUIComponent")

            parent_entity = Joint["parent"]
            child_entity = Joint["child"]

            assert parent_entity in rigids or parent_entity in scenes, (
                "%s|%s.parentRigid=%r was not found in this dump"
                % (Name["path"], Name["value"], parent_entity)
            )

            assert child_entity in rigids, (
                "%s|%s.childRigid=%r was not found in this dump"
                % (Name["path"], Name["value"], child_entity)
            )

            try:
                parent_rigid = rigids[parent_entity]
            except KeyError:
                parent_rigid = scenes[parent_entity]

            child_rigid = rigids[child_entity]

            con = commands.create_constraint(parent_rigid, child_rigid)

            with cmdx.DagModifier() as mod:
                self._apply_constraint(mod, entity, con)

                # Restore it's name too
                mod.rename(con, Name["value"])

                if ConstraintUi["multiplierEntity"] in multipliers:
                    multiplier = multipliers[ConstraintUi["multiplierEntity"]]
                    mod.connect(multiplier["ragdollId"],
                                con["multiplierNode"])

            entity_to_constraint[entity] = con

        return entity_to_constraint

    def _create_rigids(self, rigids, rdscenes, transforms, multipliers=None):
        multipliers = multipliers or []
        entity_to_rigid = {}

        for rigid in rigids:
            entity = rigid["entity"]

            try:
                transform = transforms[entity]
            except KeyError:
                continue

            Name = self.component(entity, "NameComponent")
            RigidUi = self.component(entity, "RigidUIComponent")
            Scene = self.component(entity, "SceneComponent")

            # Scenes have a rigid component too, but we've already created it
            if entity == Scene["entity"]:
                continue

            rdscene = rdscenes[Scene["entity"]]
            assert isinstance(rdscene, cmdx.DagNode), rdscene
            assert rdscene.type() == "rdScene", rdscene

            rigid = commands.create_rigid(transform,
                                          rdscene,
                                          opts=rigid["options"])

            with cmdx.DagModifier() as mod:
                self._apply_rigid(mod, entity, rigid)

                # Restore it's name too
                mod.rename(rigid, Name["value"])

                if RigidUi["multiplierEntity"] in multipliers:
                    multiplier = multipliers[RigidUi["multiplierEntity"]]
                    mod.connect(multiplier["ragdollId"],
                                rigid["multiplierNode"])

            entity_to_rigid[entity] = rigid

        return entity_to_rigid

    def _create_chain(self, chain, rdscenes, entity_to_transform):
        """Create `chains` for `entity_to_transform` belonging to `rdscenes`

        Chains are provided as a list-of-lists, each entry being an
        individual chain.

        [
            [2, 3, 4, 5],               <-- Rigids
            [10, 11, 12, 13],
            [516, 1671, 13561, 13567],
        ]

        Each entity is guaranteed to have a corresponding transform,
        one that was either found or created for this purpose.

        """

        result = {
            "rigids": [],
            "constraints": [],
            "constraintMultipliers": [],
        }

        root_rigid = chain["rigids"][0]
        Name = self.component(root_rigid, "NameComponent")
        Scene = self.component(root_rigid, "SceneComponent")

        try:
            rdscene = rdscenes[Scene["entity"]]
        except KeyError:
            raise ValueError(
                "The scene for %s hasn't yet been created"
                % Name["path"]
            )

        # Find a transform for each link in each chain
        transforms = []
        transform_to_link = {}
        for link in chain["rigids"]:

            try:
                transform = entity_to_transform[link]

            except KeyError:
                # Every link needs a transform, otherwise
                # it's not really a chain
                return result

            transform_to_link[transform] = link
            transforms.append(transform)

        # They may have all been filtered out
        if not transforms:
            return

        # All done, it's time to get creative!
        #
        #              o
        #    o        /
        #     \      /
        #      \  /\
        #        /  \
        #       /\  /  ---o
        #      /  \/
        #     /   /  \
        #    /   /    \
        #   /   /      o
        #   \  /
        #    \/
        #
        # We should have filtered these out already,
        # they would be solo rigids.
        assert len(transforms) > 1, "Bad chain: %s" % str(transforms)

        active_chain = tools.create_chain(transforms,
                                          rdscene,
                                          opts=chain["options"])

        new_rigids = [
            n for n in active_chain if n.type() == "rdRigid"
        ]
        new_constraints = [
            n for n in active_chain if n.type() == "rdConstraint"
        ]
        new_multipliers = [
            n for n in active_chain if n.type() == "rdConstraintMultiplier"
        ]

        if len(new_rigids) != len(chain["rigids"]):
            word = "were" if len(new_rigids) < 2 else "was"
            log.warning(
                "I expected %d rigids, but %d %s created",
                len(chain["rigids"]), word, len(new_rigids)
            )

        if len(new_constraints) != len(chain["constraints"]):
            word = "were" if len(new_constraints) < 2 else "was"
            log.warning(
                "I expected %d constraints, but %d %s created",
                len(chain["constraints"]), word, len(new_constraints)
            )

        if len(new_multipliers) != len(chain["constraintMultipliers"]):
            word = "were" if len(new_multipliers) < 2 else "was"
            log.warning(
                "I expected %d multipliers, but %d %s created",
                len(chain["constraintMultipliers"]), word, len(new_multipliers)
            )

        # This command generated a series of nodes. We'll want to map
        # these onto entities in the exported file such that we can
        # apply those attributes.
        #
        #    _____                        ______________
        #   |\ ___\                      |             |\
        #   | |  - | - - - - - - - - - - -o            |_\
        #    \|____|       ___           |               |
        #                 /   \          |               |
        #                 \___/          |               |
        #                    \\          |     JSON      |
        #                     \\         |               |
        #     | /|             `         |               |
        #   __|/ | - - - - - - - - - - - - - -o          |
        #      \ |                       |               |
        #       \|                       |_______________|
        #
        #
        # Map components to newly created rigids and constraints
        entity_to_rigid = {}
        entity_to_constraint = {}
        entity_to_multiplier = {}

        # Find which entity in our dump corresponds
        # to the newly created rigid.
        for rigid, new_rigid in zip(chain["rigids"], new_rigids):
            entity_to_rigid[rigid] = new_rigid

        # Next, find the corresponding constraint link
        for constraint, new_constraint in zip(chain["constraints"],
                                              new_constraints):
            entity_to_constraint[constraint] = new_constraint

        # Finally, there may be a multiplier at the root
        for multiplier, new_multiplier in zip(chain["constraintMultipliers"],
                                              new_multipliers):
            entity_to_multiplier[multiplier] = new_multiplier

        # Ok, we've mapped them all, let's get busy!
        #
        #    _____                        ______________
        #   |\ ___\        write         |             |\
        #   | |  - | <--------------------o            |_\
        #    \|____|                     |               |
        #                                |               |
        #                                |               |
        #                                |               |
        #                                |               |
        #     | /|         write         |               |
        #   __|/ | <--------------------------o          |
        #      \ |                       |               |
        #       \|                       |_______________|
        #
        #
        with cmdx.DagModifier() as mod:
            # Apply customisation to each rigid
            for entity, rigid in entity_to_rigid.items():
                self._apply_rigid(mod, entity, rigid)

            # Apply customisation to each constraint
            for entity, con in entity_to_constraint.items():
                self._apply_constraint(mod, entity, con)

            # Apply customisation to each multiplier
            for entity, mult in entity_to_multiplier.items():
                self._apply_constraint_multiplier(mod, entity, mult)

        result.update({
            "rigids": new_rigids,
            "constraints": new_constraints,
            "constraintMultipliers": new_multipliers,
        })

        return result

    def _find_leftovers(self, visited):

        leftovers = {
            "constraints": [],
            "constraintMultipliers": [],
        }

        for entity in self._dump["entities"]:
            if entity in visited:
                continue

            if self.has(entity, "ConstraintUIComponent"):
                leftovers["constraints"].append({
                    "entity": entity,
                    "options": {}
                })

            if self.has(entity, "ConstraintMultiplierUIComponent"):
                leftovers["constraintMultipliers"].append({
                    "entity": entity,
                    "options": {}
                })

        return leftovers

    def _load_rigid_multipliers(self, transforms):
        rigid_multipliers = {}

        for entity in self._dump["entities"]:
            if not self.has(entity, "RigidMultiplierUIComponent"):
                continue

            Name = self.component(entity, "NameComponent")

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

                self._apply_rigid_multiplier(mod, entity, node)

            rigid_multipliers[entity] = node

        return rigid_multipliers

    def _load_rigids(self, scenes, transforms, multipliers=None):
        multipliers = multipliers or []
        rigids = {}

        for entity in self._dump["entities"]:
            if not self.has(entity, "RigidComponent"):
                continue

            # The scene has a rigid too
            if self.has(entity, "SolverComponent"):
                continue

            # These are guaranteed to be associated to any entity
            # with a `RigidComponent`
            Name = self.component(entity, "NameComponent")
            RigidUi = self.component(entity, "RigidUIComponent")
            Scene = self.component(entity, "SceneComponent")

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
                self._apply_rigid(mod, entity, rigid)

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

        for entity in self._dump["entities"].items():
            if not self.has(entity, "ConstraintMultiplierUIComponent"):
                continue

            Name = self.component(entity, "NameComponent")

            with cmdx.DagModifier() as mod:
                try:
                    transform = transforms[entity]
                except KeyError:
                    # These may have their own transform
                    transform = mod.create_node("transform", _name(Name))

                mult = mod.create_node("rdConstraintMultiplier",
                                       name=_name(Name),
                                       parent=transform)

                self._apply_constraint_multiplier(mod, entity, mult)

                rigid_multipliers[entity] = mult

        return rigid_multipliers

    def _load_constraints(self, scenes, rigids, multipliers):
        constraints = {}

        for entity, data in self._dump["entities"].items():
            comps = data["components"]

            if "JointComponent" not in comps:
                continue

            # These are guaranteed to be associated to any entity
            # with a `JointComponent`
            Name = Component(comps["NameComponent"])
            Joint = Component(comps["JointComponent"])
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
                self._apply_constraint(mod, entity, con)

                # Restore it's name too
                mod.rename(con, _name(Name))

                if ConstraintUi["multiplierEntity"] in multipliers:
                    multiplier = multipliers[ConstraintUi["multiplierEntity"]]
                    mod.connect(multiplier["ragdollId"],
                                con["multiplierNode"])

            constraints[entity] = con

        return constraints

    def _apply_scene(self, mod, entity, scene):
        Solver = self.component(entity, "SolverComponent")

        mod.try_set_attr(scene["enabled"], Solver["enabled"])
        mod.try_set_attr(scene["gravity"], Solver["gravity"])
        mod.try_set_attr(scene["airDensity"], Solver["airDensity"])
        mod.try_set_attr(scene["substeps"], Solver["substeps"])
        mod.try_set_attr(scene["useGround"], Solver["useGround"])
        mod.try_set_attr(scene["groundFriction"], Solver["groundFriction"])
        mod.try_set_attr(scene["groundRestitution"],
                         Solver["groundRestitution"])
        mod.try_set_attr(scene["bounceThresholdVelocity"],
                         Solver["bounceThresholdVelocity"])
        mod.try_set_attr(scene["threadCount"], Solver["numThreads"])
        mod.try_set_attr(scene["enableCCD"], Solver["enableCCD"])
        mod.try_set_attr(scene["timeMultiplier"], Solver["timeMultiplier"])
        # mod.try_set_attr(scene["spaceMultiplier"], Solver["spaceMultiplier"])
        mod.try_set_attr(scene["positionIterations"],
                         Solver["positionIterations"])
        mod.try_set_attr(scene["velocityIterations"],
                         Solver["velocityIterations"])
        mod.try_set_attr(scene["solverType"], commands.PGSSolverType
                         if Solver["type"] == "PGS"
                         else commands.TGSSolverType)

    def _apply_rigid(self, mod, entity, rigid):
        comps = self._dump["entities"][entity]["components"]
        Name = Component(comps["NameComponent"])
        Desc = Component(comps["GeometryDescriptionComponent"])
        Color = Component(comps["ColorComponent"])
        Rigid = Component(comps["RigidComponent"])
        RigidUi = Component(comps["RigidUIComponent"])

        mod.try_set_attr(rigid["mass"], Rigid["mass"])
        mod.try_set_attr(rigid["friction"], Rigid["friction"])
        mod.try_set_attr(rigid["collide"], Rigid["collide"])
        mod.try_set_attr(rigid["kinematic"], Rigid["kinematic"])
        mod.try_set_attr(rigid["linearDamping"], Rigid["linearDamping"])
        mod.try_set_attr(rigid["angularDamping"], Rigid["angularDamping"])
        mod.try_set_attr(rigid["positionIterations"],
                         Rigid["positionIterations"])
        mod.try_set_attr(rigid["velocityIterations"],
                         Rigid["velocityIterations"])
        mod.try_set_attr(rigid["maxContactImpulse"],
                         Rigid["maxContactImpulse"])
        mod.try_set_attr(rigid["maxDepenetrationVelocity"],
                         Rigid["maxDepenetrationVelocity"])
        mod.try_set_attr(rigid["enableCCD"], Rigid["enableCCD"])
        mod.try_set_attr(rigid["angularMass"], Rigid["angularMass"])
        mod.try_set_attr(rigid["centerOfMass"], Rigid["centerOfMass"])

        mod.try_set_attr(rigid["shapeExtents"], Desc["extents"])
        mod.try_set_attr(rigid["shapeLength"], Desc["length"])
        mod.try_set_attr(rigid["shapeRadius"], Desc["radius"])
        mod.try_set_attr(rigid["shapeOffset"], Desc["offset"])

        # These are exported as Quaternion
        rotation = Desc["rotation"].asEulerRotation()
        mod.try_set_attr(rigid["shapeRotation"], rotation)

        mod.try_set_attr(rigid["color"], Color["value"])
        mod.try_set_attr(rigid["drawShaded"], RigidUi["shaded"])

        # Establish shape
        if Desc["type"] in ("Cylinder", "Capsule"):
            mod.try_set_attr(rigid["shapeType"], commands.CapsuleShape)

        elif Desc["type"] == "Box":
            mod.try_set_attr(rigid["shapeType"], commands.BoxShape)

        elif Desc["type"] == "Sphere":
            mod.try_set_attr(rigid["shapeType"], commands.SphereShape)

        elif Desc["type"] == "ConvexHull":
            mod.try_set_attr(rigid["shapeType"], commands.MeshShape)

        else:
            log.warning(
                "Unsupported shape type: %s.type=%s"
                % (Name["path"], Desc["type"])
            )

    def _apply_constraint(self, mod, entity, con):
        data = self._dump["entities"][entity]
        comps = data["components"]

        Joint = Component(comps["JointComponent"])
        Limit = Component(comps["LimitComponent"])
        LimitUi = Component(comps["LimitUIComponent"])
        Drive = Component(comps["DriveComponent"])
        DriveUi = Component(comps["DriveUIComponent"])

        # Frames are exported on worldspace, but Maya scales these by
        # its own transform. So we'll need to compensate for that.
        parent_rigid = con["parentRigid"].connection()
        child_rigid = con["childRigid"].connection()

        if parent_rigid:
            parent_scale = parent_rigid.scale(cmdx.sWorld)

            # Protect against possible 0-scaled transforms
            if not any(axis == 0 for axis in parent_scale):
                parent_frame = Joint["parentFrame"]
                parent_frame[3 * 4 + 0] /= parent_scale.x
                parent_frame[3 * 4 + 1] /= parent_scale.y
                parent_frame[3 * 4 + 2] /= parent_scale.z

        if child_rigid:
            child_scale = child_rigid.scale(cmdx.sWorld)

            # Protect against possible 0-scaled transforms
            if not any(axis == 0 for axis in child_scale):
                child_frame = Joint["childFrame"]
                child_frame[3 * 4 + 0] /= child_scale.x
                child_frame[3 * 4 + 1] /= child_scale.y
                child_frame[3 * 4 + 2] /= child_scale.z

        mod.try_set_attr(con["parentFrame"], parent_frame)
        mod.try_set_attr(con["childFrame"], child_frame)
        mod.try_set_attr(con["disableCollision"],
                         Joint["disableCollision"])

        mod.try_set_attr(con["limitEnabled"], Limit["enabled"])
        mod.try_set_attr(con["linearLimitX"], Limit["x"])
        mod.try_set_attr(con["linearLimitY"], Limit["y"])
        mod.try_set_attr(con["linearLimitZ"], Limit["z"])
        mod.try_set_attr(con["angularLimitX"], Limit["twist"])
        mod.try_set_attr(con["angularLimitY"], Limit["swing1"])
        mod.try_set_attr(con["angularLimitZ"], Limit["swing2"])
        mod.try_set_attr(con["limitStrength"], LimitUi["strength"])
        mod.try_set_attr(con["linearLimitStiffness"],
                         LimitUi["linearStiffness"])
        mod.try_set_attr(con["linearLimitDamping"],
                         LimitUi["linearDamping"])
        mod.try_set_attr(con["angularLimitStiffness"],
                         LimitUi["angularStiffness"])
        mod.try_set_attr(con["angularLimitDamping"],
                         LimitUi["angularDamping"])

        mod.try_set_attr(con["driveEnabled"], Drive["enabled"])
        mod.try_set_attr(con["driveStrength"], DriveUi["strength"])
        mod.try_set_attr(con["linearDriveStiffness"],
                         DriveUi["linearStiffness"])
        mod.try_set_attr(con["linearDriveDamping"],
                         DriveUi["linearDamping"])
        mod.try_set_attr(con["angularDriveStiffness"],
                         DriveUi["angularStiffness"])
        mod.try_set_attr(con["angularDriveDamping"],
                         DriveUi["angularDamping"])
        mod.try_set_attr(con["driveMatrix"], Drive["target"])

    def _apply_rigid_multiplier(self, mod, entity, mult):
        data = self._dump["entities"][entity]
        comps = data["components"]

        Mult = Component(comps["RigidMultiplierUIComponent"])

        mod.try_set_attr(mult["airDensity"], Mult["airDensity"])
        mod.try_set_attr(mult["linearDamping"], Mult["linearDamping"])
        mod.try_set_attr(mult["angularDamping"], Mult["angularDamping"])

    def _apply_constraint_multiplier(self, mod, entity, mult):
        data = self._dump["entities"][entity]
        comps = data["components"]

        Mult = Component(comps["ConstraintMultiplierUIComponent"])

        mod.try_set_attr(mult["limitStrength"],
                         Mult["limitStrength"])
        mod.try_set_attr(mult["linearLimitStiffness"],
                         Mult["linearLimitStiffness"])
        mod.try_set_attr(mult["linearLimitDamping"],
                         Mult["linearLimitDamping"])
        mod.try_set_attr(mult["angularLimitStiffness"],
                         Mult["angularLimitStiffness"])
        mod.try_set_attr(mult["angularLimitDamping"],
                         Mult["angularLimitDamping"])
        mod.try_set_attr(mult["driveStrength"],
                         Mult["driveStrength"])
        mod.try_set_attr(mult["linearDriveStiffness"],
                         Mult["linearDriveStiffness"])
        mod.try_set_attr(mult["linearDriveDamping"],
                         Mult["linearDriveDamping"])
        mod.try_set_attr(mult["angularDriveStiffness"],
                         Mult["angularDriveStiffness"])
        mod.try_set_attr(mult["angularDriveDamping"],
                         Mult["angularDriveDamping"])

    def _has_transforms(self, rigids, transforms):
        for rigid in rigids:
            if rigid not in transforms:
                Name = self.component(rigid, "NameComponent")
                log.error("%s did not have a transform" % Name["path"])
                return False
        return True

    def _validate_same_scene(self, entities):
        # Sanity check, all `entities` belong to the same scene
        scene = self.component(entities[0], "SceneComponent")["entity"]
        same_scene = all(
            self.component(link, "SceneComponent")["entity"] == scene
            for link in entities[1:]
        )

        if not same_scene:
            for link in entities:
                Name = self.component(link, "NameComponent")
                print(Name["path"])
                Scene = self.component(link, "SceneComponent")
                SName = self.component(Scene["entity"], "NameComponent")
                log.warning(
                    "%s.scene = %s" % (Name["shortestPath"],
                                       SName["shortestPath"])
                )

            log.warning(
                "Some entities that should have been "
                "part of the same scene were not."
            )

        return same_scene


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
