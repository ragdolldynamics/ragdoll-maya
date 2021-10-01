---
title: Animation Capture pt. 2/4
description: Performance, performance, performance
---

Highlight for this release is **Animation Capture**.

- [**ENHANCED** Auto Delete](#auto-delete) Nodes associated with markers now vanish when you expect them to
- [**ENHANCED** Reset Button Icon](#reset-button) More obvious what it does and how it works.

<br>

### Auto Delete

The `Delete All Physics` menu command does what it says on the tin; it deletes all Ragdoll nodes from your Maya scene. But deleting a node, such as the new `rSolver` left behind anything associated with it, like `rGroup` and any `rMarker` nodes.

This releases addresses this by automatically removing anything that depends on the node you delete. For example..

- Deleting a `rMarker` node also deletes any associated lollipop controls
- Deleting a `rGroup` also deletes the associated `rMarker` nodes
- Deleting the `rSolver` deleles all `rGroup` and `rMarker` nodes

Therefore, deleting a solver is now equivalent to `Delete All Physics`, making it much more intuitive to delete things on a whim.

<br>

### Reset Button

https://user-images.githubusercontent.com/2152766/134865922-07b55df5-1a88-4d5c-850c-bcc6976ee1d9.mp4
