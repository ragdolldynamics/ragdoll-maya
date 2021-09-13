from .. import commands, internal, constants
from ..vendor import cmdx
from maya import cmds

InputInherit = 0
InputOff = 1
InputKinematic = 2
InputGuide = 3


def assign(transforms, solver):
    assert len(transforms) > 0, "Nothing to assign to"

    time1 = cmdx.encode("time1")
    objset = cmdx.find("rMarkers")
    parent_marker = transforms[0]["worldMatrix"][0].output(type="rdMarker")

    if not objset:
        with cmdx.DGModifier() as mod:
            objset = mod.create_node("objectSet", name="rMarkers")

    suit = None
    if parent_marker:
        suit = parent_marker["startState"].output(type="rdSuit")

        # Already got a marker
        transforms.pop(0)

    if not suit:
        with cmdx.DagModifier() as mod:
            suit_parent = mod.create_node("transform", name="rSuit")
            suit = mod.create_node("rdSuit",
                                   name="rSuitShape",
                                   parent=suit_parent)

            index = solver["inputSuitStart"].next_available_index()
            mod.set_attr(suit["version"], internal.version())
            mod.connect(suit["currentState"], solver["inputSuit"][index])
            mod.connect(suit["startState"], solver["inputSuitStart"][index])
            mod.connect(solver["startTime"], suit["startTime"])
            mod.connect(time1["outTime"], suit["currentTime"])
            mod.connect(suit_parent["message"], suit["exclusiveNodes"][0])

    with cmdx.DGModifier() as dgmod:
        for index, transform in enumerate(transforms):
            name = "rMarker_%s" % transform.name()
            marker = dgmod.create_node("rdMarker", name=name)

            try:
                children = [transforms[index + 1]]
            except IndexError:
                children = None

            if parent_marker:
                parent_transform = parent_marker["inputMatrix"].input()
                dgmod.set_attr(marker["captureTranslation"], False)
            else:
                parent_transform = None

            dgmod.set_attr(marker["inputType"], InputGuide)

            # It's a limb
            if parent_marker or len(transforms) > 1:
                geo = commands.infer_geometry(transform,
                                              parent_transform,
                                              children)
                geo.shape_type = constants.CapsuleShape

            # It's a lone object
            else:
                dgmod.set_attr(marker["inputType"], InputKinematic)

                shape = transform.shape(type=("mesh",
                                              "nurbsCurve",
                                              "nurbsSurface"))
                if shape:
                    geo = commands._interpret_shape2(shape)
                else:
                    geo = commands.infer_geometry(transform)
                    geo.shape_type = constants.CapsuleShape

            # Make the root passive
            if len(transforms) > 1 and not parent_marker:
                dgmod.set_attr(marker["inputType"], InputKinematic)

            dgmod.set_attr(marker["limitType"], 0)

            dgmod.set_attr(marker["shapeType"], geo.shape_type)
            dgmod.set_attr(marker["shapeExtents"], geo.extents)
            dgmod.set_attr(marker["shapeLength"], geo.length)
            dgmod.set_attr(marker["shapeRadius"], geo.radius)
            dgmod.set_attr(marker["shapeRotation"], geo.shape_rotation)
            dgmod.set_attr(marker["shapeOffset"], geo.shape_offset)

            # Assign some random color, within some nice range
            dgmod.set_attr(marker["color"], internal.random_color())
            dgmod.set_attr(marker["version"], internal.version())

            dgmod.connect(transform["message"], marker["src"])
            dgmod.connect(transform["message"], marker["dst"][0])
            dgmod.connect(transform["worldMatrix"][0], marker["inputMatrix"])
            dgmod.connect(time1["outTime"], marker["currentTime"])
            dgmod.connect(suit["startTime"], marker["startTime"])

            index = suit["inputMarker"].next_available_index()
            dgmod.connect(marker["currentState"], suit["inputMarker"][index])
            dgmod.connect(marker["startState"],
                          suit["inputMarkerStart"][index])

            if parent_marker is not None:
                dgmod.connect(parent_marker["ragdollId"],
                              marker["parentMarker"])

            parent_marker = marker

            index = objset["dnSetMembers"].next_available_index()
            dgmod.connect(marker["message"], objset["dnSetMembers"][index])

            # Keep next_available_index() up-to-date
            dgmod.do_it()


def capture(solver,
            transforms=None,
            start_time=None,
            end_time=None):
    start_time = start_time or solver["startTime"].as_time()
    end_time = end_time or cmdx.animation_end_time()
    transforms = {t: True for t in transforms} if transforms else {}

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    start_frame = int(start_time.value)
    end_frame = int(end_time.value)

    # Allocate data
    suits = [el.input() for el in solver["inputSuitStart"]]

    markers = []
    for suit in suits:
        markers.extend([el.input() for el in suit["inputMarkerStart"]])

    markers = {m.shortest_path(): m for m in markers}
    cache = {marker: {} for marker in markers}
    anim = {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}

    def simulate():
        total = end_frame - start_frame
        for frame in range(start_frame, end_frame):
            with cmdx.Context(frame, cmdx.TimeUiUnit()):
                solver["output"].read()

                for key, marker in markers.items():
                    # Find difference between parent of rigid
                    # and parent of destination control.
                    #
                    # It's possible, and quite likely, that the parent
                    # of a control is different from the parent rigid.
                    # For example, in a double-jointed elbow, there may
                    # be 1 control for both joints which but 2 rigids.
                    #
                    # Or, a tail may have 10 segments, only 4 of which
                    # were given markers. In that case, an uneven amount
                    # of rigids have parents that differ from their
                    # destination kinematic parents.
                    #  _
                    # |o|-------o kinematic parent
                    #    .       \
                    #      ` .    \
                    # simulated.   \
                    # parent     `..o kinematic child
                    #               .\
                    #                .\
                    #       simulated .\
                    #       child      .o
                    #
                    # spm = Simulated Parent Matrix
                    # kpm = Kinematic Parent Matrix
                    #
                    spm = cmdx.Mat4()
                    kpm = cmdx.Mat4()

                    kpt = marker["dst"][0].input().parent()
                    spt = marker["parentMarker"].input()

                    if kpt:
                        kpm = kpt["worldMatrix"][0].as_matrix()

                    if spt:
                        spt = spt["dst"][0].input()
                        spm = spt["worldMatrix"][0].as_matrix()

                    cache[key][frame] = {
                        "captureTranslation": marker["catr"].read(),
                        "captureRotation": marker["caro"].read(),
                        "outputMatrix": marker["ouma"].as_matrix(),
                        "offsetMatrix": kpm * spm.inverse(),
                    }

                    if marker["inputType"] == InputKinematic:
                        cache[key][frame]["captureTranslation"] = False
                        cache[key][frame]["captureRotation"] = False

                percentage = 100 * float(frame - start_frame) / total
                yield ("simulating", percentage)

    def reformat():
        total = len(cache)
        current = 0
        for marker, frames in cache.items():
            marker = markers[marker]
            dst = marker["dst"][0].input()

            # No destination transforms here, carry on
            if dst is None:
                continue

            parent_marker = marker["parentMarker"].input()
            parent_marker = (
                parent_marker.shortest_path()
                if parent_marker else None
            )

            for frame, data in frames.items():

                # Nothing to do.
                if not any([data["captureTranslation"],
                            data["captureRotation"]]):
                    continue

                offset_mtx = data["offsetMatrix"]
                output_mtx = data["outputMatrix"]
                spm = cmdx.Mat4()

                if parent_marker in cache:
                    spm = cache[parent_marker][frame]["outputMatrix"]

                local_matrix = output_mtx * (offset_mtx * spm).inverse()

                tm = cmdx.Tm(local_matrix)
                t = tm.translation()

                # Account for rotation offsets
                try:
                    rotate_axis = dst["rotateAxis"].as_quaternion()
                except cmdx.ExistError:
                    rotate_axis = cmdx.Quaternion()

                try:
                    joint_orient = dst["jointOrient"].as_quaternion()
                except cmdx.ExistError:
                    joint_orient = cmdx.Quaternion()

                # Rotate Axis is an added rotation post-transform
                # Joint Orient is an added rotation pre-transform
                quat = (
                    cmdx.Quaternion(rotate_axis.inverse()) *
                    tm.rotation(asQuaternion=True) *
                    cmdx.Quaternion(joint_orient.inverse())
                )

                rotate_order = dst["rotateOrder"].read()
                rotate_order = cmdx.Euler.enumToOrder[rotate_order]
                euler = cmdx.Euler.decompose(quat.as_matrix(), rotate_order)

                if data["captureTranslation"]:
                    anim[marker]["tx"][frame] = t.x
                    anim[marker]["ty"][frame] = t.y
                    anim[marker]["tz"][frame] = t.z

                if data["captureRotation"]:
                    anim[marker]["rx"][frame] = euler.x
                    anim[marker]["ry"][frame] = euler.y
                    anim[marker]["rz"][frame] = euler.z

            current += 1
            yield ("reformatting", 100 * float(current) / total)

    def transfer():
        total = len(anim)
        current = 0
        with cmdx.DagModifier() as mod:
            for marker, channels in anim.items():
                node = markers[marker]
                transform = node["dst"][0].input()

                if transforms and transform not in transforms:
                    continue

                for channel, values in channels.items():
                    if not values:
                        continue

                    mod.set_attr(transform[channel], values)
                    mod.do_it()

                curve = node["inputType"].input(type="animCurveTU")

                if curve is not None:
                    mod.delete(curve)
                    mod.do_it()

                if not node["inputType"].connected:
                    mod.set_attr(node["inputType"], InputKinematic)

                current += 1
                yield ("transferring", 100 * float(current) / total)

    @internal.with_undo_chunk
    def unroll():
        rotate_channels = []
        channels = ("rx", "ry", "rz")

        def is_keyed(plug):
            return plug.input(type="animCurveTA") is not None

        for marker, channels in anim.items():
            marker = markers[marker]
            dst = marker["dst"][0].input()

            # No destination transforms here, carry on
            if dst is None:
                continue

            # Can only unroll transforms with all axes keyed
            if all(is_keyed(dst[ch]) for ch in channels):

                # Should only unrol any that was actually
                # part of our simulation output.
                if any(anim[marker][channel] for channel in channels):
                    rotate_channels += ["%s.rx" % dst]
                    rotate_channels += ["%s.ry" % dst]
                    rotate_channels += ["%s.rz" % dst]

        cmds.rotationInterpolation(rotate_channels, c="quaternionSlerp")
        cmds.rotationInterpolation(rotate_channels, c="none")

    for status in simulate():
        yield (status[0], status[1] * 0.85)

    for status in reformat():
        yield (status[0], 85 + status[1] * 0.05)

    for status in transfer():
        yield (status[0], 90 + status[1] * 0.10)

    unroll()


@internal.with_undo_chunk
def create_constraint(parent, child, opts=None):
    assert child.type() in ("rdMarker",), child.type()
    assert parent.type() in ("rdMarker", "rdSuit"), (
        "%s must be a rigid or suit" % parent.type()
    )

    opts = dict({
        "name": "rConstraint",
        "outlinerStyle": constants.RagdollStyle,
    }, **(opts or {}))

    if parent.type() == "rdSuit":
        suit = parent
    else:
        suit = parent["startState"].output(type="rdSuit")
        assert suit and suit.type() in ("rdSuit",), (
            "%s was not part of a suit" % parent
        )

    assert child["startState"].output(type="rdSuit") == suit, (
        "%s and %s was not part of the same suit" % (parent, child)
    )

    name = internal.unique_name(opts["name"])

    with cmdx.DagModifier() as mod:
        transform = mod.create_node("transform", name=name)
        con = commands._rdconstraint(mod, name, parent=transform)

        if child["src"].input().type() == "joint":
            draw_scale = child["shapeLength"].read() * 0.25
        else:
            draw_scale = sum(child["shapeExtents"].read()) / 3.0

        mod.set_attr(con["drawScale"], draw_scale)
        mod.connect(parent["ragdollId"], con["parentRigid"])
        mod.connect(child["ragdollId"], con["childRigid"])

        reset_constraint(mod, con)
        add_constraint(mod, con, suit)

        mod.set_attr(con["limitEnabled"], True)

    return con


def add_constraint(mod, con, suit):
    assert con["startState"].connection() != suit, (
        "%s already a member of %s" % (con, suit)
    )

    time = cmdx.encode("time1")
    index = suit["inputConstraintStart"].next_available_index()

    mod.set_attr(con["version"], internal.version())
    mod.connect(con["startState"], suit["inputConstraintStart"][index])
    mod.connect(con["currentState"], suit["inputConstraint"][index])
    mod.connect(time["outTime"], con["currentTime"])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def reset_constraint(mod, con, opts=None):
    assert con.type() == "rdConstraint", "%s must be an rdConstraint" % con

    opts = opts or {}

    # Setup default values
    opts = dict({
        "maintainOffset": True,
    }, **opts)

    def reset_attr(attr):
        if attr.editable:
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

    # Align constraint to whatever the local transformation is
    if opts["maintainOffset"]:

        # Ensure connection to childRigid is complete
        mod.do_it()

        reset_constraint_frames(con, _mod=mod)


def reset_constraint_frames(con, _mod=None):
    """Reset constraint frames"""

    assert con and isinstance(con, cmdx.DagNode), (
        "con was not a rdConstraint node"
    )

    parent_marker = con["parentRigid"].input(type="rdMarker")
    child_marker = con["childRigid"].input(type="rdMarker")

    assert child_marker is not None, "Unconnected constraint: %s" % con

    if parent_marker is not None:
        parent_matrix = parent_marker["inputMatrix"].as_matrix()
    else:
        # It's connected to the world
        parent_matrix = cmdx.Matrix4()

    transform = child_marker["src"].input()

    if "rotatePivot" in transform:
        child_rotate_pivot = transform["rotatePivot"].as_vector()
    else:
        child_rotate_pivot = cmdx.Vector()

    child_matrix = child_marker["inputMatrix"].as_matrix()

    child_frame = cmdx.Tm()
    child_frame.translateBy(child_rotate_pivot)
    child_frame = child_frame.as_matrix()

    child_tm = cmdx.Tm(child_matrix)
    child_tm.translateBy(child_rotate_pivot, cmdx.sPreTransform)

    parent_frame = child_tm.as_matrix() * parent_matrix.inverse()

    def do_it(mod):
        # Drive to where you currently are
        if con["driveMatrix"].writable:
            mod.set_attr(con["driveMatrix"], parent_frame)

        mod.set_attr(con["parentFrame"], parent_frame)
        mod.set_attr(con["childFrame"], child_frame)

    if _mod is not None:
        do_it(_mod)

    else:
        with cmdx.DagModifier() as mod:
            do_it(mod)
