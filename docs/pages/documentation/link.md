---
title: Link
icon: "link_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Combine, or "merge" multiple solvers together, to simulate them as one.

<br>

### Linking

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
