import os

# Avoid automatically installing plug-in and menu
# item with this environment variable.
if os.getenv("RAGDOLL_NO_AUTOLOAD", False):
    pass

else:
    from ragdoll import interactive
    interactive.install()
    del interactive

del os
