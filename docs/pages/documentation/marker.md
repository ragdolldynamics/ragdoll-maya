---
title: Marker
icon: "marker_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Markers form the fundamental building block of Ragdoll, to achieve **Animation Capture** a.k.a. "reverse motion capture".

<br>

### Animation Capture

> Capture your character rig, as though it was a live action actor.

Inspired by Motion Capture - Animation Capture is a new way to think about and work with physics in Maya. To learn about it, let's first understand how Motion Capture generally works.

![image](https://user-images.githubusercontent.com/2152766/134006344-53f2744f-cc7f-48b0-860d-d0313a353c1f.png)

Here is a typical data pipeline for motion capture, from real-life actor to final character animation.

| # | Description
|-----:|:-----------
| **1**  | Markers are attached to an actor
| **2**  | Markers are "captured"
| **3**  | A pointcloud is generated
| **4**  | A hierarchy of joints is generated
| **5**  | Joints drive a typical character rig
| **6**  | Rig drives final geometry for render

Each "Marker" is a dud. Nothing of any complexity. Something for the camera(s) to recognise and track as it moves through space. Once tracked, it's able to translate this Marker from a 2D image into a 3D position, and continues to do so for each Marker. The real processing to take place inside software.

Once the capture is complete, the human actor can remove the markers and go enjoy the rest of their day. The rest is up to the computer.

With 3D positions generated, software takes over to translate these points into a hierarchy; the FK joint hierarchy you may be familiar with if you've ever worked with mocap. The joint hierarchy can then be used to either drive the final geometry, or to drive a more complex character rig which in turn drives the final geometry.

Animation Capture is just like that, but in **reverse**. Instead of capturing a person, it captures your *character rig*.

![image](https://user-images.githubusercontent.com/2152766/134128846-7c55bfe3-b2c6-418f-ab04-4e29f61a5ec2.png)

| # | Description
|-----:|:-----------
| **1** | Markers are attached to a character rig
| **2** | Markers are "captured"
| **3** | A rigid body is generated for each Marker
| **4** | A hierarchy of constraints is generated to connect them
| **5** | Simulation is **recorded** back onto the original character rig

Unlike motion capture, we'd like the result mapped back onto our character rig again, which is how animators iterate with physics.

<br>

#### Example 1 - Basics

Here's how to simulate a box.

1. Select box
2. Run `Assign`

https://user-images.githubusercontent.com/2152766/145576767-70432ee7-6ab4-4231-b74f-03c05107ac59.mp4 controls

Once you're happy with what you see..

3. Run `Record Simulation`

https://user-images.githubusercontent.com/2152766/145576770-c5b8c0f0-b497-4bb7-80fa-38d4db6168d3.mp4 controls

<br>

#### Example 2 - Ragdoll

Here's how to setup a full Ragdoll.

**1. Setup hierarchy**

Select controls in the order you'd like them attached.

https://user-images.githubusercontent.com/2152766/145582365-c6d88809-1695-40be-81c0-c6f77005cd27.mp4 controls

**2. Edit shapes**

Fit the shapes to your character model.

https://user-images.githubusercontent.com/2152766/145582368-19d6d039-497a-4687-aa14-a9e1d1e2da3f.mp4 controls

**3. Record**

Once your happy with the way the simulation looks, record it back onto your rig.

https://user-images.githubusercontent.com/2152766/145582370-7cad0c4e-213d-4699-afa3-7c6762d198ce.mp4 controls

<br>

### Behaviour

In the above examples, I mentioned `Kinematic` and you probably spotted a few other options too, like `Inherit` and `Pose Match`. What are those?

The `Behaviour` is how Ragdoll should interpret the controls you assign. Did you mean for them remain animated, i.e. `Kinematic`? Or should they follow the control around, i.e. `Pose`? Or should they just fall with gravity, ignoring the original control altogether, i.e. `Initial State`?

The `Behaviour` can be set either for a whole group of markers, or each Marker individually.

| Type | Description
|:-----|:-----------
| Inherit       | Do whatever the group is doing, or `Kinematic` if there is no group
| Initial State | Do nothing, just fall under gravity
| Kinematic     | Follow the input *exactly*, physics need not apply
| Pose Match    | Follow the input approximately, with some `Stiffness` and `Damping`

<br>

#### Initial State

Treat the input as a starting position, but nothing else.

https://user-images.githubusercontent.com/2152766/134478792-d7f4fc46-fea0-468a-9ec0-7737072263a1.mp4 controls

<br>

#### Kinematic

Follow the input exactly, no exceptions. Not even collisions.

https://user-images.githubusercontent.com/2152766/134478795-daa12066-c151-4fd5-a762-443b60a7fc45.mp4 controls

<br>

#### Pose Match

Follow the local pose of your animation.

https://user-images.githubusercontent.com/2152766/134478800-e90f8928-b590-4b91-a314-bdcd9152cfef.mp4 controls

<br>

#### Pose Space

Pose matching happens in either `Local` or `World` space.

https://user-images.githubusercontent.com/2152766/134329974-7beb86d9-5660-44ba-b3f8-036ccc3aec28.mp4 controls

> Look, it's Ragdoll Blaine!

This is an example of **Worldspace Pose Matching**. Ragdoll will try and reach the worldspace position and orientation of your rig, rather than only looking at the relative angles between each limb.

Here's another example of the difference between `Local` and `World`space.

https://user-images.githubusercontent.com/2152766/134331199-c381ab43-4055-4e7a-a190-68d2acd0668f.mp4 controls

Notice how in `Local` space, the controls arms remain relative the torso. And with `World` space they instead follow the *worldspace* orientation of the controls.

This attribute is also **animatable**, and is how you can transition from animation into simulation and back again.

https://user-images.githubusercontent.com/2152766/134342444-2c2807ff-0be7-43f9-b106-73f231d55adb.mp4 controls

Here's a more complete example:

https://user-images.githubusercontent.com/2152766/134332515-e7879b82-4a84-4881-90cf-25f66a6d3ac8.mp4 controls

| Frame | Transition
|:------|:----
| 100 | Starts as a regular animated character
| 125 | Transitions into physics as he jumps, for a physically-correct trajectory
| 155 | Transitions back to animation once he rolls over on that cabinet
| 160 | Transitions back to physics until he stands up
| 170 | Transitions back into animation to match an exact pose
| 200 | Partially transitions into physics, for secondary motion in the upper body as his arm is raised.

<br>

### Overlap Group

Specify which markers may overlap rather than collide. This can be useful to enable dense areas of a character, like the clavicles, where there is natural overlap amongst large shapes like with the neck and spine.

| Value | Meaning
|:------|:-------------
| `-1`    | No overlap allowed
| `0`     | Default, respects self-collision on the group (if any)
| `1-255` | Overlap everything with the same number

An `rdMarker` part of a `rdGroup` can get an overlap group assigned procedurally, based on other members of that group. For example, in a complete ragdoll, all markers are part of the same group. So a `Self Collide = On` means these will all be given the same overlap group.

If it isn't in a group, then `0` is the same as `-1`, in that it will collide with everything.

Let's have a look at a few scenarios.

<br>

#### Collide with Everything

In this example, every Marker is part of the same group. The group has `Self Collide = Off`, which is fine for just about every Marker *except the fingers*. In that case, we *do* want self-collision, so they are given the group `-1`.

https://user-images.githubusercontent.com/2152766/136033654-9e84313f-d2f8-4e97-a14f-600154dfd709.mp4 controls

<br>

#### Respect Self Collision

In this case, we're happy with a default group of `0` since we don't need anything to self collide. Especially these clavicles that overlap significantly!

https://user-images.githubusercontent.com/2152766/136034921-e9fd364b-9889-430c-8ab2-215ab5b998f1.mp4 controls

<br>

#### Surgical Control

Finally, for the very specific cases of wanting two or more markers to overlap. Notice how we give both the ground and 3 of the boxes an `Overlap Group = 5`.

https://user-images.githubusercontent.com/2152766/136040503-66728dee-d4f9-4411-bd08-9bf18043c334.mp4 controls

<br>

### Material

Each Marker has a "material" to control how it interacts with other markers.

<br>

#### Mass

How much influence one Marker should have over another during contact.

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127736547-195a18f6-6567-4cdc-995e-d6fa0f7ef963.mp4" type="video/mp4">
</video>

!!! hint "Pro tip 1 - Misconception about Mass"
    A common misconception in physics is that `Mass` affects how *quickly* something falls to the ground. But in Ragdoll - like in real-life - mass is only relevant during interaction with another Marker and when forces are applied, like `Guide Strength`.

    Have a look at this video of a bowling ball falling in a vacuum alongside a feather.

    [<img class="poster" width=300 src=https://user-images.githubusercontent.com/2152766/127608727-07d0c3c2-d281-4290-93cf-392852f2d595.png>](https://www.youtube.com/watch?v=frZ9dN_ATew)

??? hint "Pro tip 2 - Making something fall faster"
    So how *do* you make something fall faster?

    1. Decrease `Scene Scale` under the solver node
    2. Increase `Gravity`, also under the solver node

    To make something "bend" faster, like an arm flexing, that would be controlled via the `Guide Strength` and typically what causes it to reach a given speed and then stay there is governed by the `Rotate Damping`. That's how much of any motion should be cancelled out, to stabilise the motion. A very *fast* motion would have very little damping, but then also run the risk of "overshooting". That is, of passing the point at which you wanted it to reach.

<br>

#### Friction

Control how much resistance should be added between two rigids rubbing against each other.

![friction2](https://user-images.githubusercontent.com/2152766/127735361-da060dc4-45c8-4699-a672-0253d177d723.gif)

<br>

#### Bounciness

Control how much rigids should *repel* each other when coming into contact.

![restitution](https://user-images.githubusercontent.com/2152766/127735506-36003376-4a70-41b2-bbb8-47c974d44278.gif)

!!! hint "Values beyond 1.0"
    Here's a tip!

    Bounciness can be greater than 1.0, which means they will *gain* energy during contact.

    In practice, energy will always dissipate in some way. The most-bouncy character in the gif above has a bounciness of `2.0`, which in theory means that for every contact it should fly `200%` faster away than it did coming in, and keep doing this forever.

<br>

#### Center of Mass

If you try and balance something on your finger, but the "center of mass" is off center, it would fall over.

![image](https://user-images.githubusercontent.com/2152766/99946359-25471500-2d6e-11eb-8c29-5d39e69f05ee.png)

It is the point at which the weight of an object is equal in all directions.

Ragdoll automatically computes this point based on what the shape looks like. For meshes, it will *voxelise* your geometry to figure out the physically accurate volumetric center of mass, assuming the density of the object is uniform throughout (rather than hollow or variadic, like swiss cheese).

You now override this point using the attribute `Center of Mass` found under the Advanced tab.

![ragdollcom](https://user-images.githubusercontent.com/2152766/99946517-64756600-2d6e-11eb-8446-469ea68073b4.gif)
![ragdollcom2](https://user-images.githubusercontent.com/2152766/99946522-663f2980-2d6e-11eb-9a5e-9aa9bf7c301a.gif)

**Guidelines**

- For realistic results, leave it at `0` to compute the point automatically based on the shape
- For full control, override it

<br>

#### Angular Mass

In real life, if you spin a broom 180 degrees along its length; that's easy. But if you spin it 180 degrees along any other axis, like a ninja, it's considerably heavier.

<img width=400 src=https://user-images.githubusercontent.com/2152766/99944546-f67b6f80-2d6a-11eb-93b1-47a49deba0d5.png>

The reason is something called "angular mass", also known as ["moment of inertia"](https://en.wikipedia.org/wiki/Moment_of_inertia). It's like mass, but in terms of rotation rather than position. The broom has a *low* angular mass along its length axis. It takes more *force* to affect a "heavier" axis than a lighter one which is why a broom spins more easily along its length.

This effect happens in Ragdoll too and is typically automatically computed for you based on the shape you use. If it looks like the broom, it will act like a broom.

With this release, you can now customise this for greater control of your rotations.

![ragdollangularmass](https://user-images.githubusercontent.com/2152766/99944815-6db10380-2d6b-11eb-9def-dba375a7e743.gif)

When would you want to do that?

1. Your shape looks like a broom, but you want it to act like a box
2. Your shape doesn't look like a broom, but you would like it to act like one

Or any combination in between. :) Generally, a broom or any thin shape is more easily spun along its length, so you may find **stability** in setting your angular mass to `(1.0, 1.0, 1.0)`, at the expense of realism.

**Guidelines**

- For realistic results, leave it at `-1` to automatically compute the angular mass
- For full control, override it
