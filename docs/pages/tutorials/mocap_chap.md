---
title: Mocap Chap
description: Learn how to simulate only part of a character
icon: "ragdoll_black.png"
order: 43
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/145552320-17d6bbd9-3562-45c7-88a5-3c48fba51a5d.png">
    <source src="https://user-images.githubusercontent.com/2152766/145552217-0663b6a5-206f-46d2-b0e4-31b0e1877c64.mp4" type="video/mp4">
</video>

### Mocap Chap

In the [previous tutorials](/tutorials/manikin) we've turned a character rig into a full ragdoll, driven by your animation.

This time we'll look at applying physics to only parts of a character, like the upper body of this mocap clip found in Maya's default Content Browser.

!!! success "Version 1.1 - Up to date"
    Written for Ragdoll `2021.12.10` and above.

**Estimated Time**

- 🕐 10 minutes

**You will learn**

- ✔️ How to apply physics to mocap
- ✔️ How to simulate only part of a character

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

<br>

### Overview

When and why would you even want simulation on *parts* of a character?

1. Tails
1. Props
1. Muscles

Are three simple and somewhat obvious examples, more complex examples include what we're about to do in this tutorial. Namely, *edit the mass of an object* picked up during the original motion capture.

https://user-images.githubusercontent.com/2152766/145550133-4d9daedc-478c-44db-8a65-5a248b26e67b.mp4 controls


https://user-images.githubusercontent.com/2152766/145550147-56714786-3ac9-44b8-b73f-b85d34e53bf4.mp4 controls


<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/8rswPm8i/mocap_chap_final.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

### Setup

Let's start by importing our motion capture clip; this can be *any* clip but if you'd like to follow along here's what you do.

1. `Windows -> General Editors -> Content Browser`
2. Drag and drop `Smash.fbx`

??? question "Unrecognized file type?"
    Make sure the `fbxmaya.mll` plug-in is loaded via the Maya Plug-in Manager.

https://user-images.githubusercontent.com/2152766/145538215-b777b23c-4796-4562-9054-aed5bffbeee2.mp4 controls

Here's what this clip looks like.

https://user-images.githubusercontent.com/2152766/145538219-46bb9939-d04e-42d5-a310-76a4b4f058f8.mp4 controls

<br>

#### Symmetry (optional)

In order for Ragdoll to recognise symmetry later when we edit the shapes using the `Manipulator`, we'll need to assign markers in a symmetrical pose.

1. Rewind to frame 0
1. Select the root
1. Set `Translate X` and `Translate Z` to 0
2. Run `Select -> Select Hierarchy`
3. Right-click and hold
3. Run `Assume Preferred Angle`
3. Set a keyframe on everything

https://user-images.githubusercontent.com/2152766/145538223-9dbf5040-1188-4450-99ff-cd54c5648d76.mp4 controls

<br>

#### Assign Markers

In this case, I'm ignoring fingers along with the center joint in each limb, like the lower arms and upper legs.

https://user-images.githubusercontent.com/2152766/145538225-66dfce35-9c70-40ec-9df3-6c546114ef84.mp4 controls

From here, we can move our simulation to frame to `1`. We don't need frame `0` anymore.

https://user-images.githubusercontent.com/2152766/145538228-d36ab724-4e4a-4252-886e-24b9caee30ad.mp4 controls

<br>

#### Kinematic Legs

In this tutorial, we're only going to worry about the upper body, so let's turn those legs into 100% animation via the `Kinematic` behaviour.

https://user-images.githubusercontent.com/2152766/145538230-8364d89c-7d4b-4461-b405-d31c3794666b.mp4 controls

<br>

### Tuning

The stage is set, it's time to tune!

<br>

#### Shapes

Nothing special here, and since we have no geometry to fill we have some creative freedom in how we want our character to look!

https://user-images.githubusercontent.com/2152766/145547877-2292f1a9-209e-414f-9a33-0795d163370a.mp4 controls

Let's have a look at where defaults values gets us.

https://user-images.githubusercontent.com/2152766/145547879-a7982b7b-b793-458a-8f2e-38e23fa354ab.mp4 controls

Not bad! But since we want our simulation to be close to the original mocap, we'll need to make some changes.

<br>

#### Stiffness and Substeps

The default solver substeps and iterations get you to a `Stiffness` of about `10`. In order to achieve a higher stiffness, we'll need more of those.

1. Select `rSolver`
2. Set `Substeps = 8`
2. Set `Iterations = 8`
1. Select `Hips_rGroup`
1. Set `Pose Stiffness = 40`
1. Set `Pose Damping = 0.25`

https://user-images.githubusercontent.com/2152766/145547884-c8252d45-45f5-4f5b-9cad-f950b11c4eaf.mp4 controls

<br>

### Box

Let's get the box in on the action.

https://user-images.githubusercontent.com/2152766/145547899-72fb1d17-399a-48ef-a807-2ce941b6a5cf.mp4 controls

<br>

#### Attach Hands to Box

He does a good job holding onto that box through friction between hand and box alone, but let's help him out by "glueing" the two together using a `Distance Constraint`

1. Select the box
2. Shift select the left hand
3. Run `Ragdoll -> Constrain -> Distance`
4. Repeat the process for the right hand

https://user-images.githubusercontent.com/2152766/145547900-a8e6f13a-c746-4fe0-b814-00cc65f86a3d.mp4 controls

The default distance will be `From Start`, meaning it will try and keep whatever the distance was between the box and the hands at the start of the simulation.

What we want however is for the `Maximum` distance to be `0`, and for it to only start having an effect once the hands overlap the box.

https://user-images.githubusercontent.com/2152766/145547903-3f3a60a0-4d93-4f8e-b8c2-4fd951abd931.mp4 controls

Now let's edit the point at which the hand and box snap together.

1. Select one of the constraint
2. Edit the `Parent Offset`

> Since we selected the box *first*, it is considered the "parent".

https://user-images.githubusercontent.com/2152766/145547908-54731121-11c6-4fb8-a410-e2a9dcf863fc.mp4 controls

<br>

#### Animate On and Off

Next, let's activate this constraint once hands are in place.

1. Go to frame `80`
1. Set a keyframe on both constraints `Stiffness = 0`
2. Go to frame `81`
2. Key `Stiffness = 0.5`

Likewise, we'll want the hands to release the box at some point later.

1. Go to frame `178`
2. Key `Stiffness = 0.5`
2. Go to frame `179`
2. Key `Stiffness = 0`

https://user-images.githubusercontent.com/2152766/145547912-9517cf39-1b7c-4fe1-8bad-970ab3daa5cf.mp4 controls

<br>

### Finalise

And that's it! We've now massaged our original motion capture into carrying a box of similar weight to the motion.

Let's make some changes and see what happens.

<br>

#### More Mass

What if the box was heavier?

1. Select the box
2. Select the `rMarker_pCube1` in the Channel Box
3. Press `T` on your keyboard
4. Set `Mass = 10`

https://user-images.githubusercontent.com/2152766/145547919-c980c7f2-928c-4a5e-9468-c42e3499c90c.mp4 controls

<br>

#### Mass and Cache

When tuning single values like this, it can be helpful to leave the Maya timeline in place and let the simulation update independently.

https://user-images.githubusercontent.com/2152766/145547924-988c4ec9-2fa2-4b79-abb8-6b278cc7e7da.mp4 controls

<br>

### Next Steps

At this point, you're able to turn any old motion capture hierarchy into a partial or fully-fledged ragdoll. Why not try a few more from the Content Browser? Or download any of the hundreds of freely available clips from here.

- https://www.mixamo.com
- https://www.rokoko.com
- http://mocap.cs.cmu.edu