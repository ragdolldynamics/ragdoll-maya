---
hidden: true
title: Interactive Manipulators
description: Out of the Channel Box and into the Viewport!
---

![image](https://user-images.githubusercontent.com/2152766/141471283-3a771240-f80d-4745-844d-6f0c0ed87bc5.png)

Highlight for this release is **Manipulators**!

- [**ADDED** Manipulator](#manipulators) Edit things faster and visually with these new tricks
- [**ADDED** Independent Pose Axes](#separate-translate-xyz-amount) Control X, Y and Z axes independently
- [**ADDED** Quality of Life](#quality-of-life) Can never have too much of this.
- [**FIXED** Auto Limits II](#auto-limits-ii) More predictable, more usable
- [**FIXED** Disappearing Limits](#disappearing-limaits) Two solvers, one removed, caused limit indicators to vanish
- [**FIXED** Lollipop Hierarchy](#lollipop-hierarchy) Lollipops could break a hierarchy of markers, but no more
- [**FIXED** Replace Intermediate Mesh](#replace-intermediate-mesh) Intermediate meshes could make Replace Mesh more complicated
- [**FIXED** White Window on Maya Exit](#maya-exit) Ragdoll could sometime prevent Maya from exiting properly
- [**ADDED** Customise Recording](#customise-recording) An advanced topic for big pipelines

<br>

### Showcase

<br>

### Manipulators

One of the most challenging aspect of Ragdoll is editing shapes and limits. These have now been greatly simplified via the use of "manipulators", similar to your standard Translate/Rotate/Scale manipulators.

#### Multi-select

Hold `Shift` to select and manipulate *multiple* markers at once.

#### Symmetry

Toggle `Enable Symmetry` to manipulate markers symmetrically along the world X axis. Change the axis using the Axis dropdown.

**Translation**

Translations are fully symmetrical, regardless of the orientation of the mirrored half of your rig.

**Rotation**

Rotations are half-symmetrical; if your rig is mirrored so is the manipulator. But that is not always the case and those cases will be addressed in a future release.

https://user-images.githubusercontent.com/2152766/143677487-6ba46a4c-0099-4ab9-b64e-e92c22bde0d5.mp4 controls

#### World Symmetry

#### Pose Symmetry

Sometimes, a character had markers assigned whilst in its T-pose or A-pose - a symmetrical pose - but later referenced and animated into a pose that is no longer symmetrical.

The `Pose` mode enables edits to remain symmetrical in this case.




| Axis | Description
|:-----|:------
| `World` | As the name suggests, World implies looking at the worldspace position of your selection with a negative X, Y or Z value. E.g. if your selection is at `Translate X = 5` then it will try and find another selection at `Translate X = -5`. If one is found, this is affected as well.
| `Pose` |

**Multiple Rigs**

If two or more characters are present in the scene, and they were all rigged in the same pose, at the center of the world, then Ragdoll will only look at markers in the same `rdGroup` as the selected marker.

<br>

#### Undo & Redo

No surprises here.

Changes made using the manipulator is undoable as you would expect, with the exception that it currently does not let you undo *the selection itself* like normal Maya selection does; this will be addressed in a future release.

<br>

#### Fit-to-view

Tap the `F` key to fit any selected marker(s) to the view, like you would expect from selected Maya nodes.

!!! hint "Pro Tip"
    This now also applies to the *solver* itself, such that you can fit the entire contents of a physics solver in view.

#### Select Node

Selecting a marker using the manipulator displays the name of the corresponding Maya node, clicking on it will select this Maya node to make edits to it via the Channel Box or Attribute Editor - without leaving the manipulator.

With `Symmetry` enabled, the mirrored marker will be included in the selection, and with multiple markers selected an additional icon will appear to let select all nodes.

<br>

### Auto Limits II

The previous release introduced [Auto Limits](/releases/2021.11.15/#auto-limits) whereby Ragdoll would look at the locked-state of your `Rotate` channels and try to figure out how to replicate this effect physically.

This sometimes worked, sometimes not. This release fixes that, covering all combinations of locked channels, with any manner of joint or rotate axis.

<br>

### Quality of Life

More of this!

#### 1D, 2D and 3D Limits

Ragdoll has a preference as to which axes you use for limits.

1. `X` is great for 1D limits, like a hinge, elbow or knee
2. `YZ` is great for 2D limits, like a shoulder or hip

But `XY` is no good. `XZ` is also bad. And god forbid you should attempt use `Y` or `Z` for a hinge limit. Ragdoll would try, but try in vain.

Knowing which combination to use is not easy, and now you no longer have to. Pick an axis, any axis or combination of axes and Ragdoll will figure things out on its end. You don't have to worry about it.

As an added bonus, the limit axis now aligns with your Maya axis!

Here's a table to make this absolutely clear. 🥰

| Rotate Axis   |   | Limit Axis
|:--------------|:--|:-------------
| `X`           | = | `X`
| `Y`           | = | `Y`
| `Z`           | = | `Z`

<br>

#### Cache On Record

Previously, when you recorded your simulation back onto your character rig, a new simulation would kick in the next time you played. And because your character rig has now changed - to follow the original simulation - the new simulation will be different.

This makes logical sense but can be unexpected. So now, the `Cache` attribute on the solver is automatically enabled to let you compare and contrast your character rig with the simulation; and avoid needless re-simulating when what you really wanted was to record-and-forget.

https://user-images.githubusercontent.com/2152766/144044232-3e72bbfa-d4e5-46c5-bb0b-057ca8c17938.mp4 controls

Once you're ready to re-simulate, run the `Uncache` command or set the `Cache` attribute back to `Off`.

https://user-images.githubusercontent.com/2152766/144044234-c72809fa-e5b4-4dba-bada-94e4798011fe.mp4 controls

<br>

#### Faster Deltas

Pose Deltas are now cleaner and more performant (up to 10x).

Deltas are the triangular-looking shapes drawn to visualise the difference between your animation and the current simulation. They are now only drawn when there is at least *some* difference, which means the vast majority of them in a complex scene are now not drawn, speeding up your viewport significantly.

<br>

#### Disappearing Limits

The limit indicator is drawn using a 2D drawing API which is initialised whenever a Solver is created. It was however *uninitialized* whenever *any* Solver was deleted, so if you had 2 solvers you were out of luck. A re-open of the scene would fix it, but it was annoying and incorrect.

This has now been fixed.

<br>

### Lollipop Hierarchy

The `Create Lollipop` option of Markers generates an extra control shape in the viewport that you can use to manipulate a marker. The goal being to make it easier to spot a marker in a potentially busy channel box.

But the last release didn't let you use `Assign Hierarchy` with `Create Lollipop` without ending up with a broken hierarchy.

**Before**

https://user-images.githubusercontent.com/2152766/142628177-f078f326-6e3e-4c68-b7c0-0dfb842527fe.mp4 controls

**After**

https://user-images.githubusercontent.com/2152766/142628180-2ea5d1aa-5560-4599-abf9-0604b50eb7bc.mp4 controls

<br>

### Replace Intermediate Mesh

In the previous release, if a mesh had a second "intermediate" mesh it would be more difficult to use it with the `Replace Mesh` command.

**Before**

https://user-images.githubusercontent.com/2152766/143280183-d076b432-28fe-41f2-b9ca-f303bd3a44cf.mp4

**After**

Here's it working with intermediate shapes, and the new `Maintain History` option which was always true in the previous release.

https://user-images.githubusercontent.com/2152766/143287859-778c4252-0ef1-43fb-a13d-190500cbf185.mp4

Without it, modifications to the original mesh are ignored; such as a skinned mesh.

https://user-images.githubusercontent.com/2152766/143287863-4adffedd-74e7-49ad-b1f5-4b7b16bae9f4.mp4

<br>

### Separate Translate XYZ Amount

The `Pose Stiffness` in `World` space affected each axis equally.

You can now control each axis independently, to for example follow an input animation closely along the ground plane, the X and Z-axes, but allow for it to deviate along the Y-axis,

https://user-images.githubusercontent.com/2152766/143435579-ec64ddad-d567-4ab2-ab85-89eb7da150e3.mp4 controls

<br>

### Separate Twist and Swing Amount

The `Pose Stiffness` and `Pose Damping` parameters of Markers apply to both Swing and Twist - that is, rotations around the X and YZ axes.

You can now control these independently, for an even finer control over the resulting simulation.

https://user-images.githubusercontent.com/2152766/143433769-325b7cbb-ae24-49f5-a32d-a5896e55e4c5.mp4 controls

<br>

### Maya Exit

There was a memory leak, whereby Maya would sometimes freeze on exit, with an anomymous-looking dialog box appearing on Windows.

![image](https://user-images.githubusercontent.com/2152766/143432430-1249fac5-bbbe-4681-a021-a37146f534b5.png)

This has been fixed.

<br>

### Customised Recording

Some rigs don't work with Maya's default Parent and Orient constraint. As a result, neither does `Record Simulation` or `Snap to Simulation` because those commands use these default constraints.

If this is you, then I have good news. You can now override the command responsible for creating these constraints with one that uses your custom in-house constraints instead.

- [Custom Attach](/custom-attach)
