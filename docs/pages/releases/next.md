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

**Ragdoll in 30 Seconds**

A brief overview of what Ragdoll is.

https://user-images.githubusercontent.com/2152766/145581522-2f229741-45c4-43f2-9c3b-5ffb5bb29fc5.mp4 controls

**Mocap Chap**

Footage from the [new tutorial](/tutorials/mocap_chap)

https://user-images.githubusercontent.com/2152766/145550133-4d9daedc-478c-44db-8a65-5a248b26e67b.mp4 controls


https://user-images.githubusercontent.com/2152766/145550147-56714786-3ac9-44b8-b73f-b85d34e53bf4.mp4 controls


<br>

### Manipulators

One of the most challenging aspect of Ragdoll to date is editing shapes and limits. These have now been *greatly* simplified via the use of "manipulators", similar to your standard Translate/Rotate/Scale manipulators. Except on steroids.

Here's a 21 second overview.

https://user-images.githubusercontent.com/2152766/145669018-15c6847a-b031-4770-afe3-5a0b0bf50082.mp4 controls

<br>

#### Activate

You have a few options for activating the manipulator.

1. Run `Ragdoll -> Manipulator`
2. Select a Ragdoll node and press `T` on your keyboard
2. Select a Ragdoll node and click the `Show Manipulator Tool` in the Toolbar

Any of the Ragdoll nodes can be selected in order to enable the manipulator via the `T` keyboard shortcut.

- `rdSolver`
- `rdGroup`
- `rdMarker`
- `rdDistanceConstraint`
- `rdPinConstraint`
- `rdFixedConstraint`

!!! info "Solver Shape"
    At the time of this writing, the solver needs its *shape* selected, not the parent transform. This will be addressed in a future release.

A comfortable workflow is..

1. Select any assigned control
2. Select the marker DG node in the Channel Box
3. Press `T`

> The selected Marker will be pre-selected in the manipulator.

https://user-images.githubusercontent.com/2152766/145669291-61d4462f-cbd2-45ab-b344-56eddb93bf8d.mp4 controls

Alternatively, press the `Show Manipulator Tool` button in the Toolbar.

https://user-images.githubusercontent.com/2152766/145669287-08aca80b-9241-41cf-aa4e-cbbcbc5c78c6.mp4 controls

<br>

#### Shape Modes

This release introduces a manipulator with two "modes".

| Mode | Description
|:-----|:----------
| Shape Mode | Edit shape properties, like `Length`, `Radius`, `Position` and `Orientation`
| Limit Mode | Edit limit properties, like `Twist` and `Swing` along with their pivots.

In Shape Mode, you currently have 5 manipulators.

| Manipulator | Description
|:------------|:------------
| `Translate` | Affects the `Shape Offset` attribute
| `Rotate`    | Affects the `Shape Rotation` attribute
| `Scale`     | Affects the `Shape Radius` and `Shape Extents` attributes
| `Length`    | Affects the `Shape Length` attribute, for the `Capsule` shape
| `HUD`       | Individual control over primary attributes, like `Shape Extents` axes

**Translate**

Hold the middle-mouse button to translate.

https://user-images.githubusercontent.com/2152766/145670525-75826331-d1ae-47d6-a046-028ed3e858da.mp4 controls

**Rotate**

Hold Ctrl + middle-mouse button to rotate.

https://user-images.githubusercontent.com/2152766/145670526-0a45e65a-f749-4b09-b394-ee65104766c1.mp4 controls

**Scale**

Hold Ctrl + left-mouse button to scale.

https://user-images.githubusercontent.com/2152766/145670528-41fc9f3e-b1e0-41ac-adcd-dcf62fa99aca.mp4 controls

**Length**

The `Capsule` shape have additional in-view manipulators you can drag to affect each side independently.

https://user-images.githubusercontent.com/2152766/145670530-bcf791d1-fa19-4059-9c14-7c283061ba8e.mp4 controls

**HUD**

Finally, attributes without a visual handle can be edited via the viewport HUD.

https://user-images.githubusercontent.com/2152766/145670533-9b176326-a6da-4a67-a014-8902a0bc913e.mp4 controls

<br>

#### Limit Mode

In Limit Mode, you currently have 2 manipulators.

| Manipulator | Description
|:------------|:------------
| `Limit`     | Affects the `Limit Range XYZ` attributes
| `HUD`       | For locking and enabling of limits

**Enable and Disable**

Click the `Axis` button to limit the rotation about a particular axis.

https://user-images.githubusercontent.com/2152766/145671609-9a5b6c88-4a52-4a41-89aa-8d8e29deb642.mp4 controls

**Lock and Unlock**

Click the `Lock` button to prevent all rotation about the axis.

https://user-images.githubusercontent.com/2152766/145671610-a23beb01-93e3-4f2b-a0d1-ba9232a3ad9e.mp4 controls

**Asymmetrical Edits**

> Hold `Ctrl` to make asymmetrical edits

Some limbs start out at the center of their limit. Like your hip and neck. They are typically modeled to enable equal movement in each axis.

Other limbs, like the elbow and knee, are typically modeled in the extreme of their limit. Able to only rotate in one direction. For these cases, they need an *asymmetrical* limit.

https://user-images.githubusercontent.com/2152766/145671611-3de2bf76-46b8-4511-a74d-40f01d6e3550.mp4 controls

With limits in multiple axes, keep an eye out for how asymmetrical edits to one axis affect the others.

https://user-images.githubusercontent.com/2152766/145671818-b0974163-4c40-4de2-822d-eb0aeb399551.mp4 controls

!!! info "Why are they moving?"
    Under the hood, each axis must be still be symmetrical; edits only appear to be asymmetrical for your convenience. What's really happening is the entire limit is both changing shape and also rotating and the rotation is causing all axes to move.

    This is an inherent limitation (pun!) of limits in Ragdoll and is unlikely to be addressed in the future, so we'll have to work with it.

If you mess up and want to start from scratch, hit the `Reset` button, also found under `Ragdoll -> Utilities -> Reset Constraint Frames`

https://user-images.githubusercontent.com/2152766/145671817-37e1b121-1860-4c4a-b097-803ba27ac6e4.mp4 controls

<br>

#### Symmetry

Enabled per default, symmetry will mirror your edits across an axis.

There are 2 types of symmetry at the time of this writing.

| Type  | Description
|:------|:----------
| `World` | Look for a marker across the current axis in worldspace
| `Pose`  | Based on the pose at the time of assigning markers, which is typically symmetrical.

https://user-images.githubusercontent.com/2152766/143677487-6ba46a4c-0099-4ab9-b64e-e92c22bde0d5.mp4 controls

Each of which can be made symmetrical in either the X, Y or Z axes. The `Pose` axis means you can make changes even if a character has been posed after having been assigned. A feature particularly useful when assigning to the A- or T-pose of a character rig.

**Pose Based Symmetry**

Because these controls were assigned in the T-pose of the rig, you can use Pose-based symmetry to make changes even when the character is currently asymmetrical.

https://user-images.githubusercontent.com/2152766/145671293-4755044e-55b6-41b7-9120-99b03cbc2889.mp4 controls

**Multiple Rigs**

If two or more characters are present in the scene, and they were all rigged in the same pose, at the center of the world, then Ragdoll will only look at markers in the same `rdGroup` as the selected Marker.

**Search Distance**

On the right-hand side of the `Enable Symmetry` button, there is a `Search Distance` gizmo.

> Drag to edit this value

When you select a marker on one side, it will search for a marker at the opposite side of the axis you've chosen. Because positions are all approximate, it uses a maximum search distance to look for it.

**Matches**

Ideally, there should only be one match. But in a crowded hierarchy there may be several. Tune the `Search Distance` to control the number of matches, to ensure it doesn't pick the wrong one.

<br>

#### Multi-select

> Disable `Symmetry` to enable multi-select

Hold `Shift` to select and manipulate *multiple* markers at once.

https://user-images.githubusercontent.com/2152766/145672423-e88cbbe0-a47f-40ab-a102-e7f6114bbc55.mp4

<br>

#### Undo & Redo

No surprises here.

Changes made using the manipulator is undoable as you would expect, with the exception that it currently does not let you undo *the selection itself* like normal Maya selection does; this will be addressed in a future release.

<br>

#### Fit-to-view

Tap the `F` key to fit any selected Marker(s) to the view, like you would expect from selected Maya nodes.

https://user-images.githubusercontent.com/2152766/145672626-5d547178-35b4-4ae7-b984-e4908033e68c.mp4 controls

!!! info "Caveat"
    This currently only applies if you've activated the manipulator using the `Ragdoll -> Manipulator` menu item, or have the `rdSolver` shape node selected.

<br>

#### Select Node

> Click the `Select Node` button to select this node in Maya

Per default, Ragdoll and Maya selection are separate. You can have Maya select the node(s) currently seleted in Ragdoll by pressing the `Select Node` button.

https://user-images.githubusercontent.com/2152766/145672548-d72c6ed2-b573-4f16-adde-c7f8ab615406.mp4 controls

You can automate this using the `Synchronise` button at the far-left of the HUD.

https://user-images.githubusercontent.com/2152766/145672549-bf13396a-6991-49b9-913a-70fc3669ae16.mp4 controls

!!! info "Why is this not on per default?"
    The solver is what is actually being fitted. If the selection is changed to a marker (which is not a DAG node, and therefore lacks a visual representation) then fit-to-view no longer works.

    This will be addressed in a future release and made into the default.

With Multi-select or symmetry enabled, all selected markers will be selected in Maya, to make bulk edits via the Channel Box easier.

<br>

#### Manipulator Help

On the right-hand side is an overview of the hotkeys and mouse button combinations you can use, and what they do.

![image](https://user-images.githubusercontent.com/2152766/145671095-2b9e3813-59f8-4a0e-a33b-022bead19b79.png)

It can be hidden via the HUD button on the upper right-hand side.

https://user-images.githubusercontent.com/2152766/145671135-31d11b87-a678-47eb-a7dc-a01b5ae570aa.mp4 controls

<br>

### Quality of Life

More of this!

<br>

#### 1D, 2D and 3D Limits

Ragdoll used to have a preference as to which axes you use for limits.

1. `X` is great for 1D limits, like a hinge, elbow or knee
2. `YZ` is great for 2D limits, like a shoulder or hip

But `XY` is no good. `XZ` is also bad. And god forbid you should attempt use `Y` or `Z` as a hinge limit. Ragdoll would try, but try in vain.

Knowing which combination to use is not easy, and now you no longer have to. Pick an axis, any axis or combination of axes and Ragdoll will figure things out on its end. You don't have to worry about it.

As an added bonus, the limit axis now (more easily) aligns with your Maya axis!

Here's a table to make this absolutely clear. 🥰

| Maya Rotate Axis   |   | Ragdoll Limit Axis
|:--------------|:--|:-------------
| `X`           | = | `X`
| `Y`           | = | `Y`
| `Z`           | = | `Z`

!!! info "Caveat"
    With one exception, see **Asymmetrical Limits** under [Limit Mode](#limit-mode) above. As soon as they rotate, they will no longer align with Maya; which isn't a problem most of the time, but can be.

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

**Before**

![image](https://user-images.githubusercontent.com/2152766/145673087-4161ea32-cf58-4be1-bdc8-4752fa15859d.png)

**After**

Notice how they only appear if there is actually a difference between the animation and simulation.

https://user-images.githubusercontent.com/2152766/145673131-a1d47cf2-6d24-415a-a7e3-ae12503cbc3a.mp4 controls

<br>

#### Disappearing Limits

The limit indicator is drawn using a 2D drawing API which is initialised whenever a Solver is created. It was however *uninitialized* whenever *any* Solver was deleted, so if you had 2 solvers you were out of luck. A re-open of the scene would fix it, but it was annoying and incorrect.

This has now been fixed.

<br>

#### Ground Fits Grid

Previous releases would put a ground underneath the first assigned controls, with a size relative the size of your selection.

Turns out, this wasn't great in practice and usually ended up being too small. In this release, the ground inherits whatever size your viewport grid is.

<br>

### Auto Limits II

The previous release introduced [Auto Limits](/releases/2021.11.15/#auto-limits) whereby Ragdoll would look at the locked-state of your `Rotate` channels and try to figure out how to replicate this effect physically.

This sometimes worked, sometimes not. This release fixes that, covering all combinations of locked channels, with any manner of joint or rotate axis.

<br>

### Lollipop Hierarchy

The `Create Lollipop` option of Markers generates an extra control shape in the viewport that you can use to manipulate a Marker. The goal being to make it easier to spot a Marker in a potentially busy channel box.

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

### Transform Limits

Recording onto transforms with Maya's native limits on them could result in this.

![image](https://user-images.githubusercontent.com/2152766/145573500-5ef2fe21-c9dd-4be6-9334-7b8569bb3e47.png)

https://user-images.githubusercontent.com/2152766/145573213-02aa2922-20d6-4d22-ae26-d6a9f7986dfb.mp4 controls

This has now been fixed.

??? question "How?"
    Since you asked, they are simply disabled. I've never seen or heard of anyone actually using these and was surprised to find they were in active use by the native motion capture library that ships with Maya.

    If you or anyone you know *do* use them, let me know and they will be given support.

https://user-images.githubusercontent.com/2152766/145573224-60f74627-fc6d-4ffc-8558-4be6560279b1.mp4 controls

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
