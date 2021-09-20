---
hidden: true
title: Animation Capture
description: Virtual motion capture, i.e. "Animation Capture" introduced, for a superior animator-friendly workflow for physics!
---

Highlight for this release is **Animation Capture.**

- [**ADDED** Animation Capture](#animation-capture) A.k.a. Virtual Motion Capture
- [**ADDED** Self Collision](#self-collision) Overlapping shapes, begone
- [**ADDED** Capture Suit](#capture-suit) Centralised character controls
- [**ADDED** Damping Ratio](#damping-ratio) One less attribute to worry about
- [**ADDED** Keyable Status](#keyable-status) Which one is keyable, which is not?
- [**FIXED** Multiple Floating Licences](#multiple-floating-licences) Now behaves as one would expect
- [**IMPROVED** Enhanced Determinism](#enhanced-determinism) 

<br>

### Overview

This release introduces a new way of thinking about physics, and is part **1** out of **4**.

| Release               | Date           | Description
|:----------------------|:---------------|:----------
| Workflow              | Today          | At least 100% faster, but primarily much easier to work with
| Render Performance    | <nobr>2 weeks later</nobr>  | The current bottleneck, expect a 50-100x boost
| Recording Performance   | <nobr>1 week later</nobr>   | Currently written in Python, to be written in optimised C++
| Interactive Tools     | <nobr>2 weeks later</nobr>   | No more fiddling with offsets in the channel box, viewport manipulators galore!

Something **amazing** has happened.

Since release only a few weeks ago, Ragdoll is now used in production across the globe in over a dozen countries at the most major of studios, several dozens of mid-sized studios wanting to gain an advantage and hundreds of independent animators and riggers alike.

And that is amazing, it is. But there something even more amazing has happened and will be what this next 4-part release is all about.

See, since launch I've had conversations with animators using Ragdoll for the very first time. One of those animators made a request that at first glance doesn't look like much.

!!! quote "The request"
    "I don't like working with green channels, can I get rid of them?"

Here's what he was referring to.

https://user-images.githubusercontent.com/2152766/134045504-28e64cbb-cf4a-4d7c-8761-e8b05275d3ee.mp4

Notice how the nodes with physics applied got green channels? The reason the are green is because Ragdoll is driving them. They are green rather than yellow because you can still edit them, at the same time as Ragdoll is editing them. Your changes will be reflected in the simulation, this is how you *control* the simulation as it is running.

Can we get rid of that connection? Well.. No? This is Ragdoll's connection to your controls. Without those.. there *is* no physics.

I quickly dismissed the idea and carried on with my day. But then something *clicked*.. What if..?

https://user-images.githubusercontent.com/2152766/134046287-5b84322b-3da7-49d6-987e-67a463b33c56.mp4

In the next section, I'll dive into how this works and why this change goes far beyond just getting rid of green channels.

**Benefits at a glance**

- 10,000% greater performance
- No more overlapping shapes
- No more green channels
- No more graph editor mess
- No more initial state
- No more cycles
- No more clutter in the Outliner
- No more clutter in the Viewport
- No more out-of-sync scale
- Support for IK/FK
- Support for space switching
- Support for follicles
- Support for native Maya constraints
- Support for ...

From here, this list has no end, because *anything* capable of affecting the worldspace position and orientation of your controls is natively supported with this workflow.

!!! info "Technically Speaking"
    The reason this works is because Ragdoll will consider the `.worldMatrix` attribute of any control and this is the same attribute Maya itself uses for just about anything.

<br>

### Animation Capture

Inspired by Motion Capture, *Animation Capture* is a new way to think about and work with physics in Maya.

![image](https://user-images.githubusercontent.com/2152766/134006344-53f2744f-cc7f-48b0-860d-d0313a353c1f.png)

Here is a typical data pipeline for motion capture, from real-life actor to final character animation.

1. An actor performs with "markers" attached
2. Markers are "captured"
3. A pointcloud is generated
4. A hierarchy of joints is generated
5. Joints drive a typical character rig
6. Character rig drives final geometry for render

Each "marker" is nothing more than a point. Something for the camera to recognise and track as it moves through space. Once tracked, it's able to translate this marker from a 2D image into a 3D position, and continues to do so for each marker.

Once the capture is complete, the human actor can remove the markers and go enjoy the rest of his day. The rest is up to the computer.

With 3D positions generated, software takes over to translate these points into a hierarchy; the FK joint hierarchy you may be familiar with if you've ever worked with mocap. The joint hierarchy can then be used to either drive the final geometry, or to drive a more complex character rig which in turn drives the final geometry.

*Animation* capture is just like that, but instead of capturing a real-life person, it captures your *character rig*.

![image](https://user-images.githubusercontent.com/2152766/134010238-8f72c573-9ff9-471f-9d46-b6bbd6aa8119.png)

1. A character rig is animated with "markers" attached
2. Markers are "captured"
3. A rigid is generated for each marker
4. Each rigid is connected to form a hierarchy
5. Simulation is **recorded** back onto the original character rig

Unlike motion capture, we'd like the result mapped back onto our character rig again, which is how animators iterate with physics.

!!! info "In other words"
    Markers are to motion and animation capture what the "red pill" is to Neo. A way for their tracking software to identify which of the many humans in a busy farm of humans is Neo.

    ![image](https://user-images.githubusercontent.com/2152766/134011228-49c878c7-928b-48b1-9cbc-2fcf70f8ec01.png)

<br>

#### Demonstration



Conversely, the current workflow of Ragdoll is for you to give control over the limbs of your character to Ragdoll, for it to output its simulation onto them. You can then create a secondary control hierarchy - a Mimic - in order to regain control over it. But this was tedious and error prone.

*Animation Capture* on the other hand borrows from Motion Capture, in that you now attach "markers" onto your character rig such that Ragdoll can monitor and simulate them.

**Workflow**

- Marker Input    (e.g. joint1)
- Marker Output   (e.g. spine_ctl)

You can change the `Input` to a marker by using `Reassign`, and change the `Output` with `Retarget`.

**Missing in Action**

- Selecting rigids interacively
- Manipulating shapes interactively
- Manipulating constraints interactively
- Toggle between previous animation and recorded simulation
- No live-link

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