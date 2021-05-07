"""Every command is undoable and redoable"""

from maya import cmds
from ..vendor import cmdx
from .. import commands
from . import _new


def setup():
    pass


def almost_equals(a, b):
    return ("%.4f" % a) == ("%.4f" % b)


def _undo(func, axiom, debug=lambda: ""):

    # It can't be true until we've done it
    assert not axiom(), debug()
    func()

    # It should now be true
    assert axiom(), debug()
    cmds.undo()

    # Also make sure redo replicates the behavior
    assert not axiom(), debug()
    cmds.redo()

    # Once redone, undo should still work
    assert axiom(), debug()

    # And one more for the road
    cmds.undo()
    assert not axiom(), debug()


def test_undo_create_scene():
    """create_scene can be undone"""

    _new()
    _undo(commands.create_scene,
          lambda: cmds.ls(type="rdScene"))


def test_undo_create_rigid():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()

    _undo(lambda: commands.create_rigid(cube, scene),
          lambda: cmds.ls(type="rdRigid"))


def test_undo_convert_rigid():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)

    _undo(lambda: commands.convert_rigid(rigid, opts={"passive": True}),
          lambda: rigid["kinematic"].read() is True)


def test_undo_create_constraint():
    _new()

    # Setup
    a, _ = map(cmdx.encode, cmds.polyCube())
    b, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    ra = commands.create_rigid(a, scene)
    rb = commands.create_rigid(b, scene)

    _undo(lambda: commands.create_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))

    _undo(lambda: commands.point_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))

    _undo(lambda: commands.orient_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))

    _undo(lambda: commands.parent_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))

    _undo(lambda: commands.hinge_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))

    _undo(lambda: commands.socket_constraint(ra, rb),
          lambda: cmds.ls(type="rdConstraint"))


def test_undo_convert_constraint():
    _new()

    # Setup
    a, _ = map(cmdx.encode, cmds.polyCube())
    b, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    ra = commands.create_rigid(a, scene)
    rb = commands.create_rigid(b, scene)
    con = commands.create_constraint(ra, rb)
    commands.convert_to_point(con)

    _undo(lambda: commands.convert_to_orient(con),
          lambda: con["linearLimitX"] == 0 and con["angularLimitX"] < 0)

    _undo(lambda: commands.convert_to_hinge(con),
          lambda: almost_equals(con["angularLimitX"], cmdx.radians(45)),
          lambda: "%s != %s" % (con["angularLimitX"].read(), cmdx.radians(45)))

    _undo(lambda: commands.convert_to_socket(con),
          lambda: almost_equals(con["angularLimitY"], cmdx.radians(45)))

    _undo(lambda: commands.convert_to_parent(con),
          lambda: con["angularLimitX"] < 0 and con["linearLimitX"] < 0)


def test_undo_create_absolute_control():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)

    _undo(lambda: commands.create_absolute_control(rigid),
          lambda: cmds.ls(type="rdControl"))


def test_undo_create_relative_control():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    parent, _ = map(cmdx.encode, cmds.polyCube())
    reference = cmdx.create_node("transform", name="reference")
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)
    parent_rigid = commands.create_rigid(parent, scene)

    # Worldspace constraint
    commands.socket_constraint(scene, rigid)

    _undo(lambda: commands.create_relative_control(rigid,
                                                   parent_rigid,
                                                   reference),
          lambda: cmds.ls(type="rdControl"))


def test_undo_create_active_control():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    reference = cmdx.create_node("transform", name="reference")
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)

    # Worldspace constraint
    commands.socket_constraint(scene, rigid)

    _undo(lambda: commands.create_active_control(reference, rigid),
          lambda: cmds.ls(type="rdControl"))


def test_undo_set_initial_state():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)

    cmds.select(cube.path())
    cmds.move(0, 5, 0)
    commands.set_initial_state([rigid])

    cmds.move(0, 0, 0)
    _undo(lambda: commands.set_initial_state([rigid]),
          lambda: rigid["cachedRestMatrix"].asTm().translation().y == 0)


def test_undo_edit_constraint_frames():
    _new()

    # Setup
    cube, _ = map(cmdx.encode, cmds.polyCube())
    scene = commands.create_scene()
    rigid = commands.create_rigid(cube, scene)
    con = commands.socket_constraint(scene, rigid)

    def count():
        return len(cmds.ls(type="transform"))

    # It'll create two new transforms, one for each frame
    pivot_count = count()
    _undo(lambda: commands.edit_constraint_frames(con),
          lambda: count() == pivot_count + 2)
