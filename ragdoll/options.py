"""Option variables

Optionvars are Maya's way of storing persistent data, they are stored
alongside the Maya preferences and persists across launches and scenes.
The values are also accessible from within C++, which makes them a
convenient method of Python to C++ communication.

"""

import logging
from maya import cmds
from . import internal as i__, __
from .vendor import qargparse

log = logging.getLogger("ragdoll")


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
                cmds.optionVar(stringValueAppend=(key, v))

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
        key = _optionvarkey(arg["name"])
        if cmds.optionVar(exists=key) and not reset:
            continue

        write(arg)


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
    for key in cmds.optionVar(list=True):
        if key.startswith("ragdoll"):
            previous[key] = cmds.optionVar(query=key)
            cmds.optionVar(remove=key)
            total += 1

    install()

    for key in __.optionvars:
        prev = previous.get(_optionvarkey(key), "")
        new = read(key)

        if prev != new:
            changed += 1
            log.info("Resetting %s (%s = %s)" % (key, prev, new))

    log.info("Resetted %d/%d optionvars" % (changed, total))
