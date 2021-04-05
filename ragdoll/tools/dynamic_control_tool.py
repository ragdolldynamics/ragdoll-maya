from ..vendor import cmdx
from .. import commands, lib


@lib.with_undo_chunk
def create(chain,
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
    new_rigids = []
    cache = {}

    root, children = chain[0], chain[1:]

    parent = root

    # Pre-cache to avoid needless evaluation
    for link in chain:
        cache[(link, "worldMatrix")] = link["worldMatrix"][0].asMatrix()

    def _make_simulated_attr(dgmod, transform):
        if transform.has_attr("simulated"):
            return

        dgmod.add_attr(transform, cmdx.Boolean(
            "simulated",
            keyable=True,
            default=True)
        )
        dgmod.add_attr(transform, cmdx.Boolean(
            "notSimulated", keyable=False)
        )

        dgmod.do_it()

        reverse = dgmod.create_node("reverse")
        dgmod.set_attr(reverse["isHistoricallyInteresting"], False)
        dgmod.connect(transform["simulated"], reverse["inputX"])
        dgmod.connect(reverse["outputX"], transform["notSimulated"])

    def _add_pairblend(dgmod, rigid, transform):
        """Put a pairBlend between `rigid` and `transform`

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

        pair_blend = dgmod.create_node("pairBlend")
        dgmod.set_attr(pair_blend["rotInterpolation"], 1)  # Quaternion
        dgmod.set_attr(pair_blend["isHistoricallyInteresting"], False)

        # Establish initial values, before keyframes
        dgmod.set_attr(pair_blend["inTranslate1"], transform["translate"])
        dgmod.set_attr(pair_blend["inRotate1"], transform["rotate"])

        dgmod.connect(rigid["outputTranslateX"], pair_blend["inTranslateX2"])
        dgmod.connect(rigid["outputTranslateY"], pair_blend["inTranslateY2"])
        dgmod.connect(rigid["outputTranslateZ"], pair_blend["inTranslateZ2"])
        dgmod.connect(rigid["outputRotateX"], pair_blend["inRotateX2"])
        dgmod.connect(rigid["outputRotateY"], pair_blend["inRotateY2"])
        dgmod.connect(rigid["outputRotateZ"], pair_blend["inRotateZ2"])
        dgmod.connect(rigid["drivenBySimulation"], pair_blend["weight"])

        dgmod.do_it()

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
                curve = dgmod.create_node(curve)
                curve.key(time, transform[src].read())
                dgmod.connect(curve["output"], pair_blend[dst])

            dgmod.do_it()

        # Transfer existing animation/connections
        for src, dst in transform.data.get("priorConnections", {}).items():
            dst = pair_blend[dst]
            dgmod.connect(src, dst)

        commands._connect_transform(dgmod, pair_blend, transform)

        # Proxy commands below aren't part of the modifier, and thus
        # needs to happen after it's done its thing.
        dgmod.do_it()

        if not central_blend:
            _make_simulated_attr(dgmod, transform)
            dgmod.connect(transform["notSimulated"], rigid["kinematic"])

        # Forward some convenience attributes
        transform_proxies = lib.UserAttributes(rigid, transform)
        transform_proxies.add_divider("Ragdoll")
        transform_proxies.add("mass")
        transform_proxies.do_it()

        if constraint:
            constraint_proxies = lib.UserAttributes(
                constraint, transform)

            # Forward some convenience attributes
            constraint_proxies.add("angularDriveStiffness",
                                   nice_name="Stiffness")
            constraint_proxies.add("angularDriveDamping",
                                   nice_name="Damping")

            constraint_proxies.do_it()

        rigid.data["pairBlend"] = pair_blend

        return pair_blend

    def _auto_blend(dgmod, rigids, root):
        # Find top-level root for blend attribute
        # It'll be the one with a multiplier node, if one exists
        mult = root.shape("rdConstraintMultiplier")

        if not mult:
            con = root.shape("rdConstraint")

            if con is not None:
                mult = con["multiplierNode"].connection(
                    type="rdConstraintMultiplier")

        if mult and "simulated" in mult.parent():
            root = mult.parent()

        if central_blend:
            # Blend everything from the parent
            _make_simulated_attr(dgmod, root)

        for rigid in rigids:
            transform = rigid.parent()
            blend = _add_pairblend(dgmod, rigid, transform)

            if auto_influence:
                _auto_influence(dgmod, rigid, blend)

            if central_blend:
                dgmod.connect(root["notSimulated"], rigid["kinematic"])

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

        make_worldspace = mod.create_node("multMatrix", name="makeAbsolute")
        mod.connect(compose["outputMatrix"], make_worldspace["matrixIn"][0])

        # Reproduce a parent hierarchy, but don't connect it to avoid cycle
        mod.set_attr(make_worldspace["matrixIn"][1],
                     rigid.parent()["parentMatrix"][0].asMatrix())

        mod.connect(make_worldspace["matrixSum"], rigid["inputMatrix"])

        # A drive is relative the parent frame, but the pairblend is relative
        # the parent Maya transform. In case these are not the same, we'll
        # map the pairblend into the space of the parent frame.
        parent_rigid = constraint["parentRigid"].connection()

        # Could be connected to a scene too
        if parent_rigid.type() != "rdRigid":
            return

        compensate = mod.create_node("multMatrix",
                                     name="compensateForHierarchy")

        # From this matrix..
        parent_transform_matrix = rigid["inputParentInverseMatrix"].asMatrix()
        parent_transform_matrix = parent_transform_matrix.inverse()

        # To this matrix..
        parent_rigid_matrix = parent_rigid["cachedRestMatrix"].asMatrix()
        parent_rigid_matrix = parent_rigid_matrix.inverse()

        mod.connect(compose["outputMatrix"], compensate["matrixIn"][0])
        compensate["matrixIn"][1] = parent_transform_matrix
        compensate["matrixIn"][2] = parent_rigid_matrix

        mod.connect(compensate["matrixSum"], constraint["driveMatrix"])

        # Keep channel box clean
        mod.set_attr(compose["isHistoricallyInteresting"], False)
        mod.set_attr(compensate["isHistoricallyInteresting"], False)
        mod.set_attr(make_worldspace["isHistoricallyInteresting"], False)

        rigid.data["compensateForHierarchy"] = compensate

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
            proxies = lib.UserAttributes(mult, parent)
            proxies.add("driveStrength", nice_name="Strength Multiplier")
            proxies.do_it()

        return mult

    with cmdx.DagModifier() as mod:
        parent_rigid = parent.shape(type="rdRigid")

        def make_parent_rigid():
            parent_rigid = commands.create_rigid(parent, scene,
                                                 passive=True,
                                                 _cache=cache)

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
                child_rigid = commands.create_rigid(child, scene,
                                                    _cache=cache)
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

            aim = None
            up = None

            if subsequent:
                aim = subsequent.transform(cmdx.sWorld).translation()

            if previous:
                up = previous.transform(cmdx.sWorld).translation()

            commands.orient(con, aim, up)

            # Let the user manually add these, if needed
            mod.set_attr(con["disableCollision"], True)
            mod.set_attr(con["angularLimitX"], 0)
            mod.set_attr(con["angularLimitY"], 0)
            mod.set_attr(con["angularLimitZ"], 0)
            mod.set_attr(con["driveStrength"], 0.5)

            previous_rigid = child_rigid
            new_rigids += [child_rigid]
            local_constraints += [con]

        if auto_blend:
            with cmdx.DGModifier() as dgmod:
                _auto_blend(dgmod, new_rigids, root)

        if auto_multiplier and new_rigids:
            if local_constraints:
                mult = _add_multiplier(local_constraints, "Local", root)

                # Tailor it to what is expected for a Dynamic Control
                # E.g. no translate forces, just rotation for local control
                mult["linearDriveStiffness"].keyable = False
                mult["linearDriveDamping"].keyable = False

    return new_rigids
