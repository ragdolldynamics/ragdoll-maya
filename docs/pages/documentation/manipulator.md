---
title: Manipulator
icon: "manipulator_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga14.png>
</div>

Interactively manipulate shapes and limits using the Manipulator.

<br>

### Manipulator

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

![image](https://user-images.githubusercontent.com/2152766/145709365-8c2384b8-1811-4df3-a863-564a88fe9fbf.png)

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

If you mess up and want to start from scratch, hit the `Reset` button, also found under..

- `Ragdoll -> Utilities -> Reset Constraint Frames`

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

!!! question "Drag Select?"
    Not yet! But will be added in a future release.


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
