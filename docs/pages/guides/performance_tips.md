---
icon: "motor_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga13.png>
</div>

Some tips and tricks on how to optimise your simulations.

<br>

### Hide Constraints

The rendering of constraints is often more expensive than actually solving them physically. Hide these if you don't need them to gain a potential 30-50% of performance (!).

![hideconstraints](https://user-images.githubusercontent.com/2152766/128217400-9b73146b-aaa0-4252-a2bd-0a157148f154.gif)

<br>

### Hide Locators

Gain another 5-10% performance by hiding *all Ragdoll nodes*, i.e. Locators. Rigids are much faster to draw than constraints, but you can never have *too much* performance.

![hiderigids](https://user-images.githubusercontent.com/2152766/128217406-44f17be1-7da6-4006-801b-14a9cb48aace.gif)

<br>

### Freeze Rigids

Rigid bodies have an `Enabled` state to exclude it from a simulation, but it will still partake in most evaluation and still cost precious CPU cycles.

In Maya 2016, an attribute was introduced for exclude nodes from Parallel Evaluation called `.frozen`. Ragdoll now supports this attribute to a limited extent.

<video autoplay="autoplay" loop="loop" width="100%"><source src="https://user-images.githubusercontent.com/2152766/124179895-58434b00-daab-11eb-8a28-a49352c58e17.mp4" type="video/mp4"></video>

This operation is completely non-destructive and affects nothing but the nodes you select.

!!! hint "Important"
    The more you freeze, the more performance you gain, and that includes *Maya's native nodes*. So go ahead and freeze the controls as well.

!!! question "Caveat"
    The optimisations are coming from deep within Maya and is mostly outside of our control. And it isn't perfect. How Maya chooses to evaluate nodes is sometimes a mystery, and sometimes even frozen nodes get included in evaluation. For the technically minded, you can read more about the attribute and behavior here.

    - https://download.autodesk.com/us/company/files/UsingParallelMaya/2020/UsingParallelMaya.html#frozen-evaluator

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

<br>

### Try PGS

Ragdoll ships with two separate solvers called `TGS` and `PGS`.

- Temporal Gauss-Seidel
- Projected Gauss-Seidel

TGS (the default) is better suited for full-body dynamics, whereas PGS is better suited for lots of independent rigid bodies, like a brick wall.
