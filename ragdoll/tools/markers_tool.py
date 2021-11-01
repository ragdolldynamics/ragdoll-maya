import logging

from .. import commands, internal, constants
from ..vendor import cmdx
from maya import cmds


log = logging.getLogger("ragdoll")
AlreadyAssigned = type("AlreadyAssigned", (RuntimeError,), {})


def assign(transforms, solver):
    assert len(transforms) > 0, "Nothing to assign to"

    if len(transforms) == 1:
        other = transforms[0]["message"].output(type="rdMarker")

        if other is not None:
            raise AlreadyAssigned(
                "%s was already assigned a marker" % transforms[0]
            )

    else:
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


def snap(solver, opts=None, _force=False):
    """Snap animation to simulation"""

    opts = opts or {}
    opts = dict({
        "include": None,
        "exclude": None,
        "includeKinematic": True,
        "ignoreJoints": False,
        "maintainOffset": True,
    }, **opts)

    include = {t: True for t in opts["include"]} if opts["include"] else {}
    markers = []

    def find_inputs(solver):
        for entity in [el.input() for el in solver["inputStart"]]:
            if not entity:
                continue

            if entity.isA("rdMarker"):
                markers.append(entity)

            elif entity.isA("rdGroup"):
                markers.extend(el.input() for el in entity["inputStart"])

            elif entity.isA("rdSolver"):
                # A solver will have markers and groups of its own
                # that we need to iterate over again.
                find_inputs(entity)

    with internal.Timer("findMarkers") as t1:
        find_inputs(solver)

    dst_to_marker = {}
    dst_to_offset = {}

    def find_destinations():
        for marker in markers:
            for index, el in enumerate(marker["dst"]):
                dst = el.input()

                if not dst:
                    continue

                if not dst.isA(cmdx.kDagNode):
                    continue

                if opts["ignoreJoints"] and dst.isA(cmdx.kJoint):
                    continue

                # Filter out unwanted nodes
                if include and dst not in include:
                    continue

                offset = marker["offsetMatrix"][index].as_matrix()

                dst_to_marker[dst] = marker
                dst_to_offset[dst] = offset.inverse()

    with internal.Timer("findDestinations") as t2:
        find_destinations()

    delete = []

    t4 = internal.Timer("generateHierarchy")
    t5 = internal.Timer("applyMatrix")
    t6 = internal.Timer("parentConstraint")

    marker_to_dagnode = generate_kinematic_hierarchy(solver)

    marker_to_matrix = {}
    for marker in marker_to_dagnode.keys():
        matrix = marker["outputMatrix"].as_matrix()
        marker_to_matrix[marker] = matrix

    with t5:
        with cmdx.DagModifier() as mod:
            for marker, dagnode in marker_to_dagnode.items():
                parent = marker["parentMarker"].input(type="rdMarker")
                matrix = marker_to_matrix[marker]
                parent_matrix = marker_to_matrix.get(parent, cmdx.Mat4())
                local_matrix = matrix * parent_matrix.inverse()

                tm = cmdx.Tm(local_matrix)
                t = tm.translation()
                r = tm.rotation()

                mod.set_attr(dagnode["translate"], t)
                mod.set_attr(dagnode["rotate"], r)

    with t6:
        for dst, marker in dst_to_marker.items():
            src = marker_to_dagnode.get(marker, None)

            if not src:
                continue

            skip_rotate = []
            skip_translate = []

            for chan, plug in zip("xyz", dst["rotate"]):
                if plug.locked:
                    skip_rotate.append(chan)

            for chan, plug in zip("xyz", dst["translate"]):
                if plug.locked:
                    skip_translate.append(chan)

            skip_rotate = skip_rotate or "none"
            skip_translate = skip_translate or "none"

            con = cmds.parentConstraint(
                src.shortest_path(),
                dst.shortest_path(),

                # We'll manually set the offset
                maintainOffset=False,

                # Account for locked channels
                skipTranslate=skip_translate,
                skipRotate=skip_rotate,
            )

            con = cmdx.encode(con[0])

            offset = dst_to_offset[dst]
            tm = cmdx.Tm(offset)
            t = tm.translation()
            r = tm.rotation()

            with cmdx.DagModifier() as mod:
                mod.set_attr(con["target"][0]["targetOffsetTranslate"], t)
                mod.set_attr(con["target"][0]["targetOffsetRotate"], r)

            # Pull to refresh
            dst["worldMatrix"][0].as_matrix()
            dst["translate"].read()
            dst["rotate"].read()

            delete.append(str(con))
        delete.extend(str(node) for node in marker_to_dagnode.values())
    t6.finish()

    with internal.Timer("delete") as t7:
        if _force:
            cmds.dgdirty(allPlugs=True)
            cmds.refresh(force=True)

        cmds.delete(delete)

    for timer in (t1, t2, t4, t5, t6, t7):
        log.debug("%s = %.4fms" % (timer.name, timer.ms))


def record(solver, opts=None):
    """Snap animation to simulation

    Arguments:
        start_time (MTime, optional): Record from this time
        end_time (MTime, optional): Record to this time
        include (list, optional): Record these transforms only
        exclude (list, optional): Do not record these transforms
        kinematic (bool, optional): Record kinematic frames too
        maintain_offset (bool, optional): Maintain whatever offset is
            between the source and destination transforms, default
            value is True

    """

    opts = opts or {}
    opts = dict({
        "startTime": None,
        "endTime": None,
        "include": None,
        "exclude": None,
        "includeKinematic": False,
        "ignoreJoints": False,
        "maintainOffset": True,
        # "simplifyCurves": True,
        "unrollRotations": True,
        "bakeToLayer": False,
        "resetMarkers": False,
        "experimental": False,
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

    end_frame += 1  # One extra for safety

    # Temporary nodes created during this process
    temp = []

    def find_inputs(solver):
        markers = []

        for entity in [el.input() for el in solver["inputStart"]]:
            if not entity:
                continue

            if entity.isA("rdMarker"):
                markers.append(entity)

            elif entity.isA("rdGroup"):
                markers.extend(el.input() for el in entity["inputStart"])

            elif entity.isA("rdSolver"):
                # A solver will have markers and groups of its own
                # that we need to iterate over again.
                find_inputs(entity)

        return markers

    def find_destinations():
        dst_to_marker = {}
        dst_to_offset = {}

        for marker in markers:
            for index, el in enumerate(marker["dst"]):
                dst = el.input()

                if not dst:
                    continue

                if not dst.isA(cmdx.kDagNode):
                    continue

                if opts["ignoreJoints"] and dst.isA(cmdx.kJoint):
                    continue

                # Filter out unwanted nodes
                if include and dst not in include:
                    continue

                if exclude and dst in exclude:
                    continue

                offset = marker["offsetMatrix"][index].as_matrix()

                dst_to_marker[dst] = marker
                dst_to_offset[dst] = offset.inverse()

        return dst_to_marker, dst_to_offset

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
            if opts["experimental"]:
                # This does run faster, but at what cost?
                cmds.setAttr("time1.outTime", int(frame))
            else:
                cmdx.current_time(cmdx.om.MTime(frame, cmdx.TimeUiUnit()))

            if frame == solver_start_frame:
                # Initialise solver
                solver["startState"].read()
            else:
                # Step simulation
                solver["currentState"].read()

            # Record results
            for marker in markers:
                if opts["includeKinematic"]:
                    is_kinematic = False
                else:
                    is_kinematic = marker["_kinematic"].read()

                cache[marker][frame] = {
                    "recordTranslation": marker["retr"].read(),
                    "recordRotation": marker["rero"].read(),
                    "outputMatrix": marker["ouma"].as_matrix(),
                    "kinematic": is_kinematic,
                    "transition": False,
                }

                if frame < start_frame:
                    cache[marker][frame]["recordTranslation"] = False
                    cache[marker][frame]["recordRotation"] = False

                if is_kinematic:
                    cache[marker][frame]["recordTranslation"] = False
                    cache[marker][frame]["recordRotation"] = False

            percentage = 100 * float(frame - start_frame) / total
            yield ("simulating", percentage)

    def generate(marker_to_dagnode):
        total = len(marker_to_dagnode)

        # Generate animation
        for index, (marker, dagnode) in enumerate(marker_to_dagnode.items()):
            parent = marker["parentMarker"].input(type="rdMarker")

            tx, ty, tz = {}, {}, {}
            rx, ry, rz = {}, {}, {}

            for frame, values in cache[marker].items():
                matrix = values["outputMatrix"]
                parent_matrix = cmdx.Mat4()

                if parent in cache:
                    parent_matrix = cache[parent][frame]["outputMatrix"]

                tm = cmdx.Tm(matrix * parent_matrix.inverse())
                t = tm.translation()
                r = tm.rotation()

                tx[frame] = t.x
                ty[frame] = t.y
                tz[frame] = t.z

                rx[frame] = r.x
                ry[frame] = r.y
                rz[frame] = r.z

            with cmdx.DagModifier() as mod:
                mod.set_attr(dagnode["tx"], tx)
                mod.set_attr(dagnode["ty"], ty)
                mod.set_attr(dagnode["tz"], tz)
                mod.set_attr(dagnode["rx"], rx)
                mod.set_attr(dagnode["ry"], ry)
                mod.set_attr(dagnode["rz"], rz)

            percentage = 100 * (index + 1) / total
            yield ("generating", percentage)

    def constrain(marker_to_dagnode):
        total = len(marker_to_dagnode)

        for index, (dst, marker) in enumerate(dst_to_marker.items()):
            src = marker_to_dagnode.get(marker, None)

            if not src:
                continue

            skip_rotate = []
            skip_translate = []

            for chan, plug in zip("xyz", dst["rotate"]):
                if plug.locked:
                    skip_rotate.append(chan)

            for chan, plug in zip("xyz", dst["translate"]):
                if plug.locked:
                    skip_translate.append(chan)

            skip_rotate = skip_rotate or "none"
            skip_translate = skip_translate or "none"

            con = cmds.parentConstraint(
                src.shortest_path(),
                dst.shortest_path(),

                # We'll manually set the offset
                maintainOffset=False,

                # Account for locked channels
                skipTranslate=skip_translate,
                skipRotate=skip_rotate,
            )

            con = cmdx.encode(con[0])

            offset = dst_to_offset[dst]
            tm = cmdx.Tm(offset)
            t = tm.translation()
            r = tm.rotation()

            with cmdx.DagModifier() as mod:
                mod.set_attr(con["target"][0]["targetOffsetTranslate"], t)
                mod.set_attr(con["target"][0]["targetOffsetRotate"], r)

            # Pull to refresh
            dst["worldMatrix"][0].as_matrix()
            dst["translate"].read()
            dst["rotate"].read()

            temp.append(str(con))

            percentage = 100 * (index + 1) / total
            yield ("constraining", percentage)

        temp.extend(str(node) for node in marker_to_dagnode.values())

    def bake(transforms):
        kwargs = {
            "attribute": ("tx", "ty", "tz", "rx", "ry", "rz"),
            "simulation": False,
            "time": (start_time.value, end_time.value),
            "sampleBy": 1,
            "oversamplingRate": 1,
            "disableImplicitControl": True,
            "preserveOutsideKeys": False,
            "sparseAnimCurveBake": False,
            "removeBakedAttributeFromLayer": False,
            "removeBakedAnimFromLayer": False,
            "bakeOnOverrideLayer": opts["bakeToLayer"],
            "minimizeRotation": False,
        }

        cmds.bakeResults(*transforms, **kwargs)

    def reset():
        groups = set()

        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], 0)

            for marker in markers:
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
    def quat_filter():
        """Unroll rotations by converting to quaternions and back to euler"""
        rotate_channels = []

        def is_keyed(plug):
            return plug.input(type="animCurveTA") is not None

        for dst in dst_to_marker:
            # Can only unroll transform with all axes keyed
            if not all(is_keyed(dst[ch]) for ch in ("rx", "ry", "rz")):
                continue

            rotate_channels += ["%s.rx" % dst]
            rotate_channels += ["%s.ry" % dst]
            rotate_channels += ["%s.rz" % dst]

        cmds.rotationInterpolation(rotate_channels, c="quaternionSlerp")
        cmds.rotationInterpolation(rotate_channels, c="none")

    @internal.with_undo_chunk
    def euler_filter():
        """Unroll rotations by applying a euler filter"""
        rotate_curves = []

        def is_keyed(plug):
            return plug.input(type="animCurveTA") is not None

        for dst in dst_to_marker:
            # Can only unroll transform with all axes keyed
            if not all(is_keyed(dst[ch]) for ch in ("rx", "ry", "rz")):
                continue

            for channel in ("rx", "ry", "rz"):
                rotate_curves += [dst[channel].input().name()]

        cmds.filterCurve(rotate_curves, filter="euler")

    markers = find_inputs(solver)
    dst_to_marker, dst_to_offset = find_destinations()
    cache = {marker: {} for marker in markers}

    with internal.Timer("simulate") as t1:
        for message, progress in simulate():
            yield (message, progress * 0.50)

    marker_to_dagnode = generate_kinematic_hierarchy(solver)

    with internal.Timer("generate") as t2:
        for message, progress in generate(marker_to_dagnode):
            yield (message, 50 + progress * 0.10)

    with internal.Timer("constrain") as t3:
        for message, progress in constrain(marker_to_dagnode):
            yield (message, 60 + progress * 0.10)

    with internal.Timer("bake") as t4:
        yield ("baking", 70)
        transforms = [dst.shortest_path() for dst in dst_to_marker]
        bake(transforms)
        yield ("baking", 95)

    with internal.Timer("cleanup") as t5:
        yield ("cleaning", 96)
        cmds.delete(temp)
        yield ("cleaning", 100)

    if opts["resetMarkers"]:
        reset()

    if opts["rotationFilter"] == 1:
        euler_filter()

    elif opts["rotationFilter"] == 2:
        quat_filter()

    # Restore time
    cmdx.current_time(initial_time)

    for timer in (t1, t2, t3, t4, t5):
        log.debug("%s = %.4fms" % (timer.name, timer.ms))


def record2(solver, opts=None):
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
        "resetMarkers": False,
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

    with internal.Timer() as sim_timer:
        for status in simulate():
            yield (status[0], status[1] * 0.50)

    if not opts["includeKinematic"]:
        initial_keyframe()
        compute_transitions()

    with internal.Timer() as write_timer:
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

    log.debug("Simulated in %.2f ms" % sim_timer.ms)
    log.debug("Wrote in %.2f ms" % write_timer.ms)


def snap2(solver, opts=None):
    """Snap animation to simulation"""

    opts = opts or {}
    opts = dict({
        "include": None,
        "exclude": None,
        "includeKinematic": True,
        "ignoreJoints": True,
        "maintainOffset": True,
    }, **opts)

    include = {t: True for t in opts["include"]} if opts["include"] else {}
    markers = []

    def find_inputs(solver):
        for entity in [el.input() for el in solver["inputStart"]]:
            if not entity:
                continue

            if entity.isA("rdMarker"):
                markers.append(entity)

            elif entity.isA("rdGroup"):
                markers.extend(el.input() for el in entity["inputStart"])

            elif entity.isA("rdSolver"):
                # A solver will have markers and groups of its own
                # that we need to iterate over again.
                find_inputs(entity)

    find_inputs(solver)

    # In case we cannot sort by evaluation order, this will be
    # our fallback. A decent but not 100% reliable outcome.
    markers = internal.sort_by_parent(markers)

    dsts = []
    dst_to_marker = {}
    for marker in markers:
        for index, el in enumerate(marker["dst"]):
            dst = el.input()

            if not dst:
                continue

            if not dst.isA(cmdx.kDagNode):
                continue

            if opts["ignoreJoints"] and dst.isA(cmdx.kJoint):
                continue

            # Filter out unwanted nodes
            if include and dst not in include:
                continue

            dsts.append(dst)
            dst_to_marker[dst] = marker

    try:
        dsts = internal.sort_by_evaluation_order(dsts)
    except RuntimeError:
        log.warning(
            "Could to reliably detect evaluation order, "
            "try re-running this command with either "
            "Parallel or Serial evaluation modes for "
            "better results."
        )

    for dst in dsts:
        marker = dst_to_marker[dst]
        output_matrix = marker["outputMatrix"].as_matrix()

        record_t = marker["recordTranslation"].read()
        record_r = marker["recordRotation"].read()

        # Nothing to do.
        if not any([record_t, record_r]):
            continue

        local_matrix = output_matrix

        if opts["maintainOffset"]:
            offset = marker["offsetMatrix"][index].as_matrix()
            local_matrix = offset.inverse() * output_matrix

        t, r = get_local_pos_rot(local_matrix, dst)

        with cmdx.DagModifier() as mod:
            if record_t:
                mod.try_set_attr(dst["tx"], t.x)
                mod.try_set_attr(dst["ty"], t.y)
                mod.try_set_attr(dst["tz"], t.z)

            if record_r:
                mod.try_set_attr(dst["rx"], r.x)
                mod.try_set_attr(dst["ry"], r.y)
                mod.try_set_attr(dst["rz"], r.z)


def cache(solvers):
    """Persistently store the simulated result of the `solvers`

    Use this to scrub the timeline both backwards and forwards without
    resimulating anything.

    """

    # Remember where we came from
    initial_time = cmdx.current_time()

    for solver in solvers:
        start_time = solver["_startTime"].asTime()

        # Clear existing cache
        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], 0)

        # Special case of caching whilst standing on the start time.
        if initial_time == start_time:
            next_time = start_time + cmdx.om.MTime(1, cmdx.TimeUiUnit())
            # Ensure start frame is visited from a frame other than
            # the start frame, as that's when non-keyed plugs are dirtied
            #
            # |   |   |   |   |   |
            # |===|---------------|
            # <---
            # --->--->--->--->--->
            #
            cmdx.current_time(next_time)
            solver["currentState"].read()

        cmdx.current_time(start_time)
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

    # Restore where we came from
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


def retarget(marker, transform, opts=None):
    """Retarget `marker` to `transform`

    When recording, write simulation from `marker` onto `transform`,
    regardless of where it is assigned.

    """

    opts = dict({
        "append": False,
    }, **(opts or {}))

    with cmdx.DGModifier() as mod:
        if not opts["append"]:
            for el in marker["dst"]:
                mod.disconnect(el, destination=False)

            for el in marker["offsetMatrix"]:
                mod.set_attr(el, cmdx.Mat4())

            mod.do_it()

        index = marker["dst"].next_available_index()
        src = marker["src"].input()
        dst = marker["dst"][index]

        mod.connect(transform["message"], dst)

        # Should we record translation?
        if all(transform["t%s" % axis].editable for axis in "xyz"):
            mod.try_set_attr(marker["recordTranslation"], True)

        # Should we record translation?
        if all(transform["r%s" % axis].editable for axis in "xyz"):
            mod.try_set_attr(marker["recordRotation"], True)

        # Store offset for recording later
        # offset = transform["worldMatrix"][0].as_matrix()
        # offset *= src["worldInverseMatrix"][0].as_matrix()
        offset = src["worldMatrix"][0].as_matrix()
        offset *= transform["worldInverseMatrix"][0].as_matrix()
        mod.set_attr(marker["offsetMatrix"][index], offset)


def _find_solver(start):
    while start and not start.isA("rdSolver"):
        start = start["startState"].output(("rdGroup", "rdSolver"))
    return start


@internal.with_undo_chunk
def create_distance_constraint(parent, child, opts=None):
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert parent["_scene"] == child["_scene"], (
        "%s and %s not part of the same solver"
    )

    solver = _find_solver(parent)
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

        mod.set_attr(con["minimum"], distance)
        mod.set_attr(con["maximum"], distance)
        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])

        commands._take_ownership(mod, con, transform)
        add_constraint(mod, con, solver)

    return con


@internal.with_undo_chunk
def create_fixed_constraint(parent, child, opts=None):
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert parent["_scene"] == child["_scene"], (
        "%s and %s not part of the same solver"
    )

    solver = _find_solver(parent)
    assert solver and solver.isA("rdSolver"), (
        "%s was not part of a solver" % parent
    )

    parent_transform = parent["src"].input(type=cmdx.kDagNode)
    child_transform = child["src"].input(type=cmdx.kDagNode)
    parent_name = parent_transform.name(namespace=False)
    child_name = child_transform.name(namespace=False)

    name = internal.unique_name("%s_to_%s" % (parent_name, child_name))
    shape_name = internal.shape_name(name)

    with cmdx.DagModifier() as mod:
        transform = mod.create_node("transform", name=name)
        con = commands._rdfixedconstraint(mod, shape_name, parent=transform)

        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])

        commands._take_ownership(mod, con, transform)
        add_constraint(mod, con, solver)

    return con


@internal.with_undo_chunk
def create_pin_constraint(child, opts=None):
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()

    solver = _find_solver(child)
    assert solver and solver.isA("rdSolver"), (
        "%s was not part of a solver" % child
    )

    source_transform = child["src"].input(type=cmdx.kDagNode)
    source_name = source_transform.name(namespace=False)
    source_tm = source_transform.transform(cmdx.sWorld)

    name = internal.unique_name("%s_rPin" % source_name)
    shape_name = internal.shape_name(name)

    with cmdx.DagModifier() as mod:
        transform = mod.create_node("transform", name=name)
        con = commands._rdpinconstraint(mod, shape_name, parent=transform)

        mod.set_attr(transform["translate"], source_tm.translation())
        mod.set_attr(transform["rotate"], source_tm.rotation())

        # Temporary means of viewport selection
        mod.set_attr(transform["displayHandle"], True)

        mod.connect(child["ragdollId"], con["marker"])
        mod.connect(transform["worldMatrix"][0], con["targetMatrix"])

        commands._take_ownership(mod, con, transform)
        add_constraint(mod, con, solver)

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


@internal.with_undo_chunk
def edit_constraint_frames(marker, opts=None):
    assert marker and marker.isA("rdMarker"), "%s was not a marker" % marker
    opts = dict({
        "addUserAttributes": False,
    }, **(opts or {}))

    parent_marker = marker["parentMarker"].connection()
    child_marker = marker

    assert parent_marker and child_marker, (
        "Unconnected constraint: %s" % marker
    )

    parent = parent_marker["src"].input(type=cmdx.kDagNode)
    child = child_marker["src"].input(type=cmdx.kDagNode)

    assert parent and child, (
        "Could not find source transform for %s and/or %s" % (
            parent_marker, child_marker)
    )

    parent = parent.parent()
    child = child.parent()

    with cmdx.DagModifier() as mod:
        parent_frame = mod.create_node("transform",
                                       name="parentFrame",
                                       parent=parent)
        child_frame = mod.create_node("transform",
                                      name="childFrame",
                                      parent=child)

        for frame in (parent_frame, child_frame):
            mod.set_attr(frame["displayHandle"], True)
            mod.set_attr(frame["displayLocalAxis"], True)

        parent_frame_tm = cmdx.Tm(marker["parentFrame"].asMatrix())
        child_frame_tm = cmdx.Tm(marker["childFrame"].asMatrix())

        parent_translate = parent_frame_tm.translation()
        child_translate = child_frame_tm.translation()

        mod.set_attr(parent_frame["translate"], parent_translate)
        mod.set_attr(parent_frame["rotate"], parent_frame_tm.rotation())
        mod.set_attr(child_frame["translate"], child_translate)
        mod.set_attr(child_frame["rotate"], child_frame_tm.rotation())

        mod.connect(parent_frame["matrix"], marker["parentFrame"])
        mod.connect(child_frame["matrix"], marker["childFrame"])

        commands._take_ownership(mod, marker, parent_frame)
        commands._take_ownership(mod, marker, child_frame)

    return parent_frame, child_frame


def generate_kinematic_hierarchy(solver):
    def find_inputs(solver):
        markers = []
        for entity in [el.input() for el in solver["inputStart"]]:
            if not entity:
                continue

            if entity.isA("rdMarker"):
                markers.append(entity)

            elif entity.isA("rdGroup"):
                markers.extend(el.input() for el in entity["inputStart"])

            elif entity.isA("rdSolver"):
                # A solver will have markers and groups of its own
                # that we need to iterate over again.
                find_inputs(entity)

        return markers

    markers = find_inputs(solver)
    marker_to_dagnode = {}
    roots = []

    def find_roots():
        for marker in markers:
            if marker["parentMarker"].input(type="rdMarker"):
                continue

            roots.append(marker)

    find_roots()

    # Recursively create childhood
    def recurse(mod, root, parent=None):
        parent = marker_to_dagnode.get(parent)
        name = root.name() + "_jnt"

        joint = mod.create_node("joint", name=name, parent=parent)
        marker_to_dagnode[root] = joint

        children = root["ragdollId"].outputs(type="rdMarker", plugs=True)

        for plug in children:
            if plug.name() != "parentMarker":
                continue

            child = plug.node()
            recurse(mod, child, root)

    with cmdx.DagModifier() as mod:
        for root in roots:
            recurse(mod, root)

    return marker_to_dagnode
