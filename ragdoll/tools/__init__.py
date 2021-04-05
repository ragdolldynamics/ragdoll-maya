from . import (
    chain_tool,
    character_tool,
    muscle_tool
)

# Keep a consistent `tools` interface for scripters
create_muscle = muscle_tool.create
create_chain = chain_tool.create
create_character = character_tool.create
create_dynamic_control = chain_tool.create


def _to_cmds(name):
    """Convert cmdx instances to maya.cmds-compatible strings

    Two types of cmdx instances are returned natively, `Node` and `Plug`
    Any other return value remains unscathed.

    """

    import sys
    import functools

    from ..vendor import cmdx

    func = getattr(sys.modules[__name__], name)

    @functools.wraps(func)
    def to_cmds_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, (tuple, list)):
            for index, entry in enumerate(result):
                if isinstance(entry, cmdx.Node):
                    result[index] = entry.shortestPath()

                if isinstance(entry, cmdx.Plug):
                    result[index] = entry.path()

        elif isinstance(result, cmdx.Node):
            result = result.shortestPath()

        elif isinstance(result, cmdx.Plug):
            result = result.path()

        return result

    return to_cmds_wrapper
