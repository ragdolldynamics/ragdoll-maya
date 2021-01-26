from .vendor import cmdx
from . import commands


class _Link(object):
    __slots__ = ["transform", "rigid", "constraint", "previous_inputs"]

    def __init__(self, transform, rigid=None, constraint=None):
        self._transform = transform
        self._rigid = rigid
        self._constraint = constraint

        self.previous_inputs = {}

    @property
    def transform(self):
        return self._transform

    @property
    def rigid(self):
        assert self._rigid, "No rigid for %s" % self.transform
        return self._rigid

    @rigid.setter
    def rigid(self, rigid):
        assert not self._rigid
        self._rigid = rigid

    @property
    def constraint(self):
        assert self._constraint, "No constraint for %s" % self._transform
        return self._constraint

    @constraint.setter
    def constraint(self, constraint):
        assert not self._constraint
        self._constraint = constraint


class DynamicControl(object):
    r"""The Ragdoll Dynamic Control

    Add physics to any animation control.

                        /|
    /--------/----------||
    \/       \/         |/

    """

    def __init__(self, chain, scene, opts=None):
        self._links = [_Link(transform) for transform in chain]
        self._scene = scene
        self._opts = opts or {}

        self._current_index = None

        self._rigids = []
        self._previous_inputs = {}

        self._dgmod = cmdx.DGModifier()
        self._dagmod = cmdx.DagModifier()

    def do_it(self):
        def loop(func):
            parent = None
            for index, link in enumerate(self._links):
                self._current_index = index
                func(link, parent)
                parent = link

        loop(self.pre_link)
        loop(self.on_link)
        loop(self.post_link)

    def find_link(self, offset=0):
        r"""Return link along the chain, with an optional offset

         __________  __________  __________  __________
        /          \/          \/          \/          \
        \__________/\__________/\__________/\__________/
             -1          0           1            2        None
                         ^
                         |
                    current_index

        """

        assert self._current_index, "Must happen during `do_it`"

        try:
            return self._links[self._current_index + offset]
        except IndexError:
            return None

    def record_inputs(self, link):
        """Remember existing translate/rotate inputs

        These are the attributes we are taking control over. If there
        are already inputs here, we need to take case not to overwrite
        these. They could be pre-existing animation, for example.

                  arm_l_ctl
                   ______________
                  |              |
        input ----o translateX   |
                  o translateY   |
                  o translateZ   |
        input ----o rotateX      |
        input ----o rotateY      |
                  o rotateZ      |
                  |______________|

        """

        inputs = {}
        for channel in ("translate", "rotate"):
            for axis in "XYZ":
                src = link.transform[channel + axis]
                src = src.connection(plug=True, destination=False)

                if src is not None:
                    dst = "in%s%s1" % (channel.title(), axis)
                    inputs[src] = dst

        link.previous_inputs = inputs

    def constrain(self, parent, child):
        """Special orientation for a Socket Constrant

        A dynamic control is guaranteed to have a parent,
        and a possible child. We can use that to orient
        a constraint more intelligently.

        """

        con = commands.socket_constraint(parent.rigid,
                                         child.rigid,
                                         self._scene)

        # Re-orient to face the immediate neighbour,
        # whilst also taking parent into account.
        previous = self.find_link(offset=-1)
        subsequent = self.find_link(offset=1)

        aim = None
        up = None

        if subsequent:
            aim = subsequent.transform(cmdx.sWorld).translation()

        if previous:
            up = previous.transform(cmdx.sWorld).translation()

        commands.orient(con, aim, up)

        return con

    def pre_link(self, link, parent=None):
        print("Validating %s.. OK")

    def on_link(self, link, parent=None):
        if parent is None:
            return self.on_root(link)

        rigid = link.transform.shape(type="rdRigid")

        # Handle overlapping controllers, like branches
        if rigid is None:
            rigid = commands.create_active_rigid(link, self._scene)
            self._dgmod.set_attr(rigid["drawShaded"], False)
        else:
            rigid = commands.convert_rigid(rigid, passive=False)

        constraint = self.constrain(parent.rigid, rigid)
        link.constraint = constraint

        return rigid

    def post_link(self, link, parent=None):
        # Let the user manually add these, if needed
        self._dgmod.set_attr(link.constraint["angularLimitX"], 0)
        self._dgmod.set_attr(link.constraint["angularLimitY"], 0)
        self._dgmod.set_attr(link.constraint["angularLimitZ"], 0)
        self._dgmod.set_attr(link.constraint["driveStrength"], 0.5)

        name = commands._unique_name("rGuideConstraint")
        self._dgmod.rename(link.constraint, name)

        # Imprit name, so we can determine whether
        # the next one is unique or not.
        self._dgmod.do_it()

        # These are not particularly useful per default
        link.constraint["angularLimit"].keyable = False
        link.constraint["limitEnabled"].keyable = False
        link.constraint["limitStrength"].keyable = False
        link.constraint["driveEnabled"].keyable = False

        previous = self.find_link(offset=-1)
        subsequent = self.find_link(offset=1)

        geo = commands.infer_geometry(
            link, parent=previous or self._links[0].transform,
            children=[subsequent] if subsequent else False
        )

        self._dgmod.set_attr(link.rigid["shapeExtents"], geo.extents)
        self._dgmod.set_attr(link.rigid["shapeLength"], geo.length)
        self._dgmod.set_attr(link.rigid["shapeRadius"], geo.radius)
        self._dgmod.set_attr(link.rigid["shapeRotation"], geo.shape_rotation)
        self._dgmod.set_attr(link.rigid["shapeOffset"], geo.shape_offset)

        if geo.length == 0:
            self._dgmod.set_attr(link.rigid["shapeType"],
                                 commands.SphereShape)
        elif self._opts.get("useCapsules"):
            self._dgmod.set_attr(link.rigid["shapeType"],
                                 commands.CapsuleShape)

    def on_root(self, link):
        r"""Generate a new rigid for the root control

          ___________  ___ _ _
         /_ _ _ _ _ _\/
         \___________/\____ _ _


        """

        rigid = commands.create_passive_rigid(link, self._scene)

        self._dgmod.set_attr(rigid["drawShaded"], False)

        # Don't collide per default, it's most likely an
        # unsuitable shape for collisions anyway.
        self._dgmod.set_attr(rigid["collide"], False)

        child = self.find_link(offset=1)
        geo = commands.infer_geometry(link,
                                      parent=None,
                                      children=[child])

        self._dgmod.set_attr(rigid["shapeLength"], geo.length)
        self._dgmod.set_attr(rigid["shapeRadius"], geo.radius)
        self._dgmod.set_attr(rigid["shapeRotation"], geo.shape_rotation)
        self._dgmod.set_attr(rigid["shapeOffset"], geo.shape_offset)
        self._dgmod.set_attr(rigid["shapeExtents"], geo.extents)

        if link.has_attr("Ragdoll"):
            self._dgmod.delete_attr(link["Ragdoll"])
            self._dgmod.do_it()
        self._dgmod.add_attr(link, cmdx.Divider("Ragdoll"))
        commands._record_attr(link, "Ragdoll")

        self._dgmod.do_it()

        return rigid
