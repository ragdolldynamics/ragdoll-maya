---
title: Record Simulation
icon: "record_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

### Overview

Markers can be recorded all together, or independently. For example, say you wanted animation from frame 1-100, simulate 101-150 and return to animation from 151-200. You can do that.

Furthermore, say you liked what the simulation was doing, but only on one half of the body. Or only on the hip, driving the main trajectory in a physically-plausible way. Keeping the rest of your animation intact.

**Record All**

With nothing selected, Ragdoll will record all marked controls to the current Maya playback range.

https://user-images.githubusercontent.com/2152766/134327104-f3d54cda-4d88-480a-b263-faceb211e87a.mp4 controls

**Record Selected Markers**

Select a few controls to control what gets recorded.

https://user-images.githubusercontent.com/2152766/134327103-5ad36b6b-177d-40a9-8666-cbaaab281527.mp4 controls

**Record Range**

Limit the Maya playback range for control over *when* recording takes place.

https://user-images.githubusercontent.com/2152766/134327097-db0af345-bf15-45f5-9bc0-6ef50d3184f4.mp4 controls

**Record Selected Range**

Or, select an explicit range interactively.

https://user-images.githubusercontent.com/2152766/134327093-ba62588e-d14f-4ff9-9b75-05d4230dbdb6.mp4 controls

**Record to Animation Layer**

Ragdoll will record to a layer per default.

https://user-images.githubusercontent.com/2152766/134775996-ea2ce5d1-8638-4d43-94f7-f7635585f532.mp4 controls

<br>

### Transitions

Let's have a look at how you would use markers to transition between simulation and animation.

https://user-images.githubusercontent.com/2152766/134507548-382a0ccd-85b6-4990-b325-16dbd3b7d568.mp4 controls

Notice how we're animated up until the jump, and then Ragdoll takes over. Once he approaches that box, we turn our `Guide Space` from `-1` to `1` and have him reach the target pose in worldspace. Once he's close, we switch `Input Type` to `Kinematic` and kinematically move him until we once again transition to `Guide`, this time with a `Guide Space` or `-1` for pose space.

https://user-images.githubusercontent.com/2152766/134507546-49e84d32-b50a-48c6-a1b9-82410281a884.mp4 controls

<br>

#### Record to Custom Attributes

Sometimes, rotation isn't coming from `Rotate X` but rather a custom `Ball Roll` attribute on a different IK control.

https://user-images.githubusercontent.com/2152766/136360430-d59f0e7c-f268-4053-ad8f-9b915c1f42f5.mp4 controls

As Ragdoll only understands `Translate` and `Rotate`, how would you go about recording onto this attribute!? Here's what you can do.

1. Create a new Locator
2. Retarget the foot to this Locator
3. Connect `Locator.rotateX -> R_foot_CTL.ballRoll`

Now Ragdoll will record onto a familiar channel, and *Maya* will handle the conversion back onto the rig.

<br>

### Extract Simulation

Get data out of the solver and into a baked joint hierarchy.

You can use this to build a library of animations, or to handle the retargeting from simulation to animation manually by just constraining to the resulting joint hierarchy.

https://user-images.githubusercontent.com/2152766/139657721-576c5b8f-e852-4e96-a9ed-dad4933920ff.mp4 controls

!!! note "Performance"
    Notice how fast this is!
