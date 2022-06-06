"""Functionality for scripting

These provide low-level access to node creation and scenegraph
manipulation and are meant for use in automation, pipeline and rigging.

These do not depend on scene selection, user preferences or Maya state.

NOTE: Every function in here MUST be undoable as-one.

"""

import logging

from maya import cmds
from .vendor import cmdx
from . import (
    internal,
    constants,
    nodes,
)

log = logging.getLogger("ragdoll")

# Exceptions thrown in this module
AlreadyAssigned = type("AlreadyAssigned", (RuntimeError,), {})
LockedTransformLimits = type("LockedTransformLimits", (RuntimeError,), {})


def create_solver(name=None, opts=None):
    r"""Create a new rdSolver node
               ____
              /    \
          /  |      |
      ---/----\____/
        /       /
    ---/-------/---
      /       /

    The solver is where the magic happens. Markers are connected to it
    and solved within; populating its .outputMatrix attribute with the
    final result.

    Arguments:
        name (str, optional): Override the default name of this solver
        opts (dict, optional): Configure the solver with these options

    Options:
        frameskipMethod (int): Method to use whenever a frame is skipped,
            can be either api.FrameskipPause or api.FrameskipIgnore

    """

    opts = dict({
        "sceneScale": 0.1,
        "frameskipMethod": constants.FrameskipPause,
    }, **(opts or {}))

    name = name or "rSolver"
    name = internal.unique_name(name)
    shape_name = internal.shape_name(name)

    with cmdx.DagModifier() as mod:
        solver_parent = mod.create_node("transform", name=name)
        solver = nodes.create("rdSolver", mod,
                              name=shape_name,
                              parent=solver_parent)

        mod.set_attr(solver["frameskipMethod"], opts["frameskipMethod"])
        mod.set_attr(solver["spaceMultiplier"], opts["sceneScale"])

        # Scale isn't relevant for the solver, what would it mean?
        mod.set_keyable(solver_parent["scaleX"], False)
        mod.set_keyable(solver_parent["scaleY"], False)
        mod.set_keyable(solver_parent["scaleZ"], False)
        mod.lock_attr(solver_parent["scaleX"])
        mod.lock_attr(solver_parent["scaleY"])
        mod.lock_attr(solver_parent["scaleZ"])

        _take_ownership(mod, solver, solver_parent)

    return solver


def assign_markers(transforms, solver, opts=None):
    """Assign markers to `transforms` belonging to `solver`

    Each marker transfers the translation and rotation of each transform
    and generates its physical equivalent, ready for recording.

    Arguments:
        transforms (list): One or more transforms to assign markers onto
        solver (rdSolver or rdGroup): Add newly created markers to this solver
        opts (dict, optional): Options, see below

    Options:
        autoLimit (bool): Transfer locked channels into physics limits
        density (enum): Auto-compute mass based on volume and a density,
            such as api.Flesh or api.Wood

    """

    assert solver and solver.is_a(("rdSolver", "rdGroup")), (
        "%s was not a solver or group" % solver
    )

    assert len(transforms) > 0, "Nothing to assign_markers to"
    assert all(isinstance(t, cmdx.Node) for t in transforms), (
        "%s was not a tuple of cmdx transforms" % str(transforms)
    )

    opts = dict({
        "density": constants.DensityFlesh,
        "autoLimit": False,
        "connect": True,
        "refit": True,
        "preventDuplicateMarker": True,
    }, **(opts or {}))

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

    parent_marker = transforms[0]["message"].output(type="rdMarker")
    refit_root = parent_marker
    markers = []

    with cmdx.DGModifier() as dgmod:
        for index, transform in enumerate(transforms):
            if opts["preventDuplicateMarker"]:
                if transform["message"].output(type="rdMarker"):
                    continue

            name = "rMarker_%s" % transform.name()
            marker = nodes.create("rdMarker", dgmod, name=name)

            try:
                child_transforms = [transforms[index + 1]]
            except IndexError:
                child_transforms = None

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

            if opts["connect"] and (parent_marker or len(transforms) > 1):
                geo = _infer_geometry(transform,
                                      parent_transform,
                                      child_transforms)

            else:
                geo = _infer_geometry(transform)

            if opts["connect"]:
                if parent_marker:
                    dgmod.connect(parent_marker["ragdollId"],
                                  marker["parentMarker"])
                else:
                    dgmod.set_attr(marker["inputType"],
                                   constants.InputKinematic)

            dgmod.set_attr(marker["shapeType"], geo.type)
            dgmod.set_attr(marker["shapeExtents"], geo.extents)
            dgmod.set_attr(marker["shapeLength"], geo.length)
            dgmod.set_attr(marker["shapeRadius"], geo.radius)
            dgmod.set_attr(marker["shapeRotation"], geo.rotation)
            dgmod.set_attr(marker["shapeOffset"], geo.offset)
            dgmod.set_attr(marker["densityType"], opts["density"])

            # Assign some random color, within some nice range
            dgmod.set_attr(marker["color"], internal.random_color())
            dgmod.set_attr(marker["version"], internal.version())

            dgmod.set_attr(marker["originMatrix"],
                           transform["worldMatrix"][0].as_matrix())

            dgmod.connect(transform["worldMatrix"][0], marker["inputMatrix"])
            dgmod.connect(transform["rotatePivot"], marker["rotatePivot"])
            dgmod.connect(transform["rotatePivotTranslate"],
                          marker["rotatePivotTranslate"])

            # Source and destination
            dgmod.connect(transform["message"], marker["src"])
            dgmod.connect(transform["message"], marker["dst"][0])

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

            if solver.is_a("rdSolver"):
                _add_to_solver(dgmod, marker, solver)
            else:
                _add_to_group(dgmod, marker, solver)

            # Keep next_available_index() up-to-date
            dgmod.do_it()

            # Used as a basis for angular limits
            reset_constraint_frames(dgmod, marker)

            # No limits on per default
            dgmod.set_attr(marker["limitRange"], (0, 0, 0))

            if opts["autoLimit"]:
                auto_limit(dgmod, marker)

            parent_marker = marker
            markers.append(marker)

    if opts["refit"] and refit_root is not None:
        reset_shape(refit_root)

    return markers


def assign_marker(transform, solver, group=None, opts=None):
    """Convenience function for passing and recieving a single `transform`"""
    assert not isinstance(transform, (tuple, list)), (
        "`transform` should not be a list: %s" % str(transform))

    opts = dict({"connect": False}, **(opts or {}))
    return assign_markers([transform], solver, opts)[0]


def assign_environment(mesh, solver, opts=None):
    """Use the triangles of `mesh` for static collision detection

    Arguments:
        mesh (mesh): A polygonal mesh shape node
        solver (rdSolver): The solver the environment should participate in

    """

    assert mesh and mesh.is_a("mesh"), "%s was not a `mesh` type" % mesh
    assert solver and solver.is_a("rdSolver"), (
        "%s was not a rdSolver type" % solver
    )

    opts = dict({
        "visualise": False,
    }, **(opts or {}))

    with cmdx.DGModifier() as mod:
        name = mesh.parent().name(namespace=False)
        name = "rEnvironment_%s" % name
        env = nodes.create("rdEnvironment", mod, name)
        mod.connect(mesh["worldMatrix"][0], env["inputGeometryMatrix"])
        mod.connect(mesh["outMesh"], env["inputGeometry"])

        index = solver["inputStart"].next_available_index()
        mod.connect(env["startState"], solver["inputStart"][index])
        mod.connect(env["currentState"], solver["inputCurrent"][index])

    if opts["visualise"]:
        with cmdx.DagModifier() as mod:
            mesh_parent = mesh.parent()
            solver_parent = solver.parent()

            name = mesh.name()
            name = "r" + name[0].upper() + (name[1:] if len(name) > 1 else "")
            vis = mod.create_node("mesh", name=mesh.name(), parent=mesh_parent)

            mod.set_attr(vis["overrideEnabled"], True)
            mod.set_attr(vis["overrideDisplayType"], 2)  # Non-selectable

            with cmdx.DGModifier() as dgmod:
                mult = dgmod.create_node("multMatrix")
                transform = dgmod.create_node("transformGeometry")

            mod.set_attr(mult["isHistoricallyInteresting"], 0)
            mod.set_attr(transform["isHistoricallyInteresting"], 0)
            mod.set_attr(vis["isHistoricallyInteresting"], 0)

            mod.connect(mesh_parent["worldMatrix"][0], mult["matrixIn"][0])
            mod.connect(solver_parent["worldMatrix"][0], mult["matrixIn"][1])
            mod.connect(mesh_parent["wim"][0], mult["matrixIn"][2])
            mod.connect(mult["matrixSum"], transform["transform"])
            mod.connect(mesh["outMesh"], transform["inputGeometry"])
            mod.connect(transform["outputGeometry"], vis["inMesh"])

            # Assign the same shader
            shading_group = mesh["instObjGroups"][0].output()
            shading_group.add(vis)

            # # Delete these when solver is deleted
            _take_ownership(mod, env, vis)
            _take_ownership(mod, env, mult)
            _take_ownership(mod, env, transform)

    return env


def group_markers(markers, name=None):
    solver = _find_solver(markers[0])

    if name is None:
        root_transform = markers[0]["src"].input()
        name = root_transform.name(namespace=False) + "_rGroup"

    with cmdx.DagModifier() as mod:
        group = _create_group(mod, name, solver)

        for marker in markers:
            _add_to_group(mod, marker, group)

    return group


def ungroup_markers(markers):
    solver = _find_solver(markers[0])

    with cmdx.DagModifier() as mod:
        for marker in markers:
            _add_to_solver(mod, marker, solver)


def create_lollipops(markers, opts=None):
    r"""Create a NURBS control for `marker` for convenience

       ____
      \    |
       \___|
       /
      /
     /
    /

    The NURBS control will carry its own Channel Box contents, making
    it easier to spot and manipulate in a complex rig scenario.

    """

    opts = dict({
        "basicAttributes": True,
        "advancedAttributes": True,
        "groupAttributes": True,
    }, **(opts or {}))

    basic_proxy_attributes = (
        "inputType",
        "driveSpace",
        "driveStiffness",
        "driveDampingRatio",
    )

    advanced_proxy_attributes = (
        "driveAbsoluteLinear",
        "driveAbsoluteAngular",
        "driveSpaceCustom",
        "linearDamping",
        "angularDamping",
        "driveInterpolation",
        "driveAbsoluteLinearX",
        "driveAbsoluteLinearY",
        "driveAbsoluteLinearZ",
        "driveAngularAmountTwist",
        "driveAngularAmountSwing",
    )

    group_proxy_attributes = (
        "selfCollide",
        "inputType",
        "driveSpace",
        "driveStiffness",
        "driveDampingRatio",
    )

    lollipops = []

    any_attributes = (
        opts["basicAttributes"] or
        opts["advancedAttributes"] or
        opts["group_parent"]
    )

    def add_attributes(marker, lol):
        if opts["basicAttributes"] or opts["advancedAttributes"]:
            proxy = internal.UserAttributes(
                marker, lol, owner=marker)

            if opts["basicAttributes"]:
                proxy.add_divider("Marker")

                for attr in basic_proxy_attributes:
                    proxy.add(attr)

            if opts["advancedAttributes"]:
                proxy.add_divider("Advanced")

                for attr in advanced_proxy_attributes:
                    proxy.add(attr)

            proxy.do_it()

        if opts["groupAttributes"]:
            if not marker["parentMarker"].connected:
                group = marker["startState"].output(type="rdGroup")

                if group is not None:
                    proxy = internal.UserAttributes(
                        group, lol, owner=group)
                    proxy.add_divider("Group")

                    for attr in group_proxy_attributes:
                        # Avoid clashes with names on the marker
                        name = attr[0].upper() + attr[1:]
                        proxy.add(attr, long_name="group%s" % name)

                    proxy.do_it()

    with cmdx.DagModifier() as mod:
        for marker in markers:
            transform = marker["src"].input()
            name = transform.name(namespace=False)

            # R_armBlend2_JNT --> R_armBlend2
            name = name.rsplit("_", 1)[0]

            # R_armBlend2 -> R_armBlend2_MRK
            name = name + "_MRK"

            lol = mod.create_node("transform", name=name, parent=transform)

            for channel in ("translate", "rotate", "scale"):
                for axis in "XYZ":
                    mod.set_keyable(lol[channel + axis], False)

                    if channel == "translate":
                        mod.set_locked(lol[channel + axis], True)

            mod.set_keyable(lol["visibility"], False)

            mod.set_attr(lol["overrideEnabled"], True)
            mod.set_attr(lol["overrideShading"], False)
            mod.set_attr(lol["overrideColor"], constants.YellowIndex)

            # Find a suitable scale
            scale = list(sorted(marker["shapeExtents"].read()))[1]
            mod.set_attr(lol["scale"], scale * 0.25)

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
            _take_ownership(mod, marker, lol)

            # Hide from channelbox
            mod.set_attr(curve["isHistoricallyInteresting"], False)

            lollipops += [lol]

            if any_attributes:
                add_attributes(marker, lol)

    return lollipops


def auto_limit(mod, marker):
    """Automatically derive physical limits based on locked rotate channels"""

    try:
        dst = marker["dst"][0].input()

    except IndexError:
        # It's possible there is no target
        raise RuntimeError("No destination transform for %s" % marker)

    # Everything is unlocked
    if not any(dst["r" + axis].locked for axis in "xyz"):
        return

    locked = set()

    if dst["rx"].locked:
        mod.set_attr(marker["limitRangeX"], cmdx.radians(-1))
        locked.add("rx")

    if dst["ry"].locked:
        mod.set_attr(marker["limitRangeY"], cmdx.radians(-1))
        locked.add("ry")

    if dst["rz"].locked:
        mod.set_attr(marker["limitRangeZ"], cmdx.radians(-1))
        locked.add("rz")

    # In case of common locked combinations, give the remaining
    # axis a visible limit.
    if locked == {"ry", "rz"}:
        mod.set_attr(marker["limitRangeX"], cmdx.radians(45))

    if locked == {"rx", "rz"}:
        mod.set_attr(marker["limitRangeY"], cmdx.radians(45))

    if locked == {"rx", "ry"}:
        mod.set_attr(marker["limitRangeZ"], cmdx.radians(45))


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


def link_solver(a, b, opts=None):
    """Link solver `a` with `b`

    This will make `a` part of `b`, allowing markers to interact.

    Arguments:
        a (rdSolver): The "child" solver
        b (rdSolver): The "parent" solver

    Returns:
        Nothing

    """

    assert a and a.isA("rdSolver"), "%s was not a solver" % a
    assert b and b.isA("rdSolver"), "%s was not a solver" % b

    with cmdx.DagModifier() as mod:
        index = b["inputStart"].next_available_index()
        mod.connect(a["startState"], b["inputStart"][index])
        mod.connect(a["currentState"], b["inputCurrent"][index])

        # Make it obvious which is main
        mod.try_set_attr(a.parent()["visibility"], False)


def unlink_solver(solver, opts=None):
    """Unlink `solver`

    From any other solver it may be connected to.

    Arguments:
        a (rdSolver): The solver to unlink from any other solver

    Returns:
        Nothing

    """

    assert solver and solver.isA("rdSolver"), "%s was not a solver" % solver
    linked_to = solver["startState"].output(type="rdSolver", plug="inputStart")

    assert linked_to, "%s was not linked" % solver

    with cmdx.DagModifier() as mod:
        mod.disconnect(solver["startState"], linked_to)
        mod.disconnect(solver["currentState"], linked_to)

        mod.try_set_attr(solver.parent()["visibility"], True)


def retarget_marker(marker, transform, opts=None):
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
        offset = src["worldMatrix"][0].as_matrix()
        offset *= transform["worldInverseMatrix"][0].as_matrix()
        mod.set_attr(marker["offsetMatrix"][index], offset)


def untarget_marker(marker, opts=None):
    """Remove all recording targets from `marker`"""

    with cmdx.DGModifier() as mod:
        for dst in marker["dst"]:
            other = dst.input(plug=True)
            mod.disconnect(dst, other)


def reparent_marker(child, new_parent, opts=None):
    """Make `new_parent` the new parent of `child`

    Arguments:
        child (rdMarker): The marker whose about to have its parent changed
        new_parent (rdMarker): The new parent of `child`

    """

    with cmdx.DGModifier() as mod:
        mod.connect(new_parent["ragdollId"], child["parentMarker"])


def unparent_marker(child, opts=None):
    """Remove parent from `child`

    Meaning `child` will be a free marker, without a parent.

    """

    old_parent = child["parentMarker"].input(type="rdMarker", plug=True)

    if not old_parent:
        log.warning("%s had no parent to remove" % child)
        return False

    with cmdx.DGModifier() as mod:
        mod.disconnect(child["parentMarker"], old_parent)

    return True


def create_ground(solver, options=None):
    """Create a ground plane, connected to `solver`

    It'll have the size of the viewport grid.

    Arguments:
        solver (rdSolver): Assign ground to this solver

    Returns:
        rdMarker: Newly created marker of the newly created polyPlane

    """

    grid_size = cmds.optionVar(query="gridSize")

    # In headless, or a fresh Maya, there is no grid size
    if not grid_size or grid_size < 0.001:
        grid_size = 10

    plane, gen = map(cmdx.encode, cmds.polyPlane(
        name="rGround",
        width=grid_size * 2,
        height=grid_size * 2,
        subdivisionsHeight=1,
        subdivisionsWidth=1,
        axis=cmdx.up_axis()
    ))

    marker = assign_marker(plane, solver)

    with cmdx.DagModifier() as mod:
        mod.set_attr(marker["inputType"], constants.InputKinematic)
        mod.set_attr(marker["displayType"], constants.DisplayWire)
        mod.set_attr(marker["densityType"], constants.DensityWood)

        mod.set_attr(plane["overrideEnabled"], True)
        mod.set_attr(plane["overrideShading"], False)
        mod.set_attr(plane["overrideColor"], constants.WhiteIndex)

        _take_ownership(mod, marker, plane)
        _take_ownership(mod, marker, gen)

    return marker


def _same_solver(a, b):
    a_scene = cmds.ragdollInfo(str(a), scene=True)
    b_scene = cmds.ragdollInfo(str(b), scene=True)
    return a_scene == b_scene


@internal.with_undo_chunk
def create_distance_constraint(parent, child, opts=None):
    """Create a new distance constraint between `parent` and `child`"""
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert _same_solver(parent, child), (
        "%s and %s not part of the same solver" % (parent, child)
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
        con = nodes.create("rdDistanceConstraint",
                           mod, shape_name, parent=transform)

        mod.set_attr(con["minimum"], distance)
        mod.set_attr(con["maximum"], distance)

        # Inherit the rotate pivot
        mod.set_attr(con["parentOffset"],
                     parent_transform["rotatePivot"].as_vector())
        mod.set_attr(con["childOffset"],
                     child_transform["rotatePivot"].as_vector())

        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])

        _take_ownership(mod, con, transform)
        _add_constraint(mod, con, solver)

        # Constraints were originally created without taking scale
        # into account, this attribute exists only for backwards
        # compatibility and have no other reason for ever being False
        mod.set_attr(con["useScale"], True)

    return con


@internal.with_undo_chunk
def create_fixed_constraint(parent, child, opts=None):
    """Create a new fixed constraint between `parent` and `child`"""
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert _same_solver(parent, child), (
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
        con = nodes.create("rdFixedConstraint",
                           mod, shape_name, parent=transform)

        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])

        _take_ownership(mod, con, transform)
        _add_constraint(mod, con, solver)

    return con


@internal.with_undo_chunk
def create_pose_constraint(parent, child, opts=None):
    assert parent.isA("rdMarker"), "%s was not a marker" % parent.type()
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()
    assert _same_solver(parent, child), (
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
        con = nodes.create("rdPinConstraint",
                           mod, shape_name, parent=transform)

        mod.set_attr(transform["translate"], child_transform.translation())
        mod.set_attr(transform["rotate"], child_transform.rotation())

        # Temporary means of viewport selection
        mod.set_attr(transform["displayHandle"], True)

        mod.connect(parent["ragdollId"], con["parentMarker"])
        mod.connect(child["ragdollId"], con["childMarker"])
        mod.connect(transform["worldMatrix"][0], con["targetMatrix"])

        _take_ownership(mod, con, transform)
        _add_constraint(mod, con, solver)

    return con


@internal.with_undo_chunk
def create_pin_constraint(child, opts=None):
    """Create a new pin constraint for `child`"""
    assert child.isA("rdMarker"), "%s was not a marker" % child.type()

    opts = dict({
        "location": constants.AnimationLocation,
    }, **(opts or {}))

    solver = _find_solver(child)
    assert solver and solver.isA("rdSolver"), (
        "%s was not part of a solver" % child
    )

    source_transform = child["src"].input(type=cmdx.kDagNode)
    source_name = source_transform.name(namespace=False)
    source_tm = source_transform.transform(cmdx.sWorld)

    if opts["location"] == constants.SimulationLocation:
        if cmds.ragdollLicence(isNonCommercial=True, query=True):
            # A nont commercial licence cannot read
            # outputMatrix beyond 100 frames
            log.info(
                "Cannot create pin at simulation "
                "with a non-commercial licence"
            )
            source_tm = source_transform.transform(cmdx.sWorld)
        else:
            source_tm = cmdx.Tm(child["outputMatrix"].as_matrix())

    name = internal.unique_name("%s_rPin" % source_name)
    shape_name = internal.shape_name(name)

    with cmdx.DagModifier() as mod:
        transform = mod.create_node("transform", name=name)
        con = nodes.create("rdPinConstraint",
                           mod, shape_name, parent=transform)

        mod.set_attr(transform["translate"], source_tm.translation())
        mod.set_attr(transform["rotate"], source_tm.rotation())

        # More suitable default values
        mod.set_attr(con["linearStiffness"], 0.01)
        mod.set_attr(con["angularStiffness"], 0.01)

        # Temporary means of viewport selection
        mod.set_attr(transform["displayHandle"], True)

        mod.connect(child["ragdollId"], con["childMarker"])
        mod.connect(transform["worldMatrix"][0], con["targetMatrix"])

        _take_ownership(mod, con, transform)
        _add_constraint(mod, con, solver)

        mod.do_it()

        if opts["location"] == constants.ConstrainedLocation:
            con = cmds.parentConstraint(source_transform.path(),
                                        transform.path(),
                                        maintainOffset=True)

            # Make way for pin constraint shape in Channel Box
            con = cmdx.encode(con[0])
            mod.set_attr(con["isHistoricallyInteresting"], False)

    return con


def _find_source_transform(marker):
    return marker["sourceTransform"].input(type=cmdx.kTransform)


def reset_shape(marker):
    with cmdx.DagModifier() as mod:
        parent_marker = marker["parentMarker"].input(type="rdMarker")
        child_markers = tuple(marker["ragdollId"].outputs(
            plugs="parentMarker", type="rdMarker"))

        parent = None
        children = []

        if parent_marker:
            parent = _find_source_transform(parent_marker)

        if child_markers:
            children = [
                _find_source_transform(m.node())
                for m in child_markers
            ]

        transform = marker["src"].input(type=cmdx.kTransform)

        geo = _infer_geometry(transform,
                              parent,
                              children)

        mod.set_attr(marker["shapeType"], geo.type)
        mod.set_attr(marker["shapeExtents"], geo.extents)
        mod.set_attr(marker["shapeLength"], geo.length)
        mod.set_attr(marker["shapeRadius"], geo.radius)
        mod.set_attr(marker["shapeRotation"], geo.rotation)
        mod.set_attr(marker["shapeOffset"], geo.offset)


def reset_constraint_frames(mod, marker, opts=None):
    """Reset constraint frames

    Options:
        symmetrical (bool): Keep limits visually consistent when inverted

    """

    opts = dict({
        "symmetrical": True,
    }, **(opts or {}))

    assert marker and isinstance(marker, cmdx.Node), (
        "%s was not a cmdx instance" % marker
    )

    if marker.isA("rdMarker"):
        parent = marker["parentMarker"].input(type="rdMarker")
        child = marker

    if parent is not None:
        parent_matrix = parent["inputMatrix"].as_matrix()
    else:
        # It's connected to the world
        parent_matrix = cmdx.Matrix4()

    rotate_pivot = child["rotatePivot"].as_vector()
    child_matrix = child["inputMatrix"].as_matrix()

    child_frame = cmdx.Tm()
    child_frame.translateBy(rotate_pivot)
    child_frame = child_frame.as_matrix()

    # Reuse the shape offset to determine
    # the direction in which each axis is facing.
    main_axis = child["shapeOffset"].as_vector()

    # The offset isn't necessarily only in one axis, it may have
    # small values in each axis. The largest axis is the one that
    # we are most likely interested in.
    main_axis_abs = cmdx.Vector(
        abs(main_axis.x),
        abs(main_axis.y),
        abs(main_axis.z),
    )

    largest_index = list(main_axis_abs).index(max(main_axis_abs))
    largest_axis = cmdx.Vector()
    largest_axis[largest_index] = main_axis[largest_index]

    x_axis = cmdx.Vector(1, 0, 0)
    y_axis = cmdx.Vector(0, 1, 0)

    if any(axis < 0 for axis in largest_axis):
        if largest_axis.x < 0:
            flip = cmdx.Quaternion(cmdx.pi, y_axis)

        elif largest_axis.y < 0:
            flip = cmdx.Quaternion(cmdx.pi, x_axis)

        else:
            flip = cmdx.Quaternion(cmdx.pi, x_axis)

        if opts["symmetrical"] and largest_axis.x < 0:
            flip *= cmdx.Quaternion(cmdx.pi, x_axis)

        if opts["symmetrical"] and largest_axis.y < 0:
            flip *= cmdx.Quaternion(cmdx.pi, y_axis)

        if opts["symmetrical"] and largest_axis.z < 0:
            flip *= cmdx.Quaternion(cmdx.pi, y_axis)

        child_frame = cmdx.Tm(child_frame)
        child_frame.rotateBy(flip)
        child_frame = child_frame.as_matrix()

    # Align parent matrix to wherever the child matrix is
    parent_frame = child_frame * child_matrix * parent_matrix.inverse()

    mod.set_attr(marker["limitRange"], (cmdx.pi / 4, cmdx.pi / 4, cmdx.pi / 4))
    mod.set_attr(marker["parentFrame"], parent_frame)
    mod.set_attr(marker["childFrame"], child_frame)
    mod.set_attr(marker["limitType"], 999)  # Custom


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

        _take_ownership(mod, marker, parent_frame)
        _take_ownership(mod, marker, child_frame)

    return parent_frame, child_frame


def replace_mesh(marker, mesh, opts=None):
    """Replace the 'Mesh' shape type in `marker` with `mesh`.

    Arguments:
        marker (cmdx.Node): Rigid whose mesh to replace
        mesh (cmdx.Node): Mesh to replace with
        clean (bool, optional): Remove other inputs, such as curve
            or surface node. Multiple inputs are supported, so this
            is optional. Defaults to True.

    Returns:
        Nothing

    """

    assert isinstance(marker, cmdx.Node), "%s was not a cmdx.Node" % marker
    assert isinstance(mesh, cmdx.Node), "%s was not a cmdx.Node" % mesh
    assert marker.isA("rdMarker"), "%s was not a 'rdMarker' node" % marker
    assert mesh.isA(("mesh", "nurbsCurve", "nurbsSurface")), (
        "%s must be either 'mesh', 'nurbsSurface' or 'nurbsSurface'" % mesh
    )

    # Setup default values
    opts = dict({
        "maintainOffset": True,
        "maintainHistory": True,
    }, **(opts or {}))

    # Clone input mesh. We aren't able to simply connect to the
    # transformGeometry and disconnect it, because it appears
    # to flush its data on disconnect. So we need a dedicated
    # mesh for this.
    if not opts["maintainHistory"]:
        with cmdx.DagModifier(interesting=False) as mod:
            copy = mod.create_node(mesh.type(),
                                   name=mesh.name() + "Orig",
                                   parent=mesh.parent())

            if mesh.type() == "mesh":
                a, b = "outMesh", "inMesh"

            elif mesh.type() == "nurbsCurve":
                a, b = "local", "create"

            elif mesh.type() == "nurbsSurface":
                a, b = "local", "create"

            mod.connect(mesh[a], copy[b])
            mod.do_it()
            cmds.refresh(force=True)
            mod.disconnect(copy["inMesh"])
            mod.set_attr(copy["intermediateObject"], True)

            mesh = copy

    with cmdx.DGModifier(interesting=False) as mod:
        if mesh.isA("mesh"):
            mod.connect(mesh["outMesh"], marker["inputGeometry"])

        elif mesh.isA("nurbsCurve"):
            mod.connect(mesh["local"], marker["inputGeometry"])

        elif mesh.isA("nurbsSurface"):
            mod.connect(mesh["local"], marker["inputGeometry"])

        if opts["maintainOffset"]:
            mesh_matrix = mesh["worldMatrix"][0].as_matrix()
            mesh_matrix *= marker["inputMatrix"].as_matrix().inverse()
            mod.set_attr(marker["inputGeometryMatrix"], mesh_matrix)


def toggle_channel_box_attributes(markers, opts=None):
    assert markers, "No markers were passed"

    opts = dict({
        "materialAttributes": True,
        "shapeAttributes": True,
        "limitAttributes": False,
        "advancedPoseAttributes": False,
    }, **(opts or {}))

    # Attributes to be toggled
    material_attrs = (
        "collide",
        "densityType",
        # ".mass",  # Auto-hidden when density is enabled
        "friction",
        "restitution",
        "displayType",
        "collisionGroup",
        "maxDepenetrationVelocity",  # A.k.a. Hardness
    )

    shape_attrs = (
        "shapeType",
        "shapeExtentsX",
        "shapeExtentsY",
        "shapeExtentsZ",
        "shapeLength",
        "shapeRadius",
        "shapeOffsetX",
        "shapeOffsetY",
        "shapeOffsetZ",
        "shapeRotationX",
        "shapeRotationY",
        "shapeRotationZ",
    )

    limit_attrs = (
        "limitStiffness",
        "limitDampingRatio",
        "limitRangeX",
        "limitRangeY",
        "limitRangeZ",
    )

    advanced_pose_attributes = (
        # "driveAngularAmountTwist",
        # "driveAngularAmountSwing",
        "driveAbsoluteLinear",
        "driveAbsoluteAngular",
        # "driveAbsoluteLinearX",
        # "driveAbsoluteLinearY",
        # "driveAbsoluteLinearZ",
    )

    attrs = []

    if opts["materialAttributes"]:
        attrs += material_attrs

    if opts["shapeAttributes"]:
        attrs += shape_attrs

    if opts["limitAttributes"]:
        attrs += limit_attrs

    if opts["advancedPoseAttributes"]:
        attrs += advanced_pose_attributes

    if not attrs:
        log.debug("Nothing to toggle")
        return False

    # Determine whether to show or hide attributes
    visible = markers[0][attrs[0]].channel_box

    for marker in markers:
        if not marker.is_referenced():
            for attr in attrs:
                cmds.setAttr("%s.%s" % (marker, attr), channelBox=not visible)
        else:
            # This will work, but isn't going to be saved along with the scene
            for attr in attrs:
                marker[attr].channel_box = not visible

    return not visible


def plans_from_nodes(nodes):
    plans = []
    shapes = []
    transforms = []

    for node in nodes:
        if node.is_a("rdPlan"):
            plans += [node]

        elif node.is_a(cmdx.kShape):
            transforms += [node.parent()]

        elif node.is_a(cmdx.kTransform):
            shapes += node.shapes()
            transforms += [node]

    for shape in shapes:
        if shape.is_a("rdPlan"):
            plans.append(shape)

    # Transforms, like body and feet, have an input to their translateY
    for transform in transforms:
        root = transform["ty"].input()

        for level in range(4):
            if root is not None and root.is_a("rdPlan"):
                break

            root = root.input()

        if root is not None and root.is_a("rdPlan"):
            plans += [root]

    return plans


@internal.with_timing
@internal.with_undo_chunk
def delete_locomotion(nodes, dry_run=False):
    assert isinstance(nodes, (list, tuple)), "First input must be a list"

    result = {
        "deletedRagdollNodeCount": 0,
        "deletedOwnedNodeCount": 0,
    }

    plans = plans_from_nodes(nodes)
    result["deletedRagdollNodeCount"] = len(plans)

    with cmdx.DagModifier() as mod:
        for plan in plans:
            mod.delete(plan)
            mod.do_it()

    return result


def delete_all_locomotion(dry_run=False):
    """Nuke it from orbit

    Return to simpler days, days before physics, with this one command.

    """

    all_nodetypes = (
        "rdPlan",
    )

    all_nodes = cmdx.ls(type=all_nodetypes)
    return delete_locomotion(all_nodes, dry_run=dry_run)


@internal.with_timing
@internal.with_undo_chunk
def delete_physics(nodes, dry_run=False):
    """Delete Ragdoll from anything related to `nodes`

    This will delete anything related to Ragdoll from your scenes, including
    any attributes added (polluted) onto your animation controls.

    Arguments:
        nodes (list): Delete physics from these nodes
        dry_run (bool, optional): Do not actually delete anything,
            but still run through the process and throw exceptions
            if any, and still return the results of what *would*
            have been deleted if it wasn't dry.

    """

    assert isinstance(nodes, (list, tuple)), "First input must be a list"

    result = {
        "deletedRagdollNodeCount": 0,
        "deletedOwnedNodeCount": 0,
    }

    # Include shapes in supplied nodes
    shapes = []
    for node in nodes:

        # Don't bother with underworld shapes
        if node.isA(cmdx.kShape):
            continue

        if node.isA(cmdx.kDagNode):
            shapes += node.shapes()

    # Include DG nodes too
    dgnodes = []
    for node in nodes:
        dgnodes += list(
            node["message"].outputs(
                type=("rdGroup",
                      "rdMarker",
                      "rdDistanceConstraint",
                      "rdFixedConstraint")))

    for shape in shapes:
        if shape.has_attr("outMesh"):
            dgnodes += list(shape["outMesh"].outputs(type="rdEnvironment"))

    shapes = filter(None, shapes)
    shapes = list(shapes) + nodes
    nodes = shapes + dgnodes

    all_nodetypes = (
        "rdCanvas",
        "rdDistanceConstraint",
        "rdEnvironment",
        "rdFixedConstraint",
        "rdGroup",
        "rdMarker",
        "rdPinConstraint",
        "rdSolver",
    )

    ragdoll_nodes = list(
        node for node in nodes
        if node.type() in all_nodetypes
    )

    # Nothing to do!
    if not ragdoll_nodes:
        return result

    # See whether any of the nodes are referenced, in which
    # case we don't have permission to delete those.
    for node in ragdoll_nodes:
        if node.is_referenced():
            raise internal.UserWarning(
                "Cannot Delete Referenced Nodes",
                "I can't do that.\n\n%s is referenced "
                "and **cannot** be deleted." % node.shortest_path()
            )

    # Delete nodes owned by Ragdoll nodes.
    #  _____________________       ___________________
    # |                     |     |                   |
    # | Marker              |     | Transform         |
    # |                     |     |                   |
    # |           owned [0] o<----o message           |
    # |_____________________|     |___________________|
    #
    #
    owned = list()
    for node in ragdoll_nodes:
        if not node.has_attr("owner"):
            continue

        for element in node["owner"]:
            for other in element.connections(source=True, destination=False):
                owned.append(other)

    result["deletedRagdollNodeCount"] = len(ragdoll_nodes)
    result["deletedOwnedNodeCount"] = len(owned)

    # It was just a joke, relax
    if dry_run:
        return result

    # Delete attributes first, as they may otherwise
    # disappear along with their node.
    with cmdx.DagModifier() as mod:
        for node in ragdoll_nodes + owned:
            try:
                mod.delete(node)
                mod.do_it()

            except cmdx.ExistError:
                # Deleting a shape whose parent transform has no other shape
                # automatically deletes the transform. This is shit behavior
                # that can be corrected in Maya 2022 onwards,
                # via includeParents=False
                pass

    return result


def delete_all_physics(dry_run=False):
    """Nuke it from orbit

    Return to simpler days, days before physics, with this one command.

    """

    all_nodetypes = (
        "rdCanvas",
        "rdDistanceConstraint",
        "rdEnvironment",
        "rdFixedConstraint",
        "rdGroup",
        "rdMarker",
        "rdPinConstraint",
        "rdSolver",
    )

    all_nodes = cmdx.ls(type=all_nodetypes)
    return delete_physics(all_nodes, dry_run=dry_run)


def assign_plan(body, feet, opts=None):
    opts = dict({
        "useTransform": False,
    }, **(opts or {}))

    assert (
        body and
        isinstance(body, cmdx.Node) and
        body.is_a(cmdx.kTransform)
    ), "`body` was not a transform"

    assert (
        feet and
        isinstance(feet, (tuple, list)) and
        all(foot.is_a(cmdx.kTransform) for foot in feet)
    ), "`feet` was not a tuple of transforms"

    # Determine the direction and distance to offset the end target
    body_pos = body.translation(cmdx.sWorld)
    relative_positions = []
    for foot in feet:
        foot_pos = foot.translation(cmdx.sWorld)
        relative_positions.append(foot_pos - body_pos)

    # Make sure each foot is below the character
    up = cmdx.up_axis()
    if up.y:
        up_index = 1
    else:
        up_index = 2

    assert all(
        foot.translation(cmdx.sWorld)[up_index] < body_pos[up_index]
        for foot in feet
    ), "Body is below one or more of the feet"

    # Assume 4 feet for now, in which case we want the character to move
    # along the narrowest axis.
    # .___________.
    # |           |.
    # |           | --->
    # .___________.
    #  .           .
    #   o           o
    #
    longest = cmdx.Vector(0, 0, 0)
    for position in relative_positions:
        longest.x = max(longest.x, abs(position.x))
        longest.y = max(longest.y, abs(position.y))
        longest.z = max(longest.z, abs(position.z))

    if cmdx.up_axis().y > 0:
        longest.y = 0
    else:
        longest.z = 0

    longest_value = max(longest)
    walking_axis = tuple(longest).index(longest_value)

    # Walk a few body lengths per default
    walking_distance = (
        feet[0].translation(cmdx.sWorld) - body_pos
    ).length() * 3

    end_offset = cmdx.Vector(0, 0, 0)
    end_offset[walking_axis] = walking_distance

    if len(feet) == 2:
        if up.y:
            walking_axis = 0 if walking_axis == 2 else 2
            rotation = cmdx.Quaternion(
                cmdx.Vector(1, 0, 0),
                cmdx.Vector(0, 0, 1)
            )

        else:
            walking_axis = 1 if walking_axis == 2 else 1
            rotation = cmdx.Quaternion(
                cmdx.Vector(1, 0, 0),
                cmdx.Vector(0, 1, 0)
            )

        end_offset = end_offset.rotate_by(rotation)

    print("end_offset: %s" % str(end_offset))

    outputs = []

    if up.y:
        limits = abs(relative_positions[0].y)
    else:
        limits = abs(relative_positions[0].z)

    limits *= 0.25
    limits = cmdx.Vector(1, 1, 1) * limits
    limits[walking_axis] *= 2

    duration = int((cmdx.max_time() - cmdx.min_time()).value) - 9
    duration = max(duration, 50)  # Minimum 2 seconds
    duration = min(duration, 100)

    WalkPreset = 0
    HopPreset = 1
    JumpPreset = 2
    GallopPreset = 3
    RunPreset = 4

    presets = {
        WalkPreset: (
            "001100110011",
            "110011001100"
        ),
        HopPreset: (
            "010101",
            "010101"
        ),
        JumpPreset: (
            "00111100",
            "00111100"
        ),
        GallopPreset: (
            "011011011",
            "101101101"
        ),
        RunPreset: (
            "01110111",
            "11011101"
        ),
    }

    preset = opts.get("preset", 0)
    preset = presets.get(preset, presets.get(WalkPreset))

    time = cmdx.encode("time1")

    with cmdx.DagModifier() as mod:
        name = "rPlan_%s" % body.name()
        plan_parent = mod.create_node("transform", name=name)
        rdplan = mod.createNode("rdPlan",
                                name=name + "Shape",
                                parent=plan_parent)

        mod.connect(time["outTime"], rdplan["currentTime"])

        mod.set_attr(rdplan["gravity"], up * -982)
        mod.set_attr(rdplan["duration"], duration)

        space_multiplier = 1.0

        body_tm = cmdx.Tm(body["worldMatrix"][0].as_matrix())
        body_tm.setScale(cmdx.Vector(1, 1, 1))

        # Guesstimate based on body height off the ground
        # NOTE: This won't work for any character not actually on the ground
        body_pos = body_tm.translation()

        if body_pos.y > 500:
            space_multiplier = 10

        elif body_pos.y < 50:
            space_multiplier = 0.1

        mod.set_attr(rdplan["spaceMultiplier"], space_multiplier)
        mod.set_attr(rdplan["color"], internal.random_color())
        mod.set_attr(rdplan["version"], internal.version())

        if opts["useTransform"]:
            plan_start_parent = mod.create_node("transform",
                                                name=body.name() + "_rStart")
            plan_end_parent = mod.create_node("transform",
                                              name=body.name() + "_rEnd")

            mod.set_attr(plan_start_parent["translate"], body_tm.translation())
            mod.set_attr(plan_start_parent["rotate"], body_tm.rotation())
            mod.set_attr(plan_start_parent["displayHandle"], True)
            mod.set_attr(plan_end_parent["displayHandle"], True)

            body_tm.translateBy(end_offset, cmdx.Transform)
            mod.set_attr(plan_end_parent["translate"], body_tm.translation())
            mod.set_attr(plan_end_parent["rotate"], body_tm.rotation())

            # Make some nice icons
            plan_start = mod.create_node("rdTrajectory",
                                         name=body.name() + "_rTrajShape",
                                         parent=plan_start_parent)
            plan_end = mod.create_node("rdTrajectory",
                                       name=body.name() + "_rTrajShape",
                                       parent=plan_end_parent)

            mod.connect(plan_start_parent["worldMatrix"][0],
                        rdplan["targets"][0])
            mod.connect(plan_end_parent["worldMatrix"][0],
                        rdplan["targets"][1])

            _take_ownership(mod, rdplan, plan_start)
            _take_ownership(mod, rdplan, plan_end)
            _take_ownership(mod, rdplan, plan_start_parent)
            _take_ownership(mod, rdplan, plan_end_parent)

        else:
            mod.set_attr(rdplan["targets"][0], body_tm.as_matrix())
            mod.do_it()
            body_tm.translateBy(end_offset, cmdx.sTransform)
            mod.set_attr(rdplan["targets"][1], body_tm.as_matrix())

        mod.do_it()

        outputs.append([rdplan, body])

        # Figure out defaults extents from body and feet positions
        bbox = cmdx.BoundingBox()
        bbox.expand(body_pos)
        for foot in feet:
            bbox.expand(foot.translation(cmdx.sWorld))

        extents = [bbox.width, bbox.height, bbox.depth]

        # For 2 feet, we have no thickness!
        if min(extents) < max(extents) / 4:
            extents[extents.index(min(extents))] = max(extents) / 4

        # For 1 foot, we have no depth!
        if min(extents) < max(extents) / 4:
            extents[extents.index(min(extents))] = max(extents) / 4

        mod.set_attr(rdplan["extents"], extents)

    with cmdx.DGModifier() as dgmod:
        for index, foot in enumerate(feet):
            rdfoot = dgmod.create_node("rdFoot", name=foot.name() + "_rFoot")

            foot_tm = cmdx.Tm(foot["worldMatrix"][0].as_matrix())
            foot_pos = foot_tm.translation()

            if up.y:
                foot_pos.y = 0
            else:
                foot_pos.z = 0

            foot_tm.set_translation(foot_pos)

            body_tm2 = body.transform(cmdx.sWorld)
            body_tm2.setScale(cmdx.Vector(1, 1, 1))

            tm = cmdx.Tm(
                foot_tm.as_matrix() *
                body_tm2.as_matrix().inverse()
            )

            dgmod.set_attr(rdfoot["nominalMatrix"], tm.as_matrix())

            if opts["useTransform"]:
                with cmdx.DagModifier() as mod2:
                    start_parent = mod2.create_node(
                        "transform",
                        name=foot.name() + "_rStart",
                        parent=plan_start_parent
                    )
                    end_parent = mod2.create_node(
                        "transform",
                        name=foot.name() + "_rEnd",
                        parent=plan_end_parent
                    )

                    mod2.set_attr(start_parent["translate"], tm.translation())
                    mod2.set_attr(start_parent["rotate"], tm.rotation())
                    mod2.set_attr(end_parent["translate"], tm.translation())
                    mod2.set_attr(end_parent["rotate"], tm.rotation())

                    mod2.set_attr(start_parent["displayHandle"], True)
                    mod2.set_attr(end_parent["displayHandle"], True)

                    # Nice icons
                    mod2.create_node("rdTrajectory",
                                     name=start_parent.name() + "Shape",
                                     parent=start_parent)
                    mod2.create_node("rdTrajectory",
                                     name=end_parent.name() + "Shape",
                                     parent=end_parent)

                    mod2.connect(start_parent["worldMatrix"][0],
                                 rdfoot["targets"][0])
                    mod2.connect(end_parent["worldMatrix"][0],
                                 rdfoot["targets"][1])

            else:
                start_mtx = tm.as_matrix() * rdplan["targets"][0].as_matrix()
                end_mtx = tm.as_matrix() * rdplan["targets"][1].as_matrix()

                dgmod.set_attr(rdfoot["targets"][0], start_mtx)
                dgmod.set_attr(rdfoot["targets"][1], end_mtx)

            idx = rdplan["inputStart"].next_available_index()
            dgmod.connect(rdfoot["startState"], rdplan["inputStart"][idx])
            dgmod.connect(rdfoot["currentState"], rdplan["inputCurrent"][idx])

            for a in ("min", "max"):
                attr = "%sFootDeviation" % a
                dgmod.set_attr(rdfoot[attr], limits)

            dgmod.connect(time["outTime"], rdfoot["currentTime"])

            dgmod.set_attr(rdfoot["color"], internal.random_color())
            dgmod.set_attr(rdfoot["version"], internal.version())

            # Make step sequence
            foot_index = index % len(preset)
            foot_preset = preset[foot_index]
            sequence = (foot_preset * 50)[:duration // 5]

            # Padding around start and end with foot-down
            sequence = "0" + sequence[:-2] + "0"

            steps = []
            for step in sequence:
                for repeat in range(5):
                    steps.append(bool(int(step)))

            dgmod.set_attr(rdfoot["stepSequence"], steps)
            outputs.append([rdfoot, foot])

    # Generate outputs
    with cmdx.DGModifier(interesting=False) as dgmod:
        for rdoutput, output in outputs:
            mult = dgmod.create_node("multMatrix")
            decompose = dgmod.create_node("decomposeMatrix")
            blend = dgmod.create_node("pairBlend")

            dgmod.connect(rdoutput["outputMatrix"], mult["matrixIn"][0])
            dgmod.connect(output["pim"][0], mult["matrixIn"][1])
            dgmod.connect(mult["matrixSum"], decompose["inputMatrix"])
            dgmod.connect(decompose["outputTranslate"], blend["inTranslate2"])
            dgmod.connect(decompose["outputRotate"], blend["inRotate2"])

            for axis in "XYZ":
                rotate_out = output["rotate" + axis]
                translate_out = output["translate" + axis]

                rotate_in = blend["inRotate%s1" % axis]
                translate_in = blend["inTranslate%s1" % axis]

                existing = rotate_out.input(plug=True)
                if existing is None:
                    dgmod.set_attr(rotate_in, rotate_out.read())
                else:
                    dgmod.connect(existing, rotate_in)

                existing = translate_out.input(plug=True)
                if existing is None:
                    dgmod.set_attr(translate_in, translate_out.read())
                else:
                    dgmod.connect(existing, translate_in)

                dgmod.connect(blend["outTranslate" + axis],
                              translate_out)
                dgmod.connect(blend["outRotate" + axis],
                              rotate_out)

            if not output.has_attr("blend"):
                dgmod.add_attr(output, cmdx.Double(
                    "blend", default=1, keyable=True, min=0, max=1
                ))
                dgmod.do_it()

            dgmod.connect(output["blend"], blend["weight"])

            _take_ownership(dgmod, rdoutput, mult)
            _take_ownership(dgmod, rdoutput, blend)
            _take_ownership(dgmod, rdoutput, decompose)

    # Compute initial plan
    rdplan["startState"].read()
    rdplan["outputMatrix"].as_matrix()

    return rdplan


"""

Internal helper functions

These things just help readability for the above functions,
and aren't meant for use outside of this module.

"""


def _find_solver(leaf):
    """Return solver for `leaf`

    `leaf` may be a marker or a group, and it will walk the physics
    hierarchy in reverse until it finds the first solver.

    Note that a solver may be connected to another solver, in which case
    this returns the *first* solver found.

    """

    while leaf and not leaf.isA("rdSolver"):
        leaf = leaf["startState"].output(("rdGroup", "rdSolver"))
    return leaf


def _find_geometry_from_lone_transform(root):
    """Given a transform without parent or children, figure out default shape

    Examples:
        >>> lone = cmdx.create_node("transform")
        >>> geo = _find_geometry_from_lone_transform(lone)
        >>> geo.radius
        1.0
        >>> geo.type == constants.SphereShape
        True

        >>> lone_shape, _ = map(cmdx.encode, cmds.polyCube())
        >>> geo = _find_geometry_from_lone_transform(lone_shape)
        >>> geo.type == constants.BoxShape
        True
        >>> geo.radius
        0.5
        >>> tuple(geo.extents)
        (1.0, 1.0, 1.0)

    """

    geometry = internal.Geometry()

    shape = root.shape(type=("mesh", "nurbsCurve", "nurbsSurface"))

    if shape:
        geometry = _interpret_shape(shape)
    else:
        geometry.radius = 1.0

    if root.is_a(cmdx.kJoint):
        joint_scale = cmds.jointDisplayScale(query=True)
        geometry.radius = root["radius"].read() * joint_scale

    return geometry


def _find_children(root):
    children = []

    # Consider cases where children have no distance from their parent,
    # common in offset groups without an actual offset in them. Such as
    # for organisational purposes
    #
    # | hip_grp
    # .-o offset_grp      <-- Some translation
    #   .-o hip_ctl
    #     .-o hip_loc   <-- Identity matrix
    #
    root_pos = root.translation(cmdx.sWorld)
    for child in root.children(type=root.type()):
        child_pos = child.translation(cmdx.sWorld)

        if not root_pos.is_equivalent(child_pos):
            children += [child]

    return children


def _position_incl_pivot(node, debug=False):
    """Return the final position of the translate and rotate handles

    That includes the rotate pivot, which isn't part
    of the worldspace matrix.

    """

    if node.type() == "joint":
        return node.translation(cmdx.sWorld)

    rotate_pivot = node.transformation().rotatePivot()

    world_tm = node.transform(cmdx.sWorld)
    world_tm.translateBy(rotate_pivot, cmdx.sPreTransform)

    pos = world_tm.translation()

    if debug:
        loc = cmdx.encode(cmds.spaceLocator(name=node.name())[0])
        loc["translate"] = pos

    return pos


def _length_and_orient_from_childhood(root, parent, children):
    r"""Return length and orientation from childhood

    Use the childhood to look for clues as to how a shape may
    be oriented.

    Examples:
        # A single child
        #
        # o-----------------> x
        #
        >>> parent = cmdx.create_node("joint")
        >>> child = cmdx.create_node("joint", parent=parent)
        >>> child["tx"] = 5.0
        >>> length, orient = _length_and_orient_from_childhood(
        ...     parent, None, [child])
        ...
        >>> length
        5.0

        # X is the default axis
        >>> euler = orient.as_euler_rotation()
        >>> tuple(map(int, map(cmdx.degrees, euler)))
        (0, 0, 0)

        # A Z-facing child
        #
        # o-----------------> z
        #
        >>> parent = cmdx.create_node("joint")
        >>> child = cmdx.create_node("joint", parent=parent)
        >>> child["tz"] = 2.5
        >>> length, orient = _length_and_orient_from_childhood(
        ...     parent, None, [child])
        ...
        >>> length
        2.5
        >>> euler = orient.as_euler_rotation()
        >>> tuple(map(int, map(round, map(cmdx.degrees, euler))))
        (0, -90, 0)

        # A fork in Y
        #
        # o     o  - c, d
        #  \   /
        #   \ /
        #    o     - b
        #    |
        #    o     - a
        #
        >>> a = cmdx.create_node("joint")
        >>> b = cmdx.create_node("joint", parent=a)
        >>> c = cmdx.create_node("joint", parent=b)
        >>> d = cmdx.create_node("joint", parent=b)
        >>> b["ty"] = 1
        >>> c["ty"] = 1
        >>> d["ty"] = 1
        >>> c["tx"] = 0.5
        >>> d["tx"] = -0.5
        >>> length, orient = _length_and_orient_from_childhood(
        ...     b, a, [c, d])
        ...
        >>> # Length is the hypothenuse of X and Y coordinates
        >>> #   .
        >>> #   |\
        >>> # y | \ length
        >>> #   |__\
        >>> #   x
        >>> #
        >>> # Namely: sqrt(x**2 + y**2)
        >>> "%.2f" % length == "1.12"
        True
        >>> euler = orient.as_euler_rotation()
        >>> tuple(map(int, map(round, map(cmdx.degrees, euler))))
        (0, 0, 90)

    """

    length = 0.0
    orient = cmdx.Quaternion()
    root_pos = _position_incl_pivot(root)

    # Support multi-child scenarios
    #
    #         o
    #        /
    #  o----o--o
    #        \
    #         o
    #
    positions = []
    for child in children:
        positions += [_position_incl_pivot(child)]

    pos2 = cmdx.Vector()
    for pos in positions:
        pos2 += pos
    pos2 /= len(positions)

    # Find center joint if multiple children
    #
    # o o o  <-- Which is in the middle?
    #  \|/
    #   o
    #   |
    #
    distances = []
    for pos in positions + [root_pos]:
        distances += [(pos - pos2).length()]
    center_index = distances.index(min(distances))
    center_node = (children + [root])[center_index]

    # Roots typically get this, where e.g.
    #
    #      o
    #      |
    #      o  <-- Root
    #     / \
    #    o   o
    #
    if center_node != root:
        parent = parent or root.parent(type=root.type())

        if not parent:
            # Try using grand-child instead
            parent = center_node.child(type=root.type())

        if parent:
            up = _position_incl_pivot(parent)
            up = (up - root_pos).normal()
        else:
            up = cmdx.up_axis()

        aim = (pos2 - root_pos).normal()
        cross = aim ^ up  # Make axes perpendicular
        up = cross ^ aim

        orient *= cmdx.Quaternion(cmdx.Vector(0, 1, 0), up)
        orient *= cmdx.Quaternion(orient * cmdx.Vector(1, 0, 0), aim)

        center_node_pos = _position_incl_pivot(center_node)
        length = (center_node_pos - root_pos).length()

    return length, orient


def _find_geometry_from_fork(root, children):
    r"""Encapsulate all children of a fork

          ______
    o----o-----o|
         |\     |
         | \    |
         |__o___|

    """

    assert root.is_a(cmdx.kTransform), "root must be a transform"
    assert len(children) > 1, (
        "This won't make sense with any less than 2 children"
    )

    geometry = internal.Geometry()
    geometry.radius = root["radius"].read()

    corner1, corner2 = cmdx.Point(), cmdx.Point()

    for child in children:
        pos = child.translation()

        # Find bottom-right corner
        if pos.x < corner1.x:
            corner1.x = pos.x
        if pos.y < corner1.y:
            corner1.y = pos.y
        if pos.z < corner1.z:
            corner1.z = pos.z

        # Find top-left corner
        if pos.x > corner2.x:
            corner2.x = pos.x
        if pos.y > corner2.y:
            corner2.y = pos.y
        if pos.z > corner2.z:
            corner2.z = pos.z

    bbox = cmdx.BoundingBox(corner1, corner2)
    offset = cmdx.Vector(bbox.center)
    size = cmdx.Vector(
        max([0.25, geometry.radius * 2, bbox.width]),
        max([0.25, geometry.radius * 2, bbox.height]),
        max([0.25, geometry.radius * 2, bbox.depth])
    )

    geometry.type = constants.BoxShape
    geometry.length = max(size)
    geometry.extents = size
    geometry.offset = offset
    geometry.radius = max(geometry.radius, geometry.length * 0.1)

    return geometry


def _infer_geometry(root,
                    parent=constants.Auto,
                    children=constants.Auto,
                    geometry=None):
    """Find length and orientation from `root`

    This function looks at the child and parent of any given root for clues as
    to how to orient it. Length is simply the distance between `root` and its
    first child.

    Arguments:
        root (transform): The root from which to derive length and orientation
        parent (transform, optional): Use this for direction
        children (list of transforms, optional): Use this for size
        geometry (internal.Geometry, optional): Build upon this geometry

    Examples:
        # A standalone tip joint
        >>> tip = cmdx.create_node("joint")
        >>> tip["radius"] = 1.234
        >>> geo = _infer_geometry(tip)
        >>> geo.radius
        1.234
        >>> tuple(map(int, map(cmdx.degrees, geo.offset)))
        (0, 0, 0)

        # A 2-joint chain
        #
        # o-------o  Length and offset from here
        #
        >>> a = cmdx.create_node("joint")
        >>> b = cmdx.create_node("joint", parent=a)
        >>> b["tx"] = 2.0
        >>> geo = _infer_geometry(a)
        >>> geo.type == constants.CapsuleShape
        True

    """

    geometry = geometry or internal.Geometry()
    original = root
    inverted = False

    # Automatically find children
    if children is constants.Auto:
        children = _find_children(root)

    if not (parent or children):
        return _find_geometry_from_lone_transform(root)

    # Special case of a tip without children
    #
    # o        How long are you?
    #  \              |
    #   \             v
    #    o------------o
    #
    # In this case, reuse however long the parent is
    if parent and not children:
        children = [root]
        root = parent
        parent = None
        inverted = True

    all_joints = all(child.is_a(cmdx.kJoint) for child in children)

    if children and len(children) > 1 and all_joints:
        return _find_geometry_from_fork(root, children)

    orient = cmdx.Quaternion()
    root_tm = root.transform(cmdx.sWorld)
    root_pos = _position_incl_pivot(root)
    root_scale = root_tm.scale()

    # There is a lot we can gather from the childhood
    if children:
        length, orient = _length_and_orient_from_childhood(
            root, parent, children)

        geometry.length = length
        geometry.orient = orient

    # Where there is a length, there is a radius
    #
    #  ___________  ___
    # /           \  |  radius
    # \___________/ _|_
    #
    #
    # Joints ship with a `radius` attribute, very convenient
    if root.has_attr("radius"):
        joint_scale = cmds.jointDisplayScale(query=True)
        geometry.radius = root["radius"].read() * joint_scale

    # Find Radius and Offset
    #
    #   ________________________  ___
    #  / _                      \  |
    # | / \_________.            | |  radius (1.0)
    # | \_/         |            | |
    #  \____________|___________/ _|_
    #               |
    #            offset (1, 0, 0)
    #
    if geometry.length > 0.0:
        offset = orient * cmdx.Vector(geometry.length / 2.0, 0, 0)

        # If we don't have that, try and establish one from the bounding box
        if not geometry.radius > 0.0:
            shape = root.shape(type=("mesh", "nurbsCurve", "nurbsSurface"))

            if shape:
                bbox = shape.bounding_box
                bbox = cmdx.Vector(bbox.width, bbox.height, bbox.depth)

                radius = sorted([bbox.x, bbox.y, bbox.z])

                # A bounding box will be either flat or long
                # That means 2/3 axes will be similar, and one
                # either 0 or large.
                #  ___________________
                # /__________________/|
                # |__________________|/
                #
                radius = radius[1]  # Pick middle one
                radius *= 0.5  # Width to radius
                radius *= 0.5  # Controls are typically larger than the model

            else:
                # If there's no visible geometry what so ever, we have
                # very little to go on in terms of establishing a radius.
                geometry.radius = geometry.length * 0.1

        geometry.extents = cmdx.Vector(geometry.length,
                                       geometry.radius * 2,
                                       geometry.radius * 2)

    else:
        size, center = _hierarchy_bounding_size(root)
        tm = cmdx.Tm(root_tm)

        if all(axis == 0 for axis in size):
            geometry.length = 0
            geometry.radius = 1
            geometry.extents = cmdx.Vector(1, 1, 1)

        else:
            geometry.length = size.x
            geometry.radius = min([size.y, size.z])
            geometry.extents = size

            # Embed length
            tm.translateBy(cmdx.Vector(0, size.x * -0.5, 0))

        offset = center - tm.translation()

    # Compute final shape matrix with these ingredients
    shape_tm = cmdx.Tm(translate=root_pos, rotate=geometry.orient)
    shape_tm.translateBy(offset, cmdx.sPostTransform)
    shape_tm = cmdx.Tm(shape_tm.as_matrix() * root_tm.as_matrix_inverse())

    geometry.offset = shape_tm.translation()
    geometry.rotation = shape_tm.rotation()

    # Special case of having a length but nothing else
    if geometry.length > 0 and geometry.type == constants.SphereShape:
        geometry.type = constants.CapsuleShape

    # Apply possible negative scale to shape rotation
    # Use `original` in case we're at the tip
    scale_mtx = original.transform(cmdx.sWorld).as_scale_matrix()
    shape_mtx = shape_tm.as_matrix()
    geometry.rotation = cmdx.Tm(shape_mtx * scale_mtx).rotation()

    # Take root_scale into account
    if abs(root_scale.x) <= 0:
        geometry.radius = 0
        geometry.extents.x = 0

    if abs(root_scale.y) > 0:
        geometry.extents.x /= root_scale.x
        geometry.length /= root_scale.y
    else:
        geometry.length = 0
        geometry.extents.y = 0

    if abs(root_scale.z) <= 0:
        geometry.extents.z = 0

    # Keep radius at minimum 10% of its length to avoid stick-figures
    geometry.radius = max(geometry.length * 0.1, geometry.radius)

    if not geometry.radius > 0:
        geometry.radius = 1.0

    return geometry


def _add_constraint(mod, con, solver):
    assert con["startState"].output() != solver, (
        "%s already a member of %s" % (con, solver)
    )

    index = solver["inputStart"].next_available_index()

    mod.set_attr(con["version"], internal.version())
    mod.connect(con["startState"], solver["inputStart"][index])
    mod.connect(con["currentState"], solver["inputCurrent"][index])

    # Ensure `next_available_index` is up-to-date
    mod.do_it()


def _take_ownership(mod, rdnode, node):
    """Make `rdnode` the owner of `node`"""

    try:
        plug = rdnode["owner"]
    except cmdx.ExistError:
        try:
            plug = rdnode["exclusiveNodes"]
        except cmdx.ExistError:
            raise TypeError("%s not a Ragdoll node" % rdnode)

    # Is the node already owned?
    existing_connection = node["message"].output(plug=True)
    if existing_connection and existing_connection.name() == "owner":
        mod.disconnect(node["message"], existing_connection)

    # Ensure next_available_index is up-to-date
    mod.do_it()

    index = plug.next_available_index()
    mod.connect(node["message"], plug[index])


def create_group(solver, name=None, opts=None):
    """Create a new group under `solver` with `name` and `opts`

    Arguments:
        solver (rdSolver): Owning solver of this group
        name (str, optional): A custom name for this group
        opts (dict, optional): Default attributes of this group

    Options:
        selfCollide (bool): Whether or not members of this
            group should collide with each other.

    """

    opts = dict({
        "selfCollide": False,
    }, **(opts or {}))

    with cmdx.DagModifier() as mod:
        group = _create_group(mod, name, solver)

        for key, value in opts.items():
            mod.set_attr(group[key], value)

        return group


def _create_group(mod, name, solver):
    name = internal.unique_name(name or "rGroup")
    shape_name = internal.shape_name(name)
    group_parent = mod.create_node("transform", name=name)
    group = nodes.create("rdGroup", mod,
                         name=shape_name,
                         parent=group_parent)

    index = solver["inputStart"].next_available_index()
    mod.connect(group["startState"], solver["inputStart"][index])
    mod.connect(group["currentState"],
                solver["inputCurrent"][index])

    _take_ownership(mod, group, group_parent)

    return group


def create_field(typ, opts=None):
    opts = opts or {}

    with cmdx.DagModifier() as mod:
        field = mod.create_node(typ)

        if field.has_attr("currentTime"):
            time1 = cmdx.encode("time1")
            mod.connect(time1["outTime"], field["currentTime"])

        for attr, value in opts.items():
            mod.set_attr(field[attr], value)

    cmds.select(str(field))

    return field


def affect_solver(field, solver):
    with cmdx.DagModifier() as mod:
        index = solver["inputFields"].next_available_index()
        mod.connect(field["message"], solver["inputFields"][index])

        # Delete field alongside this solver
        _take_ownership(mod, solver, field)


def _remove_membership(mod, marker):
    existing = list(marker["startState"].outputs(
        type=("rdGroup", "rdSolver"),
    ))

    for other in existing:
        mod.disconnect(marker["startState"], other["inputStart"])
        mod.disconnect(marker["currentState"], other["inputCurrent"])

    mod.do_it()

    # Delete empty
    for other in existing:
        if other["inputStart"].count() < 1:
            mod.delete(other)

    mod.do_it()


def move_to_group(marker, group):
    with cmdx.DagModifier() as mod:
        _add_to_group(mod, marker, group)


def move_to_solver(marker, solver):
    with cmdx.DagModifier() as mod:
        _add_to_solver(mod, marker, solver)


def extract_from_solver(markers):
    assert isinstance(markers, (tuple, list)), (
        "%s was not a list" % str(markers)
    )

    solvers = tuple(filter(None, {
        m["startState"].output(type=("rdSolver", "rdGroup")) for m in markers
    }))

    assert len(solvers) > 0, (
        "Markers were not part of any solver: \"%s\" "
        % ", ".join(str(m) for m in markers)
    )
    assert len(solvers) == 1, (
        "Markers must be part of the same solver: \"%s\" -> \"%s\""
        % (", ".join(str(m) for m in markers),
           ", ".join(str(s) for s in solvers))
    )

    original = list(solvers)[0]

    if original.isA("rdGroup"):
        original = original["startState"].output(type="rdSolver")

    assert original and original.isA("rdSolver"), "No solver was found"

    name = original.name(namespace=False) + "_extracted"
    new = create_solver(name, opts={
        "sceneScale": original["spaceMultiplier"].read()
    })

    with cmdx.DagModifier() as mod:
        for marker in markers:
            _add_to_solver(mod, marker, new)

            # Keep next available index up-to-date
            mod.do_it()

    return new


def merge_solvers(a, b):
    with cmdx.DagModifier() as mod:
        for el in a["inputStart"]:
            _add_to_solver(mod, el.input(), b)

            # Keep next available index up-to-date
            mod.do_it()

    # The `_add_to_solver` call automatically deletes the solver
    # once empty. But, if it isn't empty then that might indicate
    # that the inputStart and inputCurrent array attributes have
    # gotten out of sync.

    if a.exists and not a.is_referenced:
        log.warning(
            "%s is still alive, this may be a problem." % a
        )

    return True


def _add_to_group(mod, marker, group):
    _remove_membership(mod, marker)

    index = group["inputStart"].next_available_index()
    mod.connect(marker["startState"], group["inputStart"][index])
    mod.connect(marker["currentState"], group["inputCurrent"][index])
    return True


def _add_to_solver(mod, marker, solver):
    _remove_membership(mod, marker)

    index = solver["inputStart"].next_available_index()
    mod.connect(marker["startState"], solver["inputStart"][index])
    mod.connect(marker["currentState"], solver["inputCurrent"][index])
    return True


def find_geometry(root, parent=None, children=None):
    if root.is_a(cmdx.kJoint):
        return _interpret_joint(root, parent, children)

    return internal.Geometry()


def _interpret_joint(joint, parent=None, children=None):
    geo = internal.Geometry()

    # Bare essentials
    geo.radius = joint["radius"].read()
    geo.length = 0
    geo.type = constants.SphereShape

    # There is a lot we can gather from the childhood
    if not children:
        pass

    elif len(children) == 1:
        pass

    elif len(children) > 1:
        corner1, corner2 = cmdx.Point(), cmdx.Point()

        for child in children:
            pos = child.translation()

            # Find bottom-right corner
            if pos.x < corner1.x:
                corner1.x = pos.x
            if pos.y < corner1.y:
                corner1.y = pos.y
            if pos.z < corner1.z:
                corner1.z = pos.z

            # Find top-left corner
            if pos.x > corner2.x:
                corner2.x = pos.x
            if pos.y > corner2.y:
                corner2.y = pos.y
            if pos.z > corner2.z:
                corner2.z = pos.z

        bbox = cmdx.BoundingBox(corner1, corner2)
        offset = cmdx.Vector(bbox.center)
        size = cmdx.Vector(
            max(0.25, bbox.width),
            max(0.25, bbox.height),
            max(0.25, bbox.depth)
        )

        geo.length = max(size)
        geo.extents = size
        geo.offset = offset
        geo.type = constants.BoxShape
        geo.radius = joint["radius"].read()

        geo.radius = max(geo.length * 0.1, geo.radius)

    return geo


def _interpret_shape(shape):
    """Translate `shape` into marker shape attributes"""

    assert isinstance(shape, cmdx.DagNode), "%s was not a cmdx.DagNode" % shape
    assert shape.isA(cmdx.kShape), "%s was not a shape" % shape

    bbox = shape.bounding_box
    extents = cmdx.Vector(bbox.width, bbox.height, bbox.depth)
    center = cmdx.Vector(bbox.center)

    # Account for flat shapes, like a circle
    radius = extents.x
    length = max(extents.y, extents.x)

    # Account for X not necessarily being
    # represented by the width of the bounding box.
    if radius < internal.tolerance:
        radius = length * 0.5

    geo = internal.Geometry()
    geo.offset = center
    geo.extents = extents
    geo.radius = radius * 0.5
    geo.length = length

    gen = None

    # Guilty until proven innocent
    geo.type = constants.MeshShape

    if "inMesh" in shape and shape["inMesh"].connected:
        gen = shape["inMesh"].connection()

    elif "create" in shape and shape["create"].connected:
        gen = shape["create"].connection()

    if gen:
        # In case the shape is connected to a common
        # generator, like polyCube or polyCylinder

        if gen.type() == "polyCube":
            geo.type = constants.BoxShape
            geo.extents.x = gen["width"].read()
            geo.extents.y = gen["height"].read()
            geo.extents.z = gen["depth"].read()

        elif gen.type() == "polySphere":
            geo.type = constants.SphereShape
            geo.radius = gen["radius"].read()

        elif gen.type() == "polyPlane":
            geo.type = constants.BoxShape
            geo.extents.x = gen["width"].read()
            geo.extents.z = gen["height"].read()

            # Align top of box with plane
            if gen["axisY"]:
                average_size = (geo.extents.x + geo.extents.y) / 2.0
                geo.extents.y = average_size / 40.0
                geo.offset.y = -geo.extents.y / 2.0
            else:
                average_size = (geo.extents.x + geo.extents.y) / 2.0
                geo.extents.z = average_size / 40.0
                geo.offset.z = -geo.extents.z / 2.0

        elif gen.type() == "polyCylinder":
            geo.radius = gen["radius"].read()
            geo.length = gen["height"].read()

            # Align with Maya's cylinder/capsule axis
            # TODO: This doesn't account for partial values, like 0.5, 0.1, 1.0
            geo.rotation = list(map(cmdx.radians, (
                (0, 0, 90) if gen["axisY"] else
                (0, 90, 0) if gen["axisZ"] else
                (0, 0, 0)
            )))

            if gen["roundCap"]:
                geo.type = constants.CylinderShape

        elif gen.type() == "makeNurbCircle":
            geo.radius = gen["radius"]

        elif gen.type() == "makeNurbSphere":
            geo.type = constants.SphereShape
            geo.radius = gen["radius"]

        elif gen.type() == "makeNurbCone":
            geo.radius = gen["radius"]
            geo.length = gen["heightRatio"]

        elif gen.type() == "makeNurbCylinder":
            geo.type = constants.CylinderShape
            geo.radius = gen["radius"]
            geo.length = gen["heightRatio"]
            geo.rotation = list(map(cmdx.radians, (
                (0, 0, 90) if gen["axisY"] else
                (0, 90, 0) if gen["axisZ"] else
                (0, 0, 0)
            )))

    # In case of a zero-sized mesh
    if geo.radius < 0.001:
        geo.radius = 1
        geo.extents = cmdx.Vector(1, 1, 1)

    return geo


def _hierarchy_bounding_size(root):
    """Bounding size taking immediate children into account

            _________
         o |    a    |
    ---o-|-o----o----o--
         | |_________|
         |      |
        o-o    bbox of a
        | |
        | |
        o o
        | |
        | |
       -o o-

    DagNode.boundingBox on the other hand takes an entire
    hierarchy into account.

    """

    pos1 = root.translation(cmdx.sWorld)
    positions = [pos1]

    # Start by figuring out a center point
    for child in root.children(type=root.type()):
        positions += [child.translation(cmdx.sWorld)]

    # There were no children, consider the parent instead
    if len(positions) < 2:

        # It's possible the immediate parent is an empty
        # group without translation. We can't use that, so
        # instead walk the hierarchy until you find the first
        # parent with some usable translation to it.
        for parent in root.lineage():
            pos2 = parent.translation(cmdx.sWorld)

            if pos2.is_equivalent(pos1, internal.tolerance):
                continue

            # The parent will be facing in the opposite direction
            # of what we want, so let's invert that.
            pos2 -= pos1
            pos2 *= -1
            pos2 += pos1

            positions += [pos2]

            break

    # There were neither parent nor children,
    # we don't have a lot of options here.
    if len(positions) < 2:
        return (
            # No size
            cmdx.Vector(0, 0, 0),

            # Original center
            pos1
        )

    center = cmdx.Vector()
    for pos in positions:
        center += pos
    center /= len(positions)

    # Then figure out a bounding box, relative this center
    min_ = cmdx.Vector()
    max_ = cmdx.Vector()

    for pos2 in positions:
        dist = pos2 - center

        min_.x = min(min_.x, dist.x)
        min_.y = min(min_.y, dist.y)
        min_.z = min(min_.z, dist.z)

        max_.x = max(max_.x, dist.x)
        max_.y = max(max_.y, dist.y)
        max_.z = max(max_.z, dist.z)

    size = cmdx.Vector(
        max_.x - min_.x,
        max_.y - min_.y,
        max_.z - min_.z,
    )

    # Keep smallest value within some sensible range
    minimum = list(size).index(min(size))
    size[minimum] = max(size) * 0.5

    return size, center
