Highlight for this  release is JSON Export, this one's for you **game developers** out there!

- [**ADDED** JSON Export](#json-export) Run your ragdolls in Unreal, Unity or your own custom game engine
- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync
- [**ADDED** Active Chain](#active-chain) Next generation "Dynamic Control" with "chain"
- [**CHANGED** Dynamic Install](#dynamic-install) Tighter integration into Maya's native Plug-in Manager
- [**CHANGED** Greater Guide Strength](#greater-guide-strength) Have simulation follow animation even closelier
- [**FIXED** Crash on Cleanup](#crash-on-cleanup) A more stable clean-up experience

!!! warning "Important!"
    This version won't self-install like the past releases, see [Dynamic Install](#dynamic-install) on how you need to load the plug-in via Maya's Plug-in Manager from now on.

<br>

## JSON Export

<img width=200 src=https://user-images.githubusercontent.com/2152766/111428442-684b4080-86ef-11eb-8919-ea14e85555ec.png>

In [2021.03.01](/releases/2021.03.01/#cmdsragdolldump) we introduced `cmds.ragdollDump` to get a copy of all rigids in the form of a JSON dictionary.

This release includes **all initial state** for the simulation, such that you can reproduce the results you see in Maya in a game engine, like Unreal, Unity, CryEngine or your own custom game engine. Or why not Houdini, Blender or 3dsMax?

This enables you to use Maya as an authoring platform for physics anywhere.

```py
from maya import cmds
dump = cmds.ragdollDump()

# Convert big string to structured dictionary
import json
dump = json.loads(dump)

for entity, data in dump.items():
    components = data["components"]
    name = components["NameComponents"]["members"]["path"]
    print(name)

# |root|pelvis|rRigid1
# |root|pelvis|spine|rRigid2
# |root|pelvis|spine2|rRigid3
# ...
```

Here's an example of what to expect from the output.

- [`output_example.json`](https://gist.github.com/mottosso/ca60e9846f1becfa0c1a12681e73c917)

```py
{
  "entities": {
    "10": {
      "components": {
        "NameComponent": "upperArm",
        "ColorComponent": [1.0, 0.0, 0.0],
        "GeometryDescriptionComponent": "Capsule",
        ...
      }
    },
    "15": {
      "components": {
        "NameComponent": "lowerArm",
        "ColorComponent": [0.0, 1.0, 0.0],
        "GeometryDescriptionComponent": "Box",
        ...
      }
  }
}
```

See the new Serialisation documentation for an overview, examples and data reference.

- https://learn.ragdolldynamics.com/serialisation

<br>

## Dynamic Install

Previous releases shipped with a `userSetup.py` that triggered on launch of Maya. This made it easy to get setup, but made it challenging to *uninstall* without physically removing files off of the file system (hint: `~/Documents/maya/modules/Ragdoll.mod`).

This release associates install with plug-in load.

**Install**

![ragdollinstall](https://user-images.githubusercontent.com/2152766/111457614-55953380-8710-11eb-99a4-f2fb7cc67771.gif)

**Uninstall**

![ragdolluninstall](https://user-images.githubusercontent.com/2152766/111457654-6776d680-8710-11eb-964c-a31712f7875d.gif)

<br>

## Active Chain

Dynamic Control has been renamed `Active Chain`!



<br>

## Greater Guide Strength

The solver `Iterations` determines how high your `Guide Strength` attribute can go. Per default, `Iterations` was set to `1` which enabled strengths between `0-5` or so until their effect dimished.

This release increases this default value to `4` for ranges between `0-100`, which means "incredibly high!". The change comes at a minor performance impact - estimated between 1-5% - so if you find the need to optimise, lower this value back to 2 or 1.

!!! hint
    Bear in mind that the number of iterations are spread across all rigid in your scene. Meaning twice the number of rigids would half the amount of iterations dedicated to each one.

#### Before

![ragdolliterations3](https://user-images.githubusercontent.com/2152766/111459062-21bb0d80-8712-11eb-9eb9-1449d8352cab.gif)

#### After

![ragdolliterations4](https://user-images.githubusercontent.com/2152766/111459108-2da6cf80-8712-11eb-89a0-a2c7a7dc1675.gif)

<br>

## Crash on Cleanup

In rare cases, Ragdoll could crash Maya due to accessing memory it had no business accessing. Those have now been patched up and refactored for a more stable, crash-free experience!

![image](https://user-images.githubusercontent.com/47274066/111773312-eea98300-88a5-11eb-9f52-289b59125678.png)

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.
