---
title: Import Physics
description: Ragdoll 2021.04.08 is released! Save your physics contraptions to disk, and load them into another scene onto the same or similar character controls.
---

Highlight for this release is **import** of physics from one character to another!

- [**ADDED** Import](#import) Animator-friendly export/import workflow for physics
- [**ADDED** Edit Shape](#edit-shape) Edit shapes using normal Maya manipulators
- [**IMPROVED** Undo/Redo Stability](#undo-redo-stability) Rock-solid undo support, go nuts!
- [**IMPROVED** Maya 2022 Stability](#maya-2022-stability]) Things now works more reliably with Maya 2022
- [**IMPROVED** Explorer](#explorer) Next iteration of the Ragdoll Explorer
- [**CHANGED** Proxy Attributes](#proxy-attributes]) A small sacrifice for stability
- [**CHANGED** Python API Consistency](#python-api-consistency]) More to come

<br>

## Import

Animators can now apply physics onto a character rig in one scene, export it, and then import it onto similar characters - with different pose and/or animation - in another scene!

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

<br>

??? Show Examples
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

<br>

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

That can be converted like this.

```py
from ragdoll import ui
pixmap = ui.base64_to_pixmap(data["ui"]["thumbnail"])
```

<br>

## Edit Shape

A new menu item got added for manipulating shapes with a native Maya transform, as an alternative to fiddling with numbers in the Channel Box.

![editshape](https://user-images.githubusercontent.com/2152766/113729903-5574cc00-96ef-11eb-9c14-37f177c4b219.gif)

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

## Undo/Redo Stability

Ragdoll and Undo has a had a checkered past. Will it undo everything in one go? Will it crash Maya? Flip a coin, find out.

This release includes a boatload of improvements to undo, along with a test-suite specifically for undoing of commands. Undo, redo, undoing a redo and redoing and undone redo. These all now work great and will no longer put Maya at risk of crashing.

<br>

## Proxy Attributes

In Maya 2018 and 2020, the attributes added to your original animation controls that mirror those of Ragdoll were "proxy attributes". That is, they could be edited from either their original attribute, or the one connected to by your control.

That's really convenient.

Turns out, it is also really unstable. Most of the crashes happening so far, especially on deleting physics or starting a new scene, has come from proxy attributes messing everything up. It should't be surprising, even Maya struggles with them.

```py
node = cmds.createNode("transform")
shape = cmds.createNode("nurbsCurve", parent=node)
cmds.addAttr(node, ln="proxyVisibility", proxy=shape + ".visibility")
assert cmds.objExists(node + ".proxyVisibility")
assert cmds.getAttr(node + ".proxyVisibility") == 1

# What should happen to the proxy attribute? :O
cmds.delete(shape)

cmds.getAttr(node + ".proxyVisibility")
# RuntimeError: The value for the attribute could not be retrieved. # 
```

The same thing applies with access from the API. It just doesn't know what's going on. If we're lucky - which we have been so far - it'll just fail and tell you about it. Other times it'll fail and take Maya down with it. That's just bad.

In Maya 2019, the problem was so severe that proxy attributes were simply not used. With this release, no proxy attributes are used.

I hope to reintroduce them at a later date, once I discover is a safe method (read: workaround) to using them.

<br>

## Python API Consistency

The good news is, the Python API is maturing. The bad news is, this release introduces backwards incompatible changes.

```py
from maya import cmds
from ragdoll import api

cube, _ = cmds.polyCube()
cmds.move(0, 5, 0)
cmds.rotate(0, 45, 45)
scene = api.createScene()
rigid = api.createRigid(cube)
```

So far so good.

```py
# Before
api.socketConstraint(parent, child, maintain_offset=False)

# After
api.socketConstraint(parent, child, opts={"maintainOffset": False})
```

Here's the change. These behavior-like arguments have been moved into an `opts={}` argument, and is now consistent across any commands that take "options". It's to faciliate a large number of options, both from the UI and scripting and enhance compatibility over time; with a dictionary, you can test for availability of arguments at run-time, as opposed to suffer the consequences of not being able to call an update function.

I'm still exploring ways of getting more options into commands, without polluting the argument signature, without changing their order when an argument is deprecated, or changing an argument name when jargon inevitably changes. Using a dictionary for options-like arguments enables us to pass arbitrary sized options to functions, they can also be passed to functions that don't necessarily *need* all contained options, meaning you can establish a single options dictionary up-front and pass that to all relevant functions.

It's too soon to tell whether the cons of this approach outweighs the pros. This is one reason for the API still going through changes.

The non-optional arguments are those that are never intended to change, like the `createRigid(node)` argument. Every rigid needs something to make rigid. (Or so you'd think, as you can now also create a rigid from a new empty transform).

So, the API has changed and will continue changing for a while longer.

**Node/Attribute format**

The Ragdoll scene format is stable and has been for months. It will remain compatible with future versions of Ragdoll, which means anything you build today (or months ago) will continue to work identically.

The Python API on the other hand is not yet refined and is still changing. So when you build tools ontop of Ragdoll, keep in mind that nodes, their attributes and their connections are *stable*, but the means of creating those connections are not. So if you need stability *today*, look at what nodes and connections are made by the API, and do it yourself.

<br>

## Ragdoll Explorer

> For developers

Explorer has gotten an update, inching its way towards Outliner-like behavior and feel. Eventually maybe even an integration with the Outliner, similar to how USD slots into Maya 2022. That's quite neat!

![ragdollexplorer3](https://user-images.githubusercontent.com/2152766/113552099-9389c700-95ed-11eb-80ac-395bcededac9.gif)
