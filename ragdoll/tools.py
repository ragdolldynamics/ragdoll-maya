"""End-user tools

These combine several API functions to create more high-level functionality

"""

import logging

from maya import cmds
from .vendor import cmdx
from . import commands

log = logging.getLogger("ragdoll")


class UndoChunk(object):
    def __init__(self, name):
        self._name = name
        cmds.undoInfo(chunkName=name,
                      openChunk=True)

    def __del__(self):
        cmds.undoInfo(chunkName=self._name,
                      closeChunk=True)


class Character(object):
    """The Ragdoll auto-rigger, a.k.a. 'autoragger'"""

    Knee = 3
    Elbow = 11
    Finger = 19
    Hand = 12
    Foot = 4
    Toe = 5
    Head = 8
    Other = 18
    Skip = "skip"  # Case insensitive
    Stop = "stop"

    def __init__(self, root, scene, opts=None):
        assert root.isA(cmdx.kJoint), "%s was not a joint" % root
        self._root = root
        self._scene = scene
        self._opts = opts or {
            "inclusive": True,
        }

    def parse(self, parent=None):
        _ = UndoChunk("Character")
        return self._parse(parent)

    def _parse(self, parent=None):
        parent = parent or self._root

        # Skip any non-joints, like empty transform offset groups
        if parent.isA(cmdx.kJoint):
            result = self.dispatch(parent, parent)

            if result == self.Stop:
                return

        for child in parent.children():
            self.parse(child)

    def dispatch(self, joint, parent=None):
        mapping = {
            self.Knee: self.on_knee,
            self.Elbow: self.on_elbow,
            self.Finger: self.on_finger,
            self.Hand: self.on_hand,
            self.Foot: self.on_foot,
            self.Toe: self.on_toe,
            self.Head: self.on_head,
        }

        inclusive = self._opts.get("inclusive", False)
        exclusive = not inclusive
        label = joint["type"].read()

        if label == self.Other:
            label = joint["otherType"].read().lower()

        if label == self.Skip:
            return self.Skip

        if exclusive and label == self.Stop:
            return self.Stop

        func = mapping.get(label, self.on_unlabelled)
        func(joint)

        if inclusive and label == self.Stop:
            return self.Stop

    def make_hinge(self, joint, parent=None):
        rigid = commands.create_rigid(joint, self._scene)

        if parent is not None:
            constraint = commands.hinge_constraint(parent, rigid, self._scene)
            commands.orient(constraint)
            commands.reorient(constraint)

            with cmdx.DagModifier() as mod:
                mod.set_attr(constraint["driveEnabled"], True)
                mod.set_attr(constraint["driveStrength"], 1)
                mod.set_attr(constraint["linearDriveStiffness"], 0)
                mod.set_attr(constraint["linearDriveDamping"], 0)

            constraint["driveEnabled"].keyable = True
            constraint["driveStrength"].keyable = True
        else:
            constraint = None

        return rigid, constraint

    def make_socket(self, joint, parent=None):
        rigid = commands.create_rigid(joint, self._scene)

        if parent is not None:
            constraint = commands.socket_constraint(parent, rigid, self._scene)
            commands.orient(constraint)
        else:
            constraint = None

        return rigid, constraint

    def on_unlabelled(self, joint, parent=None):
        self.make_socket(joint, parent)

    def on_knee(self, joint, parent=None):
        print("on_knee       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_elbow(self, joint, parent=None):
        print("on_elbow      (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_finger(self, joint, parent=None):
        print("on_finger     (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_hand(self, joint, parent=None):
        print("on_hand       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)

    def on_foot(self, joint, parent=None):
        print("on_foot       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape

    def on_toe(self, joint, parent=None):
        print("on_toe        (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape

    def on_head(self, joint, parent=None):
        print("on_head       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape


@commands.with_undo_chunk
def create_character(root,
                     scene,
                     copy=True,
                     control=True,
                     inclusive=True,
                     normalise_shapes=False):
    """Convert hierarchy into a character

    Arguments:
        root (joint): Starting joint for character, typically pelvis
        scene (rdScene): Scene to which newly created character belongs
        copy (bool): Make character from a duplicate of `root`,
            or connect provided `root` to physics
        control (bool): Make `root` an input control
            to copy (implies copy=True)
        inclusive (bool): Does "stop" mean before or after a labelled joint?
        normalise_shapes (bool): Retroactively resize shapes
            relative each other

    """

    assert root.type() == "joint", "%s was not a joint"
    assert scene.type() == "rdScene", "%s was not a rdScene"

    # Supported Maya-native joint labels
    Knee = 3
    Elbow = 11
    Finger = 19
    Hand = 12
    Foot = 4
    Toe = 5
    Head = 8
    Other = 18
    Skip = "skip"  # Case insensitive
    Stop = "stop"

    exclusive = not inclusive

    # Can't do control without copying first
    if not copy:
        control = False

    # Protect against duplicate rigid-making
    self = create_character
    self.done = []

    # Recursively make rigids and add constraints to `root`
    def _recurse(child, parent=None):
        if child in self.done:
            return

        # Ignore tip-joints
        if not child.child(type="joint"):
            return

        label = child["type"]

        if label == Other:
            label = child["otherType"].read().lower()

        if exclusive and label == Stop:
            return

        if label == Skip:
            child = child.child(type="joint")
            rigid = parent

        else:
            rigid = commands.create_rigid(child, scene)

            if parent is not None:
                if label in (Knee, Elbow, Finger):
                    constraint = commands.hinge_constraint(parent,
                                                           rigid,
                                                           scene)
                    commands.orient(constraint)
                    commands.reorient(constraint)

                    with cmdx.DagModifier() as mod:
                        mod.set_attr(constraint["driveEnabled"], True)
                        mod.set_attr(constraint["driveStrength"], 1)
                        mod.set_attr(constraint["linearDriveStiffness"], 0)
                        mod.set_attr(constraint["linearDriveDamping"], 0)

                    constraint["driveEnabled"].keyable = True
                    constraint["driveStrength"].keyable = True

                else:
                    constraint = commands.socket_constraint(parent,
                                                            rigid,
                                                            scene)
                    commands.orient(constraint)

                # Make boxes out of these
                if label in (Hand, Foot, Toe, Head):
                    with cmdx.DagModifier() as mod:
                        mod.set_attr(rigid["shapeType"], commands.BoxShape)

        self.done += [child]

        if inclusive and label == Stop:
            return

        for gc in child.children(type="joint"):
            _recurse(gc, rigid)

    result = root

    if copy:
        result = cmds.duplicate(result.path(), returnRootsOnly=True)[0]
        result = cmdx.encode(result)

    _recurse(result)

    if control:
        rigid = result.shape(type="rdRigid")

        with cmdx.DagModifier() as mod:
            # Facilitate kinematic attribute
            mod.connect(root["matrix"], rigid["inputMatrix"])

        # Absolute control on hip
        ref, _, con = commands.create_absolute_control(rigid, reference=root)

        with cmdx.DagModifier() as mod:
            mod.set_attr(root["driveStrength"], 0)  # Default to off

        # Forward the kinematic attribute to the root guide
        root_proxies = commands.UserAttributes(rigid, root)
        root_proxies.add_divider("Ragdoll")
        root_proxies.add("kinematic")
        root_proxies.do_it()

        with cmdx.DagModifier() as mod:
            for reference, joint in zip(root.descendents(type="joint"),
                                        result.descendents(type="joint")):

                rigid = joint.shape(type="rdRigid")

                if rigid is None:
                    continue

                commands.create_active_control(reference, rigid)

                mod.set_attr(rigid["kinematic"], False)
                mod.do_it()

                # Forward kinematics from children too
                reference_proxies = commands.UserAttributes(rigid, reference)
                reference_proxies.add_divider("Ragdoll")
                reference_proxies.add("kinematic")
                reference_proxies.do_it()

                mod.connect(reference["worldMatrix"][0], rigid["inputMatrix"])

    if normalise_shapes:
        commands.normalise_shapes(result)

    return result


@commands.with_undo_chunk
def create_dynamic_control(chain,
                           scene,
                           auto_blend=True,
                           auto_influence=True,
                           auto_multiplier=True,
                           auto_key=False,
                           central_blend=True,
                           use_capsules=True):
    """Turn selected animation controls dynamic

    Arguments:
        chain (list): Transform nodes, like animation controllers,
            to turn into dynamic rigid bodies
        scene (rdScene): The scene to which new rigid bodies should be added
        auto_blend (bool): Put a pairBlend between rigid and controller, for
            additional control
        auto_influence (bool): Use blended animation as input to the simulation
        auto_multiplier (bool): Add a multiplier to the root
        auto_key (bool): Put keyframes on translate/rotate
        use_capsules (bool): Let the default shape be a capsule

    """

    assert scene.type() == "rdScene", "%s was not a rdScene" % scene
    assert isinstance(chain, (list, tuple)), "chain was not a list"
    assert chain, "chain was empty"

    auto_influence = auto_blend and auto_influence
    local_constraints = []
    world_constraints = []
    new_rigids = []

    root, children = chain[0], chain[1:]

    parent = root

    def _add_pairblend(mod, rigid, transform):
        """Put a pairBlend between rigid and transform

         ________________          ___________
        |                |        |           |
        | originalInput  o--------o           |
        |________________|        |           |
                                  |           |
                                  | pairBlend o------>
         ________________         |           |
        |                |        |           |
        | simulation     o--------o           |
        |________________|        |___________|


        """

        constraint = rigid.sibling(type="rdConstraint")

        pair_blend = mod.create_node("pairBlend")
        mod.set_attr(pair_blend["rotInterpolation"], 1)  # Quaternion
        mod.set_attr(pair_blend["isHistoricallyInteresting"], False)

        # Establish initial values, before keyframes
        mod.set_attr(pair_blend["inTranslate1"], transform["translate"])
        mod.set_attr(pair_blend["inRotate1"], transform["rotate"])

        mod.connect(rigid["outputTranslateX"], pair_blend["inTranslateX2"])
        mod.connect(rigid["outputTranslateY"], pair_blend["inTranslateY2"])
        mod.connect(rigid["outputTranslateZ"], pair_blend["inTranslateZ2"])
        mod.connect(rigid["outputRotateX"], pair_blend["inRotateX2"])
        mod.connect(rigid["outputRotateY"], pair_blend["inRotateY2"])
        mod.connect(rigid["outputRotateZ"], pair_blend["inRotateZ2"])

        mod.do_it()

        if auto_key:
            # Generate default animation curves, it's expected since you can no
            # longer see whether channels are keyed or not, now being green.
            time = cmdx.currentTime()
            for curve, src, dst in (("animCurveTL", "tx", "inTranslateX1"),
                                    ("animCurveTL", "ty", "inTranslateY1"),
                                    ("animCurveTL", "tz", "inTranslateZ1"),
                                    ("animCurveTA", "rx", "inRotateX1"),
                                    ("animCurveTA", "ry", "inRotateY1"),
                                    ("animCurveTA", "rz", "inRotateZ1")):
                curve = mod.create_node(curve)
                curve.key(time, transform[src].read())
                mod.connect(curve["output"], pair_blend[dst])

            mod.do_it()

        # Transfer existing animation/connections
        for src, dst in transform.data.get("priorConnections", {}).items():
            dst = pair_blend[dst]
            mod.connect(src, dst)

        commands._connect_transform(mod, pair_blend, transform)

        # Proxy commands below aren't part of the modifier, and thus
        # needs to happen after it's done its thing.
        mod.do_it()

        if not central_blend:
            if not transform.has_attr("simulated"):
                mod.add_attr(transform, cmdx.Boolean(
                    "simulated",
                    keyable=True,
                    default=True)
                )

                commands._record_attr(transform, "simulated")

                mod.do_it()

            mod.connect(transform["simulated"], pair_blend["weight"])

        # Forward some convenience attributes
        transform_proxies = commands.UserAttributes(rigid, transform)
        transform_proxies.add_divider("Ragdoll")
        transform_proxies.add("mass")
        transform_proxies.do_it()

        if constraint:
            constraint_proxies = commands.UserAttributes(
                constraint, transform)

            if central_blend:
                mod.connect(pair_blend["weight"], constraint["visibility"])
                mod.connect(pair_blend["weight"], rigid["visibility"])
            else:
                mod.connect(transform["simulated"],
                            constraint["visibility"])
                mod.connect(transform["simulated"],
                            rigid["visibility"])

            # Forward some convenience attributes
            constraint_proxies.add("angularDriveStiffness",
                                   nice_name="Stiffness")
            constraint_proxies.add("angularDriveDamping",
                                   nice_name="Damping")

            constraint_proxies.do_it()

        rigid.data["pairBlend"] = pair_blend

        return pair_blend

    def _auto_blend(mod, rigids, root):
        pair_blends = []
        for rigid in rigids:
            transform = rigid.parent()
            blend = _add_pairblend(mod, rigid, transform)

            if auto_influence:
                _auto_influence(mod, rigid, blend)

            pair_blends += [blend]

        if central_blend:
            # Blend everything from the root
            if not root.has_attr("simulated"):
                mod.add_attr(root, cmdx.Boolean(
                    "simulated",
                    keyable=True,
                    default=True)
                )

                commands._record_attr(root, "simulated")

                mod.do_it()

            for pair_blend in pair_blends:
                mod.connect(root["simulated"], pair_blend["weight"])

            # Include root rigid in hiding
            mod.connect(root["simulated"], parent_rigid["visibility"])

    def _auto_influence(mod, rigid, blend):
        """Treat incoming animation as guide constraint

         ___________
        |           |              ______________
        o           |             |              |
        |           |             |              |
        | pairBlend o-------------o .driveMatrix |
        |           |             |              |
        o           |             |______________|
        |___________|


        """

        constraint = rigid.sibling(type="rdConstraint")

        # This is fine
        if not constraint:
            return

        # Pair blend directly feeds into the drive matrix
        compose = mod.create_node("composeMatrix", name="animationToMatrix")
        mod.connect(blend["inTranslate1"], compose["inputTranslate"])
        mod.connect(blend["inRotate1"], compose["inputRotate"])

        # A drive is relative the parent frame, but the pairblend is relative
        # the parent Maya transform. In case these are not the same, we'll
        # map the pairblend into the space of the parent frame.
        parent_rigid = constraint["parentRigid"].connection()

        # Could be connected to a scene too
        if parent_rigid.type() != "rdRigid":
            return

        mult = mod.create_node("multMatrix", name="compensateForHierarchy")

        # From this matrix..
        parent_transform_matrix = rigid["inputParentInverseMatrix"].asMatrix()
        parent_transform_matrix = parent_transform_matrix.inverse()

        # To this matrix..
        parent_rigid_matrix = parent_rigid["cachedRestMatrix"].asMatrix()
        parent_rigid_matrix = parent_rigid_matrix.inverse()

        mod.connect(compose["outputMatrix"], mult["matrixIn"][0])
        mult["matrixIn"][1] = parent_transform_matrix
        mult["matrixIn"][2] = parent_rigid_matrix

        # Satisfy the curiosity of anyone browsing the node network
        mult["notes"] = cmdx.String()
        mult["notes"] = (
            "Two of the inputs are coming from initialisation\n"
            "[1] = %(rig)s['inputParentInverseMatrix'].asMatrix().inverse()\n"
            "[2] = %(pari)s['cachedRestMatrix'].asMatrix().inverse()" % dict(
                rig=rigid.name(namespace=False),
                pari=parent_rigid.name(namespace=False),
            )
        )

        mod.connect(mult["matrixSum"], constraint["driveMatrix"])

        # Keep channel box clean
        mod.set_attr(compose["isHistoricallyInteresting"], False)
        mod.set_attr(mult["isHistoricallyInteresting"], False)

        rigid.data["compensateForHierarchy"] = mult

    def _add_multiplier(constraints, name, parent):
        r"""Multiply provided `constraints`

                          _____________
                         |             |
                         o constraint1 |
                        /|_____________|
         ____________  /  _____________
        |            |/  |             |
        | multiplier o---o constraint2 |
        |____________|\  |_____________|
                       \  _____________
                        \|             |
                         o constraint3 |
                         |_____________|


        """

        assert constraints and all(
            con.type() == "rdConstraint" for con in constraints
        )

        # Use existing multiplier, if any, to support branching
        mult = parent.shape("rdConstraintMultiplier")

        if not mult:
            con = parent.shape("rdConstraint")

            if con is not None:
                mult = con["multiplierNode"].connection(
                    type="rdConstraintMultiplier")

        if mult:
            with cmdx.DagModifier() as mod:
                for constraint in constraints:
                    mod.connect(mult["message"], constraint["multiplierNode"])

        else:
            mult = commands.multiply_constraints(constraints, parent=parent)
            mult.rename(commands._unique_name("r%sMultiplier" % name))

            # Forward some convenience attributes
            proxies = commands.UserAttributes(mult, parent)
            proxies.add("driveStrength", nice_name="Strength Multiplier")
            proxies.do_it()

        return mult

    def _auto_world_constraint(rigid, parent):
        transform = rigid.parent()

        if "animatedWorldMult" in parent.data:
            ghost_mult = matrix = parent.data["animatedWorldMult"]
            matrix = ghost_mult["matrixSum"]
        else:
            matrix = parent["inputMatrix"]

        with cmdx.DagModifier() as mod:
            name = commands._unique_name("rWorldConstraint")
            con = mod.create_node("rdConstraint", name=name, parent=transform)

        with cmdx.DGModifier() as mod:
            compensate = rigid.data["compensateForHierarchy"]
            mult = mod.create_node("multMatrix", name="animatedWorldMult")
            mod.connect(compensate["matrixSum"], mult["matrixIn"][0])
            mod.connect(matrix, mult["matrixIn"][1])

            # Make worldspace guide
            mod.connect(rigid["ragdollId"], con["childRigid"])

            mod.set_attr(con["driveEnabled"], True)
            mod.set_attr(con["driveStrength"], 1.0)
            mod.set_attr(con["disableCollision"], False)

            mod.set_attr(con["drawConnection"], False)
            mod.set_attr(con["drawScale"],
                         commands._scale_from_rigid(rigid))

            mod.connect(scene["ragdollId"], con["parentRigid"])
            mod.connect(mult["matrixSum"], con["driveMatrix"])
            mod.set_attr(mult["isHistoricallyInteresting"], False)

            commands.add_constraint(mod, con, scene)

            blend = rigid.data["pairBlend"]

            if central_blend:
                mod.connect(blend["weight"], con["visibility"])
            else:
                mod.connect(transform["simulated"], con["visibility"])

        con["driveStrength"].keyable = True
        con["linearDriveStiffness"].keyable = True
        con["linearDriveDamping"].keyable = True
        con["angularDriveStiffness"].keyable = True
        con["angularDriveDamping"].keyable = True

        # Pass data from parent to child on next iteration
        rigid.data["animatedWorldMult"] = mult

        world_constraints.append(con)

    with cmdx.DagModifier() as mod:
        parent_rigid = parent.shape(type="rdRigid")

        def make_parent_rigid():
            parent_rigid = commands.create_passive_rigid(parent, scene)

            mod.set_attr(parent_rigid["drawShaded"], False)

            # Don't collide per default, it's most likely an
            # unsuitable shape for collisions anyway.
            mod.set_attr(parent_rigid["collide"], False)

            geo = commands.infer_geometry(
                parent, parent=None, children=[children[0]])

            mod.set_attr(parent_rigid["shapeLength"], geo.length)
            mod.set_attr(parent_rigid["shapeRadius"], geo.radius)
            mod.set_attr(parent_rigid["shapeRotation"], geo.shape_rotation)
            mod.set_attr(parent_rigid["shapeOffset"], geo.shape_offset)
            mod.set_attr(parent_rigid["shapeExtents"], geo.extents)

            if use_capsules:
                mod.set_attr(parent_rigid["shapeType"],
                             commands.CapsuleShape)

            return parent_rigid

        if parent_rigid is None:
            parent_rigid = make_parent_rigid()

        previous_rigid = parent_rigid
        for index, child in enumerate(children):
            child_rigid = child.shape(type="rdRigid")

            # Remember existing animation
            child.data["priorConnections"] = {}
            for channel in ("translate", "rotate"):
                for axis in "XYZ":
                    src = child[channel + axis]
                    src = src.connection(plug=True, destination=False)

                    if src is not None:
                        anim = child.data["priorConnections"]
                        dst = "in%s%s1" % (channel.title(), axis)
                        anim[src] = dst

            # Handle overlapping controllers, like branches
            if child_rigid is None:
                child_rigid = commands.create_active_rigid(child, scene)
                mod.set_attr(child_rigid["drawShaded"], False)

            else:
                child_rigid = commands.convert_rigid(child_rigid,
                                                     passive=False)

            # Figure out relationships
            count = len(children)
            previous = children[index - 1] if index > 0 else None
            subsequent = children[index + 1] if index < count - 1 else None

            # Joints are special, the user expects it to face in the
            # direction of its immediate joint child, if any
            if not subsequent and child.type() == "joint":
                subsequent = child.child(type="joint")

            geo = commands.infer_geometry(
                child, parent=previous or root,
                children=[subsequent] if subsequent else False
            )

            mod.set_attr(child_rigid["shapeExtents"], geo.extents)
            mod.set_attr(child_rigid["shapeLength"], geo.length)
            mod.set_attr(child_rigid["shapeRadius"], geo.radius)
            mod.set_attr(child_rigid["shapeRotation"], geo.shape_rotation)
            mod.set_attr(child_rigid["shapeOffset"], geo.shape_offset)

            if geo.length == 0:
                mod.set_attr(child_rigid["shapeType"],
                             commands.SphereShape)
            elif use_capsules:
                mod.set_attr(child_rigid["shapeType"],
                             commands.CapsuleShape)

            # shapeLength is used during constraint creation, for initial size
            mod.do_it()

            con = commands.socket_constraint(
                previous_rigid, child_rigid, scene
            )

            # These are not particularly useful per default
            con["angularLimit"].keyable = False
            con["limitEnabled"].keyable = False
            con["limitStrength"].keyable = False
            con["driveEnabled"].keyable = False

            aim = None
            up = None

            if subsequent:
                aim = subsequent.transform(cmdx.sWorld).translation()

            if previous:
                up = previous.transform(cmdx.sWorld).translation()

            commands.orient(con, aim, up)

            # Let the user manually add these, if needed
            mod.set_attr(con["angularLimitX"], 0)
            mod.set_attr(con["angularLimitY"], 0)
            mod.set_attr(con["angularLimitZ"], 0)
            mod.set_attr(con["driveStrength"], 0.5)

            previous_rigid = child_rigid
            new_rigids += [child_rigid]
            local_constraints += [con]

        if auto_blend:
            with cmdx.DGModifier() as mod:
                _auto_blend(mod, new_rigids, root)

        if auto_multiplier and new_rigids:
            if local_constraints:
                mult = _add_multiplier(local_constraints, "Local", root)

                # Tailor it to what is expected for a Dynamic Control
                # E.g. no translate forces, just rotation for local control
                mult["linearDriveStiffness"].keyable = False
                mult["linearDriveDamping"].keyable = False

    return new_rigids


@commands.with_undo_chunk
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


@commands.with_undo_chunk
def make_muscle(a,
                b,
                scene,
                aim_axis=None,
                up_axis=None,
                flex=0.75,
                radius=1.0):
    """Make a muscle from `a` and `b` anchor points

    Arguments:
        a (transform): Muscle attachment anchor of root
        b (transform): Muscle attachment anchor of tip

    """

    assert a and a.isA(cmdx.kTransform), "%s was not a transform" % a
    assert b and b.isA(cmdx.kTransform), "%s was not a transform" % b
    assert scene and scene.type() == "rdScene", "%s was not an rdScene" % scene

    aim_axis = aim_axis or cmdx.Vector(1, 0, 0)
    up_axis = up_axis or commands.up_axis()

    start = a.transform(cmdx.sWorld).translation()
    end = b.transform(cmdx.sWorld).translation()
    aim = (end - start).normal()
    length = (end - start).length()

    rotation = cmdx.Quat(aim_axis, aim)

    # Optional user-provided markup
    flex = a["flex"].read() if "flex" in a else flex
    radius = a["radius"].read() if "radius" in a else radius

    tm = cmdx.Tm()
    tm.setRotation(rotation)
    tm.setTranslation(start)

    # Move root start towards centre
    tm.translateBy(cmdx.Vector(length * (flex / 2), 0, 0), cmdx.sObject)

    with cmdx.DagModifier() as mod:
        root = mod.createNode("joint", name="root")
        tip = mod.createNode("joint", name="tip", parent=root)

        mod.set_attr(root["radius"], radius)
        mod.set_attr(tip["radius"], radius)

        mod.set_attr(root["translate"], tm.translation())
        mod.set_attr(root["rotate"], tm.rotation())
        mod.set_attr(tip["translateX"], length * (1 - flex))

        mod.do_it()

        muscle = commands.create_rigid(root, scene)

        mod.set_attr(muscle["linearDamping"], 2.0)
        mod.set_attr(muscle["friction"], 0.0)
        mod.set_attr(muscle["restitution"], 0.0)

    a_passive = a.parent().shape(type="rdRigid")
    b_passive = b.parent().shape(type="rdRigid")

    if not a_passive:
        a_passive = commands.create_passive_rigid(a.parent(), scene)

    if not b_passive:
        b_passive = commands.create_passive_rigid(b.parent(), scene)

    con1 = commands.point_constraint(a_passive,
                                     muscle,
                                     scene,
                                     maintain_offset=False)
    con2 = commands.point_constraint(b_passive,
                                     muscle,
                                     scene,
                                     maintain_offset=False)

    # Move tip constraint to tip of muscle
    length = muscle["shapeLength"].read()
    child_frame = cmdx.MatrixType()
    child_frame[3 * 4] = length  # Translate X

    commands._set_matrix(con2["childFrame"], child_frame)

    def parentframe_to_anchorpoints(mod):
        # Move parent frames to anchor points
        for anchor, constraint in ((a, con1), (b, con2)):
            matrix = anchor.transform(cmdx.sWorld).asMatrix()
            parent_matrix = anchor.parent().transform(cmdx.sWorld).asMatrix()
            parent_frame = matrix * parent_matrix.inverse()
            commands._set_matrix(constraint["parentFrame"], parent_frame)

    def add_to_set(mod):
        try:
            collection = cmdx.encode("ragdollMuscles")
        except cmdx.ExistError:
            with cmdx.DGModifier() as mod:
                collection = mod.create_node(
                    "objectSet", name="ragdollMuscles"
                )

        collection.add(root)

    def lock_twist(mod):
        # Lock twist, the muscle should really only rotate around Y and Z
        # First we need to reorient root to aim in the direction of the muscle

        mtm = muscle.transform(cmdx.sWorld).asMatrix()
        atm = a.parent().transform(cmdx.sWorld).asMatrix()
        tm = cmdx.Tm(mtm * atm.inverse())

        pftm = cmdx.Tm(con1["parentFrame"].asMatrix())
        pftm.setRotation(tm.rotation(asQuaternion=True))
        commands._set_matrix(con1["parentFrame"], pftm.asMatrix())
        mod.set_attr(con1["angularLimitX"], cmdx.radians(-1))

    with cmdx.DagModifier() as mod:
        for con in (con1, con2):
            mod.set_attr(con["linearLimit"], 0.01)
            mod.set_attr(con["linearLimitStiffness"], 500)
            mod.set_attr(con["linearLimitDamping"], 10)

        parentframe_to_anchorpoints(mod)
        lock_twist(mod)
        add_to_set(mod)

    return muscle, con1, con2
