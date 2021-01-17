"""Ragdoll Startup Script

The alternative is calling `interactive.install()` yourself.

"""


def init():
    import os

    # Avoid automatically installing plug-in and menu
    # item with this environment variable.
    if os.getenv("RAGDOLL_NO_AUTOLOAD", False):
        pass

    else:
        from ragdoll import interactive
        interactive.install()


# Run these from within a function call,
# to avoid polluting the global namespace
init()

# Clean up any reference to the call,
# which would otherwise be accessible from
# e.g. the Script Editor
del init
