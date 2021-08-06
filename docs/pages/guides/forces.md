---
icon: "force_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Gently affect one or more rigids with external *forces*.

<br>

### Usage

From the Ragdoll menu, select the a `Force` from the `Forces` sub-menu.

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128205311-ee1873a8-a357-42d5-89b3-52fe18e7a059.mp4" type="video/mp4">
</video>

<br>

### Forces

A "force" is some external influence to a rigid body. The currently available forces are:

| Force | Description
|:------|:----------
| `Push`  | Repel one or more rigids from a point in worldspace
| `Pull`  | Like Push, but *towards* a point in worldspace
| `Directional`  | Push one or more rigids in a single direction, similar to *gravity*
| `Wind`  | Turbulence, push rigids in random directions to emulate the look of wind

<br>

### Slice

Use the "slice" to visualise forces along an editable plane.

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128213756-a51f9911-53c4-414c-af1e-26cdcb20288b.mp4" type="video/mp4">
</video>

The plane represents a 2D "slice" of the forces, showing you the combined influence of all (connected) forces at that slice in worldspace.

Tweak the attributes to gain a better understanding of the forces.

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128213771-ffc7f93c-84e1-4596-ae99-de4bd80ba71c.mp4" type="video/mp4">
</video>
