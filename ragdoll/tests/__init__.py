import os
from maya import cmds
from ..vendor import cmdx

__ = type("internal", (object,), {})()
__.fname = cmds.file("test.ma", expandName=True, query=True)
__.export = cmds.file("tempexport.rag", expandName=True, query=True)


def _new(start=1, end=120):
    cmdx.setUpAxis(cmdx.Y)
    cmds.file(new=True, force=True)
    cmds.playbackOptions(minTime=start, maxTime=end)
    cmds.playbackOptions(animationStartTime=start, animationEndTime=end)
    cmds.currentTime(start)


def _play(node, start=1, end=5):
    if node.type() == "rdRigid":
        attr = "outputTranslateY"
    elif node.isA(cmdx.kTransform):
        attr = "translateY"
    else:
        raise TypeError("How do I evaluate %s?" % node)

    for frame in range(start, end):
        node[attr].read()  # Trigger evaluation
        cmds.currentTime(frame, update=True)


def _step(node, steps=1):
    if node.type() == "rdRigid":
        attr = "outputTranslateY"
    elif node.isA(cmdx.kTransform):
        attr = "translateY"
    else:
        raise TypeError("How do I evaluate %s?" % node)

    for step in range(steps):
        ct = cmds.currentTime(query=True)
        node[attr].read()  # Trigger evaluation
        cmds.currentTime(ct + 1, update=True)


def _rewind(scene):
    cmds.currentTime(scene["startTime"].as_time().value, updat=True)


def _save():
    __.fname = cmds.file("test.ma", rename=True)
    cmds.file(save=True, force=True)


def _load():
    cmds.file(__.fname, open=True, force=True)


def _scene(name):
    scenesdir = os.path.dirname(__file__)
    scenesdir = os.path.join(scenesdir, "scenes")
    return os.path.join(scenesdir, name)


def _open(fname):
    cmds.file(fname, open=True, force=True, ignoreVersion=True)
