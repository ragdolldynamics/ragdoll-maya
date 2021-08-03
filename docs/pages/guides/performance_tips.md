<div class="hero-container">
    <img class="hero-image" src=/yoga13.png>
</div>

Some tips and tricks on how to optimise your simulations.

<br>

### Multiple Scenes

<br>

### Freeze Rigids

<br>

### Hide Constraints

The rendering of constraints is often more expensive than actually solving them physically. Hide these if you don't need them to gain a potential 20-30% of performance.

<br>

### Hide Rigids

Gain 1-5% performance by hiding rigid bodies you aren't actively looking at. These are much faster than constraints, but still consume *some* amount of precious time.

<br>

### Try PGS

Ragdoll ships with two separate solvers called `TGS` and `PGS`.

- Temporal Gauss-Seidel
- Projected Gauss-Seidel

TGS (the default) is better suited for full-body dynamics, whereas PGS is better suited for lots of independent rigid bodies, like a brick wall.

<br>

### Decrease Iterations

Ragdoll is an "iterative" solver, which means it will make quick attempts at resolving contacts and constraints multiple times until it reaches an acceptable solution.

The more attempts you allow, the closer to the true solution it will get, at the cost of performance.

The `rdScene.iterations` is how many iterations are given to each rigid body. Greater numbers means you can use higher values for `Guide Strength` and `Limit Strength`, at the expense of performance

This number is multiplied with `rdRigid.positionIterations` which is the final value involved in determining how many iterations are spent solving a given rigid.

- 4 scene iterations and 8 rigid iterations brings a total of 32 iterations for each rigid, which is a decent value, in the upper-end of what is typically necessary.
- This number can be tweaked on a per-rigid level too, if you know that one or more rigids are more important than others you can reduce it for the rest to save on performance.

<br>

### Reduce Substeps

Every frame in Maya is divided into this amount of "substeps" which makes Ragdoll look at your animation in *slow motion*.

The more time it has to respond to contacts and resolve constraints the easier of a time it will have, at the expense of performance.

- 4 substeps is a good number, suitable for the average simulation