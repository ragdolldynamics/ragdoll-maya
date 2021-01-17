from maya import cmds
from .. import commands
from ..vendor import cmdx

from nose.tools import (
    assert_almost_equals,
)


def new():
    cmds.file(new=True, force=True)


def test_defaults():
    new()

    cube, _ = cmds.polyCube()
    cube = cmdx.encode(cube)  # Convert to cmdx
    cube["translateY"] = 10
    cube["rotate", cmdx.Degrees] = (35, 50, 30)

    cmds.currentTime(1)

    scene = commands.create_scene()
    commands.create_rigid(cube, scene)

    for frame in range(1, 30):
        cube["ty"].read()  # Trigger evaluation
        cmds.currentTime(frame)

    # It'll be resting on the ground at this point
    assert_almost_equals(cube["ty"].read(), 0.500, 3)
