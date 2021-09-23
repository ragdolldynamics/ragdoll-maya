---
hidden: true
title: Animation Capture pt. 1/4
description: Reverse motion capture, i.e. "Animation Capture" is introduced, for a superior animator-friendly workflow for physics!
---

Highlight for this release is **Animation Capture**.

- [**ADDED** Animation Capture](#animation-capture) A.k.a. Reverse Motion Capture
- [**ADDED** Groups](#capture-suit) Centralised character controls
- [**ADDED** Self-Collision](#self-collision) Overlapping shapes, begone
- [**ADDED** Collision Groups](#collision-groups) Fine control over what collides with what
- [**ADDED** Offset Simulation](#offset-simulation) Visually separate between input and output
- [**ADDED** Damping Ratio](#damping-ratio) One less attribute to worry about
- [**ADDED** Keyable Status](#keyable-status) Which one is keyable, which is not?
- [**IMPROVED** Enhanced Determinism](#enhanced-determinism) 
- [**FIXED** Multiple Floating Licences](#multiple-floating-licences) Now behaves as one would expect

<br>

### Introduction

Lighter, *faster*, **stronger**. This release introduces a new way of thinking about physics, and is part **1/4**.

- [Skip Intro](#animation-capture)

|#| Release               | Date           | Description
|:|:----------------------|:---------------|:----------
|1| Workflow              | Today          | At least 100% faster, but primarily much easier to work with
|2| Render Performance    | <nobr>2 weeks later</nobr>  | The current bottleneck, expect a 50-100x boost
|3| Recording Performance   | <nobr>1 week later</nobr>   | Currently written in Python, to be written in optimised C++
|4| Interactive Tools     | <nobr>2 weeks later</nobr>   | No more fiddling with offsets in the channel box, viewport manipulators galore!

Something **amazing** has happened.

![image](https://user-images.githubusercontent.com/2152766/134300628-565e7da1-c669-47ef-9fe2-f3b2023de875.png)

Since release only a few weeks ago, Ragdoll is now used in production across the globe in over a dozen countries at the most major of studios, several dozens of mid-sized studios wanting to gain an advantage and hundreds of independent animators and riggers alike.

And that is amazing, it is. But something even more amazing has happened; Ragdoll has **leaped forward**. And that will be what the next 4-part release is about.

See, since launch I've had conversations with animators using Ragdoll for the very first time. One of those animators made a request that at first glance didn't look like much.

!!! quote
    "I don't like working with green channels, as it is not ideal for animating. Is there a way to I can overcome this?" - [Christopher Page](https://www.linkedin.com/in/3dsketchbook/)

Here's what he was referring to.

https://user-images.githubusercontent.com/2152766/134045504-28e64cbb-cf4a-4d7c-8761-e8b05275d3ee.mp4 controls

Notice how the nodes with physics applied got green channels? The reason they are green is because Ragdoll is driving them. They are green rather than yellow because you can still edit them, at the same time as Ragdoll is editing them. Your changes will be reflected in the simulation, this is how you *control* the simulation as it is running.

Can we get rid of that connection? Well.. No? This is Ragdoll's connection to your controls. Without those.. there *is* no physics.

I quickly dismissed the idea and carried on with my day.. But then something *clicked*.. What if..?

https://user-images.githubusercontent.com/2152766/134046287-5b84322b-3da7-49d6-987e-67a463b33c56.mp4 controls

In the next section, I'll dive into how this works and why this change goes far beyond just getting rid of green channels.

**Benefits at a glance**

- ✔️ 10,000% greater performance (or more!)
- ✔️ No more graph editor mess
- ✔️ No more initial state
- ✔️ No more cycles
- ✔️ No more clutter in the Outliner
- ✔️ No more clutter in the Viewport
- ✔️ Support for interactive scale
- ✔️ Support for overlapping shapes
- ✔️ Support for IK/FK
- ✔️ Support for space switching
- ✔️ Support for follicles
- ✔️ Support for native Maya constraints
- ✔️ Support for ...

From here, this list has no end, because *anything* capable of affecting the worldspace position and orientation of your controls is natively supported with this workflow. *Anything*.

??? info "I'm a techy, gimme the deets"
    The reason this works is because Ragdoll will consider the `.worldMatrix` attribute of any control and this is the same attribute Maya itself uses for just about anything.

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

Here's an animation whereby the elbow should be resting on the table, but intersects it slightly as the torso moves about. Let's see how Ragdoll can sort this out.

**1. The Problem**

This animation looks great (thanks [Christopher Page](https://www.linkedin.com/in/3dsketchbook/) for lending it to me!) but has a problem with the elbow. Notice how it intersects the table as he moves his torso around? A difficult problem and moving target as you need to keep tweaking both the torso and hand IK handle to tune your animation.

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

> Rig and Model courtesy of Ramon Arango - [Apollo Rig](https://ramonarango.gumroad.com/l/ArtemisApolloRig)

<br>

#### Recording

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

**Intelligent Range**

A `Kinematic` marker is entirely animated, so there's no need to actually record those. Ragdoll will ensure only non-kinematic frames are recorded, so you can do things like this.

https://user-images.githubusercontent.com/2152766/134504192-3514f235-1f9c-4ce8-83e5-6704bf3036df.mp4 controls

<br>

#### Input Type

In the above examples, I mentioned `Kinematic` and you probably spotted a few other options too, like `Inherit` and `Guide`. What are those?

The `Input Type` is how Ragdoll should interpret the controls you assign. Did you mean for them remain animated, i.e. `Kinematic`? Or should they follow the control around, i.e. `Guide`? Or should they just fall with gravity, ignoring the original control altogether, i.e. `Off`?

The `Input Type` can be set either for a whole group of markers, or each marker individually.

| Type | Description
|:-----|:-----------
| Inherit  | Do whatever the group is doing, or `Kinematic` if there is no group
| Off  | Do nothing, just fall under gravity
| Kinematic | Follow the input *exactly*, physics need not apply
| Guide | Follow the input approximately, with some `Stiffness` and `Damping`

**Off**

Treat the input as a starting position, but nothing else.

https://user-images.githubusercontent.com/2152766/134478792-d7f4fc46-fea0-468a-9ec0-7737072263a1.mp4 controls

**Kinematic**

Follow the input exactly, no exceptions. Not even collisions.

https://user-images.githubusercontent.com/2152766/134478795-daa12066-c151-4fd5-a762-443b60a7fc45.mp4 controls

**Guide Balance -1**

Follow the relative angles between controls in the input.

https://user-images.githubusercontent.com/2152766/134478800-e90f8928-b590-4b91-a314-bdcd9152cfef.mp4 controls

**Guide Balance +1**

Follow the absolute position and orientation of the input.

https://user-images.githubusercontent.com/2152766/134478803-889e6732-4e7b-433e-803d-d3edfed814a1.mp4 controls

<br>

#### Retarget

We've talked a lot about "retargeting". But what *is* that?

Per default, markers are recorded onto the controls you assigned, this is called `Rig to Rig`.

![image](https://user-images.githubusercontent.com/2152766/134169658-39590bbf-bbca-41dc-af3b-de20e69e9aed.png)

But often times, rigs are more complicated and what you want is for the simulation to look at one set of nodes, but record onto another. This is called `Joint to Rig`, but can be from any source. Even other controls (like FK to IK).

![image](https://user-images.githubusercontent.com/2152766/134169635-e0a751c8-f06b-4dac-a459-50118d04821f.png)

!!! info "The Old Days"
    Think about how you would accomplish this using the `Active Rigid` or `Active Chain` commands. That would be a *huge* pain, but not with markers!

<br>

#### Reassign

Over in [Demo 2 - Ragdoll](#demo-2---ragdoll) we "reassigned" already marked controls. What does that mean?

In that example, we've assigned our FK controls directly, which means Ragdoll would grab the translation and rotation from those controls during simulation. But what we really wanted was the IK controls.

But! We couldn't just assign to the IK controls directly, since they are *indirectly* rotating a characters limbs. So instead, we `Reassign` the markers previously made onto the underlying joints that follow IK around.

We then also `Retarget` them, since they would have otherwise been recorded onto the original FK controls.

<br>

#### Reparent

Sometimes, you change your mind.

https://user-images.githubusercontent.com/2152766/134465284-f9a3bd04-9392-4f33-a161-390cbe9049d2.mp4 controls

Success!

https://user-images.githubusercontent.com/2152766/134465285-87eacea9-4b93-4526-980e-585bbc92151b.mp4 controls

<br>

#### Guide Balance

Now let's talk about a few things you *haven't* seen yet.

https://user-images.githubusercontent.com/2152766/134329974-7beb86d9-5660-44ba-b3f8-036ccc3aec28.mp4 controls

> Look, it's Ragdoll Blaine!

So what's happening here? Well, it *looks* like a [Soft Pin](/documentation/soft_pin/) to his head, along with a slight `Guide Strength` on the rest of his body. But unlike the `Rigid`, another significant advantage to `Markers` is their ability to capture both local *and worldspace* position and orientation of your controls. And because of this, you are able to interactively choose whether a marker should look at the *Worldspace* or *Localspace* position of your controls.

https://user-images.githubusercontent.com/2152766/134331199-c381ab43-4055-4e7a-a190-68d2acd0668f.mp4 controls

Notice how with a `Guide Balance = -1` the controls arms remain relative the torso. And with `Guide Balance = 1` they instead follow the *worldspace* orientation of the controls. Just like a Soft Pin.

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

### Transitions

Let's have a look at how you would use markers to transition between simulation and animation.

https://user-images.githubusercontent.com/2152766/134507548-382a0ccd-85b6-4990-b325-16dbd3b7d568.mp4 controls

Notice how we're animated up until the jump, and then Ragdoll takes over. Once he approaches that box, we turn our `Guide Balance` from `-1` to `1` and have him reach the target pose in worldspace. Once he's close, we switch `Input Type` to `Kinematic` and kinematically move him until we once again transition to `Guide`, this time with a `Guide Balance` or `-1` for pose space.

https://user-images.githubusercontent.com/2152766/134507546-49e84d32-b50a-48c6-a1b9-82410281a884.mp4 controls

<br>

### Self Collision

Previously, it was very important that your shapes did not overlap any shape other than it's immediate neighbour. If they did, chaos ensued.

**Before**

Clavicles intersect their parent spine, but also each other!

https://user-images.githubusercontent.com/2152766/134362062-4197b3d6-2694-4011-9a8e-69adec92927f.mp4 controls

**After**

With the new `Self Collision = Off`, this is no longer a problem.

https://user-images.githubusercontent.com/2152766/134362067-a2d33df3-c9d1-4aa8-b8af-956d80aeba7e.mp4 controls

This can be taken into the extreme!

https://user-images.githubusercontent.com/2152766/134362070-325aa8dc-3367-4765-a4a9-56670cc77b83.mp4 controls

And here's a another example to fill out a large volume in the center of a character.

https://user-images.githubusercontent.com/2152766/134368633-ed4f69f4-1eba-4702-a3f6-bdddd2f0a98d.mp4 controls

!!! info "Attention"
    Notice how the spine is made up of many shapes, some of which cover the width of the body, others the depth. An overlapping mess that would never have simply not have been possible without self-collision support!

https://user-images.githubusercontent.com/2152766/134368636-37cfd588-184e-46e9-b03a-6d8cacb80b76.mp4 controls

> Original asset created by Mehmet Tayfur Türkmenoğluwe and Dr. Reel, licensed by The Rookies.

<br>

### No Graph Editor Mess

Because `Rigids` were children of your controls, Maya had a funny way of including them in the Graph Editor that rightly drove animators, myself included, *absolutely mad*.

**Before**

Just look at this; why-oh-why would I want channels from a completely unrelated node when working with the hip?

https://user-images.githubusercontent.com/2152766/134341270-72843d85-70c9-43af-86cc-c981e87fe297.mp4 controls

**After**

Contrast that to this, whereby only the nodes you actually select are made visible. You can even select `Markers` via the Channel Box and *deselect* your controls to get up real close.

https://user-images.githubusercontent.com/2152766/134341497-cb64e666-75e6-4bfd-a3bd-aee27a61791b.mp4 controls

<br>

### No Initial State

A significant effort was made to make the simulation start where you expected it to.

Under the hood, simulation and animation were at odds with one another. Ragdoll needed to know where to start, but it was also telling your controls where to start. It's an inherent cycle, which was finally broken.

!!! info "Read More"
    You can read all about the month-long journey in the [release notes from March](/releases/2021.03.01/)

Nowadays, you barely have to think about it, but it does occasionally rear its ugly head. It is a hack.

With `Markers` there isn't any cycle to begin with. Ragdoll only reads from your controls, it doesn't write to anything. Under the hood, recording is a 2-step process; first it simulates, and then it writes animation back onto the controls. That's how this cycle is broken, without having any effect on the overall workflow.

<br>

### No More Cycles

With the previous version, because `Rigids` both read and wrote to each control, you could sometimes run into a situation where the parent depends on a child.

**Before**

Here, I'll try and make a second chain in the opposite direction of how the controls are laid out hierarchically. This cannot work; because in order for Ragdoll to figure out where the Passive hand should be, it would first need to consult the upper arm, which is both dynamic and a child of the spine, which is also dynamic. It's a lovely cycle. ❤️

https://user-images.githubusercontent.com/2152766/134480453-279620c2-0a68-48fc-aad4-5c24c146265d.mp4 controls

**After**

With `Markers`, this isn't a problem because to Ragdoll every limb can now be independently evaluated, in parallel.

https://user-images.githubusercontent.com/2152766/134480451-f9be80ba-2579-485e-a4e4-ad92d0da4491.mp4 controls

<br>

### Damping Ratio

The current `rdConstraint` nodes have 3 attributes to control their behavior.

- `Stiffness`
- `Damping`
- `Strength`

Where `Stiffness` and `Damping` are both multiplied by `Strength * Strength`. For example, the final value of `Stiffness` is..

```py
final_stiffness = stiffness * strength * strength
```

And that's great; it means you can animate just a single attribute in favour of two. Editing the ratio between the two attributes was done by changing either `Stiffness` or `Damping`.

The `Marker` nodes gets rid of `Strength` and instead adds an explicit `Damping Ratio` attribute to control this ratio.

Stiffness and damping is also multiplied by their associated Group and Solver.

```py
final_stiffness = maker.stiffness * group.stiffness * solver.stiffness
```

Meaning you can control either all or one marker at a time with ease.

<br>

### Quality of Life

Some minor things to brighten your day.

<br>

#### Real Ground

With `Rigids`, the ground was embedded into the scene. With `Markers`, an actual ground is created to for more stability and more control over its physical parameters. Something that can also be animated, and that dynamically appears right underneath your markers.

https://user-images.githubusercontent.com/2152766/134493174-f57cc5ce-5056-4cfa-b98e-fae9114342fc.mp4 controls

<br>

#### Joints and the Attribute Editor

The Attribute Editor doesn't show you `Rigids` related to Maya joints because of a Maya UI quirk.

With `Markers`, this is no longer a problem!

![image](https://user-images.githubusercontent.com/2152766/134464806-041e6abb-4be0-442f-b51d-d4a9776fd88b.png)

<br>

#### Hidden Solver

Hiding the solver completely removes all overhead of having Ragdoll in your scene. Previously, with `rdScene` and `rdRigid`, because they were directly connected to your controls, hiding things made little difference. But now, because we no longer have this direct connection, all computations come from explicitly seeing the `rdSolver` node.

No visible `rdSolver` node, no computations. Period.

<br>

#### Enhanced Determinism

!!! info "TLDR"
    Sometimes, re-opening the scene could lead to different results. This has now been fixed.

Each time you play a simulation starting from the beginning, the results are the same. This is an important characteristic of any simulation and is called "determinism". It used to be the case however that when you re-opened the scene, there was a small chance the results would differ from when you last saved it.

This has now been fixed. The determinism is now dependent on the order in which rigid bodies connect to the `rdSolver` node. It's an array attribute, whose order is saved with the Maya scene.

<br>

### Multiple Floating Licences

Whenever a machine connected to your floating licence server, the host and IP were stored on the machine in an effort to speed up subsequent connections made. However, this also meant that you weren't able to *update* those details.

Despite providing new details, Ragdoll would favour the already-stored details. Worse yet, the Ragdoll UI would *lie* to you, by repeating the connection details provided in the `RAGDOLL_FLOATING` environment variable, despite those not actually being used.

This release addresses this by always using the details you provide, and not bother reusing any previously provided details. In addition, you now have the option to explicitly query and set server details directly.

```py
# Will query the *actual* server used by Ragdoll, rather
# than return the environment variable you provided
cmds.ragdollLicence(getServer=True)

# Will manipulate the currently-in-use key, meaning it will
# try and drop a licence from this address as well
cmds.ragdollLicence(setServer=("localhost", 1313))
```

<br>

### Next Release

This release is part 1/4, for next 2/4 release you can expect *Performance Improvements*.

In this release, simulation and overall Maya scenegraph performance has seen a 200x performance boost, the performance is already there. You'll notice it as you try them on your rigs.

However, *rendering* performance has dropped significantly, cancelling out *most* of that performance gain. Here's what performance looks like now.

![image](https://user-images.githubusercontent.com/2152766/134397400-44ed30ce-b5c2-4cf7-9a24-2783a685b082.png)

Rendering mostly Maya default shading, rendeing its own things. Unrelated to Ragdoll. The Rig Evaluation on the other hand is almost entirely Ragdoll. It's connected to every control in this rig, forcing each control to be evaluated in serial; one after the other.

Here's what it looks like with `Markers`.

![image](https://user-images.githubusercontent.com/2152766/134399139-cbe27611-3445-4453-b901-fbe1687dd299.png)

Notice the huge pile of lines to the left? Those are all running parallel and almost entirely default Maya evaluations; things your rig would do without Ragdoll. Rendering on the other hand is almost entirely Ragdoll, it is *very* slow.

To properly compare performance between `Rigids` and `Markers`, here's what you should be looking at.

https://user-images.githubusercontent.com/2152766/134398643-bf2e3086-a8f6-4ea7-8e58-011c866acaaa.mp4 controls

This is the only thing Ragdoll does to your rig. This is the entire overhead, the added load onto your rig. 16 *microseconds*. That's `0.016 ms`. For a rig to run at 30 fps, it'll need `1,000/30 = 33 ms` per frame. This overhead, `0.016 ms/frame` is all Ragdoll needs to solve an entire character, contacts and constraints and forces, all of it. In this particular profiling, that's 430x faster than `Rigids`, which not only took longer to solve but made everything else slower by just being connected to your controls.

So how about we get this rendering performance sorted, shall we?

<br>

### Limitations

These are some of the things lacking from `Markers` in this release that we'll be working on for subsequent releases.

- Selecting rigids interacively
- Manipulating shapes interactively
- Manipulating constraints interactively
- Toggle between previous animation and recorded simulation
- Support for recording onto an animation layer
- No "live-mode", where physics drives a control interactively
- Markers cannot be exported
- Markers cannot have additional constraints
