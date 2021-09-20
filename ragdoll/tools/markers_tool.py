from .. import commands, internal, constants
from ..vendor import cmdx
from maya import cmds

InputInherit = 0
InputOff = 1
InputKinematic = 2
InputGuide = 3


def assign(transforms, solver, lollipop=False):
    assert len(transforms) > 0, "Nothing to assign to"

    time1 = cmdx.encode("time1")
    objset = cmdx.find("rMarkers")
    parent_marker = transforms[0]["worldMatrix"][0].output(type="rdMarker")

    if not objset:
        with cmdx.DGModifier() as mod:
            objset = mod.create_node("objectSet", name="rMarkers")

    group = None

    if len(transforms) > 1:
        if parent_marker:
            group = parent_marker["startState"].output(type="rdGroup")

            # Already got a marker
            transforms.pop(0)

        if not group:
            with cmdx.DagModifier() as mod:
                group_parent = mod.create_node("transform", name="rSuit")
                group = mod.create_node("rdGroup",
                                        name="rSuitShape",
                                        parent=group_parent)

                index = solver["inputStart"].next_available_index()
                mod.set_attr(group["version"], internal.version())
                mod.connect(group["startState"], solver["inputStart"][index])
                mod.connect(solver["startTime"], group["startTime"])
                mod.connect(time1["outTime"], group["currentTime"])
                mod.connect(group["currentState"],
                            solver["inputCurrent"][index])
                mod.connect(group_parent["message"],
                            group["exclusiveNodes"][0])

    markers = {}
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

                    if shape.type() == "mesh":
                        dgmod.connect(shape["outMesh"],
                                      marker["inputGeometry"])

                    if shape.type() in ("nurbsCurve", "nurbsSurface"):
                        dgmod.connect(shape["local"],
                                      marker["inputGeometry"])

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
            dgmod.connect(time1["outTime"], marker["currentTime"])
            dgmod.connect(transform["worldMatrix"][0], marker["inputMatrix"])

            if group:
                dgmod.connect(group["startTime"], marker["startTime"])

                index = group["inputMarker"].next_available_index()
                dgmod.connect(marker["currentState"],
                              group["inputMarker"][index])
                dgmod.connect(marker["startState"],
                              group["inputMarkerStart"][index])

                if parent_marker is not None:
                    dgmod.connect(parent_marker["ragdollId"],
                                  marker["parentMarker"])

                parent_marker = marker

            else:
                dgmod.connect(solver["startTime"], marker["startTime"])
                index = solver["inputStart"].next_available_index()

                dgmod.connect(marker["startState"],
                              solver["inputStart"][index])
                dgmod.connect(marker["currentState"],
                              solver["inputCurrent"][index])

            index = objset["dnSetMembers"].next_available_index()
            dgmod.connect(marker["message"], objset["dnSetMembers"][index])

            # Keep next_available_index() up-to-date
            dgmod.do_it()

            markers[transform] = marker

    if lollipop:

        with cmdx.DagModifier() as mod:
            for index, transform in enumerate(transforms[:]):
                name = transform.name(namespace=False)

                # R_armBlend2_JNT --> R_armBlend2
                name = name.rsplit("_", 1)[0]

                # R_armBlend2 -> R_armBlend2_MRK
                name = name + "_MRK"

                lol = mod.create_node("transform", name=name, parent=transform)
                mod.set_keyable(lol["translateX"], False)
                mod.set_keyable(lol["translateY"], False)
                mod.set_keyable(lol["translateZ"], False)
                mod.set_keyable(lol["rotateX"], False)
                mod.set_keyable(lol["rotateY"], False)
                mod.set_keyable(lol["rotateZ"], False)
                mod.set_keyable(lol["scaleX"], False)
                mod.set_keyable(lol["scaleY"], False)
                mod.set_keyable(lol["scaleZ"], False)

                # Find a suitable scale
                scale = sum(marker["shapeExtents"].read()) / 3.0
                mod.set_attr(lol["scale"], scale * 0.25)

                # Take over from here
                marker = markers[transform]
                mod.connect(lol["parentMatrix"][0], marker["inputMatrix"])

                # Make shape
                mod.do_it()
                curve = cmdx.curve(
                    lol, points=(
                        (0, 0, 0),
                        (4, 0, 0),
                        (5, 0, -1),
                        (6, 0, 0),
                        (5, 0, 1),
                        (4, 0, 0)),
                    mod=mod
                )

                # Hide from channelbox
                mod.set_attr(curve["isHistoricallyInteresting"], False)


def capture(solver,
            transforms=None,
            start_time=None,
            end_time=None,
            maintain_offset=True):
    """Transfer simulation into animation

    Arguments:
        transforms (list, optional): Transfer to these transforms only
        start_time (MTime, optional): Capture from this time
        end_time (MTime, optional): Capture to this time

    """

    if start_time is None:
        start_time = solver["startTime"].as_time()

    if end_time is None:
        end_time = cmdx.max_time()

    transforms = {t: True for t in transforms} if transforms else {}

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    start_frame = int(start_time.value)
    end_frame = int(end_time.value)
    total = end_frame - start_frame

    # Allocate data
    entities = [el.input() for el in solver["inputStart"]]

    markers = []
    for entity in entities:
        if entity.type() == "rdMarker":
            markers += [entity]

        if entity.type() == "rdGroup":
            members = [el.input() for el in entity["inputMarkerStart"]]
            markers.extend(members)

    markers = {m.shortest_path(): m for m in markers}
    cache = {marker: {} for marker in markers}
    anim = {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}
    # transitions = {marker: {} for marker in markers}

    def simulate():
        r"""Evaluate every frame between `start_frame` and `end_frame`

               |
               |
               |      |
               |  |   |
               | _|___|
                /     \
               |       |
               |       |
                \_____/

        ______________________


        """

        for frame in range(start_frame, end_frame):
            with cmdx.Context(frame, cmdx.TimeUiUnit()):

                # Trigger simulation
                solver["output"].read()

                # Record results
                for key, marker in markers.items():
                    kinematic = marker["_kinematic"].read()

                    cache[key][frame] = {
                        "captureTranslation": marker["catr"].read(),
                        "captureRotation": marker["caro"].read(),
                        "outputMatrix": marker["ouma"].as_matrix(),
                        "kinematic": kinematic,
                        "transition": False,
                    }

                    if kinematic:
                        cache[key][frame]["captureTranslation"] = False
                        cache[key][frame]["captureRotation"] = False

            percentage = 100 * float(frame - start_frame) / total
            yield ("simulating", percentage)

    def compute_transitions():
        r"""A destination control transitions between kinematic and dynamic

        o       o              o       o
         \     /      --->      .     .
          \   /       --->       .   .
           \ /                    . .
            o                      o

        """

        for key, frames in cache.items():
            for frame, data in frames.items():
                is_kinematic = data["kinematic"]

                try:
                    was_kinematic = frames[frame - 1]["kinematic"]
                except KeyError:
                    was_kinematic = is_kinematic

                if was_kinematic == is_kinematic:
                    continue

                # Transition <- kinematic
                if was_kinematic and not is_kinematic:
                    cache[key][frame - 1].update({
                        "captureTranslation": True,
                        "captureRotation": True,
                        "transition": True,
                    })

                # Transition -> kinematic
                if not was_kinematic and is_kinematic:
                    cache[key][frame + 1].update({
                        "captureTranslation": True,
                        "captureRotation": True,
                        "transition": True,
                    })

                was_kinematic = is_kinematic

    def initial_keyframe():
        unkeyed = []

        for marker, channels in anim.items():
            node = markers[marker]
            transform = node["dst"][0].input()

            for channel in "tr":
                for axis in "xyz":
                    if not channels[channel + axis]:
                        # This marker was entirely kinematic
                        continue

                    plug = transform[channel + axis]
                    start_frame = min(channels[channel + axis].keys())

                    # Not keyframed
                    if not plug.input(type=("animCurveTL", "animCurveTA")):
                        unkeyed.append((start_frame, plug))

        for start_frame, plug in unkeyed:
            node = plug.node().shortest_path()
            cmds.setKeyframe(node, time=start_frame, attribute=plug.name())

    def reset():
        groups = set()

        with cmdx.DagModifier() as mod:
            for marker in markers.values():
                curve = marker["inputType"].input(type="animCurveTU")

                if curve is not None:
                    mod.delete(curve)
                    mod.do_it()

                group = marker["startState"].output(type="rdGroup")

                # It may have a different kind of connection, like a proxy
                if not marker["inputType"].connected:
                    input_type = InputInherit if group else InputKinematic
                    mod.set_attr(marker["inputType"], input_type)

                groups.add(group) if group else None

            #
            # Turn all groups to kinematic
            #
            for group in groups:
                curve = group["inputType"].input(type="animCurveTU")

                if curve is not None:
                    mod.delete(curve)
                    mod.do_it()

                # It may have a different kind of connection, like a proxy
                if not group["inputType"].connected:
                    mod.set_attr(group["inputType"], 1)

    @internal.with_undo_chunk
    def unroll():
        rotate_channels = []

        def is_keyed(plug):
            return plug.input(type="animCurveTA") is not None

        for marker, channels in anim.items():
            marker = markers[marker]
            dst = marker["dst"][0].input()

            # No destination transforms here, carry on
            if dst is None:
                continue

            # Can only unroll transforms with all axes keyed
            if all(is_keyed(dst[ch]) for ch in ("rx", "ry", "rz")):

                # Should only unrol any that was actually
                # part of our simulation output.
                if any(anim[marker][ch] for ch in ("rx", "ry", "rz")):
                    rotate_channels += ["%s.rx" % dst]
                    rotate_channels += ["%s.ry" % dst]
                    rotate_channels += ["%s.rz" % dst]

        cmds.rotationInterpolation(rotate_channels, c="quaternionSlerp")
        cmds.rotationInterpolation(rotate_channels, c="none")

    @internal.with_undo_chunk
    def write():
        # Figure out kinematic hierarchy for marker order
        orders = {marker: 0 for marker in markers}

        for key, order in orders.items():
            marker = markers[key]
            parent = marker["parentMarker"].input(type="rdMarker")

            while parent:
                order += 1
                parent = parent["parentMarker"].input()

            orders[key] = order

        # Loop over each marker, in kinematic order
        ordered_markers = sorted(orders.keys(), key=lambda m: orders[m])

        def unscaled(mat):
            tm = cmdx.Tm(mat)
            tm.setScale(cmdx.Vector(1, 1, 1))
            return tm.as_matrix()

        offsets = {}
        if maintain_offset:
            with cmdx.Context(start_frame, cmdx.TimeUiUnit()):
                for key in ordered_markers:
                    start_data = cache[key][start_frame]

                    marker = markers[key]

                    for el in marker["dst"]:
                        dst = el.input()

                        if not dst:
                            continue

                        wim = dst["wim"][0].as_matrix()
                        output_matrix = start_data["outputMatrix"]

                        offset = output_matrix * wim
                        offsets[(marker, dst)] = offset

        for frame in range(start_frame, end_frame):
            with cmdx.Context(frame, cmdx.TimeUiUnit()):
                for key in ordered_markers:
                    marker = markers[key]
                    data = cache[key][frame]
                    output_matrix = data["outputMatrix"]

                    # Nothing to do.
                    if not any([data["captureTranslation"],
                                data["captureRotation"]]):
                        continue

                    for el in marker["dst"]:
                        dst = el.input()

                        if not dst:
                            continue

                        matrix = output_matrix

                        if maintain_offset:
                            offset = offsets[(marker, dst)]
                            matrix = offset.inverse() * output_matrix

                        t, r = get_local_pos_rot(matrix, dst)

                        try:
                            joint_orient = dst["jointOrient"].as_quaternion()
                            r = r.as_quaternion() * joint_orient.inverse()
                            r = r.as_euler_rotation()
                        except cmdx.ExistError:
                            pass

                        def set_keyframe(at, value):
                            path = dst.shortest_path()
                            cmds.setKeyframe(path,
                                             attribute=at,
                                             time=frame,
                                             value=value,
                                             dirtyDG=True)

                        if data["captureTranslation"]:
                            set_keyframe("tx", t.x)
                            set_keyframe("ty", t.y)
                            set_keyframe("tz", t.z)

                        if data["captureRotation"]:
                            set_keyframe("rx", cmdx.degrees(r.x))
                            set_keyframe("ry", cmdx.degrees(r.y))
                            set_keyframe("rz", cmdx.degrees(r.z))

            percentage = 100 * float(frame - start_frame) / total
            yield ("writing", percentage)

    for status in simulate():
        yield (status[0], status[1] * 0.50)

    # compute_transitions()
    # initial_keyframe()

    for status in write():
        yield (status[0], 50 + status[1] * 0.50)

    reset()
    unroll()


@internal.with_undo_chunk
def create_constraint(parent, child, opts=None):
    assert child.type() in ("rdMarker",), child.type()
    assert parent.type() in ("rdMarker", "rdGroup"), (
        "%s must be a rigid or group" % parent.type()
    )

    opts = dict({
        "name": "rConstraint",
    }, **(opts or {}))

    if parent.type() == "rdGroup":
        group = parent
    else:
        group = parent["startState"].output(type="rdGroup")
        assert group and group.type() in ("rdGroup",), (
            "%s was not part of a group" % parent
        )

    assert child["startState"].output(type="rdGroup") == group, (
        "%s and %s was not part of the same group" % (parent, child)
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
        add_constraint(mod, con, group)

        mod.set_attr(con["limitEnabled"], True)

    return con


def add_constraint(mod, con, group):
    assert con["startState"].connection() != group, (
        "%s already a member of %s" % (con, group)
    )

    time = cmdx.encode("time1")
    index = group["inputConstraintStart"].next_available_index()

    mod.set_attr(con["version"], internal.version())
    mod.connect(con["startState"], group["inputConstraintStart"][index])
    mod.connect(con["currentState"], group["inputConstraint"][index])
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


def get_local_pos_rot(wm, b):
    pim = b["parentInverseMatrix"][0].as_matrix()
    tm = cmdx.Tm(wm * pim)

    b_tm = b.transformation()
    b_rp = b_tm.rotatePivot(cmdx.sTransform)
    b_rpt = b_tm.rotatePivotTranslation(cmdx.sTransform)
    b_sp = b_tm.scalePivot(cmdx.sTransform)
    b_spt = b_tm.scalePivotTranslation(cmdx.sTransform)
    b_ro = b_tm.rotationOrientation()
    b_order = b_tm.rotationOrder()

    balance = False
    noscale = cmdx.Vector(1, 1, 1)

    tm.setRotatePivotTranslation(b_rpt, cmdx.sPostTransform)
    tm.setRotatePivot(b_rp, cmdx.sTransform, balance)
    tm.setScalePivotTranslation(b_spt, cmdx.sPostTransform)
    tm.setScalePivot(b_sp, cmdx.sTransform, balance)
    tm.setScale(noscale, cmdx.sTransform)
    tm.setRotationOrientation(b_ro)
    tm.reorderRotation(b_order)

    # MIA is a scale pivot that differs from the rotate pivot

    total_offset = b_rp + b_rpt

    tm.translateBy(-total_offset, cmdx.sTransform)
    tm.translateBy(b_rp, cmdx.sPreTransform)

    pos = tm.translation(cmdx.sPostTransform)
    rot = tm.rotation()

    return pos, rot
