from ..vendor import cmdx
from .. import commands
from maya import cmds


class UndoChunk(object):
    def __init__(self, name):
        self._name = name
        cmds.undoInfo(chunkName=name,
                      openChunk=True)

    def __del__(self):
        cmds.undoInfo(chunkName=self._name,
                      closeChunk=True)


class Character(object):
    """The Ragdoll auto-rigger, a.k.a. 'autoragger'"""

    Knee = 3
    Elbow = 11
    Finger = 19
    Hand = 12
    Foot = 4
    Toe = 5
    Head = 8
    Other = 18
    Skip = "skip"  # Case insensitive
    Stop = "stop"

    def __init__(self, root, scene, opts=None):
        assert root.isA(cmdx.kJoint), "%s was not a joint" % root
        self._root = root
        self._scene = scene
        self._opts = opts or {
            "inclusive": True,
        }

    def parse(self, parent=None):
        _ = UndoChunk("Character")
        return self._parse(parent)

    def _parse(self, parent=None):
        parent = parent or self._root

        # Skip any non-joints, like empty transform offset groups
        if parent.isA(cmdx.kJoint):
            result = self.dispatch(parent, parent)

            if result == self.Stop:
                return

        for child in parent.children():
            self.parse(child)

    def dispatch(self, joint, parent=None):
        mapping = {
            self.Knee: self.on_knee,
            self.Elbow: self.on_elbow,
            self.Finger: self.on_finger,
            self.Hand: self.on_hand,
            self.Foot: self.on_foot,
            self.Toe: self.on_toe,
            self.Head: self.on_head,
        }

        inclusive = self._opts.get("inclusive", False)
        exclusive = not inclusive
        label = joint["type"].read()

        if label == self.Other:
            label = joint["otherType"].read().lower()

        if label == self.Skip:
            return self.Skip

        if exclusive and label == self.Stop:
            return self.Stop

        func = mapping.get(label, self.on_unlabelled)
        func(joint)

        if inclusive and label == self.Stop:
            return self.Stop

    def make_hinge(self, joint, parent=None):
        rigid = commands.create_rigid(joint, self._scene)

        if parent is not None:
            constraint = commands.hinge_constraint(parent, rigid, self._scene)
            commands.orient(constraint)
            commands.reorient(constraint)

            with cmdx.DagModifier() as mod:
                mod.set_attr(constraint["driveEnabled"], True)
                mod.set_attr(constraint["driveStrength"], 1)
                mod.set_attr(constraint["linearDriveStiffness"], 0)
                mod.set_attr(constraint["linearDriveDamping"], 0)

        else:
            constraint = None

        return rigid, constraint

    def make_socket(self, joint, parent=None):
        rigid = commands.create_rigid(joint, self._scene)

        if parent is not None:
            constraint = commands.socket_constraint(parent, rigid, self._scene)
            commands.orient(constraint)
        else:
            constraint = None

        return rigid, constraint

    def on_unlabelled(self, joint, parent=None):
        self.make_socket(joint, parent)

    def on_knee(self, joint, parent=None):
        print("on_knee       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_elbow(self, joint, parent=None):
        print("on_elbow      (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_finger(self, joint, parent=None):
        print("on_finger     (%s)" % joint.shortestPath())
        rigid, constraint = self.make_hinge(joint, parent)

    def on_hand(self, joint, parent=None):
        print("on_hand       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)

    def on_foot(self, joint, parent=None):
        print("on_foot       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape

    def on_toe(self, joint, parent=None):
        print("on_toe        (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape

    def on_head(self, joint, parent=None):
        print("on_head       (%s)" % joint.shortestPath())
        rigid, constraint = self.make_socket(joint, parent)
        rigid["shapeType"] = commands.BoxShape


@commands.with_undo_chunk
def create(root,
           scene,
           copy=True,
           control=True,
           inclusive=True,
           normalise_shapes=False):
    """Convert hierarchy into a character

    Arguments:
        root (joint): Starting joint for character, typically pelvis
        scene (rdScene): Scene to which newly created character belongs
        copy (bool): Make character from a duplicate of `root`,
            or connect provided `root` to physics
        control (bool): Make `root` an input control
            to copy (implies copy=True)
        inclusive (bool): Does "stop" mean before or after a labelled joint?
        normalise_shapes (bool): Retroactively resize shapes
            relative each other

    """

    assert root.type() == "joint", "%s was not a joint"
    assert scene.type() == "rdScene", "%s was not a rdScene"

    # Supported Maya-native joint labels
    Knee = 3
    Elbow = 11
    Finger = 19
    Hand = 12
    Foot = 4
    Toe = 5
    Head = 8
    Other = 18
    Skip = "skip"  # Case insensitive
    Stop = "stop"

    exclusive = not inclusive

    # Can't do control without copying first
    if not copy:
        control = False

    # Protect against duplicate rigid-making
    self = create
    self.done = []

    # Recursively make rigids and add constraints to `root`
    def _recurse(child, parent=None):
        if child in self.done:
            return

        # Ignore tip-joints
        if not child.child(type="joint"):
            return

        label = child["type"]

        if label == Other:
            label = child["otherType"].read().lower()

        if exclusive and label == Stop:
            return

        if label == Skip:
            child = child.child(type="joint")
            rigid = parent

        else:
            rigid = commands.create_rigid(child, scene)

            if parent is not None:
                if label in (Knee, Elbow, Finger):
                    constraint = commands.hinge_constraint(parent,
                                                           rigid,
                                                           scene)
                    commands.orient(constraint)
                    commands.reorient(constraint)

                    with cmdx.DagModifier() as mod:
                        mod.set_attr(constraint["driveEnabled"], True)
                        mod.set_attr(constraint["driveStrength"], 1)
                        mod.set_attr(constraint["linearDriveStiffness"], 0)
                        mod.set_attr(constraint["linearDriveDamping"], 0)

                else:
                    constraint = commands.socket_constraint(parent,
                                                            rigid,
                                                            scene)
                    commands.orient(constraint)

                constraint["disableCollision"] = True

                # Make boxes out of these
                if label in (Hand, Foot, Toe, Head):
                    with cmdx.DagModifier() as mod:
                        mod.set_attr(rigid["shapeType"], commands.BoxShape)

                # Tag as parent for articulations
                with cmdx.DagModifier() as mod:
                    mod.connect(parent["ragdollId"], rigid["parentRigid"])

        self.done += [child]

        if inclusive and label == Stop:
            return

        for gc in child.children(type="joint"):
            _recurse(gc, rigid)

    result = root

    if copy:
        result = cmds.duplicate(result.path(), returnRootsOnly=True)[0]
        result = cmdx.encode(result)

    _recurse(result)

    if control:
        rigid = result.shape(type="rdRigid")

        with cmdx.DagModifier() as mod:
            # Facilitate kinematic attribute
            mod.connect(root["matrix"], rigid["inputMatrix"])

        # Absolute control on hip
        ref, _, con = commands.create_absolute_control(rigid, reference=root)

        with cmdx.DagModifier() as mod:
            mod.set_attr(root["driveStrength"], 0)  # Default to off

        # Forward the kinematic attribute to the root guide
        root_proxies = commands.UserAttributes(rigid, root)
        root_proxies.add_divider("Ragdoll")
        root_proxies.add("kinematic")
        root_proxies.do_it()

        with cmdx.DagModifier() as mod:
            for reference, joint in zip(root.descendents(type="joint"),
                                        result.descendents(type="joint")):

                rigid = joint.shape(type="rdRigid")

                if rigid is None:
                    continue

                commands.create_active_control(reference, rigid)

                mod.set_attr(rigid["kinematic"], False)
                mod.do_it()

                # Forward kinematics from children too
                reference_proxies = commands.UserAttributes(rigid, reference)
                reference_proxies.add_divider("Ragdoll")
                reference_proxies.add("kinematic")
                reference_proxies.do_it()

                mod.connect(reference["worldMatrix"][0], rigid["inputMatrix"])

    if normalise_shapes:
        commands.normalise_shapes(result)

    return result
