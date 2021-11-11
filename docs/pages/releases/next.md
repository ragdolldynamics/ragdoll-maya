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
- [**ADDED** Robust Recording](#robust-recording) More resilient to locked controls and custom rotation axes
- [**ADDED** Robust Caching](#caching-start-frame) Works as expected
- [**ADDED** Robust Rendering](#robust-rendering) Rendering on some hardware, especially in Maya 2019, was whack sometimes. No longer!
- [**ADDED** Snap to Simulation](#snap-to-simulation) Snap your character to wherever the simulation is, for quick and natural posing
- [**ADDED** Extract Simulation](#extract-simulation) Get the raw data as a baked joint hierarchy, super fast!
- [**FIXED** Unloading Ragdoll on Linux](#unloading-on-linux) Could easily cause a crash
- [**UPDATED** `PATH` and Windows](#path) If you don't know what this is, you don't have to worry about it

<br>

### Ragdoll for Mac

There is now an option to download Ragdoll for Mac!

If you are a Mac user, please let us know how you get along. The builds were made on Big Sur and should work well with Big Sur, but Autodesk recommends El Capitan for Maya 2018 (which appears ancient!).

<br>

### Robust Recording

Recording now defaults to ending up on an Animation Layer, with an option not to. It is also 2x faster or more, and also less sensitive to quirks in a rig or skeletal hierarchy.

- [x] Uniform Scale
- [ ] Non-uniform Scale
- [ ] Negative Scale
- [ ] Rotate Pivot
- [ ] Scale Pivot
- [ ] Rotate Axis
- [ ] Joint Orient

**Before**

49 fps.

https://user-images.githubusercontent.com/2152766/139644573-9d9c9f23-7c73-4ee0-a47d-4aa92f4c4863.mp4 controls

**After**

135 fps. The numbers speak for themselves.

https://user-images.githubusercontent.com/2152766/139644578-03717acb-26cf-411f-aef7-b1b9cb34f602.mp4 controls

<br>

### Robust Caching

Caching whilst standing on the start frame could cause hiccups on occasion, this release fixes that.

> Notice how it doesn't update the cache when standing on the start frame?

https://user-images.githubusercontent.com/2152766/139645240-34a7f89e-d0c4-4cfd-825c-5bef215191db.mp4 controls

<br>

### Snap to Simulation


https://user-images.githubusercontent.com/2152766/141302109-6818b04d-9b57-4378-bdea-e62b98220f16.mp4 controls

https://user-images.githubusercontent.com/2152766/141302185-df7ee9d0-567e-4a52-a9d3-46fcfee33eeb.mp4 controls

https://user-images.githubusercontent.com/2152766/141302197-4c895c4a-8e34-486e-8835-a91ffa50ff99.mp4 controls

<br>

### Extract Simulation

Get data out of the solver and into a baked joint hierarchy.

You can use this to build a library of animations, or to handle the retargeting from simulation to animation manually by just constraining to the resulting joint hierarchy.

!!! note "Performance"
    Notice how fast this is!

https://user-images.githubusercontent.com/2152766/139657721-576c5b8f-e852-4e96-a9ed-dad4933920ff.mp4 controls

<br>

### Robust Rendering

Whenever Ragdoll drew shapes, like capsules and convex hulls, it used part of Maya's drawing API called `MRenderItem`. Lines on the other hand - like those for limits and guides - were drawn using a simplified API called `MUIDrawManager`.

```cpp
drawManager->circle(point, radius);
drawManager->line(pointA, pointB, thickness);
// And so on..
```

Which is a fantastic, well-designed API that has worked great for the past year. Until it didn't. As it happens, this API is broken.. Reports were coming in from all across the globe about lines looking like.. Well like this.

https://user-images.githubusercontent.com/2152766/140603516-8783164c-4030-48eb-9ec7-0a071626f154.mp4 controls

Some if it I could replicate, this here is Maya 2019 in which the behavior is erratic. But the same could be said for some hardware and driver combinations; most of which I have never been able to replicate here.

This version throws all of that out the window, and reimplements it from scratch. It's a pity, because the API is very easy to work with and a great way to get started rendering in Maya.

That said, our new API is not only *much faster* but also *much more powerful*. You can expect to see a lot of new 2D rendering, including fully interactive UI elements in 3D space.

Until then, if you've been having issues with Ragdoll and lines, you can now breathe easy.

https://user-images.githubusercontent.com/2152766/140603518-d68f1b83-a20f-403f-89b9-be2073ccd25c.mp4 controls


<br>

### PATH and Windows

With the introduction of Mac support a change was made to the way LimeLM - the licencing software used by Ragdoll - is distributed. Rather than being statically linked on Linux and dynamically linked but programatically located on Windows, it is now dynamically linked and automatically located on all platforms.

> note "Windows Only"
    This only applies to Windows. Linux and Mac references the libraries relative the plug-in location. In short, you don't have to worry about it.

You don't have to care about this, unless you are on Windows and care about what's on your `PATH` to which this happens.

```py
# Windows
os.environ["PATH"] += ";\\Ragdoll\\shared\\windows"
```

The change is coming from the `Ragdoll.mod` file.

**Why am I telling you this?**

In the wildly unlikely chance that there is another plug-in using a different version of LimeLM in your arsenal, there may be a conflict whereby:

1. Ragdoll module is loaded, appends v1.0 of LimeLM to `PATH`
2. Other Plug-in module is loaded, appends v0.5beta of LimeLM to `PATH`
3. Ragdoll plug-in is loaded, picks up `v0.5beta`
4. Other Plug-in plug-in is loaded, picks up `v0.5beta`

This will be resolved in a later version of Ragdoll, but until then, in the unlikely event there is a conflict, here's what you can do.

```py
import os
before = os.environ["PATH"]
os.environ["PATH"] = "/path/to/Ragdoll/shared:%s" % before
cmds.loadPlugin("ragdoll")
os.environ["PATH"] = before
```

Namely, rather than loading Ragdoll from your plug-in manager, load it using this wrapper script. It will ensure Ragdoll's path is picked up ahead of any third-party plug-in, without negatively affecting anything around it.
