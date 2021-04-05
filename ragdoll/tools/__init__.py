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
