---
title: Active Chain
icon: "chain_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

Link multiple rigid bodies together to form a "chain".

<br>

### Usage

From the Ragdoll menu, select the `Active Chain` option.

![chainusage](https://user-images.githubusercontent.com/2152766/127740896-63c12fe0-d21a-4645-97e0-79b83134e9a5.gif)

<br>

### Attributes

Some of the most relevant attributes of the `rdRigid` node type.

| Attribute         | Description
|:------------------|:----------
| `Simulated`       | Toggle between animation and simulation
| `Global Strength` | Affect all `Guide Strength` of this chain at once

<br>

#### Simulated

Animate without physics, and then turn physics back on.

![chainwalkcycle](https://user-images.githubusercontent.com/2152766/127738668-00c50885-c401-4267-89ed-781559b3f4b8.gif)

<br>

#### Global Strength

Affect *all* guide strengths in a chain or tree.

![globalstrength](https://user-images.githubusercontent.com/2152766/127740761-50285291-5d19-4292-be9c-71805315abc7.gif)

!!! hint "More Control"
    Each connection between two rigids have its own `Guide Strength` you can use to tweak values at an individual control level.

<br>

### Tree

- 2 chains make a **branch**
- 3+ chains make a **tree**

That's how ragdolls are made!

![chain](https://user-images.githubusercontent.com/2152766/127738091-c8cbcc1d-6cdd-4043-be18-2fb890516454.gif)

!!! info "Root"
    Every chain has a "root", namely the *first* selected object. This is where the `Simulated` and `Global Strength` attributes are put and may also start its life as a `Passive Rigid`; configurable in the Active Chain Options.

    ![image](https://user-images.githubusercontent.com/2152766/127741232-f089273d-c86f-4739-a30e-f2de1867a697.png)

<br>

### Controls

Anything with a `Translate` and `Rotate` channel can be made into chain.

- Joints
- NURBS Controls
- Polygon Meshes
- Empty Groups
- ...

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/124564514-10208180-de39-11eb-80dc-5da6c2833ee5.mp4" type="video/mp4">
</video>

<br>

### Overlapping Shapes

Ragdoll tries generating shapes that best represent the underlying joints, but sometimes the result can have overlapping shapes.

There are 3 typical solutions for this.

| Solution | Description
|:---------|:----------
| Avoid overlap | Ideally the shapes would not overlap, but this is not always possible
| `Collide = Off` | Disable collisions for the offending rigid(s)
| [Ignore Contact Constraint](/documentation/constraints/#ignore-contact-constraint) | Disable collisions between the two overlapping rigids

![overlappingshapes](https://user-images.githubusercontent.com/2152766/127827143-47298854-acbb-4e74-a44d-69de0f3fe447.gif)

<br>

### API

Here's how to use the Active Chain from the Ragdoll API.

![chainexample](https://user-images.githubusercontent.com/2152766/128610157-e9181587-814d-4981-a798-79a8e0184ae1.gif)

```py
from maya import cmds
from ragdoll import api as rd

ctrl1 = cmds.createNode("joint")
ctrl2 = cmds.createNode("joint", parent=ctrl1)
ctrl3 = cmds.createNode("joint", parent=ctrl2)

cmds.move(0, 5, 0, ctrl1)
cmds.move(5, 5, 0, ctrl2)
cmds.move(10, 5, 0, ctrl3)
cmds.rotate(0, 0, 30, ctrl1)

scene = rd.createScene()
chain = rd.createChain([ctrl1, ctrl2, ctrl3], scene)

cmds.setAttr(ctrl1 + ".globalStrength", 0.02)

cmds.evalDeferred(cmds.play)
```