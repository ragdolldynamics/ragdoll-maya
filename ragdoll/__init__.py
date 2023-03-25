# State
__ = type("internal", (object,), {})
__.installed = False
__.menu = None
__.menuitems = {}
__.actiontokey = {}
__.optionvars = {}
__.xbmlangpath = "xbmlangpath"
__.aetemplates = "aetemplates"
__.callbacks = []
__.shortcut = None  # Fit to View hotkey
__.version = 0
__.version_str = "0"
__.previousvars = {}
__.widgets = {}  # Currently active widgets (incl. windows and panels)
__.solvers = []
__.uninstalled_from_py = False
__.telemetry_data = {
    "system": {},
    "ragdoll": {
        "version": 0
    },
    "maya": {
        "version": "unknown",
        "warnings": 0,
        "errors": 0,
        "crashed": False,
    }
}

if __import__("os").name.lower() == "posix":
    # Linux has this special requirement, for whatever reason
    __.xbmlangpath += "/%B"
