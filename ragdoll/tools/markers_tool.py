from .. import commands, internal
from ..vendor import cmdx


@internal.with_undo_chunk
def create_suit(root, scene=None):
    if root.isA(cmdx.kTransform):
        root = root.shape(type="rdRigid")

    assert root and root.type() == "rdRigid", "root was not a rigid"
    root_reference = root.parent()

    scene = scene or commands.create_scene(opts={"defaults": {
        "substeps": 12,
        "positionIterations": 12,
    }})

    def clone(mod, reference, parent=None):
        copy = mod.create_node("transform",
                               name=reference.name(),
                               parent=parent)

        mat = reference["worldMatrix"][0].as_matrix()

        if parent is None:
            parent_inverse_mat = cmdx.Mat4()
        else:
            parent_inverse_mat = parent["worldInverseMatrix"][0].as_matrix()

        local_mat = mat * parent_inverse_mat
        mod.set_attr(copy["offsetParentMatrix"], local_mat)

        return copy

    def make_relative(rigid, transform):
        with cmdx.DGModifier() as mod:
            relative = mod.create_node("multMatrix")
            mod.connect(transform["worldMatrix"][0], relative["matrixIn"][0])

            parent_rigid = rigid["parentRigid"].input(type="rdRigid")
            if parent_rigid is not None:
                parent_transform = parent_rigid.parent()
                mod.connect(
                    parent_transform["worldInverseMatrix"][0],
                    relative["matrixIn"][1]
                )

        return relative

    def reference_rigid(src, dst):
        rigid_attributes = (
            "kinematic",
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
                mod.connect(src[attr], dst[attr])

            mod.connect(src["worldMatrix"][0], dst["inputMatrix"])
            mod.set_keyable(src["kinematic"])

    rigid_to_copy = {}
    copy_to_reference = {}
    new_constraints = []
    new_rigids = []

    def walk(mod, root):
        for plug in root["ragdollId"].outputs(plugs=True, type="rdRigid"):

            # Only look at connections to the parentRigid attribute
            if plug.name() != "parentRigid":
                continue

            child = plug.node()

            if child.type() != "rdRigid":
                # Only look at connected rigids, the rest can go to hell
                continue

            parent = rigid_to_copy.get(root)
            reference = child.parent()

            copy = clone(mod, reference, parent)
            mod.do_it()

            copy_rigid = commands.create_rigid(copy, scene)
            reference_rigid(child, copy_rigid)

            new_rigids.append(copy_rigid)

            parent_rigid = parent.shape(type="rdRigid")
            if parent_rigid is not None:
                con = commands.socket_constraint(parent_rigid, copy_rigid)
                mod.set_attr(con["angularLimit"], (0, 0, 0))

                relative = make_relative(child, reference)
                mod.connect(relative["matrixSum"], con["driveMatrix"])
                mod.connect(parent_rigid["ragdollId"],
                            copy_rigid["parentRigid"])

                new_constraints.append(con)

            rigid_to_copy[child] = copy
            copy_to_reference[copy_rigid] = reference
            walk(mod, child)

    with cmdx.DagModifier() as mod:
        root_copy = clone(mod, root_reference)
        mod.do_it()

        # Create root
        root_copy_rigid = commands.create_rigid(root_copy, scene)
        reference_rigid(root, root_copy_rigid)

        new_rigids.append(root_copy_rigid)
        copy_to_reference[root_copy_rigid] = root_reference
        rigid_to_copy[root] = root_copy

        # Initiating warp, captain
        walk(mod, root)

    with cmdx.DagModifier() as mod:
        mult = root.sibling(type="rdConstraintMultiplier")
        if mult is not None:
            other_mult = commands.multiply_constraints(
                new_constraints, parent=root_copy)

            attrs = (
                "driveStrength",
                "linearDriveStiffness",
                "linearDriveDamping",
                "angularDriveStiffness",
                "angularDriveDamping"
            )

            for attr in attrs:
                mod.connect(mult[attr], other_mult[attr])

    # Add global hard pin
    with cmdx.DagModifier() as mod:
        attr = cmdx.Enum("hardPin", fields=["Inherit", "Off", "On"])

        # Ensure this attribute appears ahead of other attributes
        with cmdx.DGModifier() as mod:
            if "hardPin" in root_reference:
                mod.delete_attr(root_reference["hardPin"])
                mod.do_it()

            mod.add_attr(root_reference, attr)
            mod.do_it()

            index = root["userAttributes"].next_available_index()
            mod.connect(root_reference["hardPin"],
                        root["userAttributes"][index])
            mod.do_it()

        if "globalHardPin" not in root_reference:
            proxies = internal.UserAttributes(root, root_reference)
            proxies.add("kinematic",
                        long_name="globalHardPin",
                        nice_name="Global Hard Pin")
            proxies.do_it()

        with cmdx.DGModifier(interesting=False) as mod:
            for rigid, reference in copy_to_reference.items():
                mod.connect(reference["worldMatrix"][0],
                            rigid["inputMatrix"])

                if rigid != root:
                    if "hardPin" in reference:
                        mod.delete_attr(reference["hardPin"])
                        mod.do_it()

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
                commands._take_ownership(mod, rigid, choice)

    # Hide suit when global hard pin is True
    with cmdx.DGModifier() as mod:
        choice = mod.create_node("choice", "visibilityChoice")
        mod.connect(root_reference["globalHardPin"], choice["selector"])
        mod.set_attr(choice["input"][0], True)
        mod.set_attr(choice["input"][1], False)
        mod.connect(choice["output"], root_copy["visibility"])

    return new_rigids, new_constraints
