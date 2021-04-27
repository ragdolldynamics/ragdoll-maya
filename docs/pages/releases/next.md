---
title: Solver Upgrade
description: A minor upgrade to the underlying solver, with new default values.
---

This release changes the default values for any `Stiffness` and `Damping` parameters in the pursuit of stability and robustness.

- [**ADDED** Solver Upgrade](#solver-upgrade) More realistic guides, at the expense of new default values
- [**ADDED** Clear Initial State](#clear-initial-state) Return to a better time
- [**FIXED** Start Frame Explosion](#start-frame-explosion) Fixed a rare case overly eager passive rigids
- [**FIXED** Negative Scale 2.0](#negative-scale) Greater support for negative scale
- [**FIXED** Rotate Order 3.0](#rotate-order-3-0) Greater support for custom Rotate Order.
- [**FIXED** Draw Shaded](#draw-shaded) Rigids can now once again be wireframed, for less clutter whilst animating

<br>

## Solver Upgrade

The solver has been upgraded for more accuracy and stability. Unfortunately, this changes the default values `Stiffness` and `Damping` attributes, which may require changes in your scene.

!!! warning "ATTENTION: Backwards Incompatibility"
    Ragdoll takes backwards compatibility *very* seriously. At no point should a scene you have created *break* because of an update. This however is an exception to that rule, one that I expect never to happen again.

![image](https://user-images.githubusercontent.com/2152766/116086840-29b68780-a698-11eb-87a1-f0dfef282c5b.png)

### What has changed?

`Stiffness` and `Damping` need higher values.

So far, we've used the `Iterations` value on the solver to control how strong our constraints could be. As it happens, this isn't right. Iterations shouldn't control strength, it should only control how close the solution is to the true analytical solution.

- In the previous release, increasing this value produced an entirely different result based on how many iterations you used. At no point would it "converge" onto a true solution.
- In this and future releases, only stiffness and damping will affect the behavior of physics, with `Iterations` optionally bringing it closer to the *true* solution.

In practice, not much has changed. You should still increase stiffness/damping when relevant, and still increase `Iterations` if you find the values aren't being respected.

### What can I do?

- 👉 Increase `Stiffness` by 3-10x
- 👉 Increase `Damping` by 3-10x

That is, if `Stiffness` was previously 1'000, make it 10'000.

**Exceptions**

- For anything created with this version, no action is needed.
- `Projected Gauss-Seidel` (Advanced) remains unchanged.

It's not an exact science, in some cases you only need 3x, like in this case here.

![times3](https://user-images.githubusercontent.com/2152766/116083379-74360500-a694-11eb-94ff-efd94f8a5ca8.gif)

Where the `Yellow` line is from the previous version at 1'000 stiffness and 100 damping, the `Blue` line has 3'000 stiffnes and 300 damping.

### Why did this change?

The previous version was subtly faulty, so this was inevitable. In practice however, under a very particular - but useful - circumstance the solver would struggle to obey.

**Circumstance**

1. An `Active Rigid`
2. Constrained to a `Passive Rigid`
3. Limits turned off
4. *Translate* Guide turned `On`

**Use Cases**

- Dynamic muscles attached to an animated skeleton
- Dynamic props attached to an animated character
- Dynamic cloth attached to a passive collider
- Basically anything that isn't a fully-dynamic character

Here was the result.

![tgsbefore](https://user-images.githubusercontent.com/47274066/115770569-c92bff80-a3a4-11eb-83cb-9908eecfc861.gif)

Notice how the active rigid does what the active rigid does, but is a little *too* excited? One workaround was to use "Projected Gauss-Seidel" in place of the default "Temporal Gauss-Seidel", however that solver isn't as accurate or fast.

You might be thinking..

> Well that's an awefully specific case, when would I even hit that?

Which is when you realise..

![fixed](https://user-images.githubusercontent.com/2152766/116090739-17d6e380-a69c-11eb-8e9b-5b0d7da48b1d.gif)

This was previously only possible with Projected Gauss-Seidel which is less performant and less able to handle large networks of constraints like a full ragdoll.

**Result**

This behavior was due to a subtle bug in how constraints were solved, a deeply rooted bug that once sorted out was what caused this change to the overall behavior of `Stiffness` and `Damping` values.

In this release, the bug has been squashed and muscles and props now follow their passive counterpart much more accurately and without surprises.

![tgsafter](https://user-images.githubusercontent.com/47274066/115770566-c8936900-a3a4-11eb-8998-4a55d1fcf35b.gif)

<br>

## Clear Initial State

Setting the initial state can be used to *relax* a physics character or scene.

![clearinitialstate1](https://user-images.githubusercontent.com/2152766/116095203-1c9d9680-a6a0-11eb-83c8-f86e1ee3367b.gif)

But once relaxed, you had no way to returning to its original creation state, until now!

![clearinitialstate2](https://user-images.githubusercontent.com/2152766/116095219-20c9b400-a6a0-11eb-93b6-25f14f0115f0.gif)

- The set and cleared state are both saved with the scene
- This can rescue the initial state from breaking due to [Automatic Initial State](https://learn.ragdolldynamics.com/releases/2021.03.01/)

<img width=400 src=https://user-images.githubusercontent.com/2152766/116057775-0af3c900-a677-11eb-92fe-6d9b9f288009.png>

> Thanks to Jason Snyman for this suggestion!

<br>

## Start Frame Explosion

In a specific and rare circumstance, a passive rigid body could appear to have velocity on the start frame.

![startframebug1](https://user-images.githubusercontent.com/2152766/116077549-86607500-a68d-11eb-8320-d0edcaffe535.gif)

Notice here how animation starts immediately from the start frame, giving it an upwards velocity? The active rigids connected to the root on the other hand gets an even stronger velocity, for some reason.

If we move the animation to just one frame *after* the start frame, all is well.

![startframebug2](https://user-images.githubusercontent.com/2152766/116077543-85c7de80-a68d-11eb-8625-d692f0221f5a.gif)

A subtle bug, having to do with the rigid body being created on the second frame of the simulation, which in this case had a position the was different from the start frame. However! The *animation* started at the start frame, so the velocity got inherited from there instead. Yes, it's complicated. :)

And is now fixed!

<br>

## Negative Scale

Ragdoll has supported scale, but *negative* scale has been unreliable. This release extends this support to negative scale used to mirror controls and behavior across a rig.

**Before**

This whole arm has a negative scale in the X-axis, from when it was mirrored across from the other side. Notice here how it look like the arm is about to move forwards, and instead move backwards.

![negativescale_before](https://user-images.githubusercontent.com/2152766/115990764-e89d7500-a5bc-11eb-9b7b-33105ec88d9b.gif)

**After**

This has now been fixed.

![negativescale_after](https://user-images.githubusercontent.com/2152766/115990763-e76c4800-a5bc-11eb-9ff0-442924412ec3.gif)

It also means you can flip entire performances with a little more ease. :)

![negativescale](https://user-images.githubusercontent.com/2152766/116044447-d4af4d00-a668-11eb-8e8c-54b0cf5570bd.gif)

### Caveat

Avoid negative scale on the control you are animating.

- ✔️ Global negative scale
- ❌ Local negative scale

![image](https://user-images.githubusercontent.com/2152766/115992698-ee985380-a5c6-11eb-81d3-775e89f0e649.png)

You are still better off not having any negative scales in your rig, as there is still at least one special case I found that might jump up and bite you.

And that is if the animated control *itself* has negative local scale.

Typically, one or more of the parents have negative scale, so as to mirror a whole hierarchy of controls. And that is ✔️. But if the control you are animating *also* have negative scale, you might experience this.

![badnegativescale](https://user-images.githubusercontent.com/2152766/115992653-ac6f1200-a5c6-11eb-971a-ef8f6c97cbef.gif)

Notice how on rewind, it twitches at the start of playback every other time? That's because it cannot tell the whether the control has negative scale or whether it is rotated 180 degrees.

This will be addressed in a future release.

<br>

## Rotate Order

The animation constraint is what translates your keyframes into physics and with the introduction of support for Rotate Order in the previous few releases it has been possible for Ragdoll to *output* rotations onto any control with a custom rotate order.

This release now includes support for *input* of custom rotate order into the simulation.

**Before**

Notice how changing the rotate order should have changed the axis around which the Y-animation was happening, but didn't?

![rotateorderdrive1](https://user-images.githubusercontent.com/2152766/115991000-277ffa80-a5be-11eb-9b30-08c2a45f404c.gif)

**After**

Now it does!

![rotateorderdrive2](https://user-images.githubusercontent.com/2152766/115991004-2e0e7200-a5be-11eb-9e4f-2cb432441163.gif)

<br>

## Draw Shaded

The previous release revamped the rendering system in Ragdoll, but left out a the convenience attribute to disable shading when rigid bodies were used alongside animation controls.

| Before | After
|:-----|:---
|  ![image](https://user-images.githubusercontent.com/2152766/115991123-f48a3680-a5be-11eb-9dde-336619236acf.png) | ![image](https://user-images.githubusercontent.com/2152766/115991119-f05e1900-a5be-11eb-9dab-42aebbdeab6c.png)

!!! hint "Manual Override"
    The behavior can be manually adjusted to taste via the Attribute Editor.

    ![shadedonoff](https://user-images.githubusercontent.com/2152766/115991152-23a0a800-a5bf-11eb-8eea-166ea03f09c3.gif)
