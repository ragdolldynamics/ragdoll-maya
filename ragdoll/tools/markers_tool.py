from .. import commands, internal, constants
from ..vendor import cmdx


def assign(transforms, suit=None):
    assert len(transforms) > 0, "Nothing to assign to"

    suit = suit or None
    time1 = cmdx.encode("time1")
    parent = transforms[0]["worldMatrix"][0].output(type="rdMarker")
    objset = cmdx.find("rMarkers")

    if not objset:
        with cmdx.DGModifier() as mod:
            objset = mod.create_node("objectSet", name="rMarkers")

    if parent:
        suit = parent["startState"].output(type="rdSuit")

        # Already got a marker
        transforms.pop(0)

    if not suit:
        # Just pick the first one
        suit = cmdx.ls(type="rdSuit")
        suit = suit[0] if suit else None

    if not suit:
        with cmdx.DagModifier() as mod:
            suit_parent = mod.create_node("transform", name="rSuit")
            suit = mod.create_node("rdSuit",
                                   name="rSuitShape",
                                   parent=suit_parent)

            mod.set_attr(suit["startTime"], cmdx.min_time())
            mod.set_attr(suit["version"], internal.version())
            mod.connect(time1["outTime"], suit["currentTime"])
            mod.connect(suit_parent["message"], suit["exclusiveNodes"][0])

    with cmdx.DGModifier() as dgmod:
        for index, transform in enumerate(transforms):
            name = internal.unique_name("rMarker_%s" % transform.name())
            marker = dgmod.create_node("rdMarker", name=name)

            try:
                children = [transforms[index + 1]]
            except IndexError:
                children = None

            if parent:
                parent_transform = parent["inputMatrix"].input()
            else:
                parent_transform = None

            # It's a limb
            if parent or len(transforms) > 1:
                geo = commands.infer_geometry(transform,
                                              parent_transform,
                                              children)
                geo.shape_type = constants.CapsuleShape

            # It's a lone object
            else:
                shape = transform.shape(type=("mesh",
                                              "nurbsCurve",
                                              "nurbsSurface"))
                if shape:
                    geo = commands._interpret_shape2(shape)
                else:
                    geo = commands.infer_geometry(transform)
                    geo.shape_type = constants.CapsuleShape

            # Make the root passive
            if len(transforms) > 1 and not parent:
                dgmod.set_attr(marker["kinematic"], True)

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

            dgmod.set_attr(marker["constraintType"], constants.SocketPreset)

            if parent is not None:
                dgmod.connect(parent["ragdollId"], marker["parentMarker"])

            parent = marker

            index = objset["dnSetMembers"].next_available_index()
            dgmod.connect(marker["message"], objset["dnSetMembers"][index])

            # Keep next_available_index() up-to-date
            dgmod.do_it()


def capture(suit,
            transforms=None,
            start_time=None,
            end_time=None,
            _cache=None,
            _anim=None):
    start_time = start_time or suit["startTime"].as_time()
    end_time = end_time or cmdx.animation_end_time()
    transforms = {t: True for t in transforms} if transforms else {}

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    # Allocate data
    markers = [el.input() for el in suit["inputMarkerStart"]]
    markers = {m.shortest_path(): m for m in markers}
    cache = _cache or {marker: {} for marker in markers}
    anim = _anim or {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}

    def simulate():
        total = int((end_time - start_time).value)
        for frame in range(int(start_time.value), int(end_time.value)):
            time = cmdx.om.MTime(frame, cmdx.TimeUiUnit())
            suit["output"].read(time=time)

            # Room for optimisation: We could easily query
            # the registry directly, there's no need to go through the node.
            # It isn't doing anything other than passing the component data
            for marker, node in markers.items():
                matrix = node["outputMatrix"].as_matrix()
                cache[marker][frame] = matrix

            yield ("simulating", 100 * float(frame) / total)

    def reformat():
        rotate_orders = {
            0: cmdx.om.MEulerRotation.kXYZ,
            1: cmdx.om.MEulerRotation.kYZX,
            2: cmdx.om.MEulerRotation.kZXY,
            3: cmdx.om.MEulerRotation.kXZY,
            4: cmdx.om.MEulerRotation.kYXZ,
            5: cmdx.om.MEulerRotation.kZYX
        }

        total = len(cache)
        current = 0
        for marker, frames in cache.items():
            for frame, matrix in frames.items():
                node = markers[marker]
                transform = node["dst"][0].input()

                # No destination transforms here, carry on
                if transform is None:
                    continue

                parent = node["parentMarker"].input()
                parent = parent.shortest_path() if parent else None

                if parent in cache:
                    matrix = matrix * cache[parent][frame].inverse()

                tm = cmdx.Tm(matrix)
                t = tm.translation()

                try:
                    rotate_axis = transform["rotateAxis"].as_quaternion()
                except cmdx.ExistError:
                    rotate_axis = cmdx.Quaternion()

                try:
                    joint_orient = transform["jointOrient"].as_quaternion()
                except cmdx.ExistError:
                    joint_orient = cmdx.Quaternion()

                quat = (cmdx.Quaternion(rotate_axis.inverse()) *
                        tm.rotation(asQuaternion=True) *
                        cmdx.Quaternion(joint_orient.inverse()))

                rotate_order = transform["rotateOrder"].read()
                rotate_order = rotate_orders[rotate_order]

                euler = cmdx.Euler.decompose(quat.as_matrix(), rotate_order)

                anim[marker]["rx"][frame] = euler.x
                anim[marker]["ry"][frame] = euler.y
                anim[marker]["rz"][frame] = euler.z

                if parent is None:
                    anim[marker]["tx"][frame] = t.x
                    anim[marker]["ty"][frame] = t.y
                    anim[marker]["tz"][frame] = t.z

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

                mod.set_attr(node["kinematic"], True)

                current += 1
                yield ("transferring", 100 * float(current) / total)

    for status in simulate():
        yield status

    for status in reformat():
        yield status

    for status in transfer():
        yield status


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
