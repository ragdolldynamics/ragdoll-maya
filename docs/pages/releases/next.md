---
hidden: true
title: Animation Capture pt. 1/4
description: Reverse motion capture, i.e. "Animation Capture" is introduced, for a superior animator-friendly workflow for physics!
---

Highlight for this release is **Animation Capture.**

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

This release introduces a new way of thinking about physics, and is part **1** out of **4**.

- [Skip Intro](#animation-capture)

| Release               | Date           | Description
|:----------------------|:---------------|:----------
| Workflow              | Today          | At least 100% faster, but primarily much easier to work with
| Render Performance    | <nobr>2 weeks later</nobr>  | The current bottleneck, expect a 50-100x boost
| Recording Performance   | <nobr>1 week later</nobr>   | Currently written in Python, to be written in optimised C++
| Interactive Tools     | <nobr>2 weeks later</nobr>   | No more fiddling with offsets in the channel box, viewport manipulators galore!

Something **amazing** has happened.

Since release only a few weeks ago, Ragdoll is now used in production across the globe in over a dozen countries at the most major of studios, several dozens of mid-sized studios wanting to gain an advantage and hundreds of independent animators and riggers alike.

And that is amazing, it is. But something even more amazing has happened and will be what this next 4-part release is all about.

See, since launch I've had conversations with animators using Ragdoll for the very first time. One of those animators made a request that at first glance doesn't look like much.

!!! quote "The request"
    "I don't like working with green channels, can I get rid of them?"

Here's what he was referring to.

https://user-images.githubusercontent.com/2152766/134045504-28e64cbb-cf4a-4d7c-8761-e8b05275d3ee.mp4

Notice how the nodes with physics applied got green channels? The reason they are green is because Ragdoll is driving them. They are green rather than yellow because you can still edit them, at the same time as Ragdoll is editing them. Your changes will be reflected in the simulation, this is how you *control* the simulation as it is running.

Can we get rid of that connection? Well.. No? This is Ragdoll's connection to your controls. Without those.. there *is* no physics.

I quickly dismissed the idea and carried on with my day. But then something *clicked*.. What if..?

https://user-images.githubusercontent.com/2152766/134046287-5b84322b-3da7-49d6-987e-67a463b33c56.mp4

In the next section, I'll dive into how this works and why this change goes far beyond just getting rid of green channels.

**Benefits at a glance**

- ✔️ 10,000% greater performance (or more!)
- ✔️ No more green channels
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

??? info "I'm a techy, give me the deets"
    The reason this works is because Ragdoll will consider the `.worldMatrix` attribute of any control and this is the same attribute Maya itself uses for just about anything.

<br>

### Animation Capture

Inspired by Motion Capture, *Animation Capture* is a new way to think about and work with physics in Maya.

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

Each "marker" is a dud. Nothing of any complexity. Something for the camera to recognise and track as it moves through space. Once tracked, it's able to translate this marker from a 2D image into a 3D position, and continues to do so for each marker, for the real processing to take place inside software.

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

Enough talk, let's dive in.

**Before**

Here's what life was like before, with `Active Rigid`.

https://user-images.githubusercontent.com/2152766/134164228-cb35df45-ad68-4217-bb5f-8fa389a232da.mp4 controls

**After**

And here's life with `Markers`.

https://user-images.githubusercontent.com/2152766/134164221-d80135db-96b9-48ed-9ec0-1b8af73c8f86.mp4 controls

Notice how the channels are left alone?

This is the key difference between `Marker` and `Rigid`. Although you still provide Ragdoll with controls, Ragdoll no longer *drives* your controls directly. Instead, it *shows* you what they would look like *if* they were driven with physics.

Once you're happy with what you see, you `Record` it.

https://user-images.githubusercontent.com/2152766/134164217-883c0635-6103-42da-87a1-0e9cd145aa1f.mp4 controls

Makes sense? Ok,let's look at a more interesting example.

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

Now things are getting interesting. To keep our viewport clean, we can offset the simulation slightly.

https://user-images.githubusercontent.com/2152766/134213467-b0b9bae6-6778-409d-ad1a-4277e89961f9.mp4 controls

**4. Record**

Finally, and this is what separates `Markers` from `Rigids`, we record our simulation back onto our controls.

https://user-images.githubusercontent.com/2152766/134213465-5739f9b5-a391-474d-b6ee-608a6e7c0194.mp4 controls

<br>

#### Demo 3 - Inverse Kinematics

That last example was contrived. No rig is without IK, so how does `Markers` work here?

<br>

#### Input Type

How should Ragdoll interpret the original controls?

| Type | Description
|:-----|:-----------
| Inherit  | Do whatever the group is doing, or `Kinematic` if there is no group
| Off  | Do nothing, just fall under gravity
| Kinematic | Follow the input *exactly*, physics need not apply
| Guide | Follow the input approximately, with some `Stiffness` and `Damping`

<br>

#### Recording

Markers can be recorded all together, or independently. For example, say you wanted animation from frame 1-100, simulate 101-150 and return to animation from 151-200. You can do that.

Furthermore, say you liked what the simulation was doing, but only on one half of the body. Or only on the hip, driving the main trajectory in a physically-plausible way. Keeping the rest of your animation intact.

<br>

#### Transitions

Let's have a look at how you would use markers to transition between simulation and animation.

<br>

#### Retargeting

Per default, markers are recorded onto the controls they read from.

![image](https://user-images.githubusercontent.com/2152766/134169658-39590bbf-bbca-41dc-af3b-de20e69e9aed.png)

But sometimes, rigs are more complicated and

![image](https://user-images.githubusercontent.com/2152766/134169635-e0a751c8-f06b-4dac-a459-50118d04821f.png)

**Workflow**

- Marker Input    (e.g. joint1)
- Marker Output   (e.g. spine_ctl)

You can change the `Input` to a marker by using `Reassign`, and change the `Output` with `Retarget`.

**Limitations**

These are some of the things we'll be working on for subsequent releases.

- Selecting rigids interacively
- Manipulating shapes interactively
- Manipulating constraints interactively
- Toggle between previous animation and recorded simulation
- No live-link
- Cannot be exported
- Cannot be add constraints

<br>

### Performance Leap

200% performance. Wait, did I say percent? I meant **times** - 200x performance, or 20,000% whichever one you fancy. :D

- 200x greater performance
- 5x simpler workflow
- 2x more fun

Yes, you read that right. **200x** performance increase, and that's conservative. Actual numbers were `65.0 ms` turning into `0.31 ms`. Those are the numbers we want. Along with these nuggets.

- No more overlapping shapes
- No more green channels
- No more graph editor mess
- No more initial state
- No more cycles
- No more cluttering of the Outliner
- No more cluttering the viewport (offset render)
- No more out-of-sync scale

**Caveats**

1. Selecting any rigid selects all rigids, they are drawn as one
2. A hidden solver will not simulate, drawing triggers simulation

<br>

### Enhanced Determinism

!!! info "TLDR"
    Sometimes, re-opening the scene could lead to different results. This has now been fixed.

Each time you play a simulation starting from the beginning, the results are the same. This is an important characteristic of any simulation and is called "determinism". It used to be the case however that when you re-opened the scene, there was a small chance the results would differ from when you last saved it.

This has now been fixed. The determinism is now dependent on the order in which rigid bodies connect to the `rdScene` node. It's an array attribute, whose order is saved with the Maya scene.

<br>

### Dynamic Constraints

Constraints now have *presets*, which dynamically update based on wherever your creation is.

<br>

### Dynamic Time



<br>

### Damping Ratio

Constraints have 3 attributes to control their behavior.

- `Stiffness`
- `Damping`
- `Strength`

Where `Stiffness` and `Damping` are both multiplied by `Strength * Strength`. For example, the final value of `Stiffness` is..

```py
final_stiffness = stiffness * strength * strength
```

And that's great; it means you can animate just a single attribute in favour of two. Editing the relationship between the two attributes was done by changing either `Stiffness` or `Damping`.

The new `rdMarker` node have a `dampingRatio`.. Well, no. FIX

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