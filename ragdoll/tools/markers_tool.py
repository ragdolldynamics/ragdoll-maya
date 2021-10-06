from .. import commands, internal, constants
from ..vendor import cmdx
from maya import cmds


AlreadyAssigned = type("AlreadyAssigned", (RuntimeError,), {})


def assign(transforms, solver):
    assert len(transforms) > 0, "Nothing to assign to"

    if len(transforms) > 1:
        existing = []
        for t in transforms[1:]:
            other = t["message"].output(type="rdMarker")
            if other is not None:
                existing += [other]

        if existing:
            raise AlreadyAssigned(
                "At least %d transform(s) were already assigned"
                % len(existing)
            )

    time1 = cmdx.encode("time1")
    parent_marker = transforms[0]["worldMatrix"][0].output(type="rdMarker")

    group = None
    root_transform = transforms[0]

    if len(transforms) > 1:
        if parent_marker:
            group = parent_marker["startState"].output(type="rdGroup")

            # Already got a marker
            transforms.pop(0)

        if not group:
            with cmdx.DagModifier() as mod:
                root_name = root_transform.name(namespace=False)
                name = internal.unique_name("%s_rGroup" % root_name)
                shape_name = internal.shape_name(name)
                group_parent = mod.create_node("transform", name=name)
                group = mod.create_node("rdGroup",
                                        name=shape_name,
                                        parent=group_parent)

                index = solver["inputStart"].next_available_index()
                mod.set_attr(group["version"], internal.version())
                mod.connect(group["startState"], solver["inputStart"][index])
                mod.connect(time1["outTime"], group["currentTime"])
                mod.connect(group["currentState"],
                            solver["inputCurrent"][index])

                commands._take_ownership(mod, group, group_parent)

    markers = {}
    with cmdx.DGModifier() as dgmod:
        for index, transform in enumerate(transforms):
            name = "rMarker_%s" % transform.name()
            marker = dgmod.create_node("rdMarker", name=name)

            # Avoid markers getting too excited
            dgmod.set_attr(marker["maxDepenetrationVelocity"], 20.0)

            try:
                children = [transforms[index + 1]]
            except IndexError:
                children = None

            if parent_marker:
                parent_transform = parent_marker["inputMatrix"].input()
                dgmod.set_attr(marker["recordTranslation"], False)
            else:
                parent_transform = None

            shape = transform.shape(type=("mesh",
                                          "nurbsCurve",
                                          "nurbsSurface"))

            if shape and shape.type() == "mesh":
                dgmod.connect(shape["outMesh"],
                              marker["inputGeometry"])

            if shape and shape.type() in ("nurbsCurve", "nurbsSurface"):
                dgmod.connect(shape["local"],
                              marker["inputGeometry"])

            # It's a limb
            if parent_marker or len(transforms) > 1:
                geo = commands.infer_geometry(transform,
                                              parent_transform,
                                              children)

                geo.shape_type = constants.CapsuleShape

            # It's a lone object
            else:
                dgmod.set_attr(marker["inputType"], constants.InputOff)

                if shape:
                    geo = commands._interpret_shape2(shape)

                else:
                    geo = commands.infer_geometry(transform)
                    geo.shape_type = constants.CapsuleShape

            # Make the root passive
            if len(transforms) > 1 and not parent_marker:
                dgmod.set_attr(marker["inputType"], constants.InputKinematic)

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
            dgmod.connect(transform["rotatePivot"], marker["rotatePivot"])
            dgmod.connect(transform["rotatePivotTranslate"],
                          marker["rotatePivotTranslate"])

            if transform.type() == "joint":
                draw_scale = marker["shapeLength"].read() * 0.25
            else:
                draw_scale = sum(marker["shapeExtents"].read()) / 3.0

            dgmod.set_attr(marker["drawScale"], draw_scale)

            # Currently not implemented
            dgmod.lock_attr(marker["recordToExistingKeys"])
            dgmod.lock_attr(marker["recordToExistingTangents"])

            if group:
                index = group["inputCurrent"].next_available_index()
                dgmod.connect(marker["currentState"],
                              group["inputCurrent"][index])
                dgmod.connect(marker["startState"],
                              group["inputStart"][index])

                if parent_marker is not None:
                    dgmod.connect(parent_marker["ragdollId"],
                                  marker["parentMarker"])

                parent_marker = marker

            else:
                index = solver["inputStart"].next_available_index()

                dgmod.connect(marker["startState"],
                              solver["inputStart"][index])
                dgmod.connect(marker["currentState"],
                              solver["inputCurrent"][index])

            # Keep next_available_index() up-to-date
            dgmod.do_it()

            # Currently unused, markers compute their own frames
            reset_constraint_frames(dgmod, marker)

            markers[transform] = marker

    return list(markers.values())


def create_lollipop(markers):
    with cmdx.DagModifier() as mod:
        for marker in markers:
            transform = marker["src"].input()
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

            mod.set_attr(lol["overrideEnabled"], True)
            mod.set_attr(lol["overrideShading"], False)
            mod.set_attr(lol["overrideColor"], constants.YellowIndex)

            # Find a suitable scale
            scale = list(sorted(marker["shapeExtents"].read()))[1]
            mod.set_attr(lol["scale"], scale * 0.25)

            # Take over from here
            mod.connect(lol["parentMatrix"][0], marker["inputMatrix"])

            # Make shape
            mod.do_it()
            curve = cmdx.curve(
                lol, points=(
                    (-0, +0, +0),
                    (-0, +4, +0),
                    (-1, +5, +0),
                    (-0, +6, +0),
                    (+1, +5, +0),
                    (-0, +4, +0),
                ), mod=mod
            )

            # Delete this alongside physics
            commands._take_ownership(mod, marker, lol)

            # Hide from channelbox
            mod.set_attr(curve["isHistoricallyInteresting"], False)


def record(solver,
           start_time=None,
           end_time=None,
           include=None,
           exclude=None,
           kinematic=False,
           maintain_offset=True):
    """Transfer simulation into animation

    Arguments:
        start_time (MTime, optional): Record from this time
        end_time (MTime, optional): Record to this time
        include (list, optional): Record these transforms only
        exclude (list, optional): Do not record these transforms
        kinematic (bool, optional): Record kinematic frames too
        maintain_offset (bool, optional): Maintain whatever offset is
            between the source and destination transforms, default True

    """

    solver_start_time = solver["_startTime"].as_time()

    if start_time is None:
        start_time = solver_start_time

    if end_time is None:
        end_time = cmdx.max_time()

    include = {t: True for t in include} if include else {}
    exclude = {t: True for t in exclude} if exclude else {}

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    solver_start_frame = int(solver_start_time.value)
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
            members = [el.input() for el in entity["inputStart"]]
            markers.extend(members)

    markers = {m.shortest_path(): m for m in markers}
    cache = {marker: {} for marker in markers}
    anim = {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}

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

        for frame in range(solver_start_frame, end_frame):
            with cmdx.Context(frame, cmdx.TimeUiUnit()):

                # Trigger simulation
                solver["output"].read()

                # Record results
                for key, marker in markers.items():
                    if kinematic:
                        is_kinematic = False
                    else:
                        is_kinematic = marker["_kinematic"].read()

                    cache[key][frame] = {
                        "recordTranslation": marker["retr"].read(),
                        "recordRotation": marker["rero"].read(),
                        "outputMatrix": marker["ouma"].as_matrix(),
                        "kinematic": is_kinematic,
                        "transition": False,
                    }

                    if frame < start_frame:
                        cache[key][frame]["recordTranslation"] = False
                        cache[key][frame]["recordRotation"] = False

                    if is_kinematic:
                        cache[key][frame]["recordTranslation"] = False
                        cache[key][frame]["recordRotation"] = False

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
                        "recordTranslation": True,
                        "recordRotation": True,
                        "transition": True,
                    })

                # Transition -> kinematic
                if not was_kinematic and is_kinematic:
                    cache[key][frame + 1].update({
                        "recordTranslation": True,
                        "recordRotation": True,
                        "transition": True,
                    })

                was_kinematic = is_kinematic

    def initial_keyframe():
        """Include the starting position of any marker

        Otherwise, we'll key the first simulated frame which will be
        one frame after the initial state. Thus, changing the initial state!

        """

        unkeyed = []

        # for marker, channels in anim.items():
        for marker, frames in cache.items():

            # Cull entirely kinematic markers
            kinematic_translation = True
            kinematic_rotation = True

            for frame, data in frames.items():
                if data["recordTranslation"]:
                    kinematic_translation = False
                    break

            for frame, data in frames.items():
                if data["recordRotation"]:
                    kinematic_rotation = False
                    break

            if kinematic_translation and kinematic_rotation:
                # This marker was entirely kinematic
                continue

            # It'd be whichever frame got hit above, before `break`
            start_frame = frame

            marker = markers[marker]
            transform = marker["dst"][0].input()
            for channel in "tr":
                if channel == "t" and kinematic_translation:
                    continue

                if channel == "r" and kinematic_rotation:
                    continue

                for axis in "xyz":
                    plug = transform[channel + axis]

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
                    mod.set_attr(marker["inputType"], (
                        constants.InputInherit if group else
                        constants.InputKinematic
                    ))

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

            # No destination transform here, carry on
            if dst is None:
                continue

            # Can only unroll transform with all axes keyed
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
        #
        # NOTE: What we want is for Maya to finish computing anything
        # our marker depends on, like the Maya parent hierarchy. This
        # will *normally* align with the marker hierarchy, but not always.
        # It's possible for the user to create a marker hierarchy in
        # the opposite order of Maya's hierarchy.
        ordered_markers = sorted(orders.keys(), key=lambda m: orders[m])

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
                    if not any([data["recordTranslation"],
                                data["recordRotation"]]):
                        continue

                    for el in marker["dst"]:
                        dst = el.input()

                        if not dst:
                            continue

                        # Filter out unwanted nodes
                        if include and dst not in include:
                            continue

                        if exclude and dst in exclude:
                            continue

                        matrix = output_matrix

                        if maintain_offset:
                            offset = offsets[(marker, dst)]
                            matrix = offset.inverse() * output_matrix

                        t, r = get_local_pos_rot(matrix, dst)

                        def set_keyframe(at, value):
                            path = dst.shortest_path()
                            tangent = (
                                "stepnext"
                                if data["transition"]
                                else "linear"
                            )
                            cmds.setKeyframe(path,
                                             attribute=at,
                                             time=frame,
                                             value=value,
                                             inTangentType=tangent,
                                             outTangentType=tangent,
                                             dirtyDG=True)

                        if data["recordTranslation"]:
                            set_keyframe("tx", t.x)
                            set_keyframe("ty", t.y)
                            set_keyframe("tz", t.z)

                        if data["recordRotation"]:
                            set_keyframe("rx", cmdx.degrees(r.x))
                            set_keyframe("ry", cmdx.degrees(r.y))
                            set_keyframe("rz", cmdx.degrees(r.z))

            percentage = 100 * float(frame - start_frame) / total
            yield ("writing", percentage)

    for status in simulate():
        yield (status[0], status[1] * 0.50)

    initial_keyframe()
    compute_transitions()

    for status in write():
        yield (status[0], 50 + status[1] * 0.50)

    reset()
    unroll()


def snap(transforms):
    markers = {}

    for t in transforms:
        marker = None

        for plug in t["message"].outputs(type="rdMarker", plugs=True):
            if plug.name(long=False).startswith("dst["):
                marker = plug.node()
                break

        # Not every selected transform may actually have a marker assigned
        if marker is None:
            continue

        markers[t] = marker

    assert markers, "No markers found"

    poses = {}
    for transform, marker in markers.items():
        pose = marker["outputMatrix"].as_matrix()
        poses[marker] = (transform, pose)

    # Figure out kinematic hierarchy for marker order
    orders = {marker: 0 for marker in markers.values()}

    for marker, order in orders.items():
        parent = marker["parentMarker"].input(type="rdMarker")

        while parent:
            order += 1
            parent = parent["parentMarker"].input()

        orders[marker] = order

    # Loop over each marker, in kinematic order
    ordered_markers = sorted(orders.keys(), key=lambda m: orders[m])

    with cmdx.DagModifier() as mod:
        for marker in ordered_markers:
            transform, pose = poses[marker]
            pos, rot = get_local_pos_rot(pose, transform)

            if marker["recordTranslation"]:
                for index, axis in enumerate("xyz"):
                    plug = transform["t%s" % axis]

                    if plug.editable:
                        mod.set_attr(plug, pos[index])

            if marker["recordRotation"]:
                for index, axis in enumerate("xyz"):
                    plug = transform["r%s" % axis]

                    if plug.editable:
                        mod.set_attr(plug, pos[index])

            # Ensure child hierarchy is up-to-date
            mod.do_it()

    return poses


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

        reset_constraint_frames(mod, con)
        add_constraint(mod, con, group)

        mod.set_attr(con["limitEnabled"], True)

    return con


def add_constraint(mod, con, group):
    assert con["startState"].connection() != group, (
        "%s already a member of %s" % (con, group)
    )

    time = cmdx.encode("time1")
    index = group["inputStart"].next_available_index()

    mod.set_attr(con["version"], internal.version())
    mod.connect(con["startState"], group["inputStart"][index])
    mod.connect(con["currentState"], group["inputCurrent"][index])
    mod.connect(time["outTime"], con["currentTime"])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def reset_constraint_frames(mod, marker):
    """Reset constraint frames"""

    assert marker and isinstance(marker, cmdx.Node), (
        "%s was not a rdMarker node" % marker
    )

    parent_marker = marker["parentMarker"].input(type="rdMarker")
    assert marker is not None, "Unconnected constraint: %s" % marker

    if parent_marker is not None:
        parent_matrix = parent_marker["inputMatrix"].as_matrix()
    else:
        # It's connected to the world
        parent_matrix = cmdx.Matrix4()

    # transform = marker["src"].input()

    # if "rotatePivot" in transform:
    #     child_rotate_pivot = transform["rotatePivot"].as_vector()
    # else:
    #     child_rotate_pivot = cmdx.Vector()

    child_matrix = marker["inputMatrix"].as_matrix()

    child_frame = cmdx.Tm()
    # child_frame.translateBy(child_rotate_pivot)
    child_frame = child_frame.as_matrix()

    child_tm = cmdx.Tm(child_matrix)
    # child_tm.translateBy(child_rotate_pivot, cmdx.sPreTransform)

    parent_frame = child_tm.as_matrix() * parent_matrix.inverse()

    mod.set_attr(marker["parentFrame"], parent_frame)
    mod.set_attr(marker["childFrame"], child_frame)


def get_local_pos_rot(world_matrix, dag_node):
    """Get translate/rotate of `world_matrix` relative `dag_node`

    Taking into account pivots and rotation order etc.

    """

    pim = dag_node["parentInverseMatrix"][0].as_matrix()
    tm = cmdx.Tm(world_matrix * pim)

    b_tm = dag_node.transformation()
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

    try:
        joint_orient = dag_node["jointOrient"].as_quaternion()
        rot = rot.as_quaternion() * joint_orient.inverse()
        rot = rot.as_euler_rotation()
    except cmdx.ExistError:
        pass

    return pos, rot
