
- [**ADDED** JSON Export](#json-export) Run your ragdolls in Unreal, Unity or your own custom game engine
- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync
- [**ADDED** Dynamic Install](#dynamic-install) Install/uninstall by just loading/unloading the Maya plug-in

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



<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.
