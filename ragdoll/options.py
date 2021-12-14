"""Option variables

Optionvars are Maya's way of storing persistent data, they are stored
alongside the Maya preferences and persists across launches and scenes.
The values are also accessible from within C++, which makes them a
convenient method of Python to C++ communication.

"""

import os
import copy
import logging
from maya import cmds
from . import internal as i__, __
from .vendor import qargparse

log = logging.getLogger("ragdoll")


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _optionvarkey(name):
    """Avoid conflict by storing optionvars under a namespace"""
    return "ragdoll%s" % (name[0].upper() + name[1:])


def write(arg, value=None):
    if isinstance(arg, i__.string_types):
        arg = __.optionvars[arg]

    if isinstance(arg, qargparse.QArgument):
        arg = __.optionvars[arg["name"]]

    key = _optionvarkey(arg["name"])

    if value is None:
        value = arg["default"]

    if arg["type"] == "Enum":
        value = value or 0
        assert isinstance(value, int), "%s was not an enum" % value

    if arg["type"] == "Boolean":
        value = bool(value)
        assert isinstance(value, bool), (
            "%s was not a bool" % value
        )

    if arg["type"] == "String":
        value = value or ""
        assert isinstance(value, i__.string_types), (
            "%s was not a string" % value
        )

    if isinstance(value, float):
        cmds.optionVar(floatValue=(key, value))

    elif isinstance(value, int):
        cmds.optionVar(intValue=(key, value))

    elif isinstance(value, bool):
        cmds.optionVar(intValue=(key, value))

    elif isinstance(value, i__.string_types):
        cmds.optionVar(stringValue=(key, value))

    elif isinstance(value, (tuple, list)):
        # Double3
        if isinstance(value[0], float):

            # If we don't reset the first value, it'll just keep appending
            cmds.optionVar(floatValue=(key, value[0]))

            for v in value[1:]:
                cmds.optionVar(floatValueAppend=(key, v))

        # Int2
        elif isinstance(value[0], int):
            cmds.optionVar(intValue=(key, value[0]))

            for v in value[1:]:
                cmds.optionVar(intValueAppend=(key, v))

        # Bool2
        elif isinstance(value[0], bool):
            cmds.optionVar(intValue=(key, value[0]))

            for v in value[1:]:
                cmds.optionVar(intValueAppend=(key, v))

        # String2
        elif isinstance(value[0], i__.string_types):
            cmds.optionVar(stringValue=(key, value[0]))

            for v in value[1:]:
                cmds.optionVar(stringValueAppend=(key, v or ""))

    else:
        raise TypeError(
            "Unrecognised default type for optionvar %s: %s"
            % (key, value)
        )


def read(arg):
    if isinstance(arg, i__.string_types):
        arg = __.optionvars.get(arg)

    if isinstance(arg, qargparse.QArgument):
        arg = __.optionvars.get(arg["name"])

    if arg is None:
        raise ValueError("Unrecognised optionvar '%s'" % arg)

    name = arg["name"]
    key = _optionvarkey(name)

    if not cmds.optionVar(exists=key):
        return None

    value = cmds.optionVar(query=key)

    if arg["type"] == qargparse.Boolean:
        # Stored as an integer
        return bool(value)

    else:
        return value


def install(reset=False):
    """Ensure default optionvars exists

    Arguments:
        reset (bool): Whether or not to preserve those stored
            in the Maya preferences

    """

    for arg in __.optionvars.values():
        var = _optionvarkey(arg["name"])
        if cmds.optionVar(exists=var) and not reset:
            continue

        write(arg)

    write("shaderPath", _resource("shaders"))
    write("fontPath", _resource("fonts"))
    write("iconPath", _resource("icons"))


def uninstall():
    pass


def save():
    # Ragdoll's preferences are Maya's native "optionVar"
    cmds.savePrefs(general=True)


def reset():
    """Remove all persistent optionvars"""

    total = 0
    changed = 0
    previous = {}
    old = copy.deepcopy(__.optionvars)

    for var in cmds.optionVar(list=True):
        if var.startswith("ragdoll"):
            previous[var] = cmds.optionVar(query=var)
            cmds.optionVar(remove=var)
            total += 1

    install()

    for arg in __.optionvars.values():

        # These are mandatory
        if arg["name"] in ("shaderPath",
                           "fontPath",
                           "iconPath"):
            continue

        var = _optionvarkey(arg["name"])  # sceneScale -> ragdollSceneScale
        prev = previous.get(var, "''")
        new = read(arg["name"])

        if prev != new:
            changed += 1
            log.info("Resetting %s (%s = %s)" % (arg["name"], prev, new))

    log.info("Resetted %d/%d optionvars" % (changed, total))

    return old
