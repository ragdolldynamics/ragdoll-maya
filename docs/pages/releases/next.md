---
hidden: true
title: Animation Capture pt. 3/4
description: Recording Performance
---

Highlight for this release is **Recording Performance**, and is part 3 out of 4 of the new [Markers](/releases/2021.09.27/).

- [**ADDED** Performance](#performance) Faster recording is what we all want
- [**ADDED** Solver Linking](#solver-linking) Run two or more solvers together, as one
- [**ADDED** Solver Caching](#solver-caching) Run once and explore
- [**ADDED** Marker Limits](#marker-limits) On par with the previous constraints, but much easier to work with
- [**ADDED** Marker Constraints](#marker-constraints) Oh yes!

### Showcase

**Best Friends, No Matter What**

https://user-images.githubusercontent.com/2152766/137677733-af55a032-aabe-49e4-af6f-253086b68be3.mp4 controls

<br>

### Performance

<br>

### Solver Linking

Reference two characters, link their solvers.

Until now, you've been able to author a ragdoll using Active Chain and combine scenes using the `Combine Scene` menu item. That would transfer all connected rigids from one scene to another.

But, that feature is *destructive*. There's no way to "uncombine" and even if you could, there's no record of what was originally combined.

Meet `Solver Linking`.

**Linking**

This fellow is referenced twice, and get their solvers linked together.

https://user-images.githubusercontent.com/2152766/137937277-daef1729-64e0-4abb-a6a3-add67b72b848.mp4 controls

**Unlinking**

Unlinking restores their previous behavior exactly.

https://user-images.githubusercontent.com/2152766/137937281-7f71cacf-f591-494b-bbdc-14365b631000.mp4 controls

!!! question "That's neat, but can you.."
    I know exactly what you're thinking, I was thinking the exact same thing.

    Can you link a solver to another solver that is also linked? So that I can build a *network* of simple solvers that all work together to form one *complex* solver?

    Yes. Yes, you can. 🤭 See below.

<br>

#### Non-destructive Workflow

Here's 2 assets, a manikin and a backpack, referenced twice each for a total of 4 solvers. The backpack is referenced to the corresponding manikin solver, which are all linked into one final solver.

**Non-destructively link solvers**

Notice the *hierarchy* of solvers formed here, enabling you to build complex solvers out of many small solvers.

https://user-images.githubusercontent.com/2152766/137920028-d0be982a-b6a1-45c3-a2fe-19ebd0e46632.mp4 controls

**Non-destructively unlinking too**

Likewise, safely deconstruct a network of solvers by just removing the connection.

https://user-images.githubusercontent.com/2152766/137920132-0c78d52e-40f7-4c9e-9207-9c5cb2c2c698.mp4 controls

Technically, a solver is added to another solver in the same manner a marker, group and constraint is added. One big happy family.

![image](https://user-images.githubusercontent.com/2152766/137920872-903e370a-617e-4109-9f0a-0408a30c5c19.png)

<br>

#### Limitations

None were left behind for this release, but if you find anything do let us know either in [the chat](https://ragdolldynamics.com/chat) or via the [contact form](https://ragdolldynamics.com/contact).

<br>

### Solver Caching

Ragdoll runs alongside your character animation, but sometimes it can be useful to keep the results from a previous run and stop being so interactive.

Meet `Cache` and `Uncache`.

https://user-images.githubusercontent.com/2152766/137889320-1f20ecd3-a6e7-4529-8e82-d04230f8646c.mp4 controls

Caching is entirely non-destructive, and in fact leverages the very same cache you've been enjoying all this time whenever rewinding.

The menu commands toggle an attribute on your solver node, called `.cache` and automatically plays the entire timeline for you. But the same result can be achieved by setting the attribute yourself, and playing it yourself.

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

### Marker Constraints

You can now constrain two markers!

- Weld Constraint
- Distance Constraint

<br>

#### Distance Constraint

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

A `Stiffness = -1` means the constraint is "hard". It will not accept any slack or "springiness", that would be a solver fault.

In this example, the distance is animated whilst soft, and transitioned into a hard constraint. Notice how it snaps into place once hard.

https://user-images.githubusercontent.com/2152766/138226874-2fafa5c1-f8c3-4143-b6f4-e18a3b77fe87.mp4 controls

!!! hint "Limitation"
    A limitation of a hard constraint is that the distance cannot be animated whilst hard. You can however animate it between values of -1 and above, to transition to and from hard to soft.
