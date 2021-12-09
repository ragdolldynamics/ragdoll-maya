---
title: Group
icon: "ragdoll_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Ragdolls are combined into what's called a "group", with attributes to control the overall behavior of all contained Markers.

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
