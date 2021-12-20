---
title: Manikin II
description: Full Ragdoll
icon: "ragdoll_black.png"
order: 41
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/145709105-2cb36544-74fb-4e80-910d-a29f4869b4e8.png">
    <source src="https://user-images.githubusercontent.com/2152766/145709104-c8859a6b-dff3-4478-ba19-308568f60158.mp4" type="video/mp4">
</video>

### Manikin Ragdoll

In the [previous tutorial](/tutorials/manikin) we assigned markers onto a rig such that you can achieve overlapping motion.

That's enough for some things, but other times you don't want *any* animation. You just want to drop a ragdoll someplace dangerous and watch it go.

!!! success "Version 1.1 - Up to date"
    Written for Ragdoll `2021.12.10` and above.

**Estimated Time**

- 🕐 10 minutes

**You will learn**

- ✔️ How to prevent unrealistic poses
- ✔️ How to author and tune "limits"

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

<br>

### Bring Your Own Rig

Either continue from the [last tutorial](/tutorials/manikin) or start anew with your own rig.

https://user-images.githubusercontent.com/2152766/129519170-59d6a109-e9eb-4fd0-87ef-f120050c9d7e.mp4 controls

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/Q96vbUR5/manikin.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/J2SLBN2T/manikin_ragdoll_final.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

#### Limits

Next see how our character behaves when there isn't any animation around to steer it.

1. Select `hip_ctl_rGroup`
2. Set `Behavior = Initial State`

As in our last tutorial when we changed the `hip_ctl` from `Kinematic` to `Initial State`, now we do the same but for the whole character!

https://user-images.githubusercontent.com/2152766/145388195-22886314-833f-4785-9b80-1d90b35d54e7.mp4 controls


*Yikes!* That's a mess. No longer is the animation holding a pose together, it's all up to gravity and the anatomy of our character now.

The way we will address this is via "limits", which is like locked rotate channels except they also lock a *range* of values. We can use this to replicate natural limits in our human joints.

<br>

#### Legs

Let's start at legs and work our way up. First, let's figure out what axis we want to rotate, and which we want to *lock*.

https://user-images.githubusercontent.com/2152766/145369873-2c71510c-9baa-4f42-8bbe-d136b68875b3.mp4 controls

Ok, great. The Z axis should rotate but X and Y should be locked.

1. Run `Ragdoll -> Manipulator`
1. Select the lower leg
1. Switch to `Limit Mode`
1. Enable limits around `X`, `Y` and `Z`
1. Lock `X` and `Y`

https://user-images.githubusercontent.com/2152766/145389323-4f24bb98-c4cd-429b-be6f-8e859a6face8.mp4 controls

Next, tune the minimum and maximum values of the limit.

!!! hint "Tune Minimum and Maximum Separately"
    By holding the **Ctrl** key, you can manipulate one bound at a time.

https://user-images.githubusercontent.com/2152766/145389328-aa51fd69-a325-44a9-8dc5-8c214d0c0b2e.mp4 controls

Then we can do the same for the feet.

https://user-images.githubusercontent.com/2152766/145389334-c287dfd5-dc90-4e26-9e09-c7bdd0fc912d.mp4 controls

Something like that should do the trick.

<br>

#### Clavicles

Let's keep the clavicles simple. We'll allow only 1 axis of rotation by locking the others.

1. Run `Ragdoll -> Manipulator`
3. Edit the clavicle

https://user-images.githubusercontent.com/2152766/145388216-00037e3b-a9d8-43b5-afae-2469c9b678e4.mp4 controls


<br>

#### Arms

We'll lock the `X` and `Y` axes of the lower arm like we did for the lower leg.

1. Run `Ragdoll -> Manipulator`
3. Edit the lower arm
4. Edit the hand

https://user-images.githubusercontent.com/2152766/145388218-cc4eed3f-717a-4da3-8c5f-863feea53656.mp4 controls

<br>

#### Hip and Spine

Both the hip and spine should be allowed to rotate around all three axes, so we can leave these at their default values for now.

1. Run `Ragdoll -> Manipulator`
3. Edit the hip and spine

https://user-images.githubusercontent.com/2152766/145388208-d4229b41-8b0b-4143-8a06-02ce220d2da3.mp4 controls

And that's it! From here, we can hide the limits to have another look at contacts.

<br>

### Contacts

If we hide away our limits for a moment, we can see something that's not right. Notice how the arm intersects the leg? That's because, per default, the limbs within a single group are allowed to overlap.

https://user-images.githubusercontent.com/2152766/145388222-3e137858-9a8f-4f25-885b-04083bd09f8f.mp4 controls

??? hint "Should I enable Self Collision?"
    Normally the answer is "no", but when you do this can be overridden on the `rGroup` node.

    ![image](https://user-images.githubusercontent.com/2152766/145392157-cce05e62-9cd2-45d2-9bad-100816d5c051.png)

<br>

#### Overlap Group

Let's address this by having these overlap with `Nothing`.

https://user-images.githubusercontent.com/2152766/145388226-465c1f32-e4e2-40c9-9615-5209e88e5a9b.mp4 controls

<br>

### Finalise

You now know enough to construct *any* character of *any* anatomy!

**You have learnt**

- ✔️ How to *limit* the motion between two limbs
- ✔️ How to tune the minimum and maximum bound of each limit

As you tune, try dropping the Manikin from different heights and angles. Put an obstacle underneath for more detail and to catch more edge cases. Once you are unable to produce an unnatural pose, you are done!

https://user-images.githubusercontent.com/2152766/145396017-3175104f-f488-45c9-9a60-2ca326afb2e7.mp4 controls

**Download Completed Scene**

For your reference, here is the completed scene with the Manikin file referenced.

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/Q96vbUR5/manikin.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/J2SLBN2T/manikin_ragdoll_final.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

#### Damped Limits

You can tune the behavior of each limit to capture the look you're after, such as making things a little more **damped**.

https://user-images.githubusercontent.com/2152766/145394548-4c74d571-d6fc-4266-93b6-4d5058a3247e.mp4 controls

!!! hint "Global Damping"
    This, and other stiffness and damping-related attributes, can be controlled globally - for every limit in your scene - via the `rSolver` node.

    ![image](https://user-images.githubusercontent.com/2152766/145394621-c4b9e7a7-c9dc-4c3c-b265-fe46386a82ca.png)

#### Soft Limits

Sometimes, a limit is **hard**. Like your elbow. It won't allow you to continue rotating it once it's straighted out. You'll break it!

Other limits are more flexible. Let's reflect this in our simulation by reducing their range and lowering their `Stiffness`, accepting that they *will* exceed it, but get gently pushed back.

https://user-images.githubusercontent.com/2152766/145399669-b9bd968e-85d7-4bc0-8eb3-8b166caa648e.mp4 controls

<br>

#### Accurate Feet

Feet contact with the ground is often more important than other contacts. For such cases, a box or capsule shape may not be enough.

So let's use `Replace Mesh` to fix that.

1. Select `L_foot_jnt`
2. Select a mesh
3. Run `Replace Mesh`

https://user-images.githubusercontent.com/2152766/145395099-94ec0f4e-ecb6-4a65-8f7c-2087ac948ad9.mp4 controls

<br>

#### Animation

In most cases, you'll want *some* control over the resulting simulation. Just a little bit.

https://user-images.githubusercontent.com/2152766/145401847-e65cb830-d012-49eb-9953-82c4f04b503f.mp4 controls
