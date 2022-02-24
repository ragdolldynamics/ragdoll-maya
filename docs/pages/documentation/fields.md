---
title: Fields
icon: "force_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga12.png>
</div>

Environmental effects like Wind and Turbulence for your Markers.

<br>

### Fields

Ragdoll supports all of Maya's native "fields"

!!! question "What are fields?"
    A field represents a set of forces applied to each Marker. Ranging from `Gravity` to `Turbulence`, each field carries unique properties you can use to emulate some environment or environmental effect, like wind and gravity fields along a curve.

!!! question "What is the difference from regular Maya fields?"
    They are the very same!

    If you're already familiar with them, from e.g. nParticles of nCloth, then you can leverage your experience with Ragdoll, and vice versa if you ever venture into nCloth and friends.

![image](https://user-images.githubusercontent.com/2152766/153752085-8e748110-75f4-40c7-b05a-bd15d56963e5.png)

<br>

### Overview

Let's walk through these fields one-by-one.

<br>

#### Turbulence

The perhaps most interesting field. Apply forces in "random" directions, based on the worldspace positions of your Markers.

https://user-images.githubusercontent.com/2152766/153750169-07891084-b935-4dd1-b69a-7a2863873c5e.mp4 controls


https://user-images.githubusercontent.com/2152766/153713200-63ffe691-9718-4e39-a1c3-17669db5821d.mp4 controls

The way to think of turbulence is as Perlin Noise you may have seen in images such as this.

![image](https://user-images.githubusercontent.com/2152766/153750302-465f1747-0527-49e6-b946-dd96156eefad.png)

Where the amount of white determines the amount of force being applied. As a Marker travels across this field, both the magnitude and direction changes in interesting ways.

<br>

#### Drag

Apply an *opposite* force to any motion.

The faster things move, the greater the force.

!!! tip "Pro tip"
    This field is similar to Ragdoll's `Air Density`. Not *technically*, but practically.

https://user-images.githubusercontent.com/2152766/153750407-dbc9d7eb-4135-488d-8755-48bc532cf029.mp4 controls

<br>

#### Wind

Apply a uniform force, at a given speed, in a given direction. Like wind, including a kitchen fan with some `Spread`.

https://user-images.githubusercontent.com/2152766/153750615-bd2eba9e-7a29-407d-94ad-657ef59d4444.mp4 controls

<br>

#### Gravity

A familiar force, except this one can be also be animated!

https://user-images.githubusercontent.com/2152766/153750684-25ee1e0b-2120-423d-8189-9bbfd254600e.mp4 controls

<br>

#### Newton

Force Markers towards or away from a point in space.

https://user-images.githubusercontent.com/2152766/153719442-8c1b0d88-b4fa-4310-901e-ea79472c3aaa.mp4 controls

<br>

#### Radial

A more curious field; with a force which *increases* as it gets farther from the source.

https://user-images.githubusercontent.com/2152766/153750760-da2803c4-1a57-455d-9908-b7cf3a3394f7.mp4 controls

<br>

#### Uniform

Apply a constant force. That's all.

https://user-images.githubusercontent.com/2152766/153750848-f8326f5e-863a-4c2b-a052-a39a603e0d1f.mp4 controls

<br>

#### Vortex

Apply forces in a circular pattern.

https://user-images.githubusercontent.com/2152766/153750929-9c1a8e2f-c339-4b51-b451-88fe61550433.mp4 controls

<br>

#### Volume Axis Field

A field for when you don't know what field you want.

A true Swiss Army Knife of fields, can do everything from Vortex, to Newton to Turbulence in one convenient node.

https://user-images.githubusercontent.com/2152766/153751617-5b291e01-48e7-4974-bc7c-72cc7f701be6.mp4 controls

<br>

#### Volume Curve

Have some fun with this curve-based field. Perhaps to emulate an underwater current?

In this example, I'm also using a `Drag` field to keep things from flying off into space.

!!! tip "Pro tip"
    The curve is a normal Maya NURBS curve. If you need more points, right click and add points as you normally would.

https://user-images.githubusercontent.com/2152766/153767442-45e86095-a0c3-4e08-a766-93249648687a.mp4 controls

<br>

#### Combined Fields

Make two or more fields to combine their effect and create complex forces or series of forces!

https://user-images.githubusercontent.com/2152766/153752341-8f4956e9-5366-4901-95f6-c228bad85138.mp4 controls

<br>

#### Centroids

Where within each Marker should a field apply forces?

- [ ] Center of Mass
- [x] Volumetric

At the center, forces will be nice and predictable; except they won't be able to introduce *rotations* to your Marker, which may or may not be what you want. For the most realistic fields, use volumetric centroids.

![image](https://user-images.githubusercontent.com/2152766/153761018-6395874a-65f9-4a86-8e60-ec98f1b3186a.png)

https://user-images.githubusercontent.com/2152766/153760596-0ae4831a-799b-4fb2-a84c-fac4c3cd3843.mp4 controls

Here's another example using the Turbulence Field.

https://user-images.githubusercontent.com/2152766/153760597-53ed266c-d8a9-4cb7-aa55-d30e11fc4080.mp4 controls

![image](https://user-images.githubusercontent.com/2152766/153768590-07e9b49e-59fc-4fbc-bc38-420044f436d7.png)

!!! hint "Which is better?"
    Up to you! There is a *tiny* performance penalty for volumetric origins, as the number of forces increase. But you shouldn't notice much if any impact on performance.

<br>

#### Centroid Seed

For complex meshes, centroids can end up in unwanted locations or gather in an area with dense vertices. That's when you can give the algorithm a little jolt to try and see whether there is a better alternative out there.

https://user-images.githubusercontent.com/2152766/153838710-891d6604-003f-4eac-8c95-a690adc4aa8f.mp4 controls

<br>

#### Use Selected as Source

Some forces act according to their position in the world. Attach a field to a Marker to create an interesting relationship between the two.

!!! warning "Non-commercial Ragdoll"
    This feature is limited to 100 frames in non-commercial versions of Ragdoll.

https://user-images.githubusercontent.com/2152766/152635411-0f810a24-6e6e-46dc-9f56-4fcdf5494d45.mp4 controls


https://user-images.githubusercontent.com/2152766/153752546-67d71938-afd6-4187-aebd-89165fc77817.mp4 controls

Distance constrain two markers, and attach a field to the outer-most Marker for a doubly-interesting effect. That also wrecks your brain. 🙃

https://user-images.githubusercontent.com/2152766/153765980-641d3ce2-6c40-4956-8a2e-d75703e94c52.mp4 controls

<br>

#### Field Scale

If forces start becoming large, you may find yourself in a situation where the visualisation needs to tone down just a bit.

In the solver settings, you will find options to scale those lines (i.e. `Field Scale`), as well as control how many steps into the future (i.e. `Field Iterations`) it should draw for you.

https://user-images.githubusercontent.com/2152766/153766135-6804cda2-3b85-4560-bf01-f2480fb0dc49.mp4 controls

<br>

#### Ignore Field

Fine-tune the effect of fields by having one or more Markers *ignore* the effect of fields.

https://user-images.githubusercontent.com/2152766/153839253-65fa756c-373f-40e3-9c67-e1a4e52884e1.mp4 controls

<br>

#### Force Modes

Fields can apply to your markers in 2 different ways.

| Mode             | Description | Math
|:-----------------|:------------|:----------
| Force            | Traditional force            | `mass * distance / time^2`
| Impulse          | Typically used for contacts  | `mass * distance / time`

!!! question "Which should I use?"
    The default is `Force`, whereas `Impulse` is what is typically used for collision handling. Experiment, and let us know which you prefer!

https://user-images.githubusercontent.com/2152766/153840245-90a8b6b1-1270-4e4a-9849-d973e837aaed.mp4 controls

<br>

### More

Being native to Maya, Autodesk has some documentation of its own here.

- [Maya's Fields Documentation](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2020/ENU/Maya-SimulationEffects/files/GUID-85AEE528-4477-46DF-8B9E-2E8AEC3C8784-htm.html).

You may also search for fields on YouTube or ask your colleagues about them; any trick they've learnt may very well apply to Ragdoll as well!
