---
hidden: true
title: Animation Capture pt. 2/4
description: Performance, performance, performance
---

Highlight for this release is **Rendering Performance**.

- [**ENHANCED** Performance](#performance) Less work, greater parallelism and more GPU
- [**ADDED** Motion Blur](#motion-blur) More robust and actually useful compared to native Maya motion blur
- [**ENHANCED** Quality of Life](#quality-of-life) Automated clean-up, support for Z-up and more!

<br>

### Performance

In terms of time spent, Ragdoll has three stages.

| # | Stage | Description
|:--|:------|:----------
| 1 | `Evaluation` | This is your character rig - the transform hierarchy, constraints, any deformers, that kind of thing.
| 2 | `Simulation` | Once evaluated, Ragdoll considers all of this data and applies forces, solves constraints, contacts, that kind of thing.
| 3 | `Rendering` | Finally, we need pixels. In the case of Ragdoll, this means generating and uploading geometry to the GPU; including capsules but also your meshes which are converted into "convex hulls".

Simulation has always been fast and in the previous release, we focused entirely on workflow which had an indirect impact on `Evaluation` and `Rendering`. One got faster, but the other got slower.

![image](https://user-images.githubusercontent.com/2152766/135710838-f8fe9c13-ba0d-4f11-a41c-bce1155829b9.png)

!!! info "Changes in Part 1/4"
    Let's recap what happens in the previous release.

    We tackled Evaluation which boosted performance by 2-10x by unlocking parallelism. Before, the better your character rig benefited from multithreading the *worse* it would perform with Ragdoll. Ragdoll would force any control you simulated into serial evaluation - to compute one after another - because the solver was fundamentally single-threaded.

    With Markers, Ragdoll separated from the overall rig evaluation, which meant (1) your rig can continue running in parallel and (2) Ragdoll could also run in parallel.

    Consider this example.

    | Rigids | Markers
    |:-------|:----------
    | ![before](https://user-images.githubusercontent.com/2152766/135705272-0ea9e006-ed66-4f48-a442-42255844104d.png) | ![after](https://user-images.githubusercontent.com/2152766/135705269-363db122-7fe9-485d-b5a7-50af36335258.png)

    This is how Maya scheduled evaluation for this scene with `Rigid` versus `Marker`. To the left, everything runs one after the other. It's terrible. To the right, every box is evaluated in parallel. Which means the more boxes and cores you have, the better utilisation you get.

    The scene itself is very simple, it's this one here.

    <img width=300 src=https://user-images.githubusercontent.com/2152766/135705381-df6b9791-b1b5-4aea-818f-660ff6bafe43.png>

    So evaluation got faster, but rendering got slower. All-in-all we gained about 100% performance.

With this release, we'll tackle that rendering block. Let's have a look at what's changed, in order of most-to-least significance.

| Topic  | Savings | Description
|:--------|:--------|:------------
| Less CPU to GPU communication | 1550x | More buffers, less uniforms
| Connection Monitoring | 40x | Less dependence on time, more on physical connections being made and unmade
| Change Monitoring | 40x | Ignore anything that hasn't actually changed
| Less Dirty Propagation | 3x | Less of a shotgun blast, more like a sniper

<br>

#### CPU to GPU Communication

The previous release, and each one before it, had 1 shader per rigid. In the case of 600 rigid bodies, that meant 600 shaders. 600 shaders means 600 parameter updates of primarily color and 600 unique draw calls.

On top of this, all geometry was regenerated and re-uploaded to the GPU on every frame. Robust, but not very fast.

This release consolidates all shaders into *one*, colors are uploaded only once alongside their geometry and rendered using a custom GLSL shader (i.e. OpenGL 3.3).

??? info "What about DirectX?"
    If you are on Windows and can't use OpenGL for whichever reason, there is backwards compatibility built-in.

    ```py
    from ragdoll import options
    options.write("useShaders", False)
    ```

    Or via the Ragdoll Preferences.

    ![image](https://user-images.githubusercontent.com/2152766/135706370-250f4ebb-93e7-4752-9062-ffad65de47ad.png)

    Bearing in mind this will cost you 50% of the rendering performance and won't benefit from future shading related features and improvements. It will remain until it's clear whether and how much it is actually used. (Let us know in the chat!)

Let's have a look at how this change affects your overall experience.

**Before (7fps)**

https://user-images.githubusercontent.com/2152766/135825072-fb1b52b0-34bc-493c-a960-be8537a38e27.mp4

**After (130 fps)**

https://user-images.githubusercontent.com/2152766/135825078-d3c876a2-6de7-42b4-8485-6d8947e94cec.mp4

A closer look reveals exactly where this improvement comes from.

**Before**

This block is what we control, it's the Ragdoll rendering pipeline taking a whopping **93 ms** per refresh.

![image](https://user-images.githubusercontent.com/2152766/135825217-017f37fa-dae0-457f-8a33-cc0c8b6419c1.png)

**After**

With this release, this number dropped to **0.06ms** (58 microseconds) that's an improvement of 1550x (!).

![image](https://user-images.githubusercontent.com/2152766/135819476-4d2c90d9-7f16-4f6b-a809-b18f60aec826.png)

!!! question "What about the other blocks?"
    The bottleneck has now moved to that green one and all of those blue, and those are Maya's internal rendering pipeline.

    There isn't much we can do to *directly* impact it; it's mostly out of our hands. However, by massaging our data more and making life easier for Maya it should be possible to reduce these as well.

    See [Future Work](#future-work) for details on next steps, and if this is something you, fellow reader, is familiar with do [get in touch!](https://ragdolldynamics/contact)

<br>

#### Connection & Change Monitoring

In the previous release, and all versions of Ragdoll so far, we've tasked Maya with evaluating every plug on every frame, including the heavy-duty plugs between `Rigid Body` -> `Solver`.

Here's what this felt like in a scenario of 600 unique objects.

**Before (5 fps)**

Painful! The reason is because even though we're only moving a single box, Ragdoll checks-in with all other boxes too.

https://user-images.githubusercontent.com/2152766/135825726-53b76429-0d05-4fa3-847c-19c825d0c34d.mp4 controls

**After (90 fps)**

Blissful. In this case, only one of the boxes is actually updated, as one would expect.

https://user-images.githubusercontent.com/2152766/135825732-ca3631a2-2920-428a-9f8d-2cb165a4531a.mp4 controls

Let's have a closer look at where performance is going here.

**Before**

Oh that's ghastly. Not only does it spend time evaluating all of those boxes, but it's making the solver take much longer consolidating the results taking a whopping **56 ms**.

![image](https://user-images.githubusercontent.com/2152766/135825628-e671a785-38ef-4c2f-8d52-2a33a1c4b099.png)

**After**

Whereas now, as one would expect, we're only evaluating this one box in a total of **0.7ms**, resulting in a performance improvement 80x.

![image](https://user-images.githubusercontent.com/2152766/135825659-a2f96650-1d84-4994-885f-e9d10fdaa3e7.png)

!!! question "That looks like 3?"
    And that's true, it still makes three separate calls to this one box. Which means there's more room to optimise here, and we'll get there.

    Needless to say, this happened before as well but was obscured by how many calls there actually are. Luckily, at least two of these calls happen in parallel.

**600 capsules**

The current framerate on 600 unique objects, something for future Ragdoll to try and compete with. For reference, an average ragdoll consists of about 20-30 objects.

https://user-images.githubusercontent.com/2152766/135828652-cc0ef941-a6ad-4ecd-9c9d-f69469a29a17.mp4 controls

<br>

#### Future Work

There is at least 4-16x performance left on the table for specialised cases.

| Work | Savings | Benefit
|:-----|:--------|:----
| Optimised Render Items | 4x | Native Maya still renders 4x faster than us
| Instancing for Rendering | 2-4x | Every render item is currently unique which means neither Maya nor your GPU is able to reuse geometry. Instancing is how games is able to render millions of objects on-screen at 60 fps, and best we can hope for is thousands.
| Instancing for Simulation | 2-4x | Likewise, every physics object is unique and, again, instancing in simulation is how games is able to run destruction and have thousands of objects interact in real-time.

The challenge in both of these is deduplication; of identifying which of the many shapes you use can reuse their geometry.

<br>

### Motion Blur

An unintended conseqence of the optimisation and shader work, we're currently compliant with Maya's requirement for motion blur. Since all of our simulation is transform-based, it means all of what you simulate can be motion blurred, as opposed to deformer and particle-based motion.

https://user-images.githubusercontent.com/2152766/135816508-81aae73d-7f4a-4165-9af8-abbc0c074409.mp4 controls

!!! info "Heads up"
    I use the word "currently" because there are a few key requirements that we might not be able to maintain into the future. Motion blur changes the evaluation graph almost entirely, needing to evaluate things before and after the current time, and doing a lot of that work in parallel. Our code is 99% parallelised already which is how this can work, but some code simply cannot be run in parallel.

<br>

### Quality of Life

A few things to make your day that much more bright.

<br>

#### Guide Space 2.0

In the previous release, we introduced `Guide Space`. Which was a quick way of controlling whether a simulation should follow your animation in..

1. Local space
2. Worldspace
3. Both

But it was challenging to control, not very obvious. Especially with how it was also taking into account its "group" guide space. This release addresses this by enabling you to specify a guide space for *all* markers and selectively override only the ones you're interested in. Just like how the `Input Space` works.

#### Auto Delete

The `Delete All Physics` menu command does what it says on the tin; it deletes all Ragdoll nodes from your Maya scene. But deleting a node, such as the new `rSolver` left behind anything associated with it, like `rGroup` and any `rMarker` nodes.

This releases addresses this by automatically removing anything that depends on the node you delete. For example..

- Deleting a `rMarker` node also deletes any associated lollipop controls
- Deleting a `rGroup` also deletes the associated `rMarker` nodes
- Deleting the `rSolver` deleles all `rGroup` and `rMarker` nodes

Therefore, deleting a solver is now equivalent to `Delete All Physics`, making it much more intuitive to delete things on a whim.

<br>

#### Reset Button

Minor cosmetic improvement, the `Reset to Default` button now has an icon so you can actually *tell* it's a reset button (and not a bug, as many have pointed out 😅).

https://user-images.githubusercontent.com/2152766/134865922-07b55df5-1a88-4d5c-850c-bcc6976ee1d9.mp4 controls

<br>

#### Z-up

The default plane and solver offset was a off in the previous release, this fixes that. You can also manually re-adjust the plane and remove and orientation from the solver node to fix it locally, the solver itself is A-OK.

https://user-images.githubusercontent.com/2152766/135707451-00b49389-47b6-4d4e-8798-2dbe34532c2f.mp4

<br>

#### Auto Time

Start simulating at the Maya start time, wherever it may be.



<br>

### Limitations

Because monitoring for and responding to changes is a hard problem to solve, odds are some things aren't updating the way you expect. If you encounter any such issues, let us know in [the chat](https://ragdolldynamics.com/chat) or ping me directly at marcus@ragdolldynamics.com.

**Known Issues**

| Limitation | Description
|:-----------|:----------
| Constraint frames and translation | Frames are automatically computed based on the position and pivots of a control. Changing the pivot will update the constraint, but changing the position currently does not do a good job updating the constraint at both ends of the connection. Work around this by editing the position or pivot of any children and undo afterwards, to trigger a refresh. Alternatively re-open the scene to refresh everything.

<br>

### Resources

Some well-hidden but essential resources for any of the above.

- [Parallel Evaluation](https://download.autodesk.com/us/company/files/UsingParallelMaya/2020/UsingParallelMaya.html)
- [VP2 API Porting Guide for Locators](images.autodesk.com/adsk/files/VP2_API_Porting_Guide_for_Locators.pdf)
- [VP2 API Porting Guide Part 1](images.autodesk.com/adsk/files/VP2_API_Porting_Guide0.pdf)
- [VP2 API Porting Guide Part 2](images.autodesk.com/adsk/files/VP2_API_Porting_Guide_Details0.pdf)
