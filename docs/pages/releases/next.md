---
hidden: true
title: Interactive Manipulators
description: Out of the Channel Box and into the Viewport!
---

Minor maintenance release.

- [**FIXED** Unselectable Viewport Icons](#robust-viewport-icons) Happened from time to time
- [**FIXED** Clean Channel Box](#clean-channel-box) An option to clean or not to clean
- [**FIXED** Legacy Viewport](#legacy-viewport) A rare case of unselectable widgets in the Manipulator UI.
- [**FIXED** Overlap Group for non Grouped Markers](#collision-group) Markers not part of a group would have trouble respecting its overlap group
- [**ADDED**](#edit-constraint-frames) Fine-grained control over unconvenitional orientations

<br>

### Showcase

As is tradition, we must start with candy. Now. it's only been 2 days so all I have for you today is this amazing piece of animation here. 😅

**Wyvern 2**

Follow-up to the WIP from last release from The Wizard, a.k.a. Jason Snyman.

- https://www.linkedin.com/posts/jason-snyman-84711b1_maya-animation-simulation-activity-6876796400018051072-HZv5

https://user-images.githubusercontent.com/2152766/146225647-8a978dc3-a237-4f6b-b59e-dc82f1bb02a8.mp4 controls

**Wasp**

Here's a response to a question on LinkedIn about whether or not you can use Ragdoll to make animation cycles. So here are 3 parts.

1. The finished cycle
2. The input animation
3. The default simulation, before cycling it

Total time spent 1h, including rigging and skinning. The model is a default Maya model from the Content Browser.

https://user-images.githubusercontent.com/2152766/146225143-d7a878bd-3524-4fda-891b-644f8afd0b7a.mp4 controls

<br>

### Robust Viewport Icons

The viewport icons would sometimes be unselectable.

![ui](https://user-images.githubusercontent.com/2152766/145959389-93393227-f1b8-4a3d-96f8-bc1fdfc85c72.gif)

This was due to Maya being unable to provide Ragdoll with the correct "Active View", which Ragdoll uses to map your mouse to 3D. This has now been fixed, by no longer relying on the Active View.

<br>

### Clean Channel Box

With the manipulator in the last release, the Channel Box saw a huge spring cleaning.

| Before | After
|:-------|:-----
| ![image](https://user-images.githubusercontent.com/2152766/145183746-43dc99ab-bdf5-44b1-87d9-2cd548967cfd.png) | ![image](https://user-images.githubusercontent.com/2152766/145186788-2f6e6de5-f6f9-49a0-8048-e24ea09a03e3.png)

It was, however, a little too aggressive. Some of the attributes were still useful, especially for making sweeping changes across lots of markers at once. So in this release, you know have the option of:

1. Having these attributes visible on `Assign` via the Option Dialog
2. Toggling these attributes on/off via `Ragdoll -> Utilities -> Toggle Marker Attributes`



<br>

### Legacy Viewport

More specifically, the environment variable `MAYA_ENABLE_VP2_PLUGIN_LOCATOR_LEGACY_DRAW`, is still in use in some studios. This variable would cause the Manipulator UI to be unselectable.

https://user-images.githubusercontent.com/2152766/146153487-23b86735-76f3-4a33-ba14-e3075afb1c10.mp4 controls

This has now been fixed.

<br>

### Collision Group

Long markers, like free boxes and other environment assets and props have an `Overlap Group` like any other. But unless they are also part of a group, they would sometimes not respect the `Overlap Group`, requiring a scene re-open in order to take effect.

This has now been fixed.

<br>

### Edit Constraint Frames

The previous release simplified limits by a lot, but there are still cases where the default orientation of some rig controls ends up in a funny situation.

https://user-images.githubusercontent.com/2152766/146166397-79adb644-a922-4fad-9c5d-a372b22bda2d.mp4 controls

!!! info "Note"
    This does *not* matter to the simulation. It is only a rendering artefact.

To make this a little easier to work with, you can rotate the entire limit like this.

https://user-images.githubusercontent.com/2152766/146166283-937400e5-5de8-43a4-b02a-9db822c91639.mp4 controls

!!! info "Note"
    You don't need the locators once you are done editing them, you should definitely delete them.

This will be made redundant in a future version as it gets much too technical and too easy to shoot yourself in the foot. If you make a mistake, delete the locators and call `Reset Constraint Frames` in the same menu to start again.
