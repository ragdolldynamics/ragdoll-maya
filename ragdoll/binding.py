"""Python bindings for the Ragdoll C++ backend

This module replaces itself with the compiled binary, see dir(binding)
for which members are present, and help(binding.activate_licence)
for help on individual members.

"""

import os
import sys

if "RAGDOLL_DO_NOT_LOAD_BINDING" in os.environ:
    def dump():
        return ""

    def init_licence():
        return 0

    def activate_licence(*args, **kwargs):
        return 0

    def deactivate_licence():
        return 0

    def reverify_licence():
        return 0

    def licence_key():
        return 0

    def is_licence_trial():
        return False

    def is_licence_activated():
        return True

    def is_licence_genuine():
        return True

    def is_licence_verified():
        return True

    def licence_trial_days():
        return 0

    def licence_magic_days():
        return 10


else:
    from maya import cmds

    # Next to the Maya plug-in there is a compiled Python module
    pluginfname = (
        os.environ.get("RAGDOLL_PLUGIN") or
        cmds.pluginInfo("ragdoll", path=True, query=True)
    )

    plugindir = os.path.dirname(pluginfname)

    # Replace ourselves with the statically compiled C++ bindings
    sys.path.insert(0, plugindir)
    pyragdoll = __import__("pyragdoll")
    assert "pyragdoll" in sys.modules  # Leave reference for cleanup later
    sys.path.pop(0)

    # This immediately erases any and all traces of this module
    # NOTE: So do NOT call anything beyond this point
    sys.modules["ragdoll.binding"] = pyragdoll
