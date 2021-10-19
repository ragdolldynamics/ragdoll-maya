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

https://user-images.githubusercontent.com/2152766/137677733-af55a032-aabe-49e4-af6f-253086b68be3.mp4 controls

<br>

### Performance

<br>

### Solver Linking

Until now, you've been able to author a ragdoll using Active Chain and combine scenes using the `Combine Scene` menu item. That would transfer all connected rigids from one scene to another.

But, the feature is *destructive*. There's no way to "uncombine" and if you could, there's no record of what was originally combined.

Meet `Scene Linking`.

<br>

### Solver Caching

Ragdoll runs alongside your character animation, but sometimes it can be useful to keep the results from a previous run and stop being so interactive.

Meet `Cache` and `Uncache`.

https://user-images.githubusercontent.com/2152766/137889320-1f20ecd3-a6e7-4529-8e82-d04230f8646c.mp4 controls

These toggle an attribute on your solver node, called `.cache` and plays the entire timeline for you. The same result can be achieved by setting the attribute yourself, and playing it yourself.

https://user-images.githubusercontent.com/2152766/137889717-dac3ed54-6105-4742-a312-a79aa1bba945.mp4 controls

The minimal HUD will show you what's been cached, and like before once you resume playback from a cached to an uncached frame, Ragdoll will continue filling up the cache as one would expect.

Look forward to a future release where caching happens in the background, as you work. Something that can also be handy from time to time (pun!).

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

