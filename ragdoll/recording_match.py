import logging

from maya import cmds

from . import internal, recording, constants
from .vendor import cmdx

log = logging.getLogger("ragdoll")


@internal.maintain_selection
def _add_to_layer(name, pairs):
    temp = []

    # Select and add individual attributes, keyable ones only
    for pair in pairs:
        for keyable in pair["keyable"]:
            temp.append("%s.%s" % (pair["dst"], keyable))

    cmds.select(temp)

    layer = cmds.animLayer(
        name,
        override=True,
        addSelectedObjects=True,

        # A.k.a. only include translate and rotate
        excludeBoolean=True,
        excludeDynamic=True,
        excludeEnum=True,
        excludeScale=True,
        excludeVisibility=True
    )

    # Let the user blend this layer with good rotation interpolation
    cmds.setAttr(layer + ".rotationAccumulationMode", 1)

    return layer


def _is_equivalent(src_mtx,
                   dst_mtx,
                   translate_tolerance=0.001,
                   rotate_tolerance=0.01):
    dst_tm = cmdx.Tm(dst_mtx)
    dst_t = dst_tm.translation()
    dst_r = dst_tm.rotation()

    src_tm = cmdx.Tm(src_mtx)
    src_t = src_tm.translation()
    src_r = src_tm.rotation()

    t_matched = dst_t.is_equivalent(src_t, translate_tolerance)
    r_matched = dst_r.is_equivalent(src_r, rotate_tolerance)

    if t_matched and r_matched:
        return True
    else:
        return False


def _find_destinations(cache, opts=None):
    opts = dict({
        "include": None,
        "exclude": None,
        "includeDisabled": False,
        "includeKinematic": False,
    }, **(opts or {}))

    include = opts["include"] or []
    exclude = opts["exclude"] or []

    dst_to_marker = {}

    for marker in cache:
        if not opts["includeDisabled"]:
            if not recording._is_enabled(marker):
                continue

        if not (marker["recordTranslation"].read() or
                marker["recordRotation"].read()):
            continue

        if not opts["includeKinematic"]:
            frames = cache[marker].values()
            if all(frame["kinematic"] for frame in list(frames)):
                continue

        for index, el in enumerate(marker["dst"]):
            dst = el.input()

            if not dst:
                continue

            if not dst.isA(cmdx.kDagNode):
                continue

            # Filter out unwanted nodes
            if include and dst not in include:
                continue

            if exclude and dst in exclude:
                continue

            dst_to_marker[dst] = marker

    return dst_to_marker


def record_simulation(solver, opts=None):
    assert isinstance(solver, cmdx.DagNode) and solver.is_a("rdSolver")

    opts = dict({
        "startFrame": int(solver["_startTime"].as_time().value),
        "endFrame": int(cmdx.max_time().value),
        "minIterationCount": 1,
        "maxIterationCount": 1,
        "translateTolerance": 0.01,
        "rotateTolerance": 0.01,
        "include": set(),
        "keepCache": False,
        "closedLoop": False,
        "setInitialKey": True,
        "toLayer": True,
        "keyframe": True,
        "rotationFilter": constants.QuaternionFilter,

        # Internal
        "_keepSource": False,
    }, **(opts or {}))

    initial_time = cmdx.current_time()
    cmdx.current_time(opts["startFrame"])

    # Very small characters will have smaller position deltas between frames
    scene_scale = solver["spaceMultiplier"].read()
    translate_tolerance = opts["translateTolerance"] * scene_scale
    rotate_tolerance = opts["rotateTolerance"]

    recorder = recording._Recorder(solver, {
        "startTime": opts["startFrame"],
        "endTime": opts["endFrame"],
    })

    with cmdx.DagModifier() as mod:
        mod.set_attr(solver["cache"], True)

    for message, progress in recorder.extract():
        yield message, progress / 2

    marker_to_src = recorder._skeleton
    cache = recorder._cache
    dst_to_marker = _find_destinations(cache)

    def editable(attr):
        return attr.editable and attr.keyable

    # Pre-process matches for static information
    # Note: This assumes that pivots are not animated
    pairs = []
    with cmdx.DagModifier() as mod:
        cmdx.current_time(opts["startFrame"])

        for dst, marker in dst_to_marker.items():
            src = marker_to_src[marker]
            rest_imtx = src["worldMatrix"][0].as_matrix().inverse()

            # Maintain whatever offset exists between the pure FK
            # marker and the current controller.
            src_with_offset = mod.create_node("transform", parent=src)
            dst_mtx = dst["worldMatrix"][0].as_matrix()
            offset_tm = cmdx.Tm(dst_mtx * rest_imtx)
            offset_translate = offset_tm.translation()
            offset_rotate = offset_tm.rotation()
            mod.set_attr(src_with_offset["translate"], offset_translate)
            mod.set_attr(src_with_offset["rotate"], offset_rotate)

            # For debugging
            if opts["_keepSource"]:
                mod.set_attr(src_with_offset["displayHandle"], True)

            pairs.append({
                "marker": marker,
                "src": src,
                "dst": dst,
                "src_with_offset": src_with_offset,
                "include_position": any(
                    editable(dst[channel])
                    for channel in ("tx", "ty", "tz")
                ),
                "include_rotation": any(
                    editable(dst[channel])
                    for channel in ("rx", "ry", "rz")
                ),
                "keyable": set(
                    channel
                    for channel in (
                        "tx", "ty", "tz",
                        "rx", "ry", "rz"
                    ) if editable(dst[channel])
                ),
            })

    # Channels without keyframes can still get recorded onto a layer,
    # but when such a layer is deleted Maya will forget the original
    # value of said channel, resulting in pair loss for the animator.
    # This protects against that by storing the original value.
    if opts["setInitialKey"]:
        base_layer = cmds.animLayer(root=True, query=True)

        for pair in pairs:
            for channel in pair["keyable"]:
                attr = pair["dst"][channel]

                # If it's got an input connection,
                # the original value is already safe
                if attr.connected:
                    continue

                kwargs = {
                    "attribute": channel,
                    "insertBlend": False,
                }

                if base_layer:
                    kwargs["animLayer"] = base_layer

                cmds.setKeyframe(str(pair["dst"]), **kwargs)

    layer = None
    if opts["toLayer"]:
        layer = solver.parent().name() + "_layer"
        layer = _add_to_layer(layer, pairs)

    matched = set()
    frames = list(range(opts["startFrame"], opts["endFrame"] + 1))
    total = len(frames)

    for frame in frames:
        cmdx.current_time(frame)

        for it in range(opts["maxIterationCount"]):
            for pair in pairs:
                if not pair["keyable"]:
                    continue

                with internal.no_autokeyframe():
                    cmds.matchTransform(
                        str(pair["dst"]),
                        str(pair["src_with_offset"]),
                        position=pair["include_position"],
                        rotation=pair["include_position"]
                    )

                matched.add(pair["dst"])

            keep_going = (
                it > opts["minIterationCount"] and
                1 < opts["maxIterationCount"]
            )

            if keep_going:
                if all(_is_equivalent(
                       cache[p["marker"]][frame]["outputMatrix"],
                       p["dst"]["worldMatrix"][0].as_matrix(),
                       translate_tolerance, rotate_tolerance)
                       for p in pairs):
                    break

        if opts["keyframe"]:
            for pair in pairs:
                for channel in pair["keyable"]:
                    kwargs = {"attribute": channel}

                    if layer:
                        kwargs["animLayer"] = layer

                    cmds.setKeyframe(str(pair["dst"]), **kwargs)

        progress = frame - opts["startFrame"]
        percentage = 100.0 * progress / total
        yield "Recording", percentage / 2 + 50

    if opts["rotationFilter"] == constants.EulerFilter:
        recording._euler_filter(dst_to_marker.keys())
    elif opts["rotationFilter"] == constants.QuaternionFilter:
        recording._quat_filter(dst_to_marker.keys())

    cmdx.current_time(initial_time)

    if not opts["_keepSource"]:
        temp = list(str(pair["src"]) for pair in pairs)
        cmds.delete(temp)

    if not opts["keepCache"]:
        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], True)

    yield "Success", 100


def record(solver, opts=None):
    """Transfer simulation from `solver` to animation land

    Options:
        startFrame (int, optional): Record from this time
        endFrame (int, optional): Record to this time
        include (list, optional): Record these transforms only

    """

    assert solver and solver.is_a("rdSolver"), "%s was not a solver" % solver

    for message, progress in record_simulation(solver, opts):
        log.info(message)
