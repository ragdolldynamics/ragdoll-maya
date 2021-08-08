---
title: Scene Management
icon: "scene_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Move rigids between physics scenes, or combine multiple scenes into one.

<br>

### Usage

From the Ragdoll menu, select the one of the `Extract`, `Move` and `Combine` options.

<video autoplay="autoplay" loop="loop" width="100%"><source src="https://user-images.githubusercontent.com/2152766/124179074-30071c80-daaa-11eb-9f21-a199bfceceb5.mp4" type="video/mp4"></video>

<br>

### Scene Management

Sometimes, you find yourself with rigid bodies that could run separately, in parallel. Either for performance, or because they could benefit from independent solver settings like iterations and substeps, or time scale and more.

Scene management tools allow you to *extract* rigid bodies from one scene into a new scene, akin to extracting polygons from one mesh into another.

<br>

#### Extract

Move one or more rigids out of one scene, and into another.

<video autoplay="autoplay" loop="loop" width="100%"><source src="https://user-images.githubusercontent.com/2152766/124179064-2b426880-daaa-11eb-8021-310b2e9d277f.mp4" type="video/mp4"></video>

<br>

#### Move

Move one rigid between two scenes.

<video autoplay="autoplay" loop="loop" width="100%"><source src="https://user-images.githubusercontent.com/2152766/124179074-30071c80-daaa-11eb-9f21-a199bfceceb5.mp4" type="video/mp4"></video>

<br>

#### Combine

Collapse two or more scenes into the first-selected scene.

<video autoplay="autoplay" loop="loop" width="100%"><source src="https://user-images.githubusercontent.com/2152766/124179058-2978a500-daaa-11eb-9842-1cb461b69a0f.mp4" type="video/mp4"></video>

!!! info "Constraints"
    For constraints to work, both rigids must be in the same scene and currently extracting only one rigid from a constrained pair would break the constraint. In a later version, the rigid will automatically become a Passive rigid in the extracted scene, such that it can still be constrained albeit indirectly.

    This will enable you to extract parts of a simulation, like muscle and cloth, from an overall dynamic character without breaking anything.
