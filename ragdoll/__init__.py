import os

# Internal
__ = type("internal", (object,), {})
__.installed = False
__.menu = None
__.menuitems = {}
__.optionvars = {}
__.xbmlangpath = "xbmlangpath"
__.aetemplates = "aetemplates"
__.callback = None
__.version = 0
__.version_str = "0"
__.previousvars = {}

if os.name.lower() == "posix":
    # Linux has this special requirement, for whatever reason
    __.xbmlangpath += "/%B"

# Leave no trace
del os
