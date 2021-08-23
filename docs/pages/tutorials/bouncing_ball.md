---
title: Bouncing Ball
description: Expore the fundamentals of Ragdoll
icon: "physics_black.png"
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/130401392-0d4549ab-3545-46ec-98d2-6b084b2a8465.jpg">
    <source src="https://user-images.githubusercontent.com/2152766/130034996-98912ff5-7a3c-4ca4-8486-3906b50cc780.mp4" type="video/mp4">
</video>

### Bouncing Ball

> The fundamentals of animation

In this tutorial, we will reproduce a classic animation tutorial, the Bouncing Ball. With it, we will explore various material properties of a ball whilst learning about the inner workings of Ragdoll.

!!! success "Version 1.0 - Up to date"
    Written for Ragdoll `2021.08.06` and above, but should still apply for `2021.06` and newer.

**Estimated Time**

- 🕐 10 minutes

**You will learn**

- ✔️ How to convert a `polySphere` into a "rigid"
- ✔️ How to tune physical properties such as bounciness and friction
- ✔️ How to configure the solver for accurate high-frequency motion

**Where to find help**

If you find or run into any issues with this tutorials, here's what you can do.

- ✔️ Ask in [the chat](https://ragdolldynamics.com/chat)
- ✔️ Ask on [the forums](https://forums.ragdolldynamics.com/)

<div class="hboxlayout justify-left">
<a href="https://files.ragdolldynamics.com/api/public/dl/J0nMny95/bouncing_ball_v003.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

### Motivation

Why should an animator *simulate* a ball bouncing, rather than just keyframe it? 

If you are new to animation or in a neighbouring field such as modeling or lighting, it might seem silly to consider such a trivial task for simulation. But as the more seasoned animator knows, getting the trajectory of any free-flying object right is *incredibly* hard. It can mean the difference between a believable character, and a character that looks like Earths gravity varies for the duration of a single jump, or one that appears to be on a different planet altogether.

With that in mind, althoguh a single ball bouncing on a flat plane may *seem* trivial, it can be enough to challenge even the most senior of animators.

<br>

### Setup

For this tutorial, all you need is an empty Maya scene. So go ahead and clear out all of those references and meshes with hours of history on it and let's get crackin'!

<br>

#### Poly Sphere

Let's make our ball out of a regular Maya `polySphere`.

1. Run `Sphere` from the `Polygon Primitives` submenu of the `Create` main menu
2. Translate the sphere to `Translate Y = 5.0`

??? question "What about NURBS?"
    Yes, if you prefer, you can also use a NURBS sphere.

https://user-images.githubusercontent.com/2152766/130042846-17b46ae2-e8b1-432f-9382-945a7727f494.mp4 controls

<br>

#### Dynamics

With our sphere in place, let's give it some physical properties by turning it into a `Active Rigid`.

1. Select `pSphere1`
2. Run `Active Rigid` from the `Ragdoll` Menu

https://user-images.githubusercontent.com/2152766/130044033-f5d695ad-08cd-4703-9061-c950e15555aa.mp4 controls

That's great! Except hm.. It's not really a *bouncing* ball just yet.

<br>

#### Bounciness

Default settings make the ball rather dull, so let's try introducing some bounciness via its material properties.

1. Select `pSphere1`
2. Increase `Bounciness = 1.0`

??? question "What does 1.0 mean?"
    It means 100%! Technically, it means any force produced by the ball hitting the ground is reversed in its entirety with *no* loss of energy what-so-ever.

https://user-images.githubusercontent.com/2152766/130352353-3ac29137-0e11-4e8d-9e01-4808f9818809.mp4

<br>

#### More Bounciness

The reason the ball stops bouncing is that even though our *ball* is 100% bouncy, the **ground** is not. Like dropping a bowling ball on grass or a wooden floor. For perfect bounce, they *both* need to be 100% bouncy.

1. Select `rScene`
2. Set `Ground Bounciness = 1.0`

??? question "Where did the ground come from?"
    Ragdoll creates this ground automatically for you whenever the first rigid is made. It can be disabled by setting `Use Ground = Off` on the `rScene` node.

https://user-images.githubusercontent.com/2152766/130045101-f98d2ace-7766-4871-8f0c-46e1d1cec022.mp4 controls

<br>

#### Even More Bounciness

Around the 11-second mark of the video above, you'll notice the ball suddenly comes to a halt. As if it suddenly remembered it isn't actually a bouncing ball anymore. Why is this? 😯

The default values are tuned for the simulation of ragdolls (surprise surprise!) so in order to accurately simulate just a ball we need to make some tweaks.

1. Select `rScene`
2. Go to the `Advanced` tab in the `Attribute Editor`
3. Set `Bounce Threshold = 0.1`

??? question "What does Bounce Threshold mean?"
    It is how small of a bounce Ragdoll should consider to be a bounce, until it eventually stops it from bouncing.

    A value of `0.0` theoretically means the objects would *never* stop bouncing. No matter their `Bounciness`. Each bounce would simply get smaller and smaller into infinity!

    In the real world, objects would naturally come to a halt at some point due to friction in the air and along the surfaces of the two objects. With Ragdoll, we only have approximations of such things so as to make a simulation run in real-time, and as a result we need to manually tune this parameter until we find a value that suits our taste.

https://user-images.githubusercontent.com/2152766/130048001-8e3b6e0f-b407-45a8-922f-f9da58648bbd.mp4 controls

<br>

#### Infinite Bounciness

Let's keep pursuing that sweet sweet *perfect* bounce.

1. Select `rScene`
2. Reduce `Air Density = 0.0`

??? question "What is Air Density?"
    This attribute can be used to emulate the effect air has on your simulation. It can be used to achieve effects *other* than air too.

    | Air Density | Effect
    |:------------|:----------
    | `0.0`       | Vacuum
    | `5.0`       | Water
    | `10.0`      | Mud
    | `100.0+`    | Sand

    Technically, the attribute is a multiplier of `Translate Damping` and `Rotate Damping` of each `rdRigid` node, which can be used to affect individual rigids.

https://user-images.githubusercontent.com/2152766/130062842-2519b73b-c76c-4250-abbe-52c618b7f989.mp4 controls

<br>

### Finalise

Now that we have complete control over our ball, let's put it to good use.

**You have learnt**

- ✔️ How to convert a `polySphere` into a "rigid"
- ✔️ How to tune physical properties such as bounciness and friction
- ✔️ How to configure the solver for accurate high-frequency motion

<br>

#### Initial Velocity

Give the ball a little push.

1. Select `pSphere1`
2. Run `Hard Pin` from the `Controls` submenu of the `Ragdoll` menu

https://user-images.githubusercontent.com/2152766/130067077-9957d017-6f60-4a07-9442-d4ec1ece3b99.mp4 controls

A new node was created called a "Hard Pin", which tells Ragdoll exactly where this ball should be at any given moment. We can now animate this pin which in turn animates the ball, until we "unpin" it.

1. Select `rHardPin`
2. Set the following keyframes.

| Frames        | 1             | 2             | 3
|:--------------|:--------------|:--------------|:-------
| `Translate Z` | `0.0`         | `0.5`         |
| `Passive`     |               | `On`          | `Off`

https://user-images.githubusercontent.com/2152766/130067337-7f19d854-45a5-44a0-9581-20e648a5d2ad.mp4 controls

<br>

#### Trajectory

With our bouncing ball underway, let's gain a deeper understanding of what it looks like over time.

1. Select `rScene`
2. Go to the `Visualisation` tab
3. Toggle `Trajectories`

https://user-images.githubusercontent.com/2152766/130074593-668bca60-6b48-4502-8521-7c8393558bbe.mp4 controls

Now, as every animator knows, this is **not** the trajectory of a bouncing ball. It looks as if the ball isn't actually touching the floor half the time, what's up with that? 🤔

| Expected Result<br>✔️ | ![Expected result](https://user-images.githubusercontent.com/2152766/130076967-0d84f40b-2d02-4da5-94af-826ee4baac29.png)
|:---------------|:--------------
| **Actual Result**<br>❌ | ![Actual result](https://user-images.githubusercontent.com/2152766/130076971-56b3460a-1399-4fd1-bd80-e4d850b30769.png)

This is a problem of *resolution*. Cameras have this problem too.

https://user-images.githubusercontent.com/2152766/130089534-22b88ab5-f5c7-41f0-8987-6961e9133f0c.mp4 controls

See how despite this most definitely *not* being a simulation (or is it?) we are *still* getting bounces that don't actually touch the ground! The reason is simply that a camera can only capture *moments* of reality. It can only *sample* it.

In this case, the ball *did* touch the floor, but the camera caught at a slightly different time. Shortly before and after contact. This is how you can think of Ragdoll too; a camera for physics.

??? question "Can you overeducate me?"
    With pleasure. 😁 Let's look at *audio*.

    ![image](https://user-images.githubusercontent.com/2152766/130089957-7261ab3b-a0ab-4861-933a-f034d4debcee.png)
    
    - [Wikipedia Reference](https://en.wikipedia.org/wiki/Sampling_(signal_processing))

    Notice how sound itself, represented by the curved line, is continuous - of infinite resolution - and that what we capture in our computers are samples of it, at some fixed resolution - typically at 44,000 fps or as it is more commonly known `44khz`.

    Ragdoll works like this too. Physics is continous, but Ragdoll can only provide you with snapshots of physics at a fixed resolution; the resolution of your framerate.

??? question "Is every bouncing ball tutorial on YouTube wrong?"
    A typical bouncing ball tutorial has the ball come into contact on whole frames. But because the time between each bounce is decreasing, it is *impossible* for every bounce to land on a whole frame.

    So in a way, yes, they are wrong! Science says so!

??? question "Should I change the way I animate?"
    Well, it depends. Take motion blur for example.

    Because you see, the final position from a video recorded tennis ball is only half the story. Motion blur isn't the result of only these samples, but of the *actual* continous motion. As light hits the lens inbetween the shutter opening and closing, the ball is still moving.

    To accurately reproduce this effect in your animation or with Ragdoll, you still need those inbetween positions of the ball. Just so that your renderer can throw those away once it's done computing motion blur.

    Even without motion blur, your eyes and brain still interprets the ball not hitting the ground as though it floats or hits an invisible obstacle. So for the greatest sense of realism when everything has been said and done and the images actually reach your eyes (brain), you may *still* want to defy physics and realism.

    Because at the end of the day, the animation curves isn't what you are making. They are mere tools for you to achieve realism in the final output picture.

<br>

#### Tennis Ball

Now that we've got some reference for a tennis ball, let's tune our settings to match.

1. Select `pSphere1`
1. Set `Bounciness = 0.4`

https://user-images.githubusercontent.com/2152766/130199902-b5b54f6e-f1e9-46ef-83a9-a3b0784e2418.mp4 controls

Let's also take it out of orbit and into Earths atmosphere by restoring the `Air Density`

1. Select `rScene`
1. Set `Air Density = 1.0`

https://user-images.githubusercontent.com/2152766/130199900-f165d6d1-c9da-493a-930e-ad271c5a40ed.mp4 controls

<br>

### Practical Examples

Now that we've got a ball, what could we possible do with it?

<br>

#### Squash

https://user-images.githubusercontent.com/2152766/130283151-4c6225b9-0ba0-40c9-af34-f826ae4e20a1.mp4

Now we can use what we've learnt and combine it with some traditional rigging to *deform* our ball!

We'll achieve this by reducing the size of our simulated ball, whilst keeping our Maya geometry the same. That will result in the Maya geometry actually *intersecting* the ground. We will then "fix" the intersection whilst preserving the overall volume of the mesh.

Let's go.

| #    | Description | Screenshot
|:----:|:------------|:--------------
| 1    | Create a new `Icosahedron` with 4 subdivisions of triangles.<br><br>We will use this as the deformed version of our rigid. | ![image](https://user-images.githubusercontent.com/2152766/130214110-d49eb9df-016f-4af8-9da6-c88d1192049e.png)
| 2    | Create a floor out of a box, we need something with volume. | ![image](https://user-images.githubusercontent.com/2152766/130218959-56d37941-c9e3-4e72-8919-6eded7037336.png)
| 3    | Parent Constrain `pPlatonic1` to `pSphere1`.<br><br>Do not maintain the offset such that the new sphere follows the original sphere. | ![parentconstraint](https://user-images.githubusercontent.com/2152766/130283490-f5e60402-3ea3-46d4-9361-6fa1f13094f7.gif)
| 4    | Reduce the `Radius` of `pSphere1 = 0.5` | ![radius](https://user-images.githubusercontent.com/2152766/130219540-2c394185-0823-4fd8-b97f-55228f2ba7a6.gif)

With a radius less than our geometry, the geometry will naturally *intersect* with our ground. Let's compensate for this using a `membrane` deformer.

1. Select `pPlatonic1`
2. Run the following MEL comment

```cpp
createMembrane
```

https://user-images.githubusercontent.com/2152766/130234021-61c568e4-c086-4375-959d-48870c44a237.mp4

Not much will happen yet, apart from a small offset along Y. We'll get to that. But first.

1. Select `pPlatonic1`
2. Shift select `pCube1`
3. Run the following MEL command

```cpp
collideMembrane
```

https://user-images.githubusercontent.com/2152766/130234697-9aec0728-6f20-40f2-8887-aa82312a1b39.mp4

Great, so the ground pushes against the ball, solving the intersection we created earlier by reducing the `Radius`.

Let's tune the `membrane`

1. Select `pPlatonic1`
2. Set these attributes

| Attribute                 | Value      | Description
|:--------------------------|:-----------|:----
| `Gravity`                 | `0.0`      | Remove that offset along Y
| `Thickness`               | `0.01`     | Get the ball and ground closer
| `Steps`                   | `5`        | Fix the intersection with the ground
| `Compression Resistance`  | `5`        | Maintain the volume of the ball
| `Bend Resistance`         | `2`        | Spread the deformation
| `Stretch Resistance`      | `1`        | Smoother overall surface

https://user-images.githubusercontent.com/2152766/130282792-a358d07a-be70-4319-a137-57c2ab61e55a.mp4

From here, you can tune `Bend Resistance` for more or less stiffness in the overall surface, and `Steps` for more or less of an effect.

<br>

#### Pong

Let's recreate a classic game of pong, with two animatable paddles.

https://user-images.githubusercontent.com/2152766/130352449-a57fc0b0-7d6e-48b5-bdd4-373c43542dbf.mp4

| # | Description | Video
|:--|:------------|:------------
| 1 | Create a new rigid.<br><br>We won't need any geometry, the default shape will be a `Sphere` | <video autoplay class="poster" muted="muted" loop="loop" width=100%>    <source src="https://user-images.githubusercontent.com/2152766/130351250-74cd9933-a0d1-468c-b39a-a5ae15cea473.mp4" type="video/mp4"></video>
| 2 | Let's look from a `side` view. | <video autoplay class="poster" muted="muted" loop="loop" width=100%>    <source src="https://user-images.githubusercontent.com/2152766/130351249-817039ea-5846-4c26-a941-46a21c128c0f.mp4" type="video/mp4"></video>
| 3 | Create the floors.<br><br>Same thing, except this time as a `Passive Rigid` and we'll adjust the shape to a `Box`. | <video autoplay class="poster" muted="muted" loop="loop" width=100%>    <source src="https://user-images.githubusercontent.com/2152766/130351246-e76310fc-2b93-40ae-b79a-aab4858e61ac.mp4" type="video/mp4"></video>
| 4 | Create the paddles. | <video autoplay class="poster" muted="muted" loop="loop" width=100%>    <source src="https://user-images.githubusercontent.com/2152766/130351245-7403de5f-1999-42d9-9263-95ed8b51a602.mp4" type="video/mp4"></video>
| 5 | Create a `Soft Pin`, and animate its `Guide Strength` across the first two frames.<br><br>We'll use this to give the ball its initial velocity. You can tweak the position and strength to give it more or less speed in your chosen direction. | <video autoplay class="poster" muted="muted" loop="loop" width=100%>    <source src="https://user-images.githubusercontent.com/2152766/130351244-2edbf976-8b87-4939-a278-7f8fcc774fd1.mp4" type="video/mp4"></video>

Now let's tune some settings.

1. Select every rigid
1. Set `Friction = 0.0`
1. Set `Bounciness = 0.0`
1. Select `rScene`
1. Set `Air Density = 0.0`
1. Set `Use Ground = Off`
1. Set `Bounce Threshold = 0.1`

https://user-images.githubusercontent.com/2152766/130351241-279c3d81-cdd4-46c9-b98f-8ae5855d02e7.mp4

Finally, we can **animate** the paddles. Winning is a little easier than normal Pong, since we can not only freeze time, but rewind it too. 😅

https://user-images.githubusercontent.com/2152766/130351243-f1776748-f513-4b88-a884-77d09b6bf988.mp4 controls

<br>

#### Incredible Machine

In the 1990s, there was a game developed called The Incredible Machine. In it, you were tasked with creating an obstacle course for a set of mechanical contraptions and physical objects in order to get some object from one place to another.

> Coming soon

<br>

#### For Science

The shortest path isn't necessarily the fastest.

<!-- WIP of an Omniverse example -->

> Coming soon

<br>

#### Pool

A classic game of pool with balls constrained onto a 2D plane.

> Coming soon

<br>

### Troubleshooting

Let's have a look at some common issues.

<br>

#### Vibrating at Rest

There is no right value for `Bounce Threshold`, it's an art. And it depends on the size of your scene and rigids, their shape, how fast they move and the look you are after.

When the threshold is too low, Ragdoll can get into an infinite bounce like this.

https://user-images.githubusercontent.com/2152766/130202752-539c1836-d8c7-4745-98ad-98b783d8e7ea.mp4 controls

To address this, increase the threshold until it stops.

https://user-images.githubusercontent.com/2152766/130202749-db01636e-402a-4a4d-ac4b-932eb1795828.mp4 controls

