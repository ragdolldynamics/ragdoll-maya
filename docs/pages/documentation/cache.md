---
title: Cache
icon: "bake_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

### Caching

Ragdoll runs alongside your character animation, but sometimes it can be useful to keep the results from a previous run and stop being so interactive.

Meet `Cache` and `Uncache`.

https://user-images.githubusercontent.com/2152766/137889320-1f20ecd3-a6e7-4529-8e82-d04230f8646c.mp4 controls

Caching is entirely non-destructive, and in fact leverages the very same cache you've been enjoying all this time whenever rewinding.

The menu commands toggle an attribute on your solver node, called `.cache` and automatically plays the entire timeline for you. But the same result can be achieved by setting the attribute and playing it yourself.

https://user-images.githubusercontent.com/2152766/137889717-dac3ed54-6105-4742-a312-a79aa1bba945.mp4 controls

The minimal HUD will show you what's been cached, and like before once you resume playback from a cached to an uncached frame, Ragdoll will continue filling up the cache as one would expect.

Look forward to a future release where caching happens in the background, as you work. Something that can also be handy from time to time (pun!).
