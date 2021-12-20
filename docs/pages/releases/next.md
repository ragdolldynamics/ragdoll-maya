---
title: Christmas
description: ...
---

Minor maintenance release.

- [**FIXED** Crash on Deleted Mesh](#crash-on-deleted-mesh) Replace a mesh, delete it and crash no more.
- [**FIXED** Mandarin Serial Number](#mandarin-serial-number) Unicode mishap led to a non-sensical message
- [**FIXED** Delta Drawing Bug](#delta-drawing-bug) Funny drawing in the viewport has been fixed
- [**ADDED** Max Mass Ratio](#max-mass-ratio) Keeping you safe

<br>

### Showcase

Let's start with the good stuff.

**DMV Lady**

Courtesy of Dragana Mandic.

- [On LinkedIn](https://www.linkedin.com/posts/dragana-mandi%C4%87-a6a6a2111_dynamics-animation-simulation-activity-6878674478977568768-SlbE)

https://user-images.githubusercontent.com/2152766/146805387-bffea211-5dd7-4cd8-ad30-d5b1fb75c3f2.mp4 controls

<br>

### Trial Key

It has come to my attention that the first thing every new user of Ragdoll sees is this dialog, with this message for a serial number.

![image](https://user-images.githubusercontent.com/2152766/146526900-6815e9ad-4da3-4531-bb2c-bb0e239affff.png)

According to my Mandarin-speaking friends, this is jibberish (or at least should be!) and is a result of badly translated Unicode to ASCII characters.

This has now been fixed!

![image](https://user-images.githubusercontent.com/2152766/146527505-c79a897c-74cc-4e4c-b3c3-becae0ebd99d.png)

<br>

### Delta Drawing Bug

The worldspace deltas were drawn separate from the marker they affected, which could produce a jarring effect especially when the solver position had been offset.

**Before**

https://user-images.githubusercontent.com/2152766/146639337-8df8d52e-8e6f-4d87-94f8-5973b03a7f1e.mp4 controls

**After**

This has now been fixed.

https://user-images.githubusercontent.com/2152766/146639364-34dcba69-b174-4950-8431-19303fb343f4.mp4 controls

!!! info "More Performance"
    As an added bonus, we're now also doing 2 matrix multiplications less *per frame*, *per marker*. That kind of thing adds up quickly.

<br>

### Auto Mass

Ragdoll can now compute a suitable mass of each Marker, based on the geometric shape you give it.

In a word, big objects become heavy, small objects become light.

**Before**

https://user-images.githubusercontent.com/2152766/146757327-507ea062-d4e7-45dd-b9a1-59406340fc89.mp4 controls

**After**

https://user-images.githubusercontent.com/2152766/146757333-b56046c7-467f-4edf-91b8-45d260ffc101.mp4 controls

<br>

### Max Mass Ratio

With `Auto Mass`, there's a chance Markers get Ragdoll into a situation it does not like; namely that the difference between masses are too great.

??? info "Give me the technical details"
    As you wish. :)

    Ragdoll doesn't like differences any greater than 10x, sometimes 100x, else it can fail or become unstable. For example, if your character has a mass of 100kg, and the foot Marker has a mass of 0.5kg, that's a ratio of 100/0.5 = 200x which is far greater than Ragdoll would like. As a result, the body would *crush* the foot which would be unable to properly hold the entire body up.

    Up until now, the masses on all Markers have had a default value of 1kg. Meaning that regardless of the *size* of a Marker - be it the torso, the head or tip of a finger - it would always have a mass of 1.0. As a result, *hands* would typically end up far heavier than the rest of the body.

**Before**

Here's an example of the solver failing. There are three identical chains, the tip of the last one having a mass of 10,000. That's 10,000x greater then each link in the chain. As a result, Markers separate; that is incorrect.

https://user-images.githubusercontent.com/2152766/146761954-6218f6bf-9fbe-4100-b831-589fd7d94914.mp4 controls

**After**

If we limit the maximum ratio to just 1000x, we get the correct behavior. You can also see how it affected the other two chains. They now behave more similarly, because in order to ensure a mass ratio across the whole system, the mass of their tips need to be reduced as well.

https://user-images.githubusercontent.com/2152766/146761956-211ce2b6-42b6-4f70-a9de-42326b4fb17c.mp4 controls


The new `Max Mass Ratio` attribute protects against these situations, letting you give objects a suitable mass and only have to worry about which should weigh more, and which should weigh less. Ragdoll will balance everything out before passing it along to be simulated.

!!! info "What are the consequences?"
    Sometimes, large mass ratios are what you want. For example, a heavy weight on a string tends to do quite well with ratios up to 1000x. But markers being crushed by another marker 1000x its weight tends to not do as well.

    So the result is less of an effect at the extreme ratios.
