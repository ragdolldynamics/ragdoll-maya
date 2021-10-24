---
hidden: true
title: Animation Capture pt. 3/4
description: Linking and Caching
---

<video autoplay="" class="poster" muted="" loop="" controls="" height="30%" width="100%"><source src="https://user-images.githubusercontent.com/2152766/138547703-7b6ba449-1b8b-43c9-9728-7d309e0d8db8.mp4" type="video/mp4"></video>

Highlight for this release is **Linking and Caching**, and is part 3 out of 4 of the new [Markers](/releases/2021.09.27/).

- [**ADDED** Solver Linking](#solver-linking) Run two or more solvers together as one
- [**ADDED** Solver Caching](#solver-caching) Run once and update on-demand
- [**ADDED** Marker Limits](#marker-limits) On par with the previous constraints, but much easier to work with
- [**ADDED** Marker Constraints](#marker-constraints) Including Soft Pin!
- [**ADDED** Recording Performance](#recording-performance) A bit faster recording

### Showcase

Let's start these notes with some examples of what you can do with all of the new features added. 🥰

**Best Friends, No Matter What**

Two referenced characters, their solvers linked.

https://user-images.githubusercontent.com/2152766/137677733-af55a032-aabe-49e4-af6f-253086b68be3.mp4 controls

**Hang On!**

The new `Distance Constraint` at work.

https://user-images.githubusercontent.com/2152766/138250857-27c10b93-4fc4-4b96-bb55-ba31407cf57b.mp4 controls

**Dance Baby!**

An example of the new Pin Constraint for Markers, working alongside a the Distance Constraint and regular old pose matching.

https://user-images.githubusercontent.com/2152766/138433045-cd14d52c-a54e-4703-a858-42f702c5f5b4.mp4 controls

<br>

### Manikin Rig

Updated with *limits* from this release.

As before, this guy can either be opened or referenced into your scene. See [Solver Linking](#solver-linking) for how you can reference *multiple* characters into the same simulation.

<div class="hboxlayout">
<a href="https://files.ragdolldynamics.com/api/public/dl/4Lok2bRj/manikin_v002.zip" class="button red"><b>Download Manikin</b></a>
</div>

![image](https://user-images.githubusercontent.com/2152766/138433444-101076cf-566a-4b2a-ac8f-a319f8ddc1d2.png)

<br>

### Tutorials

Markers have part 4 out of 4 remaining, for a next-generation UI, before being considered feature complete. But until then here's how you can get started with Markers today.

So far, the parts missing functionally from Rigids are:

- Forces
- Export/Import

Both of which will be handled in either the next release or the release following. Forces are getting an overhaul too, of integrating with the native Maya forces such that you can simulate nHair and nCloth alongside Ragdoll, using the same forces (called "fields" in Maya) like turbulence and wind.

|   | Tutorial | Duration | Description
|:--|:--------|:-----------
|   | [Overlapping Motion I]()  | 02:27 | The very basics or Capture and Record
|   | [Overlapping Motion II]() | 02:21 | Animation layers
|   | [Full Ragdoll I]()        | 04:08 | Hierarchy and volume
|   | [Full Ragdoll II]()       | 04:05 | Kinematic and animation
|   | [Full Ragdoll III]()      | 04:30 | Self collisions and recording
|   | [IK I]()                  | 02:30 |
|   | [IK II]()                 | 02:30 |
|   | [Elbow Intersection]()    | 02:30 | Chris's example
|   | [Replace Reference]()     | 02:30 |
|   | [FK/IK/Physics]()         | 02:30 |

<br>

### Solver Linking

Reference two characters, link their solvers.

![image](https://user-images.githubusercontent.com/2152766/138452628-3cf97eb1-876f-43f5-8d1c-1a3dbd0eaecb.png)

Until now, you've been able to author physics using `Active Chain` and combine scenes using the `Combine Scene` menu item. That would transfer all connected rigids from one scene to another.

But, that feature is *destructive*. There's no way to "uncombine" and even if you could, there's no record of what was originally combined.

Let me introduce `Solver Linking`, a lightweight and non-destructive alternative.

**Linking**

This fellow is referenced twice, and get their solvers linked together.

https://user-images.githubusercontent.com/2152766/137937277-daef1729-64e0-4abb-a6a3-add67b72b848.mp4 controls

**Unlinking**

Unlinking restores their previous behavior exactly.

https://user-images.githubusercontent.com/2152766/137937281-7f71cacf-f591-494b-bbdc-14365b631000.mp4 controls

!!! question "That's neat, but can you.."
    I know exactly what you're thinking, I was thinking the same thing.

    Can you link a solver to another solver that is also linked? So that I can build a *network* of simple solvers that all work together to form one *complex* solver?

    Yes. Yes, you can. 🤭 See below.

<br>

#### Example

Here are 2 assets, a manikin and a backpack.

| Manikin | Backback
|:---------|:--------
| ![image](https://user-images.githubusercontent.com/2152766/138450294-4582e087-0472-436c-97cc-cf99dffb9fa2.png) | ![image](https://user-images.githubusercontent.com/2152766/138450174-10295b96-3527-4b1f-9904-d58994fbb064.png)

The backback and manikin has been combined into one, which is then referenced twice into the final scene for a total of 4 unique solvers.

**Non-destructively link solvers**

Notice the *hierarchy* of solvers formed here, enabling you to build complex solvers out of many small solvers.

https://user-images.githubusercontent.com/2152766/137920028-d0be982a-b6a1-45c3-a2fe-19ebd0e46632.mp4 controls

**Non-destructively unlinking too**

Likewise, safely deconstruct a network of solvers by just removing the connection.

https://user-images.githubusercontent.com/2152766/137920132-0c78d52e-40f7-4c9e-9207-9c5cb2c2c698.mp4 controls

Technically, a solver is added to another solver in the same manner a marker, group and constraint is added. One big happy family.

![image](https://user-images.githubusercontent.com/2152766/137920872-903e370a-617e-4109-9f0a-0408a30c5c19.png)

<br>

### Solver Caching

![image](https://user-images.githubusercontent.com/2152766/138453070-02e69094-6c37-469c-8bb1-7348ba9f42ac.png)

Ragdoll runs alongside your character animation, but sometimes it can be useful to keep the results from a previous run and stop being so interactive.

Meet `Cache` and `Uncache`.

https://user-images.githubusercontent.com/2152766/137889320-1f20ecd3-a6e7-4529-8e82-d04230f8646c.mp4 controls

Caching is entirely non-destructive, and in fact leverages the very same cache you've been enjoying all this time whenever rewinding.

The menu commands toggle an attribute on your solver node, called `.cache` and automatically plays the entire timeline for you. But the same result can be achieved by setting the attribute and playing it yourself.

https://user-images.githubusercontent.com/2152766/137889717-dac3ed54-6105-4742-a312-a79aa1bba945.mp4 controls

The minimal HUD will show you what's been cached, and like before once you resume playback from a cached to an uncached frame, Ragdoll will continue filling up the cache as one would expect.

Look forward to a future release where caching happens in the background, as you work. Something that can also be handy from time to time (pun!).

<br>

#### Limitations

The viewport HUD currently draws relative the solver node in your Outliner. Moving this node also moves the HUD, which isn't right. Moving it along the Z-axis can actually cause the HUD to vanish due to being outside of the camera frustrum.

Other than that, if you encounter odd behavior let me know. This should work just fine in all cases where Ragdoll works, since the underlying mechanics are the same.

<br>

### Marker Limits

Markers now support the limits you've grown accustomed to from chains and constraints. They are much easier to work with, now that they are built-in to each marker and have an understanding for what a "parent" is.

https://user-images.githubusercontent.com/2152766/137694082-0815757a-119f-47c6-b21f-fe0c5693a6c3.mp4 controls

You should find a lot less need to use `Edit Pivots` from here on, and in the next release you'll also get some interactive manipulators to avoid the Channel Box even more.

**Limit Type**

![image](https://user-images.githubusercontent.com/2152766/137695508-4be75646-a683-48be-8365-37fcdb32591e.png)

<br>

#### Hinge Limit

The simplest of limits, allow a limb to rotate along a single axis. Like hinges on a door.

Use this for knees and elbows.

https://user-images.githubusercontent.com/2152766/138458863-6f7c0b0e-1dd0-4251-a764-6814bdba6169.mp4 controls

<br>

#### Ragdoll Limit

For more complex anatomical limits, such as shoulders and hips, use the "ragdoll" limit for control over each of the 3 rotate axes.

**Defaults**

A good place to start is to just play with default settings and get an idea of what it looks like.

https://user-images.githubusercontent.com/2152766/138458750-a07eff3b-e2a0-409a-95eb-3b0278f59583.mp4 controls

**Customise**

In this case, we'll keep the leg from crossing over too far, and from bending too far backwards. Like a real human leg.

https://user-images.githubusercontent.com/2152766/138458753-76246fc5-aa71-489c-a9a8-bc8939f5f28d.mp4 controls

<br>

#### Custom Limit

The Hinge and Ragdoll limits should cover the vast majority of limit needs, but sometimes you need more control. The `Custom` limit lets you control the parent and child frames independently, similar to the "traditional" Rigid constraints let you do.

Here's an example of replicating the `Ragdoll` constraint with a custom limit.

https://user-images.githubusercontent.com/2152766/138463267-bedc1a6f-ce97-4f29-aee8-f1bdf3855146.mp4 controls

<br>

#### Axis

Specify the "main" axis for your limit.

Different rigs follow different conventions, and this attribute enables you to keep Ragdoll in the loop. It should typically align with whatever axis your joint or control points in the direction of the child joint or control.

https://user-images.githubusercontent.com/2152766/138464613-17e23daf-5c91-437a-a94a-e2b6faef3190.mp4 controls

<br>

#### Rotation vs Offset

You can either rotate or *offset* the limit.

- `Rotation` rotates both parent and child frames
- `Offset` rotates only the parent frame

!!! hint "Remember"
    The `Parent Frame` is the space in which a `Child Frame` is allowed to move.

https://user-images.githubusercontent.com/2152766/138464618-8ffaab80-a649-4bd9-bb30-6f936a571cbe.mp4 controls

<br>

### Marker Constraints

You can now constrain one marker to anothe!

| Constraint Type | Description
|:----------------|:-------------
| Weld Constraint | Simplest of constraints, welds two markers together; no change to their distance or relative orientation is allowed. This is akin to the Maya `Parent Constraint`
| Distance Constraint | Maintain a minimum, maximum or total distance between two markers.
| Pin Constraint | Match a position and orientation in worldspace, similar to `Drive Space = World`.

https://user-images.githubusercontent.com/2152766/138263114-b9a9e3a8-230c-4676-a757-073cfc42af70.mp4 controls

<br>

#### Weld

Maintain the position and orientation of one marker relative another from the first frame onwards.

https://user-images.githubusercontent.com/2152766/138453515-936e7297-b40e-46bf-a63e-bb1153f8f166.mp4 controls


https://user-images.githubusercontent.com/2152766/138267073-dfd2e913-9a92-437b-8ba3-b99fe24223b4.mp4 controls

<br>

#### Distance

A simple but versatile constraint with animatable distance.

**Maintain Start Distance**

Whatever the distance between two markers, it will be maintained throughout a simulation.

https://user-images.githubusercontent.com/2152766/138162535-8bc269cf-e0f0-47d6-8bf2-ec124b1a62f0.mp4 controls

**Minimum Distance**

Alternatively, only respond to when two controls get too close.

https://user-images.githubusercontent.com/2152766/138162536-a208a381-d7c1-4f0d-821e-a1e93b95a24d.mp4 controls

**Maximum Distance**

Conversely, keep markers from getting too far *away* from each other.

https://user-images.githubusercontent.com/2152766/138162537-ce2ed22b-5f1c-4565-80e9-f24f51776950.mp4 controls

**Custom Distance**

Or go all-in, with both a minimum *and* maximum distance, for the most complex behavior.

https://user-images.githubusercontent.com/2152766/138162542-572f72e1-6420-46be-852c-092352a267e6.mp4 controls

**Offsets**

Control at which point on a control to measure the distance.

https://user-images.githubusercontent.com/2152766/138123321-31dadba0-175b-46f9-8116-e3b6416c4fca.mp4 controls

**Animated Distance**

Both min and max distance, along with stiffness and damping, can be animated for some pretty rad effects.

https://user-images.githubusercontent.com/2152766/138125038-390d999d-dad3-474d-92b9-83be7f5fbea1.mp4 controls

**Hard Distance**

A `Stiffness = -1` means the constraint is "hard". It will not accept any slack or "springiness".

In this example, the distance is animated whilst soft, and transitioned into a hard constraint. Notice how it snaps into place once hard.

https://user-images.githubusercontent.com/2152766/138226874-2fafa5c1-f8c3-4143-b6f4-e18a3b77fe87.mp4 controls

!!! hint "Limitation"
    A limitation of a hard constraint is that the distance cannot be animated whilst hard. You can however animate it between values of -1 and above, to transition to and from hard to soft.

<br>

#### Pin

Similar to the `Soft Pin` used with Rigids, this creates a new position and orientation a marker will try and reach. It's exactly what you get using `Guide Space = World` on the markers themselves, but with the convenience of a new transform you can animate. They will both try and pull on the marker, greatest stiffness wins!

https://user-images.githubusercontent.com/2152766/138454713-ceaedf52-3777-4af8-81de-e543318316f5.mp4 controls

<br>

### Recording Performance

A mere 15% boost to Recording performance.

**Before**

https://user-images.githubusercontent.com/2152766/138439243-4ed9022e-9e34-4b31-81c5-080adcbdf8d6.mp4 controls

**After**

https://user-images.githubusercontent.com/2152766/138439246-68acc8c2-10a0-4a59-ad2f-c9dc2f3adb04.mp4 controls

More was expected, and odds are there's room to optimise this further. But, the bottleneck is writing keyframes which cannot happen across multiple threads. It also needs to happen alongside evaluating your rig, which is dirtied with setting of each key, else it cannot take into account the various constraints, offset groups and IK solvers happening in there.

On the upside, the more complex your rig, the more benefit you should see from this optimisation. What happens in the above examples are extremely lightweight rigs with no animation, hence the difference is minor.

<br>

### Tutorial

- No retargeting
- Retarget joint to control
- Retarget control to another control, e.g. FK/IK/Physics
- Retarget one rig to another
