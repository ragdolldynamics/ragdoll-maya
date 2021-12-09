---
title: Snap to Simulation
icon: "snap_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

### Snap to Simulation

Yet another way to work with physics, by transferring individual poses from the solver into your animation. You can use it to pose or layout a scene.

https://user-images.githubusercontent.com/2152766/141302109-6818b04d-9b57-4378-bdea-e62b98220f16.mp4 controls


https://user-images.githubusercontent.com/2152766/141302185-df7ee9d0-567e-4a52-a9d3-46fcfee33eeb.mp4 controls


https://user-images.githubusercontent.com/2152766/141302197-4c895c4a-8e34-486e-8835-a91ffa50ff99.mp4 controls

!!! note "Coming Up"
    An upcoming release will enable you to advance time in the simulation, without affecting time in Maya. Such that you can "relax" a pose, for example. 😁

<br>

#### A Debugging Companion

It can also be used for situations where `Record Simulation` doesn't do what you need it to. The extracted skeleton will be a plain joint hierarchy, with no scale, and guaranteed to match the simulation exactly. So you can extract it, and constrain your rig to it.
