<div class="hero-container">
  <img class="hero-image" src=/yoga13.png>
</div>

Ragdoll consists of custom nodes written in C++, but everything involved in connecting these up and generating the dependency network happens in Python. This API is exposed to you for integration with auto-rigging, tools development and to generally just extend the capabilities of the system.

The full source code of everything Python is also [available on GitHub](https://github.com/mottosso/ragdoll), where you may also submit issues and pull-requests to improve the tooling for everyone.

**See Also**

- [API Reference](/api_reference)

<br>

## Overview

There are 3 supported methods of integrating Ragdoll into your pipeline. Each with its own flare.

- [`api.py`](#apipy) - Public interface
- [`commands.py`](#commandspy) - Low-level commands
- [`interactive.py`](#interactivepy) - User-facing commands

<br>

### api.py

The publicly facing programming interface to Ragdoll. Use this for tools integrated with other tools that rely on heavy compatibility between versions and few surprises on what goes in and out.

- ✔️ Guaranteed backwards compatibility
- ✔️ High interoperability with `maya.cmds`, including `camelCase`
- ✔️ No dependence on user selection or preferences
- ❌ Limited to documented and officially supported features

```py
from maya import cmds
from ragdoll import api as rd

cube, _ = cmds.polyCube()
cmds.move(0, 10, 0)
cmds.rotate(35, 50, 30)

solver = rd.createSolver()
marker = rd.assignMarker(cube, solver)

rd.record()

cmds.evalDeferred(cmds.play)
```

![ragdollapi1](https://user-images.githubusercontent.com/2152766/95583484-1a415b00-0a34-11eb-8f24-5a83b4ae2629.gif)

**Member Reference**

- [API Member Reference](/api_reference)

<br>

### commands.py

The `api.py` module builds on `commands.py`, but wraps it in a string-based interface so as to make it compatible with your everyday calls to `maya.cmds`.

All of `api.py` is present in `commands.py`, along with a few extras that may or may not change over time. It is best suited for tight integration and control but is primarily used internally for implementing `interactive.py` and `tools.py`.

- ✔️ Fast
- ✔️ Flexible
- ✔️ Same guarantees as `api.py` for identical members
- ❌ Unfamiliar data `cmdx` types

> `commands.py` uses the highly performant [`cmdx`](https://github.com/mottosso/cmdx) library to communicate with Maya and all return values are instances of `cmdx`.

```py
from maya import cmds
from ragdoll import commands as rc
from ragdoll.vendor import cmdx

cmds.file(new=True, force=True)

cube, _ = map(cmdx.encode, cmds.polyCube())
cube["translateY"] = 10
cube["rotate", cmdx.Degrees] = (35, 50, 30)

# Every simulation needs a solver
solver = rc.create_solver("mySolver")
assert isinstance(solver, cmdx.DagNode)
assert solver.isA("rdSolver")

# Every solver needs one or more marker bodies
marker = rc.assign_marker(cube, solver)
assert isinstance(marker, cmdx.DagNode)
assert marker.isA("rdMarker")

# Allow start frame to evaluate before progressing
cmds.evalDeferred(cmds.play)
```

<br>

### interactive.py

Finally, this module is used for UI elements like the main Ragdoll menu. Every function takes selection into account, along with any preferences set via the Option Dialogs.

It's useful for when you want to replicate what the menu does, including taking selection into account and outputting warning messages in the Script Editor. It won't raise exceptions like `api` and `commands`, instead each function return either `True` for success or nothing for failure. Failures typically follow one or more warning messages.

- ✔️ Animator-friendly, useful for quick scripts
- ❌ No usable return value
- ❌ Sensitive to user preferences
- ❌ No guarantee on backwards compatibility
- ❌ Verbose output in Script Editor

```py
from maya import cmds
from ragdoll import interactive as ri

cube, _ = cmds.polyCube()
cmds.move(0, 10, 0)
cmds.rotate(35, 50, 30)

cmds.select(cube)
ri.assign_marker()

cmds.evalDeferred(cmds.play)
```

!!! hint "Pro Tip"
  Whenever you click a menu item, this Python command is printed in the Script Editor!

<br>

## Members

Currently available members of `ragdoll.api`.

- Call `help()` for usage instructions

```py
# Fundamentals
api.createSolver(name="mySolver")
api.assignMarker(transform, solver)
api.assignMarkers([transform1, transform2], solver)

# Constraints
api.createFixedConstraint(marker1, marker2)
api.createDistanceConstraint(marker2, marker2)
api.createPinConstraint(marker1)

# Edit
api.reconnect(child_marker, parent_marker)
api.retarget(marker, new_transform)
api.replaceMesh(marker, new_mesh)

# IO
api.record()
api.export()
api.reinterpret()
```

<br>

## Environment Variables

Gain more control over the integration of Ragdoll into your pipeline with these optional environment variables. For example, to avoid the startup dialog on first launch, set `RAGDOLL_NO_STARTUP_DIALOG=1` before loading the plug-in.

| Variable                  | Description | Default
|:--------------------------|:------------|:--------
| RAGDOLL_PLUGIN            | Override absolute path to binary plugin, .mll on Windows .so on Linux. This overrides whatever is on `MAYA_PLUG_IN_PATH` | <nobr>`"ragdoll"`</nobr>
| RAGDOLL_NO_STARTUP_DIALOG | Do not display the startup-dialog on first launch. | `False`
| RAGDOLL_AUTO_SERIAL       | Automatically activate Ragdoll on install using this serial number. | Unset
| RAGDOLL_TELEMETRY         | Help development by uploading usage data. | Enabled for non-commercial licences, optional for commercial licences.
