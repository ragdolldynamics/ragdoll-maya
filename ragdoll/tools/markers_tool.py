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

                if constants.RAGDOLL_DEVELOPER:
                    mod.set_keyable(group["articulated"], True)
                    mod.set_keyable(group["articulationType"], True)

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

            # Root or lone object
            if not parent_marker:
                dgmod.lock_attr(marker["limitType"])
                dgmod.lock_attr(marker["limitAxis"])
                dgmod.lock_attr(marker["limitRotation"])
                dgmod.lock_attr(marker["limitRange"])
                dgmod.lock_attr(marker["limitOffset"])
                dgmod.lock_attr(marker["limitStiffness"])
                dgmod.lock_attr(marker["limitDampingRatio"])

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

            # For the offset, we need to store the difference between
            # the source and destination transforms. At the time of
            # creation, these are the same.
            dgmod.set_attr(marker["offsetMatrix"][0], cmdx.Matrix4())

            if transform.type() == "joint":
                draw_scale = geo.length * 0.25
            else:
                draw_scale = sum(geo.extents) / 3.0

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


def record(solver, opts):
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

    opts = opts or {}
    opts = dict({
        "startTime": None,
        "endTime": None,
        "include": None,
        "exclude": None,
        "includeKinematic": False,
        "ignoreJoints": True,
        "maintainOffset": True,
        "simplifyCurves": True,
        "unrollRotations": True,
        "resetMarkers": True,
    }, **opts)

    initial_time = cmdx.current_time()
    start_time = opts["startTime"]
    end_time = opts["endTime"]
    solver_start_time = solver["_startTime"].as_time()

    if start_time is None:
        start_time = solver_start_time

    if end_time is None:
        end_time = cmdx.max_time()

    include = {t: True for t in opts["include"]} if opts["include"] else {}
    exclude = {t: True for t in opts["exclude"]} if opts["exclude"] else {}

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    solver_start_frame = int(solver_start_time.value)
    start_frame = int(start_time.value)
    end_frame = int(end_time.value)
    total = end_frame - start_frame

    end_frame += 1  # One more for safety

    # Allocate data
    markers = []

    def find_inputs(solver):
        for entity in [el.input() for el in solver["inputStart"]]:
            if entity.isA("rdMarker"):
                markers.append(entity)

            if entity.isA("rdGroup"):
                markers.extend(el.input() for el in entity["inputStart"])

            if entity.isA("rdSolver"):
                # A solver will have markers and groups of its own
                # that we need to iterate over again.
                find_inputs(entity)

    find_inputs(solver)

    markers = {m.shortest_path(): m for m in markers}
    cache = {marker: {} for marker in markers}
    anim = {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}

    def simulate():
        r"""Evaluate every frame between `solver_start_frame` and `end_frame`

        We'll need to start from the solver start frame, even if the user
        provides a later frame. Since the simulation won't be accurate
        otherwise.


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
            cmdx.current_time(cmdx.om.MTime(frame, cmdx.TimeUiUnit()))

            if frame == solver_start_frame:
                # Initialise solver
                solver["startState"].read()
            else:
                # Step simulation
                solver["currentState"].read()

            # Record results
            for key, marker in markers.items():
                if opts["includeKinematic"]:
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
            for el in marker["dst"]:
                transform = el.input()

                if opts["ignoreJoints"] and transform.isA(cmdx.kJoint):
                    continue

                for channel in "tr":
                    if channel == "r" and kinematic_rotation:
                        continue

                    for axis in "xyz":
                        plug = transform[channel + axis]

                        # Not keyframed
                        if channel == "t" and not kinematic_translation:
                            if not plug.input(type="animCurveTL"):
                                unkeyed.append((start_frame, plug))

                        if channel == "r" and not kinematic_rotation:
                            if not plug.input(type="animCurveTA"):
                                unkeyed.append((start_frame, plug))

        for start_frame, plug in unkeyed:
            node = plug.node().shortest_path()
            cmds.setKeyframe(node,
                             time=start_frame,
                             attribute=plug.name(),
                             dirtyDG=True)

    def reset():
        groups = set()

        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], 0)

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
                    mod.set_attr(group["inputType"], constants.InputKinematic)

    @internal.with_undo_chunk
    def unroll():
        rotate_channels = []

        def is_keyed(plug):
            return plug.input(type="animCurveTA") is not None

        for marker, channels in anim.items():
            marker = markers[marker]

            for el in marker["dst"]:
                dst = el.input()

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
    def simplify():
        """TODO This isn't the same as simplify-dense in the Graph Editor"""
        for marker, channels in anim.items():
            marker = markers[marker]
            recorded_channels = []

            for el in marker["dst"]:
                dst = el.input()

                # No destination transform here, carry on
                if dst is None:
                    continue

                # Should only simplify any that was actually
                # part of our simulation output.
                recorded_channels = [
                    "%s.%s" % (dst, chan)
                    for chan in ("rx", "ry", "rz",
                                 "tx", "ty", "tz")
                    if chan in channels
                ]

                cmds.simplify(
                    recorded_channels,
                    timeTolerance=0.005,
                    valueTolerance=0.01
                )

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

        for frame in range(start_frame, end_frame):
            cmdx.current_time(cmdx.om.MTime(frame, cmdx.TimeUiUnit()))

            for key in ordered_markers:
                marker = markers[key]
                data = cache[key][frame]
                output_matrix = data["outputMatrix"]

                # Nothing to do.
                if not any([data["recordTranslation"],
                            data["recordRotation"]]):
                    continue

                for index, el in enumerate(marker["dst"]):
                    dst = el.input()

                    if not dst:
                        continue

                    # Filter out unwanted nodes
                    if include and dst not in include:
                        continue

                    if exclude and dst in exclude:
                        continue

                    if opts["ignoreJoints"] and dst.isA(cmdx.kJoint):
                        continue

                    matrix = output_matrix

                    if opts["maintainOffset"]:
                        offset = marker["offsetMatrix"][index].as_matrix()
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

    if not opts["includeKinematic"]:
        initial_keyframe()
        compute_transitions()

    for status in write():
        yield (status[0], 50 + status[1] * 0.50)

    if opts["resetMarkers"]:
        reset()

    if opts["unrollRotations"]:
        unroll()

    if opts["simplifyCurves"]:
        simplify()

    # Restore time
    cmdx.current_time(initial_time)


def cache(solvers):
    initial_time = cmdx.current_time()

    for solver in solvers:
        cmdx.current_time(solver["_startTime"].asTime())

        # Clear existing cache
        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], 0)

        solver["startState"].read()

        # Prime for updated cache
        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], 1)

    start_frames = {
        s: int(s["_startTime"].asTime().value)
        for s in solvers
    }

    start_frame = min(start_frames.values())
    end_frame = int(cmdx.max_time().value)
    total = end_frame - start_frame

    for frame in range(start_frame, end_frame + 1):
        time = cmdx.om.MTime(frame, cmdx.TimeUiUnit())
        cmdx.current_time(time)

        for solver in solvers:
            if frame == start_frames[solver]:
                solver["startState"].read()

            elif frame > start_frames[solver]:
                solver["currentState"].read()

        percentage = 100 * float(frame - start_frame) / total
        yield percentage

    cmdx.current_time(initial_time)


def link(a, b):
    assert a and a.isA("rdSolver"), "%s was not a solver" % a
    assert b and b.isA("rdSolver"), "%s was not a solver" % b

    with cmdx.DagModifier() as mod:
        index = b["inputStart"].next_available_index()
        mod.connect(a["startState"], b["inputStart"][index])
        mod.connect(a["currentState"], b["inputCurrent"][index])

        # Make it obvious which is main
        mod.try_set_attr(a.parent()["visibility"], False)


def unlink(solver):
    assert solver and solver.isA("rdSolver"), "%s was not a solver" % solver
    with cmdx.DagModifier() as mod:
        mod.disconnect(solver["startState"])
        mod.disconnect(solver["currentState"])

        mod.try_set_attr(solver.parent()["visibility"], True)


def retarget(marker, transform, append=False):
    """Retarget `marker` to `transform`

    When recording, write simulation from `marker` onto `transform`,
    regardless of where it is assigned.

    """

    with cmdx.DGModifier() as mod:
        if not append:
            for el in marker["dst"]:
                mod.disconnect(el, destination=False)

            for el in marker["offsetMatrix"]:
                mod.disconnect(el, destination=False)

            mod.do_it()

        index = marker["dst"].next_available_index()
        src = marker["src"].input()
        dst = marker["dst"][index]

        mod.connect(transform["message"], dst)

        # Store offset for recording later
        offset = src["worldMatrix"][0].as_matrix()
        offset *= transform["worldInverseMatrix"][0].as_matrix()
        mod.set_attr(marker["offsetMatrix"][index], offset)


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
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert parent["_scene"] == child["_scene"], (
        "%s and %s not part of the same solver"
    )

    def find_solver(start):
        while start and not start.isA("rdSolver"):
            start = start["startState"].output(("rdGroup", "rdSolver"))
        return start

    solver = find_solver(parent)
    assert solver and solver.isA("rdSolver"), (
        "%s was not part of a solver" % parent
    )

    parent_transform = parent["src"].input(type=cmdx.kDagNode)
    child_transform = child["src"].input(type=cmdx.kDagNode)
    parent_name = parent_transform.name(namespace=False)
    child_name = child_transform.name(namespace=False)

    parent_position = cmdx.Point(parent_transform.translation(cmdx.sWorld))
    child_position = cmdx.Point(child_transform.translation(cmdx.sWorld))
    distance = parent_position.distanceTo(child_position)

    name = internal.unique_name("%s_to_%s" % (parent_name, child_name))
    shape_name = internal.shape_name(name)

    with cmdx.DagModifier() as mod:
        transform = mod.create_node("transform", name=name)
        con = commands._rddistanceconstraint(mod, shape_name, parent=transform)

        # if child_transform and child_transform.isA(cmdx.kJoint):
        #     draw_scale = child["shapeLength"].read() * 0.25
        # else:
        #     draw_scale = sum(child["shapeExtents"].read()) / 3.0

        # mod.set_attr(con["drawScale"], draw_scale)
        mod.set_attr(con["minimum"], distance)
        mod.set_attr(con["maximum"], distance)
        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])

        add_constraint(mod, con, solver)
        # reset_constraint_frames(mod, con)

    return con


def add_constraint(mod, con, solver):
    assert con["startState"].output() != solver, (
        "%s already a member of %s" % (con, solver)
    )

    time = cmdx.encode("time1")
    index = solver["inputStart"].next_available_index()

    mod.set_attr(con["version"], internal.version())
    mod.connect(con["startState"], solver["inputStart"][index])
    mod.connect(con["currentState"], solver["inputCurrent"][index])
    mod.connect(time["outTime"], con["currentTime"])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def reset_constraint_frames(mod, con):
    """Reset constraint frames"""

    assert con and isinstance(con, cmdx.Node), (
        "%s was not a cmdx instance" % con
    )

    if con.isA("rdMarker"):
        parent = con["parentMarker"].input(type="rdMarker")
        child = con
    elif con.isA("rdConstraint"):
        parent = con["parentRigid"].input(type="rdMarker")
        child = con["childRigid"].input(type="rdMarker")

    if parent is not None:
        parent_matrix = parent["inputMatrix"].as_matrix()
    else:
        # It's connected to the world
        parent_matrix = cmdx.Matrix4()

    rotate_pivot = child["rotatePivot"].as_vector()
    rest_matrix = child["inputMatrix"].as_matrix()

    child_frame = cmdx.Tm()
    child_frame.translateBy(rotate_pivot)
    child_frame = child_frame.as_matrix()

    child_tm = cmdx.Tm(rest_matrix)
    child_tm.translateBy(rotate_pivot, cmdx.sPreTransform)

    parent_frame = child_tm.as_matrix() * parent_matrix.inverse()

    mod.set_attr(con["parentFrame"], parent_frame)
    mod.set_attr(con["childFrame"], child_frame)


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
