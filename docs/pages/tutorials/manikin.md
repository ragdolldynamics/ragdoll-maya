---
title: Manikin
description: Make your own motion reference
icon: "ragdoll_black.png"
order: 40
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/130401314-a78576ca-cc51-4976-8b37-d5482d74fc38.jpg">
    <source src="https://user-images.githubusercontent.com/2152766/129716006-ca769612-8a14-4fff-9305-683fe00f26f4.mp4" type="video/mp4">
</video>

### Manikin

> "Make your own motion reference"

In this tutorial, we will setup a human-like character for use as reference or constraint target to your rig. You will be able to pose and position this Manikin like you would a real Manikin, and drop it from various heights and onto various obstacles to produce realistic poses as it falls.

Something the animator can import and throw around for *reference* on how it would look like.

!!! success "Version 1.0 - Up to date"
    Written for Ragdoll `2021.08.06` and above, but should still apply for `2021.06` and newer.

**Estimated Time**

- 🕐 30 minutes

**You will learn**

- ✔️ How to limit limbs to realistic angles
- ✔️ How to pose a dynamic character
- ✔️ How to apply forces to a specific rigid

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

??? question "Spelling"
    There's two ways to spell "Manikin", this tutorial is based on this term here.

    - https://www.healthysimulation.com/Manikin/

<br>

### Bring Your Own Rig

Follow this tutorial either using our provided Manikin rig, or your own character. It can have any number of limbs.

https://user-images.githubusercontent.com/2152766/129519170-59d6a109-e9eb-4fd0-87ef-f120050c9d7e.mp4 controls

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/8CKfRSk3/manikin_rigging_v001_publish.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/01lBKSdb/manikin_walkthrough_v003.zip" class="button red"><b>Download Final Scene</b></a>
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

??? question "What about IK?"
    We can achieve IK through physics, using the Soft Pin and Hard Pin controls.

https://user-images.githubusercontent.com/2152766/129543646-4880f774-85cc-418b-aa24-e19f169d9538.mp4 controls

<br>

### Dynamics

The stage is set, now let's apply physics.

<br>

#### Torso

If you experimented with the pose earlier, reset all controls to 0 before proceeding.

??? question "Do I have to?"
    No, only for the sake of this tutorial.

    Ragdoll will use the starting pose as a template for how to generate rigid bodies and constraints. The character can be in any pose, it can even be *animated* before applying any physics.

1. Select `hip_ctl`
1. Shift select `torso_ctl`
1. Shift select `head_ctl`
1. Run `Active Chain`

This will produce our first `Active Chain`, which is a set of `Active Rigid` with a `Socket Constraint` in between them.

https://user-images.githubusercontent.com/2152766/129546001-92bc9c50-e847-47ba-9bbc-f71486ebefa5.mp4 controls

<br>

#### Left Arm

Next we will continue from the `torso_ctl` and out into the arms.

1. Select the `torso_ctl`
1. Shift select `L_clavicle_ctl`
1. Shift select `L_upperArm_ctl`
1. Shift select `L_lowerArm_ctl`
1. Shift select `L_hand_ctl`
1. Run `Active Chain`

??? question "Is the order important?"
    Yes, the order in which you *select* will determine how the rigids are **connected**.

    Your first selection is extra important, as it determines whether to start a *new* chain, like for the `hip_ctl`, or to *continue* from an existing chain, like the `torso_ctl`.

    In this case, we would very much like our arm to be connected to the torso.

??? question "Can I skip the clavicles?"
    Yes, if you have extra controls - such as `twist` or `bend` -  you do *not* have to include these. So long as there is a natural parent/child relationship between your controls, Ragdoll should behave just fine.

    Simply skip over them as you select, from `torso_ctl` directly to `L_upperarm_ctl`.

    In this tutorial however, we will use the clavicles to demonstrate a physical aspect of the Manikin which allows the arm to rotate in a very specific way.

https://user-images.githubusercontent.com/2152766/129546874-379a8fac-06bb-4c8b-90f0-10d195366e45.mp4 controls

<br>

#### Right Arm

Now repeat the above process for the other arm.

https://user-images.githubusercontent.com/2152766/129548392-2e989f33-3b7a-4060-90f0-43a5a57938be.mp4 controls

Oh no! What happened! 😨

Turns out, the clavicles of this character are so close to each other that they intersect. Intersections can be ok, so long as there is nothing holding the intersection together, which in this case is our torso.

One way of solving this is to simply disable collisions between the two clavicles.

??? question "Why can the clavicles not intersect?"
    Intersections aren't always a problem. When two rigids intersect, Ragdoll will typically push them apart once, and leave them apart.

    https://user-images.githubusercontent.com/2152766/129675313-7455c570-410c-4cab-9e3d-1b5c47966c3c.mp4 controls
    
    The reason it isn't working for our clavicles is because the clavicles are intersecting whilst *also* being held together by the `torso_ctl`. Only one of these can be true, so we must either fix the intersection or remove the connection to the torso.

??? question "Is there an alternative?"
    Yes, you can also play with the `Shape Length` and `Shape Radius` parameters to avoid any overlap, or you can use an [Ignore Contarct Constraint](/documentation/constraints/#ignore-contact-constraint) to only disable contacts between these exact two rigids.

    Notice how the upper and lower arms intersect with each other. This is OK, because they are *neighbours*. Neighbours *should* intersect, that is a good thing and in many case *mandatory*.

https://user-images.githubusercontent.com/2152766/129548401-2e42056c-039e-4a51-a776-5022a07cfca1.mp4 controls

<br>

#### Legs

Now let's continue down the hips and into the legs.

1. Select the `hip_ctl`
2. Shift select `L_thigh_ctl`
2. Shift select `L_knee_ctl`
2. Shift select `L_foot_ctl`
3. Run `Active Chain`

https://user-images.githubusercontent.com/2152766/129550718-fa9b1a57-6c10-4285-8378-5380c61aa488.mp4 controls

Notice that we skipped the `hip_ctl` since we do not need it, and since the legs are far-enough apart there was no overlap between them. Great!

<br>

#### Drop Test

That's enough setup, let's drop him!

1. Select `hip_ctl`
2. Run `Active Rigid`

The default behaviour for `Active Chain` is to turn the first selection - the `Root` - into a `Passive Rigid`. That's how why he doesn't fall over as we run the simulation.

Calling `Active Rigid` on something that is already dynamic will *convert* a rigid from `Passive` to `Active`, which is exactly what we want.

https://user-images.githubusercontent.com/2152766/129551447-c9d313f4-dd58-483b-b7bc-61e8b1366add.mp4 controls

But he's too *stiff*. Let's reduce the `Global Strength` and turn him more into a classic "ragdoll".

https://user-images.githubusercontent.com/2152766/129551449-0a920ee8-6935-438e-9600-2580f474756a.mp4 controls

<br>

### Tuning

*Yikes!* What a mess. Let's see if we can turn spaghetti into an anatomically plausible character.

<br>

#### Volumes

A good first step is usually to ensure our collision shapes do a good job capturing the character. They represent not only how and where to collide against the environment, but also how they should behave; their center of gravity and angular mass.

The arms and legs are fine, let's address the torso.

1. Select `hip_ctl`
2. Edit `Shape Radius` and `Shape Length` to fit the model
3. Repeat for `torso_ctl` and `head_ctl`

https://user-images.githubusercontent.com/2152766/129554059-160831a2-a45b-477d-a46b-422093117123.mp4 controls

That's more like it.

**Before**

https://user-images.githubusercontent.com/2152766/129553800-80ab2b93-8323-4c72-bed8-99f6fd4aff41.mp4 controls

**After**

https://user-images.githubusercontent.com/2152766/129553808-8fc9210f-d0e3-4a3b-839c-c403a401c78f.mp4 controls

<br>

#### Clavicles

We're not out of the woods yet. Half-way through the fall, we can spot a few of the worst offending limbs.

1. **Clavicles** are dropping
1. **Feet** are bending too far
1. **Knees** are bending too far

![image](https://user-images.githubusercontent.com/2152766/129556921-d77f2b55-bfc1-41df-9786-f20b39dedf40.png)

Let's address the clavicles first.

![image](https://user-images.githubusercontent.com/2152766/129557225-05d846c9-4d8f-45e8-87fa-71aeeaca1193.png)

Here's what we want, the spherical little wooden thing can rotate, but only around one axis. The arm is then attached to this sphere, and is only able to rotate around one other axis.

1. Select `L_clavicle_ctl`
2. Set `Rotate Limit X = 60` under the `rPoseConstraint` node
2. Set `Rotate Limit Y = -1`
2. Set `Rotate Limit Z = -1`
3. Repeat this process for `R_clavicle_ctl`

https://user-images.githubusercontent.com/2152766/129563791-850f0553-e2c8-4d0c-96dc-ebbc72f8d026.mp4 controls

Now they stick to the sides of the torso, whilst still being able to spin around their length axis.

<br>

#### Feet Geometry

Next let's have a look at those feet.

https://user-images.githubusercontent.com/2152766/129564294-de954fed-1e0a-4819-a169-eee9ced473bf.mp4 controls

They intersect the ground, so let's address that first.

1. Select `L_foot_geoShape`
1. Shift select the `rRigid` shape of `L_foot_ctl`
1. Run `Replace Geometry`
1. Repeat this process for the other foot

??? question "Why is it so complicated"
    Yes, you are right.

    It's because the mesh is under the same parent as the rigid body, so we need to explicitly select the `mesh` geometry and `rdRigid` nodes in order to not confuse Ragdoll.

    Normally, you would select the mesh from the viewport instead.

https://user-images.githubusercontent.com/2152766/129566124-b4afe652-dfd6-464c-8770-2018c009ed72.mp4 controls

There we go, feet that perfectly align with the ground.

https://user-images.githubusercontent.com/2152766/129566683-918303b0-949b-4902-941b-eed5e5b8cbb6.mp4 controls

<br>

#### Feet Limits

The feet are still bending too far, let's address that.

1. Select both `L_foot_ctl` and `R_foot_ctl`
2. Set `Rotate Limit XYZ` to `35.0`

https://user-images.githubusercontent.com/2152766/129568274-2c4fc340-7c29-4e1e-a985-d6024c980e62.mp4 controls

But there's a problem. We want the `Limit Rotate X` axis aligned with our primary rotate axis.

??? question "What's special about X?"
    The X axis of a limit - also known as [Twist](http://localhost:8001/documentation/constraints/#twist-and-swing) - is ideal for limbs with only 1 moving axis, like this foot.

https://user-images.githubusercontent.com/2152766/129569239-a227045a-136c-429a-9aed-e987741bd9a4.mp4 controls

1. Select both `L_foot_ctl` and `R_foot_ctl`
2. Run `Edit Constraint Pivots`
3. Using the rotate manipulator in `Object` mode, rotate 90 degrees along `Z`
3. Rotate 90 degrees along `Y`

https://user-images.githubusercontent.com/2152766/129568280-da2393fa-4cc7-4e41-8ad2-4ccc9435e5fd.mp4 controls

**Everything allright?**

??? question "How do I reset my constraint?"
    Editing pivots can be tricky, and if you make a mistake you can **reset** a constraint like this.

    1. Remove any existing `parentFrame` and `childFrame` handles
    2. Select the `rPoseConstraint` node
    3. Run `Socket Constraint`

    By re-running a constraint command on an existing constraint, we reset its attributes and pivots to their default values so you can try again.

    <video autoplay controls class="poster" muted="muted" loop="loop" width=100%>
        <source src="https://user-images.githubusercontent.com/2152766/129570683-1ee98d1e-70f2-43f4-8041-66123bf2fb49.mp4 controls" type="video/mp4">
    </video>

??? question "How do I rotate it?"
    Make sure that when you rotate, you use the `Object` or `World` rotate gizmo and that you include both pivots called `parentFrame` and `childFrame`.

    https://user-images.githubusercontent.com/2152766/129571204-2c282bd1-7e2e-4d18-b8d3-e8de1145984e.mp4 controls

??? question "Something else happened"
    Sorry to hear that! Please let me know [in the chat](https://ragdolldynamics.com/chat) or [on the forums](https://forums.ragdolldynamics.com) and I'll try and fix this as soon as possible.

Finally, now we can, *lock* the Y and Z axes.

https://user-images.githubusercontent.com/2152766/129568275-4835196f-175a-4e7c-8421-b32bd41c83b2.mp4 controls

<br>

#### Lower Leg Pivots

Let's carry on with the knees.

The knees are special in that they should be able to bend in one direction but not the other, like a typical healthy human knee.

1. Select `L_knee_ctl` and `R_knee_ctl`
1. Set `Rotate Limit X = 40` to see the axis
1. Run `Edit Pivots` from the `Constraints` submenu
1. Rotate `90` degrees around Z
1. Rotate `90` degrees around Y

https://user-images.githubusercontent.com/2152766/129685773-6298aff1-8fc6-456a-b3a8-3c56a4d7a322.mp4 controls

<br>

#### Lower Leg Frames

Now we've got a problem. The knee is able to bend in the wrong direction.

https://user-images.githubusercontent.com/2152766/129687844-8614b782-aeee-4a93-ae69-3d7b6e02a8bd.mp4 controls

We *could* try and reduce the range, but that just moves the problem to the other side.

https://user-images.githubusercontent.com/2152766/129687847-dfaae124-15a8-4896-baae-f114c864ee82.mp4 controls

So what we need to do is *rotate* this limit. For this I'd like to introduce the parent and child **frames**.

<div class="hboxlayout">
<div class="vboxlayout align-left">
<code><b>Parent Frame</b></code>
<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/129691248-110ba46b-fc99-49cb-a58a-6f67eb0949ef.mp4" type="video/mp4">
</video>
</div>
<div class="vboxlayout align-left">
<code><b>Child Frame</b></code>
<video autoplay class="poster" muted="muted" loop="loop" width=100%><source src="https://user-images.githubusercontent.com/2152766/129691250-80d7c0b7-da6f-4ef5-a14d-430c29ad260a.mp4" type="video/mp4"></video>
</div>
</div>

Here's how to do it.

1. Select `L_knee_ctl` and `R_knee_ctl`
1. Find these in the Outliner
1. Select both `parentFrame` handles
1. Rotate both `parentFrame` such that it lines up with the `thigh_ctl`

https://user-images.githubusercontent.com/2152766/129685767-e8d9c85d-a841-40b4-8ceb-d80d28186710.mp4 controls

Now the knee will only ever bend back, but not forwards. To finish this off, let's **lock** the `Rotate Limit Y` and `Z` axes.

https://user-images.githubusercontent.com/2152766/129685764-b72014d7-4a36-4a5c-8002-b37106aeafbd.mp4 controls

Test it out, by dropping the Manikin from a few different angles. With the legs complete, they should not be able to form an unnatural pose. If they do, you now know how to tune the limits!

https://user-images.githubusercontent.com/2152766/129686347-f5aed5c6-347c-4bdb-8cef-ba532465dc85.mp4 controls

<br>

#### Upper Legs

Unlike knees, the upper legs are free to rotate around all 3 axis, X, Y and Z.

1. Select `L_thigh_ctl` and `R_thigh_ctl`
2. Set `Rotate Limit XYZ` to `40.0`

https://user-images.githubusercontent.com/2152766/129695064-1c9fd0a7-a367-4242-bc9e-6063fd303348.mp4 controls

Let's now use what we've learnt about the `parentFrame` to tune the range of motion of the thighs.

1. Select `L_thigh_ctl` and `R_thigh_ctl`
2. Run `Edit Pivots` under the `Constraints` submenu
3. Find and edit both `parentFrame` nodes

https://user-images.githubusercontent.com/2152766/129695049-86a2b035-b8e3-42f7-9e9d-8cf402877eb4.mp4 controls

<br>

### Finalise

You now know enough to construct *any* character of *any* anatomy!

**You have learnt**

- ✔️ How to *limit* the motion between two rigids
- ✔️ How to manipulate the *pivot* of a constraint
- ✔️ How to edit the range of motion using the *parent frame*

With these lessons in mind, try your hand at the remaining parts of the character, namely the Head, Shoulders, Elbows and Hands.

https://user-images.githubusercontent.com/2152766/129698559-623fd04b-9285-4478-b281-018ee1616138.mp4 controls

As you tune, try dropping the Manikin from different heights and angles. Put an obstacle underneath for more detail and to catch more edge cases. Once you are unable to produce an unnatural pose, you are done!

https://user-images.githubusercontent.com/2152766/129698550-61c15074-a134-4339-a4da-e469da7d4aeb.mp4 controls

**Download Completed Scene**

For your reference, here is the completed scene with the Manikin file referenced.

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/8CKfRSk3/manikin_rigging_v001_publish.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/01lBKSdb/manikin_walkthrough_v003.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

#### Soft Limits

Let's enhance the realism of our character with *soft limits*

1. Run `Constraints` from the `Select` submenu
2. Reduce `Limit Strength` to `0.1`

A default value of `1.0` means "very stiff" whereas a value of `0.1` means "less stiff". Depending on the number of limbs your character has, and its physical size and `Mass`, this value may need to be greater or smaller.

https://user-images.githubusercontent.com/2152766/129700459-e675fd5b-1dea-4fb4-8674-6a82c144c363.mp4 controls

There are two kinds of softness in the world; springy and damped. The defaults values are a little too springy for my taste, so I'll increase the `Rotate Limit Damping` by adding another `0`.

https://user-images.githubusercontent.com/2152766/129700464-26d795bb-03f7-4050-b594-d209d292eee7.mp4 controls

With yet another `0` added, we get some nice subtle "relaxing" of a pose as he's coming to rest on the ground. This is not unlike what you would see if you were to try and relax into a position near your own physical limits.

<br>

### Practical Examples

So now that we have an anatomically correct character, what can we do with it?

- We can **pose it** for motion reference
- We can **transfer** the simulation onto another rig
- We can **transition** from animation to simulation
- We can **double** or triple the amount of characters
- We can **free** it from gravity and achieve weightlessness
- ...

<br>

#### Motion Reference

What would it look like to get shot in this pose, from this specific angle, with this specific force?

1. Pose the character
2. Select `head_ctl`
3. Run `Push Force` from the `Forces` submenu
4. Give it a high value, such as `20000`
5. Give it a low `Max Distance`, such as `7.5`

By having the head selected, the force is applied onto onto the head.

https://user-images.githubusercontent.com/2152766/129709932-643b186b-af06-41d0-ab67-38e9a4cc679c.mp4 controls

Use the force visualiser (a.k.a. "Slice") to visualise the force in 3D.

https://user-images.githubusercontent.com/2152766/129709929-3c4d46cc-2e7c-429f-bc49-2c1e84132655.mp4 controls

**Experiment**

This example assigned a force to the head and didn't change the strength of that force. What if you..

- Assigned a force to the torso, or thigh?
- Assigned one to the *whole body*, like an explosion?
- Increased or decreased the force?
- ...

<br>

#### Transfer Simulation

Given that we ran our simulation on the actual character rig, exporting the simulation is *identical* to exporting regular animation. Which means we can use regular animation export tools to transfer this between rigs and characters.

Here's an example using [Studio Library](https://www.studiolibrary.com); a popular tool for transferring animation between characters and shots in both games and film pipelines.

1. Bake
2. Export
3. Undo

By undoing the bake, we get to keep our simulation after export.

**Bake Simulation**

Studio Library only deals with keyframes, so we first need to convert our simulation into keyframes.

https://user-images.githubusercontent.com/2152766/129720294-6ed30def-8c3e-469b-b363-3786ae64a51e.mp4 controls

**Export Animation**

Next, select all controls and export it like you normally would using Studio Library. After export, you can *undo* the Bake we did earlier, to restore our physics settings and export produce more results.

https://user-images.githubusercontent.com/2152766/129720296-e445d4c4-6280-49db-a9e0-ea242bb6d0d5.mp4 controls

**Import Animation**

In a new scene, with a clean rig - completely unrelated to Ragdoll - import the animation back onto the rig.

https://user-images.githubusercontent.com/2152766/129720301-273c75d8-9261-4593-a000-2394ca14097f.mp4 controls

<br>

#### Transition From Animation

With access to our reference in full 3D space, with controls similar or identical to our animation rig, why not pass the torch to simulation once we're happy with our animation?

> This chapter is in development

<br>

#### Multiple Manikins

Having gone through the trouble of setting this whole thing up, it would be a waste not to *multiply*  our efforts onto more characters!

> This chapter is in development

<br>

#### Life

There's no reason our Manikin cannot be alive and well as it drops, using the Mimic along with Soft and Hard Pin controls we can shape the simulation to our will.

> This chapter is in development

<br>

#### Space

In an environment without gravity, animation takes on a whole different level of difficulty. We humans are surprisingly good at spotting when weightlessness isn't weightless; you'll know this from watching any space movies like Life or 2001.

With our newfound knowledge and understanding of how to use Mimic and Pins to bring life into a character, let's explore a world beyond earth and head into space.

> This chapter is in development

<br>

#### Initial Velocity

So far our Manikin has started out still and either fallen or gotten hit by a force. But what about if our Manikin is in the middle of some motion? We can use a `Mimic` to give our Manikin some starting velocity.

> This chapter is also in development
