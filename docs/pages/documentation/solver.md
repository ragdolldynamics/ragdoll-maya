---
title: Solver
icon: "solver_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga13.png>
</div>

Markers connect to a solver, and anything connected to one solver is able to interact.

<br>

### Solver

Where the magic happens.

The `rdSolver` node is akin to the motion capture camera(s). It'll monitor any markers in your Maya scene and show you what their physical equivalent version looks like.

- ✔️ Real-time
- ✔️ Deterministic
- ✔️ Rewind and Resume
- ✔️ Caching
- ✔️ Support for scale
- ✔️ Support for non-uniform scale
- ✔️ Support for negative scale
- ✔️ Support for overlapping shapes
- ✔️ Support for IK/FK
- ✔️ Support for space switching
- ✔️ Support for follicles
- ✔️ Support for native Maya constraints
- ✔️ And more

<br>

### Frameskip Method

Ragdoll needs a consistent progression of time to provide reliable results. So per default, if it notices a frame being *skipped*, it kindly pauses and waits until you revisit the last simulated frame.

Alternatively, you can let it look the other way and pretend time has progressed linearly, like nCloth and countless other solvers do.

#### Pause

The default. It's safe, predictable, but requires `Play Every Frame` to work.

https://user-images.githubusercontent.com/2152766/141657769-bc44ac55-8481-4185-8e00-9a1b98cd1b9a.mp4 controls

#### Ignore

The nCloth and nHair default, of trying its best to simulate even though it wasn't given the frames inbetween. Unpredictable, unreliable but may handle playing along with sound.

https://user-images.githubusercontent.com/2152766/141657770-e74b4e4f-173a-4193-825d-6af10d725816.mp4 controls

Aside from not giving you the same result each time you play, if too many frames are skipped your simulation can completely explode. You can semi-work around this by increasing the number of substeps, forcing more simulation frames to fill for the missing frames.

https://user-images.githubusercontent.com/2152766/141657771-d4da158a-bf10-4158-a9e8-3980614c6d69.mp4 controls

!!! warning "Non-deterministic"
    Bear in mind that the `Ignore` method cannot give you the same results each playthrough. The `Pause` method is guaranteed to give you the same results, and are identical to what you get when you use the `Record Simulation` or `Cache` commands.


### Auto Time

Rather than having to specify which frame to start simulating at, Ragdoll can keep track of your animation start frame. Either the start of the *range*, or the full timeline. Or, you can still set a `Custom` start time for when you do care about specifics.

![image](https://user-images.githubusercontent.com/2152766/136388759-8cf91122-c779-4425-9c5b-492597595262.png)

<br>

### Pee-gees and Tee-gees

Two sides of the same coin.
