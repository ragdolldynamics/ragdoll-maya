---
title: Marker
icon: "marker_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

### Animation Capture

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

Each "marker" is a dud. Nothing of any complexity. Something for the camera(s) to recognise and track as it moves through space. Once tracked, it's able to translate this marker from a 2D image into a 3D position, and continues to do so for each marker, for the real processing to take place inside software.

Once the capture is complete, the human actor can remove the markers and go enjoy the rest of their day. The rest is up to the computer.

With 3D positions generated, software takes over to translate these points into a hierarchy; the FK joint hierarchy you may be familiar with if you've ever worked with mocap. The joint hierarchy can then be used to either drive the final geometry, or to drive a more complex character rig which in turn drives the final geometry.

Animation Capture is just like that, but in **reverse**. Instead of capturing a person, it captures your *character rig*.

![image](https://user-images.githubusercontent.com/2152766/134128846-7c55bfe3-b2c6-418f-ab04-4e29f61a5ec2.png)

| # | Description
|-----:|:-----------
| **1** | Markers are attached to a character rig
| **2** | Markers are "captured"
| **3** | A rigid is generated for each marker
| **4** | A hierarchy of constraints is generated
| **5** | Simulation is **recorded** back onto the original character rig

Unlike motion capture, we'd like the result mapped back onto our character rig again, which is how animators iterate with physics.

<br>

#### Demo 1 - Basics

Ok, enough prelude, let's dive in.

**Before**

Here's what life was like before, with `Active Rigid`.

https://user-images.githubusercontent.com/2152766/134164228-cb35df45-ad68-4217-bb5f-8fa389a232da.mp4 controls

**After**

And here's life with `Markers`.

https://user-images.githubusercontent.com/2152766/134164221-d80135db-96b9-48ed-9ec0-1b8af73c8f86.mp4 controls

Notice how the channels are left alone?

This is the key difference between `Marker` and `Rigid`. Although you still provide Ragdoll with controls, Ragdoll no longer *drives* your controls directly. Instead, it *shows* you what they would look like *if* they were driven with physics.

Once you're happy with what you see, you `Record`.

https://user-images.githubusercontent.com/2152766/134164217-883c0635-6103-42da-87a1-0e9cd145aa1f.mp4 controls

<br>

#### Demo 2 - Ragdoll

Let's have a look at how `Markers` work with a full ragdoll.

**1. Setup hierarchy**

The first step is nothing new, you've seen it before.

https://user-images.githubusercontent.com/2152766/134213480-bcf2f185-f0f1-4ab5-9f5c-9a72f108e7d3.mp4 controls

**2. Edit shapes**

This too, it's second nature by now.

https://user-images.githubusercontent.com/2152766/134213470-fa51e083-cfb9-494d-8f1b-2fb795a7ed9d.mp4 controls

!!! info "Except!"
    Notice how the shapes overlap? That's ok! No longer will you have to worry about self-intersecting shapes. Unless you want it to, with the new `Self Collide` attribute. :D I'll touch on this a bit more below, under #self-collide

!!! hint "Double Except!"
    Release 4/4 in this series will deal with the channel box, and make editing these values interactive in the viewport for a superior experience and a lot less clicks and fiddling with numbers.

**3. Animate**

Now things are getting interesting. To keep our viewport clean, we can offset the simulation slightly. The offset is purely visual and won't affect the simulation or subsequent recording.

https://user-images.githubusercontent.com/2152766/134213467-b0b9bae6-6778-409d-ad1a-4277e89961f9.mp4 controls

**4. Record**

Finally, and this is what separates `Markers` from `Rigids`, we record our simulation back onto our controls.

https://user-images.githubusercontent.com/2152766/134213465-5739f9b5-a391-474d-b6ee-608a6e7c0194.mp4 controls

<br>

#### Demo 3 - Inverse Kinematics

That last example was contrived. No rig is without IK, so how does `Markers` work here?

**1. No IK**

Since we put markers on the FK controls, Ragdoll doesn't know about what the IK controls are doing.

https://user-images.githubusercontent.com/2152766/134312071-0eeb5ced-6bab-4793-9edd-6f5747ceb3ed.mp4 controls

**2. Reassign**

So let's put markers on the *joints* driven by both IK and FK, such that when you switch between the two, Ragdoll knows how to follow along. So let's `Reassign`.

https://user-images.githubusercontent.com/2152766/134312058-20f64011-954c-4d7b-b201-3950655449c0.mp4 controls

**3. Retarget**

But recording still targets our original FK controls, and what we want is to record our IK controls. So we can `Retarget`.

https://user-images.githubusercontent.com/2152766/134312048-5e9100d8-ce55-4fa1-b704-2201182733db.mp4 controls

**4. Record Translation**

Unlike FK, IK isn't just rotation, but translation too. So let's tell Ragdoll to record the translation from these markers too.

https://user-images.githubusercontent.com/2152766/134312041-fdaaad31-5273-44f4-891c-d1a80739de20.mp4 controls

And there you have it! This works with IK, SpineIK, Follicles, Geometry Constraints; *anything* you can throw at it.

<br>

#### Demo 4 - Real World Example

Here's a work-in-progress animation from [Christopher Page](https://www.linkedin.com/in/3dsketchbook/) (thanks for lending it to me!) Let's see how we can use Ragdoll to help improve upon it.

**1. The Problem**

Notice how the elbow intersects the table as he moves his torso around? A difficult problem and moving target as you need to keep tweaking both the torso and hand IK handle to tune your animation.

https://user-images.githubusercontent.com/2152766/134319921-6e96ef8c-1226-47b4-b3db-7f076047c62a.mp4 controls

**2. Isolate Timeline**

Since this animation is over 600 frames, we'll isolate our work to a small portion of it. For both performance and cleanliness; Ragdoll will only record onto the current timeline (or selected portion of it).

https://user-images.githubusercontent.com/2152766/134319912-57c3a8c6-3488-4129-9b1e-9567f77a0752.mp4 controls

**3. Assign Markers**

Like before, we'll assign markers to the underlying skeleton to respect what the IK solver does. We'll also make the hand `Kinematic` to respect the original animation exactly. The clavicle is also `Kinematic` per default, as it was the first assigned control - and is thus the "root" of our dynamic hierarchy.

https://user-images.githubusercontent.com/2152766/134319902-dc446cae-37c4-4c86-a746-2fd19364160c.mp4 controls

**4. Include Table**

Since we're interacting with the table, we'll include this too. Also `Kinematic`, no dynamics will be affecting it, and also as a `Box` shape to speed up and improve the stability of the simulation.

https://user-images.githubusercontent.com/2152766/134319896-0ddd0f5b-8e64-4f59-a93a-2fafc58b9994.mp4 controls

**5. Tune Shapes**

Next we'll isolate contacts with just the elbow area, to respect the hand and lower arm animation.

https://user-images.githubusercontent.com/2152766/134319889-6f7403cd-fec2-4fae-8b78-0efabf5afb04.mp4 controls

**6. Tune Material**

In this case, we'd like for the elbow to slide across the table, no friction.

??? info "More Realism?"
    In the real world, there would be friction and it could come in handy here too. But what should we expect from the elbow rubbing against the table? We should include the torso for this as well, which you absolutely can (and maybe should!). But to keep things simple, we'll let the clavicle preserve it's original animation exactly.

https://user-images.githubusercontent.com/2152766/134319878-d57ce899-bd03-4eb3-b97f-2e4dd5761f74.mp4 controls

**7. Retargeting**

Ragdoll will record onto the nodes you originally assign, but like before we want recording to go elsewhere; from joints to IK controls.

https://user-images.githubusercontent.com/2152766/134319871-2c804a4d-26b1-4a8f-932c-722aeb98189f.mp4 controls

**8. Record Translation**

Likewise, we'd also like translation included. And we don't care for the shoulder and clavicle animation; all we want is the IK handle and Pole Vector.

https://user-images.githubusercontent.com/2152766/134319865-dc88b9a9-bb8d-48df-9ec0-f3f5fe760903.mp4 controls

**9. Record Simulation**

We're all set! Let's hit `Record`!

https://user-images.githubusercontent.com/2152766/134319858-e82de1cc-4ed7-4dea-be07-8e59acc078af.mp4 controls

**10. Before And After**

And there we go! 2 minutes or less, and you've got a reusable setup for correcting the elbow whenever the animation changes. IK is intact and you can keep working with keyframes. Keeping Ragdoll attached to your rig has *zero* impact on performance (as you can see by looking at the fps counter near the bottom of the two comparisons), and once hidden it has no impact on your Outliner either. All clean!

https://user-images.githubusercontent.com/2152766/134319855-66c960d7-9d74-4bbf-bde4-5e813c7123cd.mp4 controls

Here's one more I couldn't find room for, an earlier version of the animation with *stepped keys* and finger simulation. Look at all that juicy finger interaction with the table. 😊

https://user-images.githubusercontent.com/2152766/134513003-7b25c2d1-87e8-4853-a89d-a73b3a5ba2e2.mp4 controls

> Rig and Model courtesy of Ramon Arango - [Apollo Rig](https://ramonarango.gumroad.com/l/ArtemisApolloRig)

<br>

#### Input Type

In the above examples, I mentioned `Kinematic` and you probably spotted a few other options too, like `Inherit` and `Pose Match`. What are those?

The `Input Type` is how Ragdoll should interpret the controls you assign. Did you mean for them remain animated, i.e. `Kinematic`? Or should they follow the control around, i.e. `Pose`? Or should they just fall with gravity, ignoring the original control altogether, i.e. `Off`?

The `Input Type` can be set either for a whole group of markers, or each marker individually.

| Type | Description
|:-----|:-----------
| Inherit  | Do whatever the group is doing, or `Kinematic` if there is no group
| Initial State  | Do nothing, just fall under gravity
| Kinematic | Follow the input *exactly*, physics need not apply
| Pose Match | Follow the input approximately, with some `Stiffness` and `Damping`

**Initial State**

Treat the input as a starting position, but nothing else.

https://user-images.githubusercontent.com/2152766/134478792-d7f4fc46-fea0-468a-9ec0-7737072263a1.mp4 controls

**Kinematic**

Follow the input exactly, no exceptions. Not even collisions.

https://user-images.githubusercontent.com/2152766/134478795-daa12066-c151-4fd5-a762-443b60a7fc45.mp4 controls

**Pose Match**

Follow the local angles of the input.

https://user-images.githubusercontent.com/2152766/134478800-e90f8928-b590-4b91-a314-bdcd9152cfef.mp4 controls

<br>

#### Pose Space

Now let's talk about a few things you *haven't* seen yet.

https://user-images.githubusercontent.com/2152766/134329974-7beb86d9-5660-44ba-b3f8-036ccc3aec28.mp4 controls

> Look, it's Ragdoll Blaine!

So what's happening here? Well, it *looks* like a [Soft Pin](/documentation/soft_pin/) to his head, along with a slight `Pose Strength` on the rest of his body. But unlike the `Rigid`, another significant advantage to `Markers` is their ability to capture both local *and worldspace* position and orientation of your controls. And because of this, you are able to interactively choose whether a marker should look at the *Worldspace* or *Localspace* position of your controls.

https://user-images.githubusercontent.com/2152766/134331199-c381ab43-4055-4e7a-a190-68d2acd0668f.mp4 controls

Notice how with a `Pose Space = -1` the controls arms remain relative the torso. And with `Pose Space = 1` they instead follow the *worldspace* orientation of the controls. Just like a Soft Pin.

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

In this example, every marker is part of the same group. The group has `Self Collide = Off`, which is fine for just about every marker *except the fingers*. In that case, we *do* want self-collision, so they are given the group `-1`.

https://user-images.githubusercontent.com/2152766/136033654-9e84313f-d2f8-4e97-a14f-600154dfd709.mp4 controls

<br>

#### Respect Self Collision

In this case, we're happy with a default group of `0` since we don't need anything to self collide. Especially these clavicles that overlap significantly!

https://user-images.githubusercontent.com/2152766/136034921-e9fd364b-9889-430c-8ab2-215ab5b998f1.mp4 controls

<br>

#### Surgical Control

Finally, for the very specific cases of wanting two or more markers to overlap. Notice how we give both the ground and 3 of the boxes an `Overlap Group = 5`.

https://user-images.githubusercontent.com/2152766/136040503-66728dee-d4f9-4411-bd08-9bf18043c334.mp4 controls
