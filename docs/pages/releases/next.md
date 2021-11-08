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
- [**FIXED** Robust Rendering](#robust-rendering) Rendering on some hardware, especially in Maya 2019, was whack sometimes. No longer!
- [**ADDED** Extract Simulation](#extract-simulation) Get the raw data as a baked joint hierarchy, super fast!
- [**FIXED** Unloading Ragdoll on Linux](#unloading-on-linux) Could easily cause a crash
- [**UPDATED** LD_LIBRARY_PATH](#ld_library_path) If you don't know what this is, you don't have to worry about it

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

<br>

### Robust Rendering

https://user-images.githubusercontent.com/2152766/140603516-8783164c-4030-48eb-9ec7-0a071626f154.mp4 controls

https://user-images.githubusercontent.com/2152766/140603518-d68f1b83-a20f-403f-89b9-be2073ccd25c.mp4 controls


<br>

### LD_LIBRARY_PATH

With the introduction of Mac support a change was made to the way LimeLM - the licencing software used by Ragdoll - is distributed. Rather than being statically linked on Linux and dynamically linked but programatically located on Windows, it is now dynamically linked and automatically located on all platforms.

TLDR; your environment is updated for Ragdoll to find these libraries.

```py
# Windows
os.environ["PATH"] += ";\\Ragdoll\\shared\\windows"

# Linux
os.environ["LD_LIBRARY_PATH"] += ":/Ragdoll/shared/linux"

# Mac
os.environ["DYLD_LIBRARY_PATH"] += ":/Ragdoll/shared/mac"
```

The change is coming from the `Ragdoll.mod` file.

**Why am I telling you this?**

In the off chance that there is another plug-in using a different version of LimeLM in your arsenal, there may be a conflict whereby:

1. Ragdoll module is loaded, appends v1.0 of LimeLM to `LD_LIBRARY_PATH`
2. Embergen module is loaded, appends v0.5beta of LimeLM to `LD_LIBRARY_PATH`
3. Ragdoll plug-in is loaded, picks up `v0.5beta`
4. Embergen plug-in is loaded, picks up `v0.5beta`

This will be resolved in a later version of Ragdoll, but until then, in the unlikely event there is a conflict, here's what you can do.

```py
import os
before = os.environ["LD_LIBRARY_PATH"]
os.environ["LD_LIBRARY_PATH"] = "/path/to/Ragdoll/shared:%s" % before
cmds.loadPlugin("ragdoll")
os.environ["LD_LIBRARY_PATH"] = before
```

Namely, rather than loading Ragdoll from your plug-in manager, load it using this wrapper script. It will ensure Ragdoll's path is picked up ahead of any third-party plug-in, without negatively affecting anything around it.

This also applies to Windows and Mac.