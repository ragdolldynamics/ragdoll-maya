from ..vendor import cmdx
from .. import commands, internal as i__


@i__.with_undo_chunk
def create(a,
           b,
           scene,
           aim_axis=None,
           up_axis=None,
           flex=0.75,
           radius=1.0):
    """Make a muscle from `a` and `b` anchor points

    Arguments:
        a (transform): Muscle attachment anchor of root
        b (transform): Muscle attachment anchor of tip

    """

    assert a and a.isA(cmdx.kTransform), "%s was not a transform" % a
    assert b and b.isA(cmdx.kTransform), "%s was not a transform" % b
    assert scene and scene.type() == "rdScene", "%s was not an rdScene" % scene

    aim_axis = aim_axis or cmdx.Vector(1, 0, 0)
    up_axis = up_axis or commands.up_axis()

    start = a.transform(cmdx.sWorld).translation()
    end = b.transform(cmdx.sWorld).translation()
    aim = (end - start).normal()
    length = (end - start).length()

    rotation = cmdx.Quat(aim_axis, aim)

    # Optional user-provided markup
    flex = a["flex"].read() if "flex" in a else flex
    radius = a["radius"].read() if "radius" in a else radius

    tm = cmdx.Tm()
    tm.setRotation(rotation)
    tm.setTranslation(start)

    # Move root start towards centre
    tm.translateBy(cmdx.Vector(length * (flex / 2), 0, 0), cmdx.sObject)

    with cmdx.DagModifier() as mod:
        root = mod.createNode("joint", name="root")
        tip = mod.createNode("joint", name="tip", parent=root)

        mod.set_attr(root["radius"], radius)
        mod.set_attr(tip["radius"], radius)

        mod.set_attr(root["translate"], tm.translation())
        mod.set_attr(root["rotate"], tm.rotation())
        mod.set_attr(tip["translateX"], length * (1 - flex))

        mod.do_it()

        muscle = commands.create_rigid(root, scene)

        # These may be connected to user attributes
        mod.smart_set_attr(muscle["linearDamping"], 2.0)
        mod.smart_set_attr(muscle["friction"], 0.0)
        mod.smart_set_attr(muscle["restitution"], 0.0)

    a_passive = a.parent().shape(type="rdRigid")
    b_passive = b.parent().shape(type="rdRigid")

    if not a_passive:
        a_passive = commands.create_passive_rigid(a.parent(), scene)

    if not b_passive:
        b_passive = commands.create_passive_rigid(b.parent(), scene)

    opts = {"maintainOffset": False}
    con1 = commands.point_constraint(a_passive, muscle, opts=opts)
    con2 = commands.point_constraint(b_passive, muscle, opts=opts)

    def parentframe_to_anchorpoints(mod):
        # Move parent frames to anchor points
        for anchor, constraint in ((a, con1), (b, con2)):
            matrix = anchor.transform(cmdx.sWorld).asMatrix()
            parent_matrix = anchor.parent().transform(cmdx.sWorld).asMatrix()
            parent_frame = matrix * parent_matrix.inverse()
            mod.set_attr(constraint["parentFrame"], parent_frame)

    def add_to_set(mod):
        try:
            collection = cmdx.encode("ragdollMuscles")
        except cmdx.ExistError:
            with cmdx.DGModifier() as mod:
                collection = mod.create_node(
                    "objectSet", name="ragdollMuscles"
                )

        collection.add(root)

    def lock_twist(mod):
        # Lock twist, the muscle should really only rotate around Y and Z
        # First we need to reorient root to aim in the direction of the muscle

        mtm = muscle.transform(cmdx.sWorld).asMatrix()
        atm = a.parent().transform(cmdx.sWorld).asMatrix()
        tm = cmdx.Tm(mtm * atm.inverse())

        pftm = cmdx.Tm(con1["parentFrame"].asMatrix())
        pftm.setRotation(tm.rotation(asQuaternion=True))
        mod.set_attr(con1["parentFrame"], pftm.asMatrix())
        mod.set_attr(con1["angularLimitX"], cmdx.radians(-1))

    with cmdx.DagModifier() as mod:

        # Move tip constraint to tip of muscle
        length = muscle["shapeLength"].read()
        child_frame = cmdx.Matrix4()
        child_frame[4 * 3] = length  # Row 4, column 3 = Translate X

        mod.set_attr(con2["childFrame"], child_frame)

        for con in (con1, con2):
            mod.set_attr(con["linearLimit"], 0.01)
            mod.set_attr(con["linearLimitStiffness"], 500)
            mod.set_attr(con["linearLimitDamping"], 10)

        parentframe_to_anchorpoints(mod)
        lock_twist(mod)
        add_to_set(mod)

    return muscle, con1, con2
