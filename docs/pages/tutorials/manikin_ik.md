---
title: Manikin and IK
description: Learn how to simulate IK controls
icon: "chain_black.png"
order: 42
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/145708966-91805ac3-a6ea-473d-b27f-b2173f8236e2.png">
    <source src="https://user-images.githubusercontent.com/2152766/145708943-123c151d-a76f-4594-9b69-167e7258d587.mp4" type="video/mp4">
</video>

### Manikin and IK

In the [previous tutorial](/tutorials/manikin_ragdoll) we turned a character rig into a ragdoll, driven by your animation.

In this tutorial, we'll have a look at how we apply this to the IK controls of a rig.

!!! success "Version 1.1 - Up to date"
    Written for Ragdoll `2021.12.10` and above.

**Estimated Time**

- 🕐 10 minutes

**You will learn**

- ✔️ How to assign markers to joints
- ✔️ How to retarget joints to controls

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

<br>

### Bring Your Own Rig

Follow this tutorial either using our provided Manikin rig, or your own character. It can have any number of limbs.

https://user-images.githubusercontent.com/2152766/129519170-59d6a109-e9eb-4fd0-87ef-f120050c9d7e.mp4 controls

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/Q96vbUR5/manikin.zip" class="button blue"><b>Download Manikin</b></a>
<a href="https://files.ragdolldynamics.com/api/public/dl/UJbKTN-T/manikin_ik_final.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

### Setup

Let's start fresh, with a non-dynamic character rig. In this case, the IK controls are disabled per default, so let's enable them.

1. Select `master_ctl`
2. Set `Left Leg Fk Ik = 1`
2. Set `Right Leg Fk Ik = 1`

https://user-images.githubusercontent.com/2152766/145432575-132c48ca-b10e-4a0f-b6b2-ee910b8e0fe3.mp4 controls

<br>

#### Assign to Upper Body

As per usual, let's assign markers onto the FK controls in the upper body.

https://user-images.githubusercontent.com/2152766/145432579-e8151940-6e86-4637-b2b2-0d4cd92b3ea2.mp4 controls

<br>

#### Find IK Joints

The legs are different. We don't want to pass the position of the IK controls in the solver, instead what we want are the joints they drive.

!!! question "Where are the joints in my rig?"
    The location of these will differ in every rig. What's important is that they are the ones that move when you move your IK controls. Any joints that do that will suffice.

    In the case of the Manikin, these will be located under the `skeleton_grp`.

https://user-images.githubusercontent.com/2152766/145432588-d4e07350-802b-4f3c-8fa0-316d79c9b0e8.mp4 controls

<br>

#### Assign to IK Joints

Once you've found a suitable set of joints, assign to them as per usual. Starting from the hip.

https://user-images.githubusercontent.com/2152766/145432594-db8681ca-a7e7-404f-ac11-01e8d0a5a7bc.mp4 controls

<br>

### Recording

Per default, Ragdoll will record onto the control you assign.

However, we don't want keyframes on our IK joints. We want keyframes on our IK *controls*. Therefore, we aren't ready to record just yet.

https://user-images.githubusercontent.com/2152766/145432599-d8178633-a337-4d29-aa91-ac3a0705189d.mp4 controls

> Notice how our IK controls didn't get any keyframes?

<br>

#### Retarget

Because we did not assign to our IK controls, we'll need to retarget the joints onto the controls.

https://user-images.githubusercontent.com/2152766/145432601-6815ab3f-fe74-42bb-96b2-bac55cf28e99.mp4 controls

Now when we record, our retargeted IK controls will be getting keyframes from our simulated IK joints.

!!! tip "Not Just IK"
    This will work between *any* controls or joints. Even from one rig to another, or more complex IK like Spline IK. The `Record Simulation` command uses a native Maya `Parent Constraint` between the assigned and retargeted controls, so anywhere you could manually do this will work with this command.

<br>

### Finalise

That's it for this tutorial! Here's some test animation.

<br>

#### Shapes

Grab the manipulator and tweak those shapes to fit your character.

https://user-images.githubusercontent.com/2152766/145432610-855587f9-61ae-49d7-ab83-e911706dc740.mp4 controls

<br>

#### Test Animation

Then drop some keys on our IK rig to see it in action.

https://user-images.githubusercontent.com/2152766/145432615-71f93122-8608-4eb5-8df9-5ad58141a2cf.mp4 controls
