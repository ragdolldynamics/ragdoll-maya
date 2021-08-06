---
icon: "rigid_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car14.png>
</div>

The most fundamental building block of Ragdoll, the `Rigid Body`.

<br>

### Usage

From the Ragdoll menu, select the `Active Rigid` option.

![active_rigid](https://user-images.githubusercontent.com/2152766/127508854-f8fcbb38-a2b7-4bc3-8c0e-796219620428.gif)

<br>

### Attributes

Some of the most relevant attributes of the `rdRigid` node type.

| Attribute       | Description
|:----------------|:----------
| `Collide`       | Should this rigid collide with other rigid bodies?
| `Mass`          | How strongly is should affect other rigids, and resist other forces
| `Friction`      | How much resistance to give one rigid moving along the surface of another
| `Bounciness`    | A.k.a. "restitution", how strongly one rigid should repel another

<div class="hboxlayout justify-center">
    <a href="/nodes/rdRigid" class="button blue">Full Reference</a>
</div>

<br>

#### Collide

Control whether a rigid should collide with any other rigid.

![collide](https://user-images.githubusercontent.com/2152766/127737524-fc4f8aa4-3aa7-493b-8e6b-dd187e58b152.gif)

![](https://user-images.githubusercontent.com/2152766/116609863-ca24da00-a92c-11eb-869e-daf642cdd229.gif)

!!! hint "Pro tip - Disable contacts between two specific rigids"
    The `Collide` attribute is great for disabling contacts with *all* other rigids, but what if you wanted finer control than that?

    - See [Disable Contact Constraint](/constraints#disable-contact-constraint) for how to do that

<br>

#### Mass

How much influence one rigid should have over another during contact.

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127736547-195a18f6-6567-4cdc-995e-d6fa0f7ef963.mp4" type="video/mp4">
</video>

!!! hint "Pro tip 1 - Misconception about Mass"
    A common misconception in physics is that `Mass` affects how *quickly* something falls to the ground. But in Ragdoll - like in real-life - mass is only relevant during interaction with another rigid and when forces are applied, like `Guide Strength`.

    Have a look at this video of a bowling ball falling in a vacuum alongside a feather.

    [<img class="poster" width=300 src=https://user-images.githubusercontent.com/2152766/127608727-07d0c3c2-d281-4290-93cf-392852f2d595.png>](https://www.youtube.com/watch?v=frZ9dN_ATew)

??? hint "Pro tip 2 - Making something fall faster"
    So how *do* you make something fall faster?

    1. Decrease `Scene Scale` under the solver node
    2. Increase `Gravity`, also under the solver node

    To make something "bend" faster, like an arm flexing, that would be controlled via the `Guide Strength` and typically what causes it to reach a given speed and then stay there is governed by the `Rotate Damping`. That's how much of any motion should be cancelled out, to stabilise the motion. A very *fast* motion would have very little damping, but then also run the risk of "overshooting". That is, of passing the point at which you wanted it to reach.

<br>

#### Friction

Control how much resistance should be added between two rigids rubbing against each other.

![friction2](https://user-images.githubusercontent.com/2152766/127735361-da060dc4-45c8-4699-a672-0253d177d723.gif)

<br>

#### Bounciness

Control how much rigids should *repel* each other when coming into contact.

![restitution](https://user-images.githubusercontent.com/2152766/127735506-36003376-4a70-41b2-bbb8-47c974d44278.gif)

!!! hint "Values beyond 1.0"
    Here's a tip!

    Bounciness can be greater than 1.0, which means they will *gain* energy during contact.

    In practice, energy will always dissipate in some way. The most-bouncy character in the gif above has a bounciness of `2.0`, which in theory means that for every contact it should fly `200%` faster away than it did coming in, and keep doing this forever.

<br>

#### Center of Mass

If you try and balance something on your finger, but the "center of mass" is off center, it would fall over.

![image](https://user-images.githubusercontent.com/2152766/99946359-25471500-2d6e-11eb-8c29-5d39e69f05ee.png)

It is the point at which the weight of an object is equal in all directions.

Ragdoll automatically computes this point based on what the shape looks like. For meshes, it will *voxelise* your geometry to figure out the physically accurate volumetric center of mass, assuming the density of the object is uniform throughout (rather than hollow or variadic, like swiss cheese).

You now override this point using the attribute `Center of Mass` found under the Advanced tab.

![ragdollcom](https://user-images.githubusercontent.com/2152766/99946517-64756600-2d6e-11eb-8446-469ea68073b4.gif)
![ragdollcom2](https://user-images.githubusercontent.com/2152766/99946522-663f2980-2d6e-11eb-9a5e-9aa9bf7c301a.gif)

**Guidelines**

- For realistic results, leave it at `0` to compute the point automatically based on the shape
- For full control, override it

<br>

#### Angular Mass

In real life, if you spin a broom 180 degrees along its length; that's easy. But if you spin it 180 degrees along any other axis, like a ninja, it's considerably heavier.

<img width=400 src=https://user-images.githubusercontent.com/2152766/99944546-f67b6f80-2d6a-11eb-93b1-47a49deba0d5.png>

The reason is something called "angular mass", also known as ["moment of inertia"](https://en.wikipedia.org/wiki/Moment_of_inertia). It's like mass, but in terms of rotation rather than position. The broom has a *low* angular mass along its length axis. It takes more *force* to affect a "heavier" axis than a lighter one which is why a broom spins more easily along its length.

This effect happens in Ragdoll too and is typically automatically computed for you based on the shape you use. If it looks like the broom, it will act like a broom.

With this release, you can now customise this for greater control of your rotations.

![ragdollangularmass](https://user-images.githubusercontent.com/2152766/99944815-6db10380-2d6b-11eb-9def-dba375a7e743.gif)

When would you want to do that?

1. Your shape looks like a broom, but you want it to act like a box
2. Your shape doesn't look like a broom, but you would like it to act like one

Or any combination in between. :) Generally, a broom or any thin shape is more easily spun along its length, so you may find **stability** in setting your angular mass to `(1.0, 1.0, 1.0)`, at the expense of realism.

**Guidelines**

- For realistic results, leave it at `-1` to automatically compute the angular mass
- For full control, override it

<br>

### Shapes

Every rigid body needs a shape, a *collision volume*.

| # | Type       | Description
|:--|:-----------|:----------
| <img class="invertme icon" width=20 src=/icons/box.png> | `Box`      | A typical box with customisable `Shape Extents`
| <img class="invertme icon" width=20 src=/icons/sphere.png> | `Sphere`   | A perfect sphere with a customisable `Radius`, the *fastest* collision shape
| <img class="invertme icon" width=20 src=/icons/capsule.png> | `Capsule`  | An extruded sphere, the *second-fastest* collision shape
| <img class="invertme icon" width=20 src=/icons/mesh.png> | `Mesh`     | A convex hull generated from either a polygonal or NURBS input geometry

<br>

#### Meshes

Before meshes are used for simulation they are converted into a "convex hull", which is a mesh with no valleys.

![convexhull](https://user-images.githubusercontent.com/2152766/127818504-f831a7bd-b421-4250-9748-82578e0d8474.gif)

!!! question "How do I make more complex collision shapes?"
    You can break a mesh into several rigid bodies and use a Ragdoll Parent Constraint to hold them together. See [Parent Constraint](/guides/constraints/#parent-constraint) for details.

    This approach isn't very convenient however - and also doesn't perform well - so in a future release you will be able to turn individual polygon islands of a single mesh into a *combined* convex hull.

Here's an example of how Ragdoll converts a mesh into a convex hull. Notice how it can't make any holes or valleys this way.

![convexhull2](https://user-images.githubusercontent.com/2152766/127820852-87db9e97-ff8a-4dd1-980f-d1ce53e95477.gif)

<br>

#### Replace Mesh

When you turn a mesh dynamic, the vertices are plugged into the rigid node.

- `mesh` nodes plug into `rdRigid.inputMesh`
- `nurbsCurve` nodes plug into `rdRigid.inputCurve`
- `nurbsSurface` nodes plug into `rdRigid.inputSurface`

But what if you wanted a different mesh? What if there *was* no mesh, such as for a joint or empty transform?

I give you, `Replace Mesh`. 👏

![replacemesh](https://user-images.githubusercontent.com/2152766/123130851-09f7d180-d445-11eb-8ec0-fe3a47a20505.gif)

Here's a more practical example, of a dynamic joint being replaced with the mesh of a car wheel.

![replacemeshpractical](https://user-images.githubusercontent.com/2152766/123131832-f9942680-d445-11eb-99b3-41f03a0e9eb4.gif)

<br>

#### Edit Shape

Manipulate shapes with a native Maya transform, as an alternative to fiddling with numbers in the Channel Box.

![editshape](https://user-images.githubusercontent.com/2152766/113729903-5574cc00-96ef-11eb-9c14-37f177c4b219.gif)

<br>

### API

Here's how to use the Active Rigid from the Ragdoll API.

```py
from maya import cmds
from ragdoll import api as rd

cube, _ = cmds.polyCube()
cmds.move(0, 10, 0)
cmds.rotate(35, 50, 30)

scene = rd.createScene()
rigid = rd.createRigid(cube, scene)

cmds.evalDeferred(cmds.play)
```