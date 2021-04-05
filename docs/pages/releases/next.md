---
title: Maya 2022
description: Ragdoll 2021.03.25 is released! Now compatible with Maya 2022 (and Python 3!)
---

Highlight for this release is **import**!

- [**ADDED** Import](#import) Animator-friendly export/import workflow for physics
- [**IMPROVED** Explorer](#explorer) Next iteration of the Ragdoll Explorer
- [**IMPROVED** Maya 2022 Stability](#maya-2022-stability]) Things now works more reliably with Maya 2022

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.

<br>

## Import

Animators can now apply physics onto a character rig in one scene, export it, and then import it onto the same character in another scene!

- [Import to selection](#import-to-selection)
- [Import everything from file](#import-everything)
- [Regenerate Maya scene from file](#regenerate)
- [Reinterpret commands from file](#reinterpret)
- [Profiles](#profiles)
- [Examples](#examples)

### Introduction

Did you see Snyder's Justice League? In it, they introduce and explain the "mother box" and how it is capable of turning the dust of a burnt house *back* into a house.

This `Import` feature is the Mother Box of Ragdoll.

The export format is identical to what game developers use to author physics in Maya and import it into their game engine. It contains *all* data managed by Ragdoll in full detail. Enough detail to reverse-engineer it back into a Maya scene, which is exactly what's going on here.

There are a few caveats with that however.

1. It isn't export native Maya nodes

### Workflow A - Additive

Limit import to whatever you've got selected, and import multiple times to keep adding things from the exported file into your current scene.

- Example import parts of scene, then character
- Example import to one character at a time

### Workflow B - Subtractive

Similar to the Additive workflow, you can also import *more* than you need, and use `Delete Physics` to subtract parts of an exported file.

- Example import whole character, remove arm

### Supported Data

On export, physics is converted to text and written to a file. Not all relevant information is captured by that export, only the things that related to Ragdoll.

For example, if you've turned a controller dynamic and then added your own attribute, then this attribute will not be included in the export.

Ok, so what *is* included in the export?

**Included**

| Node                     | Description
|:-------------------------|:---------
| `rdScene`                | Each Ragdoll scene is imported, along with their original rigid relationships
| `rdRigid`                | Every rigid body and all of its attributes are included
| `rdConstraint`           | Along with all constraints
| `rdRigidMultiplier`      | And all multipliers
| `rdConstraintMultiplier` |

That should cover 95% of what you would expect to be included in an exported physics contraption.

**Excluded**

These are currently excluded but will be included in a later release.

| Excluded | Description
|:---------|:---------
| `rdRigid.inputMatrix` | This is what enables animation on passive rigid bodies

### New Components

For you developers out there, the export format has been graced with new components to accommodate for the import feature. As the name suggests, these are stricly related to UI and aren't required for reproducing the physics in another application or engine.

They are meant to cover user elements in Maya such that they can be accurately reproduced on re-import back into Maya.

**New Components**

- `RigidUIComponent`
- `ConstraintUIComponent`
- `LimitUIComponent`
- `DriveUIComponent`
- `RigidMultiplierUIComponent`
- `ConstraintMultiplierUIComponent`

!!! Examples
    Here's what the new components may look like in your exported file.
    <br>
    ```json
    {
        "type": "RigidUIComponent",
        "members": {
            "shaded": false,
            "airDensity": 1.0,
            "multiplierEntity": {
                "type": "Entity",
                "value": 0
            }
        }
    },
    {
        "type": "ConstraintUIComponent",
        "members": {
            "multiplierEntity": {
                "type": "Entity",
                "value": 0
            },
            "childIndex": 2
      }
    },
        "type": "LimitUIComponent",
        "members": {
            "strength": 1.0,
            "angularStiffness": 1000000.0,
            "angularDamping": 10000.0,
            "linearStiffness": 1000000.0,
            "linearDamping": 10000.0
      }
    },
        "type": "DriveUIComponent",
        "members": {
            "strength": 0.5,
            "angularStiffness": 10000.0,
            "angularDamping": 1000.0,
            "linearStiffness": 0.0,
            "linearDamping": 0.0
      }
    }
    ```

In addition, some values were entities themselves, but there wasn't any way of knowing unless you explicitly new that `JointComponent.parent` is in fact an entity. This has now been addressed, and all entities now carry a `["type"]` signature.

```json
{
    "type": "JointComponent",
    "members": {
        "disableCollision": true,
        "parent": {
            "type": "Entity",
            "value": 16
        },
        "child": {
            "type": "Entity",
            "value": 15
        }
    }
}
```

There's also an added section for "ui" related data, most interestingly a base64-encoded QPixmap of a `thumbnail`.

```json
    "ui": {
        "description": "",
        "filename": "C:/scenes/demo/advancedskeleton5.rag",
        "thumbnail": "iVBORw0KGgoAAAAN ... lots more characters ..."
    }
```

<br>

## Maya 2022 Stability

The multiplier nodes didn't quite work with Maya 2022, or more specifically with Python 3.

```bash
from ragdoll import interactive as ri
ri.multiply_rigids()
# Error: 'filter' object is not subscriptable
# Traceback (most recent call last):
#   File "<maya console>", line 2, in <module>
#   File "C:\Users\marcus\Documents\maya\modules\Ragdoll\python\ragdoll\interactive.py", line 2112, in multiply_rigids
#     root = rigids[0].parent()
# TypeError: 'filter' object is not subscriptable #
```

There were also crashes happening on deleting rigid bodies from your scene, these got swept away alongside a number of other fixes to the handling of nodes. No more crashes, in any version of Maya, period!

<br>

### Ragdoll Explorer

> For developers

Explorer has gotten an update, inching its way towards Outliner-like behavior and feel. Eventually maybe even an integration with the Outliner, similar to how USD slots into Maya 2022. That's quite neat!

![ragdollexplorer3](https://user-images.githubusercontent.com/2152766/113552099-9389c700-95ed-11eb-80ac-395bcededac9.gif)
