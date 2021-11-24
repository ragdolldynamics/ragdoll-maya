---
hidden: true
title: Interactive Manipulators
description: Out of the Channel Box and into the Viewport!
---

![image](https://user-images.githubusercontent.com/2152766/141471283-3a771240-f80d-4745-844d-6f0c0ed87bc5.png)

Highlight for this release is **Markers part 4 of 4**!

- [**ADDED** Manipulator](#manipulators) Edit things faster and visually with these new tricks
- [**ADDED** Faster & Cleaner Deltas](#clean-deltas) Pose Deltas are now cleaner and more performant (up to 10x)
- [**FIXED** Disappearing Limits](#disappearing-limaits) Two solvers, one removed, caused limit indicators to vanish
- [**FIXED** Lollipop Hierarchy](#lollipop-hierarchy) Lollipops could break a hierarchy of markers, but no more

<br>

### Showcase

<br>

### Manipulator

Common values can now be edited interactively via the viewport, using the new `Manipulator`.

#### Multi-select
#### Symmetry
#### Undo/Redo
#### Fit-to-view

<br>

### Faster Deltas

Deltas are the triangular-looking shapes drawn to visualise the difference between your animation and the current simulation. They are now only drawn when there is at least *some* difference, which means the vast majority of them in a complex scene are now not drawn, speeding up your viewport significantly.

<br>

### Disappearing Limits

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
