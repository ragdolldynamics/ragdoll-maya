"""Option variables

Optionvars are Maya's way of storing persistent data, they are stored
alongside the Maya preferences and persists across launches and scenes.
The values are also accessible from within C++, which makes them a
convenient method of Python to C++ communication.

"""

import logging
from maya import cmds
from . import __
from .vendor import qargparse

log = logging.getLogger("ragdoll")

# Backwards compatibility for Python 2
try:
    string_types = basestring,
except NameError:
    string_types = str,


def _optionvarkey(name):
    """Avoid conflict by storing optionvars under a namespace"""
    return "ragdoll%s" % (name[0].upper() + name[1:])


def write(arg, value=None):
    if isinstance(arg, string_types):
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

    elif isinstance(value, string_types):
        cmds.optionVar(stringValue=(key, value))

    elif isinstance(value, (tuple, list)):
        # Double3
        cmds.optionVar(floatValue=(key, value[0]))
        cmds.optionVar(floatValueAppend=(key, value[1]))
        cmds.optionVar(floatValueAppend=(key, value[2]))

    else:
        raise TypeError(
            "Unrecognised default type for optionvar %s: %s"
            % (key, value)
        )


def read(arg):
    if isinstance(arg, string_types):
        arg = __.optionvars.get(arg)

    if isinstance(arg, qargparse.QArgument):
        arg = __.optionvars.get(arg["name"])

    if arg is None:
        log.warning("Unrecognised optionvar '%s'" % arg)
        return None

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


def reset():
    """Remove all persistent optionvars"""

    count = 0
    for key in cmds.optionVar(list=True):
        if key.startswith("ragdoll"):
            cmds.optionVar(remove=key)
            count += 1

    install()

    for key in __.optionvars:
        log.info("Resetting %s = %s" % (key, read(key)))

    log.info("Resetted %d optionvars" % count)
