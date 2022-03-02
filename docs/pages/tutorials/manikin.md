---
title: Manikin I
description: Make your own motion reference
icon: "ragdoll_black.png"
order: 40
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/145709207-470d897f-b025-498d-8ebf-c9217ca6a047.png">
    <source src="https://user-images.githubusercontent.com/2152766/145709200-b65f5328-832d-4f15-a2d2-166bc766b452.mp4" type="video/mp4">
</video>

### Manikin

> "Make your own motion reference"

In this tutorial, we will setup a human-like character for use as reference or constraint target to your rig. You will be able to pose and position this Manikin like you would a real Manikin, and drop it from various heights and onto various obstacles to produce realistic poses as it falls.

Something the animator can import and throw around for *reference* on how it would look like.

!!! success "Version 1.1 - Up to date"
    Written for Ragdoll `2021.12.10` and above.

**Estimated Time**

- 🕐 10 minutes

**You will learn**

- ✔️ How to apply markers onto rig controls
- ✔️ How to tune the collision shapes of the markers
- ✔️ How to record your simulation back onto the rig controls

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

??? question "Spelling"
    There are two ways to spell "Manikin", this tutorial is based on this term here.

    - https://www.healthysimulation.com/Manikin/

<br>

### Bring Your Own Rig

Follow this tutorial either using our provided Manikin rig, or your own character. It can have any number of limbs.

https://user-images.githubusercontent.com/2152766/129519170-59d6a109-e9eb-4fd0-87ef-f120050c9d7e.mp4 controls

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/Q96vbUR5/manikin.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/7PBY38gw/manikin1_final.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

### Motivation

> Why should we even bother simulating a character?

Finding *motion reference* is one of the most important activities for any animator. And yet I can safely challenge you to find reference for perhaps the most common motion in all blockbuster movies today, something that is either *impossible* or **dangerous** for actors or animators alike.

https://user-images.githubusercontent.com/2152766/129709932-643b186b-af06-41d0-ab67-38e9a4cc679c.mp4 controls

Or how about reference of someone simply falling over, perhaps from heat stroke or staring into the sun.

https://user-images.githubusercontent.com/2152766/129698550-61c15074-a134-4339-a4da-e469da7d4aeb.mp4 controls

This is, after all, one of the major reasons for pursuing computer graphics in storytelling rather than real people.

Animators bring *life* to characters, but of equal challenge is that of *lifelessness*. Of natural and realistic motion without someone behind the wheel. Be it getting <u>hit</u> or *shot*, blasted or **thrown**, animating lifelessnes is a enough to challenge even the most senior of animators.

As you will find, there is a lot more we can do once our motion reference is in 3D, on our actual character rig witin Maya and infinitely *customisable*. As opposed to some video on the internet.

<br>

### Setup

Create a new reference of your chosen character rig or download this Manikin rig to get started.

https://user-images.githubusercontent.com/2152766/129542838-94f80604-326d-4625-aac6-559092a4338d.mp4 controls

Play around with the controls to get a feel for what we're working with. This character is entirely FK which will make simulating it straightforward.

https://user-images.githubusercontent.com/2152766/129543646-4880f774-85cc-418b-aa24-e19f169d9538.mp4 controls

<br>

### Dynamics

The stage is set, now let's apply physics.

<br>

#### Torso

Let's start with the Torso.

1. Select `hip_ctl`
1. Shift select `torso_ctl`
1. Shift select `head_ctl`
1. Run `Assign and Connect`

This will produce our first `Group`, which is a collection of connected `Markers`.

!!! hint "New Concept"
    **Group**

    The `rdGroup` node contains attributes that affect all contained markers. It's where you'd edit the overall look and feel of your character, like how stiff it should be and whether or not body parts should collide with each other.

    Each Marker can either **inherit** or otherwise override these values.

https://user-images.githubusercontent.com/2152766/145268730-9c58b545-63f8-4de7-8dd6-4a3e8e4a70a1.mp4 controls

<br>

#### Left Arm

Next we will continue from the `torso_ctl` and out into the arms.

1. Select the `torso_ctl`
1. Shift select `L_clavicle_ctl`
1. Shift select `L_upperArm_ctl`
1. Shift select `L_lowerArm_ctl`
1. Shift select `L_hand_ctl`
1. Run `Assign and Connect`

??? question "Is the order important?"
    Yes, the order in which you *select* will determine how the markers are **connected**.

    Your first selection is extra important, as it determines whether to start a *new* group, like for the `hip_ctl`, or to *add to* an existing group, like the `torso_ctl`.

    In this case, we would very much like our arm to be connected to the torso.

??? question "Can I skip the clavicles?"
    Yes, if you have extra controls - such as `twist` or `bend` - you can skip these if you don't care to simulate them.

    Simply skip over them as you select, from `torso_ctl` directly to `L_upperarm_ctl`.

https://user-images.githubusercontent.com/2152766/145269586-121c8a06-5021-4f77-99a6-8373e23f6af4.mp4 controls

<br>

#### Right Arm

Now repeat the above process for the other arm.

https://user-images.githubusercontent.com/2152766/145269591-d4494551-00fc-4697-84d8-b378f4db22c1.mp4 controls

<br>

#### Legs

Now let's continue down the hips and into the legs.

1. Select the `hip_ctl`
2. Shift select `L_thigh_ctl`
2. Shift select `L_knee_ctl`
2. Shift select `L_foot_ctl`
3. Run `Assign and Connect`

We will address those *long* feet shortly. 👃

https://user-images.githubusercontent.com/2152766/145269594-29ca3623-b5bf-4cb9-ba4e-13fc5cb88fef.mp4 controls

<br>

#### Drop Test

That's enough setup, let's drop him!

1. Select `hip_ctl`
2. Set `Behaviour = Dynamic`
3. Drop the Manikin a few times

!!! hint "New Concept"
    **Behaviour**

    Each Marker has a "behaviour", which tells Ragdoll it should interpret the control it has been assigned. Should it fall with gravity? Should it try and match the pose? Should it remain fully animated, even in simulation?

https://user-images.githubusercontent.com/2152766/145350753-c9a74397-6e5c-41ed-b06b-03e596860952.mp4 controls

The default behaviour for `Assign and Connect` is to give the first selection - the "root" - a `Kinematic` behaviour.

!!! question "What does Kinematic mean?"
    **Kinematic** means "copy the animation into simulation and make no changes to it"

    By instead setting this to `Dynamic`, then Ragdoll will only use the animation for the starting position and orientation of the simulation.

!!! tip "Inherit"
    Alternatively, you can set it to `Inherit` to have it *inherit* the value of the `rGroup` node that was created for the whole character.

<br>

### Tuning

Next let's address the elephant in the room; the shapes. They look aweful.

https://user-images.githubusercontent.com/2152766/145351245-e409ff65-9c6e-4f43-896d-21d341179363.mp4

<br>

#### Volumes

The shape of each collider affects your simulation in 2 ways.

- **Contact Points**
- **Rotation Mass**

The contact point can be important if your character interacts with an environment or another character. Like in this case where the feet are incorrectly colliding with the ground because of a bad shape.

https://user-images.githubusercontent.com/2152766/145351664-8d20a42e-f2d1-434f-8154-dd0729a008fa.mp4 controls

That's not always the case though, sometimes you just want overlapping motion without contacts in which case the shapes won't matter.

They do however also affect their resistance to rotation. Consider this.

https://user-images.githubusercontent.com/2152766/145358819-b3131cc7-bea3-461c-9ce7-37ce2c18f9ef.mp4 controls

> Here, we rotate the exact same shapes, the exact same amount in the exact same amount of time. And yet they respond differently.

This shape has vastly different dimensions in the X, Y and Z directions, resulting in a different rotation mass for each one. As a result, the effort required to rotate it in each axis differs too.

In practice, you'll find this for just about any limb on a character, which is typically longer in one axis. For our Manikin, this is especially true for the default clavicle shapes.

!!! hint "Override Rotate Mass"
    In some cases, you have a shape but want it to act like a different shape. `Rotate Mass` is very similar to normal `Mass`, except in 3 dimensions. Where the position of an object is affected equal in X, Y and Z directions, rotations have 3 separate masses.

<br>

#### Shapes

With this in mind, let's tune some shapes.

1. Run `Manipulator` from the `Ragdoll` menu

!!! note "Alternatively"
    Select a `rMarker` node in the Channel Box, or the `rGroup` node in your Outliner, and hit the `T` key on your keyboard. You can also select the *shape* of the `rSolver` node.

This brings up the [**Manipulator**](/documentation/manipulator) interface, where you can manipulate shapes using mouse gestures.

https://user-images.githubusercontent.com/2152766/145367273-6a2ffdba-08e7-41d0-88d6-684033030a83.mp4 controls

Great, now let's turn those hands and feet into boxes.

https://user-images.githubusercontent.com/2152766/145367278-ef9726c3-976c-45b6-b586-8bbc550ab76b.mp4 controls

!!! tip "Translate, Rotate and Scale"
    Notice I'm using the..

    - **Middle-Mouse Button** to `Translate`
    - **CTRL + Middle-Mouse Button** to `Rotate`
    - **CTRL + Left-Mouse Button** to `Scale`

    The help text screen-right will help you remember these.

!!! tip "Symmetry"
    Also notice the edits are symmetrical; even when they don't start out that way like the feet!

<br>

### Recording

That's all there is for setting up your character rig for simulation! Let's now transfer the simulation back onto the rig.

1. Run `Record Simulation`
2. Enjoy

https://user-images.githubusercontent.com/2152766/145383840-3759f76b-5e21-44d7-959d-27c202069f16.mp4 controls

<br>

#### Start Again

The recorded simulation ends up on an **Animation Layer**, and is also **Cached**. To start over, delete this layer and disable the cache.

https://user-images.githubusercontent.com/2152766/145383834-69a72a25-0e85-442a-bc65-acc31bfbf197.mp4 controls

<br>

### Next Steps

In the next tutorial, we'll take this a bit further. As you play around with the `Pose Stiffness` on either the `rGroup` or individual `rMarker` nodes, you'll find some limbs start to misbehave. Especially the knees and elbows, that normally won't allow rotations past a certain angle in a real human (or Manikin for that matter!). That isn't the case here, because we've left out a critical part of any complete ragdoll.

- [Full Ragdoll](/tutorials/manikin_ragdoll)

See you there!
