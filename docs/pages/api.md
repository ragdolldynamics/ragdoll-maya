<div class="hero-container">
  <img class="hero-image" src=/yoga13.png>
</div>

Ragdoll consists of custom ([`MPxLocatorNode`](https://help.autodesk.com/view/MAYAUL/2020/ENU/?guid=__cpp_ref_class_m_px_locator_node_html)) nodes written in C++, but everything involved in connecting these up and generating the dependency network happens in Python. This API is exposed to you for integration with auto-rigging, tools development and to generally just extend the capabilities of the system.

The API is also [available on GitHub](https://github.com/mottosso/ragdoll) for issue tracking and user contributions.

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

scene = rd.createScene()
rigid = rd.createRigid(cube, scene)

cmds.evalDeferred(cmds.play)
```

![ragdollapi1](https://user-images.githubusercontent.com/2152766/95583484-1a415b00-0a34-11eb-8f24-5a83b4ae2629.gif)

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

# Every simulation needs a scene
scene = rc.create_scene()
assert isinstance(scene, cmdx.DagNode)
assert scene.type() == "rdScene"

# Every scene needs one or more rigid bodies
rigid = rc.create_rigid(cube, scene)
assert isinstance(rigid, cmdx.DagNode)
assert rigid.type() == "rdRigid"

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
ri.create_rigid()

cmds.evalDeferred(cmds.play)
```

<br>

## Members

Currently available members of `ragdoll.api`.

- Call `help()` for usage instructions

```py
# Fundamentals
api.createScene()
api.createRigid(node, scene, passive=False, compute_mass=True)

# Constraints
api.pointConstraint(parent, child, scene)
api.orientConstraint(parent, child, scene)
api.hingeConstraint(parent, child, scene)
api.socketConstraint(parent, child, scene)
api.parentConstraint(parent, child, scene)

api.convertToPoint(con)
api.convertToOrient(con)
api.convertToHinge(con, secondary_axis="y")
api.convertToSocket(con)
api.convertToParent(con)

# Controls
api.createAbsoluteControl(rigid)
api.createRelativeControl(rigid)
api.createActiveControl(reference, rigid)
api.createKinematicControl(rigid)

# Forces
api.createForce(type, rigid, scene)
api.createSlice(scene)
api.assignForce(rigid, force)

# Utilities
api.transferAttributes(a, b, mirror=True)
api.transferRigid(ra, rb)
api.transferConstraint(ca, cb, mirror=True)
api.editConstraintFrames(con)
api.duplicate(rigid)
```

<br>

## Environment Variables

Gain more control over the integration of Ragdoll into your pipeline with these optional environment variables. For example, to manually load the Ragdoll plug-in and Maya menu, set `RAGDOLL_NO_AUTOLOAD=1` and then call:

```py
import ragdoll.interactive
ragdoll.interactive.install()
```

> Added `Ragdoll 2021.01.14`

| Variable                  | Description | Default
|:--------------------------|:------------|:--------
| RAGDOLL_PLUGIN            | Override absolute path to binary plugin, .mll on Windows .so on Linux. This overrides whatever is on `MAYA_PLUG_IN_PATH` | <nobr>`"ragdoll"`</nobr>
| RAGDOLL_NO_STARTUP_DIALOG | Do not display the startup-dialog on first launch. | `False`
| RAGDOLL_AUTO_SERIAL       | Automatically activate Ragdoll on install using this serial number. | Unset
| RAGDOLL_INSTALL_ON_IDLE   | Restore plug-in load behavior pre-2021.04.30 | Unset
