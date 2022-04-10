import logging
import traceback

from .vendor import cmdx
from . import constants, internal, commands, licence

from maya import cmds

log = logging.getLogger("ragdoll")


def record(solver, opts=None):
    """Transfer simulation from `solver` to animation land

    Options:
        start_time (int, optional): Record from this time
        end_time (int, optional): Record to this time
        include (list, optional): Record these transforms only
        exclude (list, optional): Do not record these transforms
        kinematic (bool, optional): Record kinematic frames too
        maintain_offset (bool, optional): Maintain whatever offset is
            between the source and destination transforms, default
            value is True

    """

    recorder = _Recorder(solver, opts)
    for message, progress in recorder.record():
        log.info(message)


def snap(solver, opts=None, _force=False):
    """Snap animation to simulation

    Like record() except it sets values on the current frame.
    If the translate/rotate channels are unlocked and keyed,
    and you have auto-key enabled, it'll set key too.

    """

    recorder = _Recorder(solver, opts)
    recorder.snap(_force)


def extract(solver, opts=None):
    """Generate an animated joint hierarchy from `solver`

    This will generate a new joint hierarchy and apply the full
    simulation as keyframes onto it, for a complete replica of
    the simulation in a Ragdoll-independent way.

    """

    recorder = _Recorder(solver, opts)

    for message, progress in recorder.extract():
        pass


class _Recorder(object):
    """Stateful recording class

    Recording has 5 steps.

    1. Run and store the simulation as worldspace matrices
    2. Create and apply simulation onto a new FK hierarchy as keyframes
    3. Constrain destination controls to FK hierarchy
    4. Call cmds.bakeResults()
    5. Delete constraints and FK hierarchy

    2, 3 and 5 are very wasteful and should not be necessary, and
    bakeResults does not communicate progress. But, the parent constraint
    does a few things for us we know we need, like rotate and scale pivots,
    whilst likely handling other things we don't know we need. The edgecases
    around translating from a matrix to local translate/rotate values are
    large and severe, so we use the parent constraint as a kind of buffer
    against that. Likewise, bakeResults does things we clearly have not yet
    mastered. Our approach of calling cmds.setKeyframe was 2x slower than
    bakeResults, which tells us its doing something differently.

    So todo, replace steps 2-5 with our own implementation.

    """

    def __del__(self):
        self.clean()

    def __init__(self, solver, opts=None):
        opts = dict({
            "startTime": None,
            "endTime": None,
            "include": None,
            "exclude": None,
            "toLayer": True,
            "rotationFilter": 1,
            "ignoreJoints": False,
            "resetMarkers": False,
            "experimental": False,
            "maintainOffset": constants.FromStart,
            "extractAndAttach": False,
            "includeKinematic": False,
            "protectOriginalInput": True,
            "mode": constants.RecordNiceAndSteady,
        }, **(opts or {}))

        # Make sure solver is initialised
        solver["startState"].read()

        start_time = opts["startTime"]
        end_time = opts["endTime"]
        solver_start_time = solver["_startTime"].as_time()

        if start_time is None:
            start_time = solver_start_time

        if end_time is None:
            end_time = cmdx.max_time()

        if isinstance(start_time, int):
            start_time = cmdx.time(start_time)

        if isinstance(end_time, int):
            end_time = cmdx.time(end_time)

        # We're only ever interested in whole frames
        solver_start_frame = int(solver_start_time.value)
        start_frame = int(start_time.value)
        end_frame = int(end_time.value)

        # Worst case, just do one
        if start_frame >= end_frame:
            end_frame = start_frame + 1

        end_frame += 1  # Padding, just in case

        # Pre-processing, only relevant once
        markers = _find_markers(solver)
        dst_to_marker, dst_to_offset = _find_destinations(markers, {
            "include": opts["include"] or [],
            "exclude": opts["exclude"] or [],
            "ignoreJoints": opts["ignoreJoints"]
        })

        self._cache = {marker: {} for marker in markers}

        self._solver_start_frame = solver_start_frame
        self._start_frame = start_frame
        self._end_frame = end_frame

        self._dst_to_marker = dst_to_marker
        self._dst_to_offset = dst_to_offset

        self._solver = solver
        self._markers = markers

        self._opts = opts

        # Nodes temporarily created by this class, during e.g. record
        self._temporaries = []

        # You found it!
        #
        # However, removing this check won't enable the recording
        # of more frames. Once a frame greater than 100 is attempted,
        # Ragdoll will return a translate/rotate value of 0. This
        # check is merely for your convenience.
        if not licence.commercial() and not licence.early_bird():
            if (self._end_frame - self._solver_start_frame) > 101:
                self._end_frame = self._solver_start_frame + 101

    @internal.with_undo_chunk
    def record(self):
        if self._solver_start_frame >= self._end_frame:
            raise RuntimeError(
                "Start Frame=%d is greater than End Frame=%d" %
                (self._end_frame, self._solver_start_frame)
            )

        if not self._validate_transform_limits():
            raise commands.LockedTransformLimits(
                "There were transform limits, "
                "Ragdoll cannot cope with these. See above."
            )

        self.clean()

        for progress in self._sim_to_cache():
            yield ("simulating", progress * 0.49)

        marker_to_joint = _generate_kinematic_hierarchy(self._solver)

        # Keep track of any mess we make
        def find_roots():
            roots = set()
            for joint in marker_to_joint.values():
                if joint.parent() is None:
                    roots.add(joint.shortest_path())

            return roots

        self._temporaries.extend(find_roots())

        for progress in self._cache_to_curves(marker_to_joint):
            yield ("transferring", 49 + progress * 0.10)

        # Attach uses Maya constraints. They are special, because
        # if there already is a constraint Maya will append to it,
        # rather than create one anew. We can't have that, since
        # we need to delete those on completion.
        if self._opts["protectOriginalInput"]:
            try:
                connections = self._detach(marker_to_joint)
                constraints = self._attach(marker_to_joint)
            finally:
                self._reattach(connections)

        else:
            constraints = self._attach(marker_to_joint)

        self._temporaries.extend(
            con.shortest_path() for con in constraints
        )

        yield ("baking", 60)

        self._bake()

        yield ("finishing", 95)

        if self._opts["resetMarkers"]:
            self._reset()

        try:
            if self._opts["rotationFilter"] == 1:
                _euler_filter(self._dst_to_marker.keys())
            elif self._opts["rotationFilter"] == 2:
                _quat_filter(self._dst_to_marker.keys())

        except Exception:
            # There are a ton of edge cases here, but it shouldn't
            # prevent the artist from carrying on without filtering
            pass

        self.clean()

        yield ("done", 100)

    def extract(self):
        for progress in self._sim_to_cache():
            yield ("simulating", progress * 0.50)

        marker_to_dagnode = _generate_kinematic_hierarchy(
            self._solver, tips=True, visible=True)

        for progress in self._cache_to_curves(marker_to_dagnode):
            yield ("transferring", 50 + progress * 0.50)

        if self._opts["extractAndAttach"]:
            self._attach(marker_to_dagnode)

    def snap(self, _force=False):
        if self._opts["maintainOffset"] == constants.FromStart:
            return self._snap_from_start()
        else:
            return self._snap_from_retarget()

    @property
    def is_clean(self):
        if self._temporaries:
            return False
        return True

    def clean(self):
        if not self._temporaries:
            # All clean
            return

        # Ahead of deleting tnings, ensure we're on the solver start
        # frame. Why? Because those are the values we want stored in
        # the BaseAnimation layer, if the animation was in fact
        # written to a layer.
        initial_time = cmdx.current_time()
        cmdx.current_time(self._solver_start_frame)

        cmds.delete(self._temporaries)
        cmdx.current_time(initial_time)

        self._temporaries[:] = []

    def _snap_from_start(self):
        """Maintain offset from the start frame"""

        initial_time = cmdx.current_time()
        start_frame = self._solver_start_frame
        current_frame = int(initial_time.value)

        marker_to_dagnode = _generate_kinematic_hierarchy(self._solver)
        sim_to_cache = self._sim_to_cache([current_frame, start_frame])
        cache_to_curves = self._cache_to_curves(marker_to_dagnode,
                                                [start_frame, current_frame])

        for _ in sim_to_cache:
            pass

        for _ in cache_to_curves:
            pass

        cons = self._attach(marker_to_dagnode)

        # Put a keyframe on everything with keyframes
        for dst in self._dst_to_marker:
            for channel in ("tx", "ty", "tz",
                            "rx", "ry", "rz"):
                if dst[channel].input():
                    # They may be connected but locked, or whatever
                    # else going on there. Either way, it's not important
                    try:
                        cmds.setKeyframe(dst.path(), attribute=channel)
                    except RuntimeError:
                        log.debug(traceback.format_exc())
                        log.warning(
                            "Could not keyframe %s.%s" % (dst, channel)
                        )

        temp = []
        temp.extend(str(con) for con in cons)
        temp.extend(str(node) for node in marker_to_dagnode.values())

        cmds.delete(temp)

        if self._opts["rotationFilter"] == 1:
            _euler_filter(self._dst_to_marker.keys())

        elif self._opts["rotationFilter"] == 2:
            _quat_filter(self._dst_to_marker.keys())

    def _snap_from_retarget(self, _force=False):
        marker_to_dagnode = _generate_kinematic_hierarchy(self._solver)

        # Align kinematic hierarchy to worldspace simulation
        marker_to_matrix = {}
        for marker in marker_to_dagnode.keys():
            matrix = marker["outputMatrix"].as_matrix()
            marker_to_matrix[marker] = matrix

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

        # Temporarily forcibly use the retargeted offset for now
        cons = self._attach(marker_to_dagnode)

        if _force:
            cmds.dgdirty(allPlugs=True)
            cmds.refresh(force=True)

        temp = []
        temp.extend(str(con) for con in cons)
        temp.extend(str(node) for node in marker_to_dagnode.values())

        cmds.delete(temp)

    @internal.with_timing
    def _sim_to_cache(self, _range=None):
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

        if _range is None:
            _range = range(self._solver_start_frame, self._end_frame + 1)

        initial_time = cmdx.current_time()

        # Ensure time is restored
        try:
            total = self._end_frame - self._solver_start_frame
            for frame in _range:
                if self._opts["experimental"]:
                    # This does run faster, but at what cost?
                    cmds.setAttr("time1.outTime", int(frame))
                else:
                    cmdx.current_time(cmdx.time(frame))

                if frame == self._solver_start_frame:
                    # Initialise solver
                    self._solver["startState"].read()
                else:
                    # Step simulation
                    self._solver["currentState"].read()

                # Record results
                for marker in self._markers:
                    self._cache[marker][frame] = {
                        "recordTranslation": marker["retr"].read(),
                        "recordRotation": marker["rero"].read(),
                        "outputMatrix": marker["ouma"].as_matrix(),
                        "kinematic": marker["_kinematic"].read(),
                    }

                progress = frame - self._solver_start_frame
                percentage = 100.0 * progress / total
                yield percentage

        finally:
            cmdx.current_time(initial_time)

    @internal.with_timing
    def _cache_to_curves(self, marker_to_dagnode, _range=None):
        r"""Convert worldspace matrices into translate/rotate channels

                                 ___ z
        x |______       ____    /
          |   ___\_____/____\__/
        y |--/--  \___/      \
          | /   \________     \_____ x
          |/             \__________ y
        z o--------------------------

        """

        assert self._cache, "Must call `_sim_to_cache()` first"

        total = len(marker_to_dagnode)

        if _range is None:
            _range = range(self._solver_start_frame, self._end_frame)

        # Generate animation
        progress = 0
        for marker, dagnode in marker_to_dagnode.items():

            # In the rare case of markers being part of a hierarchy
            # of other markers, that is not part of any scene. They
            # would get picked up during the kinematic_hierarchy call,
            # but not be viable to cache. Let the user know something
            # is not right
            if marker not in self._cache:
                log.warning("%s was skipped" % marker)
                continue

            parent = marker["parentMarker"].input(type="rdMarker")

            tx, ty, tz = {}, {}, {}
            rx, ry, rz = {}, {}, {}
            s = cmdx.Vector(1, 1, 1)

            for frame in _range:
                values = self._cache[marker][frame]
                matrix = values["outputMatrix"]
                parent_matrix = cmdx.Mat4()

                if parent in self._cache and _is_enabled(parent):
                    parent_matrix = self._cache[parent][frame]["outputMatrix"]

                tm = cmdx.Tm(matrix * parent_matrix.inverse())
                t = tm.translation()
                r = tm.rotation()

                tx[frame] = t.x
                ty[frame] = t.y
                tz[frame] = t.z

                rx[frame] = r.x
                ry[frame] = r.y
                rz[frame] = r.z

                if frame == self._start_frame:
                    s = tm.scale()

            with cmdx.DagModifier() as mod:
                mod.set_attr(dagnode["tx"], tx)
                mod.set_attr(dagnode["ty"], ty)
                mod.set_attr(dagnode["tz"], tz)
                mod.set_attr(dagnode["rx"], rx)
                mod.set_attr(dagnode["ry"], ry)
                mod.set_attr(dagnode["rz"], rz)
                mod.set_attr(dagnode["scale"], s)

            progress += 1
            percentage = 100 * progress / total
            yield percentage

    def _validate_transform_limits(self):
        """Ragdoll cannot cope with Maya's concept of limits"""

        limits = (
            "minRotXLimitEnable",
            "minRotYLimitEnable",
            "minRotZLimitEnable",
            "maxRotXLimitEnable",
            "maxRotYLimitEnable",
            "maxRotZLimitEnable",
        )

        enabled = set()
        for dagnode in self._dst_to_marker.keys():
            for limit in limits:
                if dagnode[limit]:
                    enabled.add((dagnode, limit))

        if not enabled:
            return True

        try:
            # Leave a breadcrumb in this rare circumstance
            log.debug(
                "Disabling native transform limits, these are unsupported:"
            )

            with cmdx.DagModifier() as mod:
                for dagnode, limit in enabled:
                    log.debug("%s.%s" % (dagnode.shortest_path(), limit))
                    mod.set_attr(dagnode[limit], False)

        except Exception as e:
            log.debug(traceback.format_exc(e))
            return False

        return True

    def _detach(self, marker_to_dagnode):
        connections = {}

        with cmdx.DagModifier() as mod:
            for dst in self._dst_to_marker:
                for channel in ("tx", "ty", "tz",
                                "rx", "ry", "rz"):
                    constraint = dst[channel].input(
                        type=("parentConstraint", "orientConstraint"),
                        plug=True
                    )

                    if constraint is not None:
                        attr = dst[channel]
                        connections[constraint] = attr
                        mod.disconnect(constraint, attr)

        return connections

    def _reattach(self, connections):
        with cmdx.DagModifier() as mod:
            for src, dst in connections.items():
                mod.connect(src, dst)

    def _attach(self, marker_to_dagnode):
        """Constrain destination controls to extracted simulated hierarchy

                 o
                 |
              o--o--o
             /   |   \
            /    |    \
           o   o-o-o   o
          /    |   |    \
         /     |   |     \
        o      |   |      o
               o   o
               |   |
               |   |
               |   |
             --o   o--

        """

        new_constraints = []

        # Maintain offset from here, markers and controls
        # are guaranteed to be aligned here.
        initial_time = cmdx.current_time()
        cmdx.current_time(self._solver_start_frame)

        for dst, marker in self._dst_to_marker.copy().items():
            src = marker_to_dagnode.get(marker, None)

            if not src:
                continue

            tm = cmdx.Tm(self._dst_to_offset[dst])

            b_tm = dst.transformation()
            b_rp = b_tm.rotatePivot(cmdx.sTransform)
            b_ro = b_tm.rotationOrientation()

            tm.setRotationOrientation(b_ro)  # A.k.a. rotateAxis
            tm.translateBy(b_rp, cmdx.sPreTransform)

            t = tm.translation(cmdx.sPostTransform)
            r = tm.rotation()

            skip_rotate = set()
            skip_translate = set()

            for chan, plug in zip("xyz", dst["rotate"]):
                if plug.locked:
                    skip_rotate.add(chan)

            for chan, plug in zip("xyz", dst["translate"]):
                if plug.locked:
                    skip_translate.add(chan)

            maintain = self._opts["maintainOffset"] == constants.FromStart

            if skip_translate != {"x", "y", "z"}:
                try:
                    pcon = cmds.parentConstraint(
                        src.shortest_path(),
                        dst.shortest_path(),

                        # Either from wherever it's being constrained
                        # or from the offset at the time of being retargeted
                        maintainOffset=maintain,

                        # Account for locked channels
                        skipTranslate=list(skip_translate) or "none",
                        skipRotate=list("xyz"),
                    )

                except RuntimeError:
                    self._dst_to_marker.pop(dst)
                    log.debug(traceback.format_exc())
                    log.info(
                        "Unable to parent constrain %s"
                        % (dst.shortest_path())
                    )
                    continue

                pcon = cmdx.encode(pcon[0])
                new_constraints.append(pcon)

                if self._opts["maintainOffset"] == constants.FromRetargeting:
                    with cmdx.DagModifier() as mod:
                        target = pcon["target"][0]
                        mod.set_attr(target["targetOffsetTranslate"], t)

            if skip_rotate != {"x", "y", "z"}:
                try:
                    ocon = cmds.orientConstraint(
                        src.shortest_path(),
                        dst.shortest_path(),

                        # Either from wherever it's being constrained
                        # or from the offset at the time of being retargeted
                        maintainOffset=maintain,

                        # Account for locked channels
                        skip=list(skip_rotate) or "none",
                    )

                except RuntimeError:
                    self._dst_to_marker.pop(dst)
                    log.debug(traceback.format_exc())
                    log.info(
                        "Unable to orient constrain %s"
                        % (dst.shortest_path())
                    )
                    continue

                ocon = cmdx.encode(ocon[0])
                new_constraints.append(ocon)

                if self._opts["maintainOffset"] == constants.FromRetargeting:
                    with cmdx.DagModifier() as mod:
                        mod.set_attr(ocon["offset"], r)

            # Pull to refresh
            dst["worldMatrix"][0].as_matrix()
            dst["translate"].read()
            dst["rotate"].read()

        cmdx.current_time(initial_time)

        return new_constraints

    @internal.with_timing
    def _bake(self, time=None):
        if time is None:
            time = (self._start_frame, self._end_frame - 1)

        kwargs = {
            "attribute": ("tx", "ty", "tz", "rx", "ry", "rz"),
            "simulation": self._opts["mode"] == constants.RecordNiceAndSteady,
            "time": time,
            "sampleBy": 1,
            "oversamplingRate": 1,
            "disableImplicitControl": True,
            "preserveOutsideKeys": False,
            "sparseAnimCurveBake": False,
            "removeBakedAttributeFromLayer": False,
            "removeBakedAnimFromLayer": False,
            "minimizeRotation": False,
            "bakeOnOverrideLayer": self._opts["toLayer"]
        }

        initial_time = cmdx.current_time()

        # The cheeky little bakeResults changes our selection
        selection = cmds.ls(selection=True)
        destinations = []

        for dst, marker in self._dst_to_marker.items():
            if not _is_enabled(marker):
                continue

            if not self._opts["includeKinematic"]:
                frames = self._cache[marker].values()
                if all(frame["kinematic"] for frame in list(frames)):
                    continue

            if not (marker["recordTranslation"].read() or
                    marker["recordRotation"].read()):
                continue

            destinations += [str(dst)]

        if destinations:
            cmds.bakeResults(*destinations, **kwargs)
        else:
            log.warning(
                "Nothing was baked\n"
                "Either everything was kinematic or markers were set "
                "to recordTranslation=Off and recordRotation=Off"
            )

        cmds.select(selection)

        # Restore time
        cmdx.current_time(initial_time)

    @internal.with_timing
    def _reset(self):
        groups = set()

        with cmdx.DagModifier() as mod:
            mod.set_attr(self._solver["cache"], 0)

            for marker in self._markers:
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


def _is_keyed(plug):
    return plug.input(type=(

        # Regular keyframe
        "animCurveTA",

        # Keyed on a layer
        "animBlendNodeAdditiveRotation",

    )) is not None


@internal.with_undo_chunk
@internal.with_timing
def _quat_filter(transforms):
    """Unroll rotations by converting to quaternions and back to euler"""
    rotate_channels = []

    for transform in transforms:
        # Can only unroll transform with all axes keyed
        if not all(_is_keyed(transform[ch]) for ch in ("rx", "ry", "rz")):
            continue

        rotate_channels += ["%s.rx" % transform]
        rotate_channels += ["%s.ry" % transform]
        rotate_channels += ["%s.rz" % transform]

    try:
        cmds.rotationInterpolation(rotate_channels, c="quaternionSlerp")
        cmds.rotationInterpolation(rotate_channels, c="none")
    except Exception:
        log.info(traceback.format_exc())
        log.warning(
            "Had trouble applying the Euler filter, "
            "check the Script Editor for details."
        )


@internal.with_undo_chunk
@internal.with_timing
def _euler_filter(transforms):
    """Unroll rotations by applying a euler filter"""
    rotate_curves = []

    for transform in transforms:
        # Can only unroll transform with all axes keyed
        if not all(_is_keyed(transform[ch]) for ch in ("rx", "ry", "rz")):
            continue

        for channel in ("rx", "ry", "rz"):
            curve = transform[channel].input()
            rotate_curves += [curve.name(namespace=True)]

    cmds.filterCurve(rotate_curves, filter="euler")


def _is_enabled(marker):
    return marker["enabled"].read() and not marker["_culled"].read()


def _generate_kinematic_hierarchy(solver,
                                  root=None,
                                  tips=False,
                                  visible=False):
    markers = _find_markers(solver)
    marker_to_dagnode = {}

    def find_roots():
        roots = set()
        for marker in markers:
            parent = marker["parentMarker"].input(type="rdMarker")
            if parent and _is_enabled(parent):
                continue

            roots.add(marker)
        return roots

    roots = find_roots() if root is None else [root]

    # Recursively create childhood
    def recurse(mod, marker, parent=None):
        if not _is_enabled(marker):
            return

        parent = marker_to_dagnode.get(parent)
        name = marker.name() + "_jnt"

        dagnode = mod.create_node("joint", name=name, parent=parent)
        marker_to_dagnode[marker] = dagnode

        children = marker["ragdollId"].outputs(type="rdMarker", plugs=True)

        if not visible and not parent:
            mod.set_attr(dagnode["visibility"], visible)

        for plug in children:
            if plug.name() != "parentMarker":
                continue

            child = plug.node()
            recurse(mod, child, marker)

    def extend_tips(mod):
        for marker, dagnode in marker_to_dagnode.items():
            child = dagnode.child()

            if child:
                continue

            offset = marker["shapeOffset"].as_vector()
            name = marker.name() + "_tip"
            joint = mod.create_node("joint", name=name, parent=dagnode)
            mod.set_attr(joint["t"], offset * 2)

    with cmdx.DagModifier() as mod:
        for root in roots:
            recurse(mod, root)

    if tips:
        with cmdx.DagModifier() as mod:
            mod.do_it()
            extend_tips(mod)

    return marker_to_dagnode


def _find_markers(solver, markers=None):
    if markers is None:
        markers = []

    for entity in [el.input() for el in solver["inputStart"]]:
        if entity is None:
            continue

        if entity.isA("rdMarker"):
            markers.append(entity)

        elif entity.isA("rdGroup"):
            for other in [el.input() for el in entity["inputStart"]]:
                if other is None:
                    continue

                markers.append(other)

        elif entity.isA("rdSolver"):
            # A solver will have markers and groups of its own
            # that we need to iterate over again.
            _find_markers(entity, markers)

    # Unique, preserving order
    markers = list(internal.unique_everseen(markers))
    markers = list(filter(None, markers))

    return markers


def _find_destinations(markers, opts=None):
    opts = dict({
        "include": None,
        "exclude": None,
        "ignoreJoints": True,
    }, **(opts or {}))

    include = opts["include"] or []
    exclude = opts["exclude"] or []

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

            # Retrieve whatever offset was associate to
            # this destination at the time of retargeting
            offset = marker["offsetMatrix"][index].as_matrix()

            dst_to_marker[dst] = marker
            dst_to_offset[dst] = offset.inverse()

    return dst_to_marker, dst_to_offset
