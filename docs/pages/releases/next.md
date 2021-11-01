---
hidden: true
title: Animation Capture pt. 4/4
description: Markers 1.0
---

Highlight for this release is **Performance and Mac**, and is the final part of the new [Markers](/releases/2021.09.27/) which are now able to do everything Rigids could, and more.

!!! into "In with the new, out with the old"
    The next few releases will slowly but surely replace Rigids with Markers. So if there is anything you find yourself unable to do with Markers, let us know and we'll get that in there as soon as possible.

    - [Chat](https://ragdolldynamics.com/chat)
    - [Contact](https://ragdolldynamics.com/contact)

- [**ADDED** Ragdoll for Mac](#ragdoll-for-mac) You heard it right, it's here!
- [**FIXED** Robust Recording](#robust-recording) More resilient to locked controls and custom rotation axes
- [**FIXED** Robust Caching](#caching-start-frame) Works as expected
- [**ADDED** Extract Simulation](#extract-simulation) Get the raw data as a baked joint hierarchy, super fast!
- [**FIXED** Unloading Ragdoll on Linux](#unloading-on-linux) Could easily cause a crash

<br>

### Ragdoll for Mac

There is now an option to download Ragdoll for Mac!

If you are a Mac user, please let us know how you get along. The builds were made on Big Sur and should work well with Big Sur, but Autodesk recommends El Capitan for Maya 2018 (which appears ancient!).

<br>

### Robust Recording

Now 2x faster or more, and also less sensitive to quirks in a rig or skeletal hierarchy.

**Before**

49 fps.

https://user-images.githubusercontent.com/2152766/139644573-9d9c9f23-7c73-4ee0-a47d-4aa92f4c4863.mp4

**After**

135 fps. The numbers speak for themselves.

https://user-images.githubusercontent.com/2152766/139644578-03717acb-26cf-411f-aef7-b1b9cb34f602.mp4

<br>

### Robust Caching

Caching whilst standing on the start frame could cause hiccups on occasion, this release fixes that.

> Notice how it doesn't update the cache when standing on the start frame?

https://user-images.githubusercontent.com/2152766/139645240-34a7f89e-d0c4-4cfd-825c-5bef215191db.mp4

<br>

### Extract Simulation

Get data out of the solver and into a baked joint hierarchy.

You can use this to build a library of animations, or to handle the retargeting from simulation to animation manually by just constraining to the resulting joint hierarchy.

!!! note "Performance"
    Notice how fast this is!

https://user-images.githubusercontent.com/2152766/139657721-576c5b8f-e852-4e96-a9ed-dad4933920ff.mp4 controls
