from .. import commands, internal, constants
from ..vendor import cmdx


def assign(transforms):
    assert len(transforms) > 0, "Nothing to assign to"

    suit = None
    time1 = cmdx.encode("time1")
    parent = transforms[0]["worldMatrix"][0].output(type="rdMarker")

    if parent:
        suit = parent["startState"].output(type="rdSuit")

        # Already got a marker
        transforms.pop(0)

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
            name = internal.unique_name("rMarker")
            marker = dgmod.create_node("rdMarker", name=name)

            try:
                children = [transforms[index + 1]]
            except IndexError:
                children = None

            if parent:
                parent_transform = parent["inputMatrix"].input()
            else:
                parent_transform = None

            geo = commands.infer_geometry(transform,
                                          parent_transform, children)

            dgmod.set_attr(marker["shapeType"], constants.CapsuleShape)
            dgmod.set_attr(marker["shapeExtents"], geo.extents)
            dgmod.set_attr(marker["shapeLength"], geo.length)
            dgmod.set_attr(marker["shapeRadius"], geo.radius)
            dgmod.set_attr(marker["shapeRotation"], geo.shape_rotation)
            dgmod.set_attr(marker["shapeOffset"], geo.shape_offset)

            # Assign some random color, within some nice range
            dgmod.set_attr(marker["color"], internal.random_color())
            dgmod.set_attr(marker["version"], internal.version())

            dgmod.connect(transform["worldMatrix"][0], marker["inputMatrix"])
            dgmod.connect(time1["outTime"], marker["currentTime"])
            dgmod.connect(suit["startTime"], marker["startTime"])

            index = suit["markers"].next_available_index()
            dgmod.connect(marker["startState"], suit["markersStart"][index])
            dgmod.connect(marker["currentState"], suit["markers"][index])

            dgmod.set_attr(marker["constraintType"], constants.SocketPreset)

            if parent is not None:
                dgmod.connect(parent["ragdollId"], marker["parentMarker"])

            parent = marker

            # Keep track of next_available_index
            dgmod.do_it()


def capture(suit, start_time=None, end_time=None, _cache=None, _anim=None):
    start_time = start_time or suit["startTime"].as_time()
    end_time = end_time or cmdx.animation_end_time()

    assert end_time > start_time, "%d must be greater than %d" % (
        end_time, start_time
    )

    # Allocate data
    markers = [el.input() for el in suit["markersStart"]]
    markers = {m.shortest_path(): m for m in markers}
    cache = _cache or {marker: {} for marker in markers}
    anim = _anim or {marker: {
        "tx": {}, "ty": {}, "tz": {},
        "rx": {}, "ry": {}, "rz": {},
    } for marker in markers}

    def simulate():
        for frame in range(int(start_time.value), int(end_time.value)):
            time = cmdx.om.MTime(frame, cmdx.TimeUiUnit())
            suit["output"].read(time=time)

            # Room for optimisation: We could easily query
            # the registry directly, there's no need to go through the node.
            # It isn't doing anything other than passing the component data
            for marker, node in markers.items():
                matrix = node["outputMatrix"].as_matrix()
                cache[marker][frame] = matrix

    def reformat():
        rotate_orders = {
            0: cmdx.om.MEulerRotation.kXYZ,
            1: cmdx.om.MEulerRotation.kYZX,
            2: cmdx.om.MEulerRotation.kZXY,
            3: cmdx.om.MEulerRotation.kXZY,
            4: cmdx.om.MEulerRotation.kYXZ,
            5: cmdx.om.MEulerRotation.kZYX
        }

        for marker, frames in cache.items():
            for frame, matrix in frames.items():
                node = markers[marker]
                transform = node.parent()

                parent = node["parentMarker"].input()
                parent = parent.shortest_path() if parent else None

                if parent in cache:
                    matrix = matrix * cache[parent][frame].inverse()

                tm = cmdx.Tm(matrix)
                t = tm.translation()

                rotate_axis = transform["rotateAxis"].as_quaternion()

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

    def transfer():
        with cmdx.DagModifier() as mod:
            for marker, channels in anim.items():
                node = markers[marker]
                transform = node.parent()

                for channel, values in channels.items():
                    if not values:
                        continue

                    mod.set_attr(transform[channel], values)
                    mod.do_it()

                mod.set_attr(node["kinematic"], True)

    simulate()
    reformat()
    transfer()

    return cache, anim
