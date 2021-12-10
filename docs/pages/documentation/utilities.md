---
title: Replace Mesh
icon: "replace_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

### Replace Mesh

You can now replace the original geometry assigned to your marker, just like you could with Rigids.

https://user-images.githubusercontent.com/2152766/141688044-c2de9054-e2c1-4758-80c2-95c337de47e6.mp4 controls

<br>

### Auto Limits

Markers are now able to infer which axes to lock in the simulation, based on the locked channels of your control or joint.

https://user-images.githubusercontent.com/2152766/141749188-f0c5e734-3d5f-49c2-afb3-c2707f05223c.mp4 controls

Notice in this example how some of the channels are locked. With the `Auto Limit` option checked, the corresponding limit axes will be locked too, such as to prevent the simulation from rotating around those axes.

If you forget or want to detect locked axes on an existing marker, you can use the Utility option too.

https://user-images.githubusercontent.com/2152766/141749191-bd5206e0-8802-48de-b580-587dfe6f0153.mp4 controls
