"""Support for chains and trees

Animators can either author rigid bodies and constraint these. Or, they could
select a chain of controls and generate a rigid body chain from that. With a
chain, we're better equipt to generate appropriate collision geometry and
can automatically figure out constraints and limits based on order of
selection, locked channels and leverage the angle between controls to
figure out the constraint frames.

- Single
- Chain
- Tree
- Network

"""

from .vendor import cmdx
from . import commands


# Python 2 backwards compatibility
try:
    string_types = basestring,
except NameError:
    string_types = str,


class Chain(object):
    """Create and manipulate a series of connected rigid bodies

    Arguments:
        links (list): Transforms and/or shapes for which to generate a chain
        scene (rdScene): The parent scene of this chain

    """

    def __init__(self, links, scene, options=None, defaults=None):
        assert scene.type() == "rdScene", "%s was not a rdScene" % scene
        assert isinstance(links, (list, tuple)), "links was not a list"
        assert links, "links was empty"

        options = options or {}
        options["centralBlend"] = options.get("centralBlend", True)
        options["autoKey"] = options.get("autoKey", False)
        options["drawShaded"] = options.get("drawShaded", False)
        options["blendMethod"] = options.get("blendMethod",
                                             commands.SteppedBlendMethod)
        options["computeMass"] = options.get("computeMass", False)
        options["shapeType"] = options.get("shapeType", commands.CapsuleShape)
        options["limited"] = options.get("limited", False)
        options["addUserAttributes"] = options.get("addUserAttributes", True)
        options["autoInfluence"] = (
            options.get("autoInfluence", False) and
            options.get("autoBlend", False)
        )

        self._new_rigids = []
        self._new_constraints = []
        self._new_userattrs = []

        self._defaults = defaults or {}
        self._cache = {}
        self._root = links[0]
        self._children = links[1:]
        self._scene = scene
        self._opts = options

        # Separate input into transforms and (optional) shapes
        self._pairs = []

        for link in links:
            if isinstance(link, string_types):
                link = cmdx.encode(link)

            assert isinstance(link, cmdx.DagNode), type(link)
            assert not link.shape(type="rdRigid"), (
                "%s already has a rigid" % link
            )

            if link.isA(cmdx.kShape):
                transform = link.parent()
                shape = link

            else:
                # Supported shapes, in order of preference
                transform = link
                shape = link.shape(type=("mesh",
                                         "nurbsCurve",
                                         "nurbsSurface"))

            # For now, we can't allow custom pivots
            with cmdx.DagModifier() as mod:
                commands._remove_pivots(mod, transform)

            self._pairs.append((transform, shape))

    def pre_flight(self):
        """Before doing anything, make sure the basics are accounted for"""

        def check_already_chain():
            """In case a user runs the command twice on the same input"""
            all_are_already_rigids = True
            for transform, _ in self._pairs:
                if not transform.shape(type="rdRigid"):
                    all_are_already_rigids = False
                    break

            assert not all_are_already_rigids, (
                "Every transform is already dynamic"
            )

        def check_hierarchy():
            """Ensure incoming chain reflects a physical hierarchy

            For example, this is what a valid selection looks like,
            including a non-selected offset group that is still part
            of the hierarchy.

            o- clavicle
             |-o upperArm
               |-o lowerArm
                 |-o ( offsetGroup )
                   |-o hand

            """

            pairs = self._pairs[:]
            while pairs:
                transform, _ = pairs.pop()
                expected_parent, _ = pairs[-1] if pairs else (None, None)

                if not expected_parent:
                    break

                # Walk up the hierarchy until you find what
                # is supposed to be the parent.
                found = False
                for parent in transform.lineage():
                    if parent == expected_parent:
                        found = True
                        break

                assert found, (
                    "%s was not a parent of %s" % (
                        expected_parent, transform)
                )

        def pre_cache():
            """Pre-cache attributes to avoid needless evaluation"""
            for transform, _ in self._pairs:
                matrix = transform["worldMatrix"][0].asMatrix()
                translate = transform["translate"].as_vector()
                rotate = transform["rotate"].as_euler()

                self._cache[(transform, "worldMatrix")] = matrix
                self._cache[(transform, "translate")] = translate
                self._cache[(transform, "rotate")] = rotate

        def remember_existing_inputs():
            # Remember existing animation
            for transform, _ in self._pairs:
                transform.data["priorConnections"] = {}
                for channel in ("translate", "rotate"):
                    for axis in "XYZ":
                        src = transform[channel + axis]
                        src = src.connection(plug=True, destination=False)

                        if src is not None:
                            anim = transform.data["priorConnections"]
                            dst = "in%s%s1" % (channel.title(), axis)
                            anim[src] = dst

        check_already_chain()
        check_hierarchy()
        remember_existing_inputs()
        pre_cache()

    def do_it(self):
        self.pre_flight()
        self._do_all()
        return self._new_rigids[:]

    def _do_all(self):
        root_transform, root_shape = self._pairs[0]
        root_rigid = root_transform.shape(type="rdRigid")
        root_rigid = root_rigid

        # Root
        with cmdx.DagModifier() as mod:
            if not root_rigid:

                # Add divider to new root
                transform_attrs = commands.UserAttributes(None, root_transform)
                transform_attrs.add_divider("Ragdoll")
                self._new_userattrs += [transform_attrs]

                root_rigid = self.make_rigid(
                    mod, root_transform, root_shape, passive=True
                )

                for key, value in self._defaults.items():
                    mod.set_attr(root_rigid[key], value)

        # Links
        with cmdx.DagModifier() as mod:
            previous_rigid = root_rigid
            for transform, shape in self._pairs[1:]:
                previous_rigid = self._do_one(mod,
                                              transform,
                                              shape,
                                              previous_rigid)

        # Optionals
        with cmdx.DGModifier() as dgmod:
            # Blend everything from the root
            if self._opts["centralBlend"]:
                self._make_simulated_attr(dgmod, self._root)

            if self._opts["autoBlend"]:
                self._auto_blend(dgmod)

            if self._opts["autoMultiplier"]:
                self._auto_multiplier(dgmod)

        if self._opts["addUserAttributes"]:
            for userattr in self._new_userattrs:
                userattr.do_it()

    def _do_one(self, mod, transform, shape, previous_rigid):
        assert transform and transform.isA(cmdx.kTransform), transform
        assert shape is None or shape.isA(cmdx.kShape), shape
        assert previous_rigid and previous_rigid.type() == "rdRigid"

        rigid = transform.shape(type="rdRigid")

        # Handle branching
        #
        #  o
        #   \          o
        #    \        /
        #     o------o
        #     |       \
        #     |        o---o
        #     o
        #
        if rigid is not None:
            rigid = commands.convert_rigid(rigid, passive=False)

        else:
            rigid = self.make_rigid(mod, transform, shape)

            # Add header to newly created rigid
            transform_attrs = commands.UserAttributes(None, transform)
            transform_attrs.add_divider("Ragdoll")
            self._new_userattrs += [transform_attrs]

        # Figure out hierarchy
        #
        #               |
        #               v
        #     o---------o---------o
        # previous            subsequent
        #
        #
        index = self._children.index(transform)
        count = len(self._children)
        previous = self._children[index - 1] if index > 0 else self._root
        subsequent = self._children[index + 1] if index < count - 1 else None

        # Joints are special.
        #
        # The user expects it to face in the direction
        # of its immediate joint transform, if any, even
        # if the actual axis is all messed up.
        #
        # o     o<>----o
        #  \   /
        #   \ /
        #    o
        #
        if not subsequent and transform.type() == "joint":
            subsequent = transform.child(type="joint")

        geo = commands.infer_geometry(
            transform,
            parent=previous or self._root,
            children=[subsequent] if subsequent else False
        )

        mod.set_attr(rigid["shapeExtents"], geo.extents)
        mod.set_attr(rigid["shapeLength"], geo.length)
        mod.set_attr(rigid["shapeRadius"], geo.radius)
        mod.set_attr(rigid["shapeRotation"], geo.shape_rotation)
        mod.set_attr(rigid["shapeOffset"], geo.shape_offset)

        shape_type = self._opts["shapeType"]

        if geo.length == 0:
            shape_type = commands.SphereShape

        mod.set_attr(rigid["shapeType"], shape_type)

        # `shapeLength` is used during constraint creation,
        # to figure out draw scale
        mod.do_it()

        con = commands.socket_constraint(
            previous_rigid, rigid, self._scene
        )

        # These are not particularly useful per default
        mod.set_keyable(con["limitStrength"], False)
        mod.set_keyable(con["driveEnabled"], False)
        mod.set_keyable(con["limitEnabled"], False)
        mod.set_keyable(con["angularLimit"], self._opts["limited"])

        if self._opts["limited"]:
            fourtyfive = cmdx.radians(45)
            mod.set_attr(con["angularLimitX"], fourtyfive)
            mod.set_attr(con["angularLimitY"], fourtyfive)
            mod.set_attr(con["angularLimitZ"], fourtyfive)

        aim = None
        up = None

        if subsequent:
            aim = subsequent.translation(cmdx.sWorld)

        if previous:
            up = previous.translation(cmdx.sWorld)

        commands.orient(con, aim, up)

        # Let the user manually add these, if needed
        mod.set_attr(con["angularLimitX"], 0)
        mod.set_attr(con["angularLimitY"], 0)
        mod.set_attr(con["angularLimitZ"], 0)
        mod.set_attr(con["driveStrength"], 0.5)

        # Record hierarchical relationship, for articulations
        mod.connect(previous_rigid["ragdollId"], rigid["parentRigid"])

        for key, value in self._defaults.items():
            mod.set_attr(rigid[key], value)

        # Forward some convenience attributes
        constraint_attrs = commands.UserAttributes(con, transform)
        constraint_attrs.add("angularDriveStiffness", nice_name="Stiffness")
        constraint_attrs.add("angularDriveDamping", nice_name="Damping")

        self._new_rigids += [rigid]
        self._new_constraints += [con]
        self._new_userattrs += [constraint_attrs]

        return rigid

    def _make_simulated_attr(self, dgmod, transform):
        if transform.has_attr("simulated"):
            return

        if self._opts["blendMethod"] == commands.SmoothBlendMethod:
            dgmod.add_attr(transform, cmdx.Double(
                "simulated",
                min=0.0,
                max=1.0,
                keyable=True,
                default=True)
            )
        else:
            dgmod.add_attr(transform, cmdx.Boolean(
                "simulated",
                keyable=True,
                default=True)
            )

        dgmod.add_attr(transform, cmdx.Boolean(
            "notSimulated", keyable=False)
        )

        commands._record_attr(transform, "simulated")
        commands._record_attr(transform, "notSimulated")

        dgmod.do_it()

        reverse = dgmod.create_node("reverse")
        dgmod.set_attr(reverse["isHistoricallyInteresting"], False)
        dgmod.connect(transform["simulated"], reverse["inputX"])
        dgmod.connect(reverse["outputX"], transform["notSimulated"])

    def _add_pairblend(self, dgmod, rigid, transform):
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

        assert isinstance(dgmod, cmdx.DGModifier)

        pair_blend = dgmod.create_node("pairBlend")
        dgmod.set_attr(pair_blend["rotInterpolation"], 1)  # Quaternion
        dgmod.set_attr(pair_blend["isHistoricallyInteresting"], False)

        # Establish initial values, before keyframes
        translate = self._cache[(transform, "translate")]
        rotate = self._cache[(transform, "rotate")]
        dgmod.set_attr(pair_blend["inTranslate1"], translate)
        dgmod.set_attr(pair_blend["inRotate1"], rotate)

        dgmod.connect(rigid["outputTranslateX"], pair_blend["inTranslateX2"])
        dgmod.connect(rigid["outputTranslateY"], pair_blend["inTranslateY2"])
        dgmod.connect(rigid["outputTranslateZ"], pair_blend["inTranslateZ2"])
        dgmod.connect(rigid["outputRotateX"], pair_blend["inRotateX2"])
        dgmod.connect(rigid["outputRotateY"], pair_blend["inRotateY2"])
        dgmod.connect(rigid["outputRotateZ"], pair_blend["inRotateZ2"])
        dgmod.connect(rigid["drivenBySimulation"], pair_blend["weight"])

        if self._opts["autoKey"]:
            # Generate default animation curves, it's expected since you can no
            # longer see whether channels are keyed or not, now being green.
            time = cmdx.currentTime()
            mapping = (
                ("animCurveTL", translate.x, "inTranslateX1"),
                ("animCurveTL", translate.y, "inTranslateY1"),
                ("animCurveTL", translate.z, "inTranslateZ1"),
                ("animCurveTA", rotate.x, "inRotateX1"),
                ("animCurveTA", rotate.y, "inRotateY1"),
                ("animCurveTA", rotate.z, "inRotateZ1")
            )

            for curve, value, dst in mapping:
                curve = dgmod.create_node(curve)
                curve.key(time, value)
                dgmod.connect(curve["output"], pair_blend[dst])

        # Transfer existing animation/connections
        for src, dst in transform.data.get("priorConnections", {}).items():
            dst = pair_blend[dst]
            dgmod.connect(src, dst)

        commands._connect_transform(dgmod, pair_blend, transform)

        if not self._opts["centralBlend"]:
            self._make_simulated_attr(dgmod, transform)
            dgmod.connect(transform["notSimulated"], rigid["kinematic"])

        # Forward some convenience attributes
        transform_attrs = commands.UserAttributes(rigid, transform)
        transform_attrs.add("mass")

        self._new_userattrs.append(transform_attrs)

        return pair_blend

    def _auto_blend(self, dgmod):
        """Add a `Simulated` attribute to new links

        """

        assert isinstance(dgmod, cmdx.DGModifier)

        # Find top-level root for blend attribute
        # It'll be the one with a multiplier node, if one exists
        mult = self._root.shape("rdConstraintMultiplier")

        if not mult:
            con = self._root.shape("rdConstraint")

            if con is not None:
                mult = con["multiplierNode"].connection(
                    type="rdConstraintMultiplier")

        if mult and "simulated" in mult.parent():
            self._root = mult.parent()

        for rigid in self._new_rigids:
            transform = rigid.parent()
            blend = self._add_pairblend(dgmod, rigid, transform)

            if self._opts["autoInfluence"]:
                self._auto_influence(dgmod, rigid, blend)

            if self._opts["centralBlend"]:
                dgmod.connect(self._root["notSimulated"], rigid["kinematic"])

    def _auto_influence(self, mod, rigid, blend):
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

        # This is fine (but what does it mean? :O )
        if not constraint:
            return

        # Pair blend directly feeds into the drive matrix
        compose = mod.create_node("composeMatrix", name="animationToMatrix")
        mod.connect(blend["inTranslate1"], compose["inputTranslate"])
        mod.connect(blend["inRotate1"], compose["inputRotate"])

        make_worldspace = mod.create_node("multMatrix", name="makeWorldspace")
        mod.connect(compose["outputMatrix"], make_worldspace["matrixIn"][0])

        # Reproduce a parent hierarchy, but don't connect it to avoid cycle
        mod.set_attr(make_worldspace["matrixIn"][1],
                     rigid.parent()["parentMatrix"][0].asMatrix())

        mod.connect(make_worldspace["matrixSum"], rigid["inputMatrix"])

        # Satisfy the curiosity of anyone browsing the node network
        make_worldspace["notes"] = cmdx.String()
        make_worldspace["notes"] = (
            "matrixIn[1] is the original parentMatrix "
            "of the rigid parent transform."
        )

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

        # Satisfy the curiosity of anyone browsing the node network
        compensate["notes"] = cmdx.String()
        compensate["notes"] = (
            "Two of the inputs are coming from initialisation\n"
            "[1] = %(rig)s['inputParentInverseMatrix'].asMatrix().inverse()\n"
            "[2] = %(pari)s['cachedRestMatrix'].asMatrix().inverse()" % dict(
                rig=rigid.name(namespace=False),
                pari=parent_rigid.name(namespace=False),
            )
        )

        mod.connect(compensate["matrixSum"], constraint["driveMatrix"])

        # Keep channel box clean
        mod.set_attr(compose["isHistoricallyInteresting"], False)
        mod.set_attr(compensate["isHistoricallyInteresting"], False)
        mod.set_attr(make_worldspace["isHistoricallyInteresting"], False)

        rigid.data["compensateForHierarchy"] = compensate

    def _auto_multiplier(self, dgmod):
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

        assert self._new_constraints and all(
            con.type() == "rdConstraint" for con in self._new_constraints
        )

        # Use existing multiplier, if any, to support branching
        mult = self._root.shape("rdConstraintMultiplier")

        if not mult:
            con = self._root.shape("rdConstraint")

            if con is not None:
                mult = con["multiplierNode"].connection(
                    type="rdConstraintMultiplier")

        if mult:
            for constraint in self._new_constraints:
                dgmod.connect(mult["message"], constraint["multiplierNode"])

        else:
            # There isn't any, let's make one
            mult = commands.multiply_constraints(self._new_constraints,
                                                 parent=self._root)
            mult.rename(commands._unique_name("rLocalMultiplier"))

            # Forward some convenience attributes
            multiplier_attrs = commands.UserAttributes(mult, self._root)
            multiplier_attrs.add("driveStrength",
                                 nice_name="Strength Multiplier")
            self._new_userattrs += [multiplier_attrs]

        return mult

    def make_rigid(self, mod, transform, shape, passive=False):
        rigid = commands._rdrigid(mod, "rRigid", parent=transform)

        # Copy current transformation
        rest = self._cache[(transform, "worldMatrix")]

        mod.set_attr(rigid["cachedRestMatrix"], rest)
        mod.set_attr(rigid["inputMatrix"], rest)

        commands.add_rigid(mod, rigid, self._scene)

        if shape:
            commands._interpret_shape(mod, rigid, shape)
        else:
            commands._interpret_transform(mod, rigid, transform)

        if passive:
            commands._connect_passive(mod, transform, rigid)
        else:
            commands._connect_active(mod, transform, rigid)

        if self._opts["computeMass"]:
            # Establish a sensible default mass, also taking into
            # consideration that joints must be comparable to meshes.
            # Mass unit is kg, whereas lengths are in centimeters
            extents = rigid["extents"].as_vector()
            mod.set_attr(rigid["mass"], max(0.01, (
                extents.x *
                extents.y *
                extents.z *
                0.01
            )))

        self._new_rigids.append(rigid)
        return rigid
