<div class="hero-container">
    <img class="hero-image" src=/yoga14.png>
</div>

Connect one rigid to another.

<br>

### Usage

From the Ragdoll menu, select one of the constraint options.

![constraintusage](https://user-images.githubusercontent.com/2152766/127750242-6bed4506-aa4e-4da3-9dc3-c12b43e8e539.gif)

<br>

### Types

All constraint types share the same underlying Maya node, the `rdConstraint`, but start their life with slightly different attribute values.

| Constraint | Description
|:-----------|:--------------
| Point      | Locked <code class="code-red">translation</code>, free <code class="code-green">rotation</code>
| Orient     | Locked <code class="code-green">rotation</code>, free <code class="code-red">translation</code>
| Parent     | Locked <code class="code-red">translation</code> and <code class="code-green">rotation</code>
| Hinge      | Locked <code class="code-red">translation</code> and *partially* locked <code class="code-green">rotation</code>
| Socket     | Locked <code class="code-red">translation</code> and *limited* <code class="code-green">rotation</code>

<br>

#### Point Constraint

Locked <code class="code-red">translation</code>, free <code class="code-green">rotation</code>

This constraint prevents the translate values of one rigid to change, relative another rigid. The result is a freely rotating rigid, pinned at a point somewhere on the other rigid.

![pintcosntraint2](https://user-images.githubusercontent.com/2152766/127768080-b3b7662e-d305-4419-a7d5-7b6ea1b2a701.gif)

<br>

#### Orient Constraint

Locked <code class="code-green">rotation</code>, free <code class="code-red">translation</code>

When you want to match the orientation between two rigids, whilst letting them translate freely.

![ofrientconstraint3](https://user-images.githubusercontent.com/2152766/127770622-9508c9ee-71ea-4db0-aac3-8567cb01b268.gif)

<br>

#### Parent Constraint

Locked <code class="code-red">translation</code> and <code class="code-green">rotation</code>

Make one rigid appear as the child of another, by locking both rotation and translation values. Counter-intuitively, this constraint is the *most expensive* to compute. But, sometimes you have have no choice, such as when you want to create a more complex collision shape by parenting multiple rigids together.

![parentconstraint5](https://user-images.githubusercontent.com/2152766/127770883-dbc373e7-6292-449b-8c6b-7d7ab33e12d5.gif)

<br>

#### Hinge Constraint

Locked <code class="code-red">translation</code> and *partially* locked <code class="code-green">rotation</code>

This constraint is very handy for knees and elbows, and anything that should only be allowed to rotate around a single axis.

![hingeconstraint3](https://user-images.githubusercontent.com/2152766/127768082-94648c80-55e8-433a-a324-404f41eaba69.gif)

<br>

#### Socket Constraint

Locked <code class="code-red">translation</code> and *limited* <code class="code-green">rotation</code>

For more complex joints, such as hips and shoulders, that should be allowed to rotate around all 3 axes in a very specific way. It includes a pre-defined limit on all axes, along with a default guide to drive a rigid towards its starting orientation.

![socketconstriaint2](https://user-images.githubusercontent.com/2152766/127768084-1192d09c-ff5a-4e50-8a41-02ae5b5ad1c8.gif)

<br>

#### Ignore Contact Constraint

A special constraint with both `Limit` and `Guide` turned off, leaves only its ability to tell the solver to ignore contacts between the two constrained rigid bodies.

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/124230562-147e2f00-db07-11eb-8125-78d0dbc156c7.mp4" type="video/mp4">
</video>

<br>

### Limit

The above types mostly vary the "limit" attribute of a constraint, but what *is* a "limit"? A limit *prevents* the motion of one rigid relative another.

!!! hint "Inverted Collider"
    You can think of a limit as a inverted collider, in that a rigid body is allowed to move only *within* this collider; as opposed to *outside* of it. Under the hood, this is very much like how it actually works!

![limits](https://user-images.githubusercontent.com/2152766/127743099-3fc12417-6c13-46d5-a728-7e61e0761a17.gif)

<br>

#### Degrees of Freedon

The axes of a limit are called "degrees of freedom" (or DOF) and comes in 6 flavours.

| # | Axis | Description
|:--|:-----|:------
| 1 | <code class="code-red">Translate X</code> | Typically `Locked` for limbs and `Limited` for mechanical things
| 2 | <code class="code-green">Translate Y</code> | 
| 3 | <code class="code-blue">Translate Z</code> |
| 4 | <code class="code-red">Rotate X</code>    | Also called `Twist`, great for elbows and knees
| 5 | <code class="code-green">Rotate Y</code>    | Also called `Swing`, great for shoulders and hips
| 6 | <code class="code-blue">Rotate Z</code>    

One or more of these can be used simultaneously to express almost any relationship between two rigids.

<br>

#### Twist and Swing

The `X` and `YZ` axes of rotation have nicknames - <code class="code-green">"twist"</code> and <code class="code-red">"swing"</code>. Twist is rendered like a pie whereas swing is rendered as a cone.

- <code class="code-green">Twist</code> is well suited for motion with only one degree of freedom, like elbows and knees
- <code class="code-red">Swing</code> covers the rest; like shoulders, hips and wrists

![](https://user-images.githubusercontent.com/2152766/125652541-8f557854-154c-448f-8133-29e346481c14.png)

<br>

#### Limit States

Each axis can be in one of 3 possible states.

| State   | Value | Description
|:--------|:------|:----------
| Locked  | `< 0` | A value less than 0 means "locked", it cannot change *at all*
| Free    | `= 0` | A value of exactly 0 means "free", it is free to change
| Limited | `> 0` | A value greater than 0 means "limited", it is free to move within this *range*

When an axis is "limited", the value represents the number of degrees it is limited to (or centimters for a translation limit).

![](https://user-images.githubusercontent.com/2152766/117270305-fa9ad580-ae50-11eb-9258-fbfb08bcbd12.gif)

<br>

#### Softness

When an axis is `Limited` it will respond to the `Limit Stiffness` and `Limit Damping` attributes. A limit can be made "soft" by reducing these values.

**Soft Rotate Limit**

Human "limits" are quite pliable. They flex, they give way to a strong-enough force being applied. Mechanical limits however are typically very hard, like the maximum permitted height of vehicle suspension.

![softangularlimite](https://user-images.githubusercontent.com/2152766/127768734-4cfb0f59-ca4e-4487-8e00-d5fe0a6ae227.gif)

**Soft Translate Limit**

Notice how the rigid is allowed to move *outside* of the limit, but is being gently pulled back. The strength and elastiticy of this effect is governed by the `Translate Limit Stiffness` and `Translate Limit Damping`.

![](https://user-images.githubusercontent.com/2152766/117269725-70527180-ae50-11eb-93db-0b95c40feb91.gif)

<br>

#### Pivots

Every constraint has 2 pivots called `Parent Frame` and `Child Frame`.

![constraintframes](https://user-images.githubusercontent.com/2152766/127747031-89998dfa-373e-41f3-b784-f183426b4404.gif)

The most finnicky part of pivots is editing rotations. For example, to make knees and elbows, you'll want to align the <code class="code-green">Twist</code> axis with the knee and this process has 2 steps.

1. Rotate both <code class="code-red">Parent Frame</code> and <code class="code-green">Child Frame</code> align with the knee
2. Rotate only the <code class="code-red">Parent Frame</code> to align the current pose of the knee with how far it should bend.

<video controls autoplay loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/127773089-681c5f9c-3f42-458f-b8ce-5ecedb6a1c84.mp4" type="video/mp4">
</video>


<br>

### Guide

Make one rigid reach a given target pose.

Drawn as a transparent red/green pie between two rigid bodies, the Guide enables one rigid to reach a translation and/or rotation relative another rigid.

![constraintrendering](https://user-images.githubusercontent.com/2152766/117299037-f92cd580-ae6f-11eb-96e4-7f236e8a92ab.gif)

<br>

#### Guide Pie

This represents the difference between where a rigid is, and where it wants to go. It is the target angle, your animation and how far away it currently is from the simulation.

<br>

#### Guide Line

Translation is drawn as a dotted line between a rigid and the animation.

![guideline](https://user-images.githubusercontent.com/2152766/127774034-95f1b5a2-a7de-47a7-98ca-f658449f8e85.gif)

![translationguide](https://user-images.githubusercontent.com/2152766/127773936-f3451d30-7577-40d9-8e97-0beb7184a7fb.gif)

<br>

### Constraint Colours

When rigids have *multiple* constraints, it can be hard to tell them apart visually given they all share the same red/green colours. And if you're amongst the colour-blind things are even more challenging.

Give some extra flare to your constraints, by editing the `Twist` and `Swing` colors.

![constraintcolors3](https://user-images.githubusercontent.com/2152766/116964947-9dfab780-aca4-11eb-978f-b896756a5731.gif)
![customconstraintcolor2](https://user-images.githubusercontent.com/2152766/116921663-2bf68400-ac4c-11eb-874c-dcfcd3e84597.gif)
