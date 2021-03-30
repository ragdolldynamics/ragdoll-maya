- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync
- [**ADDED** Import](#import) Animator-friendly export/import workflow for physics
- [**FIXED** Multiplier Nodes 2022](#multiplier-nodes-2022) These now work with Maya 2022

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.

<br>

## Import

Animators can now apply physics onto a character rig in one scene, export it, and then import it onto the same character in another scene!

- Import to selection
- Import everything from file
- Regenerate Maya scene from file
- Reinterpret commands from file
- Examples

### Introduction

Did you see Snyder's Justice League? In it, they introduce and explain the "mother box" which is capable of turning the dust of a burnt house *back* into a house.

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

| New Component                     | Description
|:----------------------------------|:---------
| `RigidUIComponent`                | 
| `ConstraintUIComponent`           | 
| `LimitUIComponent`                | 
| `DriveUIComponent`                | 
| `RigidMultiplierUIComponent`      | 
| `ConstraintMultiplierUIComponent` | 

<Br>

## Multiplier Nodes 2022

These didn't quite work with Maya 2022, or more specifically with Python 3.

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

This has now been fixed.
