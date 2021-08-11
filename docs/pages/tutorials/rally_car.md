---
title: Rally Car
description: Learn how to create a physically realistic race car.
icon: "car_black.png"
---

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128611375-82a3f65e-7c89-4e42-a40e-3ae1b10c12ce.mp4" type="video/mp4">
</video>

### Rally Car

In this tutorial, we will create the wheels and chassi of a car in a semi-realistic fashion. It will have realistic suspension and limited to spinning along only one axis, but it won't be able to steer.

!!! success "Up to date"
    Written for Ragdoll `2021.08.06` and above, but should still apply for `2021.06` and newer.

**You will learn**

- ✔️ How to make geometry *dynamic*
- ✔️ How to *constrain* two rigids
- ✔️ How to make wheels with translate and rotate "*limits*"
- ✔️ How to build a *static environment*

<div class="hboxlayout">
<a href="https://files.ragdolldynamics.com/api/public/dl/TQf6flzc/rallycar_v001.zip" class="button red"><b>Download Final Scene</b></a>
</div>

<br>

### Motivation

Before we dive in, let's first consider why anyone would want to simulate a car in the first place. To answer this I invite you to take a gander at this clip here.

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/124288785-81b2b400-db49-11eb-8b36-e61e9246ecdb.mp4" type="video/mp4">
</video>

If we ignore that characters for a moment and look at just the car itself; there are a few things going on that would be both challenging and time consuming to animate by hand.

1. Wheel suspension responding realistically to the ground
1. Chassi responding realistically to the wheels
1. Contact with and response to debree on the ground
1. Wheels loosing grip due to on debree
1. Matching the wheel rotation to contact with a non-flat ground

The subtle detail alone is enough to make a senior animator sweat, not to mention *changes* to the environment would require an almost complete redo of all of that work.

<br>

### Setup

Let's start with some basic polygons.

![image](https://user-images.githubusercontent.com/2152766/128613548-df9b109a-4aeb-4489-ac43-c3428578af09.png)

One chassi, one wheel duplicated 3 times.

<br>

#### Chassi

Our chassi will be a simple `polyCube`.

| Attribute | Value
|:----------|:-------
| Width   | `3.0`
| Height  | `1.0`
| Depth   | `4.0`

![image](https://user-images.githubusercontent.com/2152766/128637669-f0b626ca-c9d7-4512-85d1-42434ce01404.png)

<br>

#### Wheel

Wheels will take the shape of a `polyCylinder`. We will later bevel it, for nice round edges.

| Attribute | Value
|:--------|:-------
| Height  | `0.7`
| Radius  | `1.0`
| Axis    | `X`
| Axis Divisions | 19

!!! warning "Important"
    Make sure to make the cylinder in the `X` axis, that is the axis our wheels will rotate about.

![image](https://user-images.githubusercontent.com/2152766/128631542-835a1936-f564-4ecc-a871-802b4386d003.png)

<br>

#### Assembly

Putting the pieces together.

1. Move the chassi up by 2 units along Y
2. Duplicate the wheels 4 times
1. Parent the wheels to the chassi
3. Position the wheel alongside the chassi

!!! hint "My values"
    For the wheels, I used `Translate` values `X=2`, `Y=0` and `Z=1.5`

You should now have this. (Naming is optional)

![image](https://user-images.githubusercontent.com/2152766/128978513-6c0d9ea0-6194-4eb5-a054-496b217a71b2.png)

![image](https://user-images.githubusercontent.com/2152766/128613548-df9b109a-4aeb-4489-ac43-c3428578af09.png)

<br>

### Dynamics

Now it's time to apply physics to these objects!

<br>

#### Active Rigid

Select all 5 pieces, the chassi and wheels, and run the `Active Rigid` command from the `Ragdoll` menu.

![makerigids](https://user-images.githubusercontent.com/2152766/128631221-270afecd-de3a-4b4b-81b1-3181bd04f979.gif)

??? info "Your Outliner should now look like this"
    In your Outliner, you should now find a `rRigid` *shape* node for each wheel and chassi.

    ![outlinerrigid](https://user-images.githubusercontent.com/2152766/128980018-1312686c-48d1-47c5-a3f5-59593d195b1d.gif)

    The `rRigid` node is where you will find attributes to control the physical material and behavior of the chassi and wheels, such as the `Friction` of the wheels against the ground and `Mass` of the chassi.

<br>

#### Parent Constraint

Next, select the chassi and `Shift + Select` one of the wheels to make move together with the chassi.

![parentconstraint](https://user-images.githubusercontent.com/2152766/128631322-9c62b6f2-3176-4eae-9e27-5f1975f274ec.gif)

Repeat this process for the 3 remaining wheels.

![parentconstraint2](https://user-images.githubusercontent.com/2152766/128631349-97cc0db8-2a06-4e7e-a8e2-94eb6b9a3c94.gif)

This will glue the wheels onto the chassi, and we will shortly "unlock" the axes we are interested in for suspension and roll.

??? info "Your Outliner should now look like this."
    ![image](https://user-images.githubusercontent.com/2152766/128980117-77c6754a-9457-4e5e-b631-e7ca5462c961.png)

    With the new constraints lying beside the `rRigid`.

<br>

#### Suspension - Free

The wheels are currently *fixed* onto the chassi, but what we really want is for the chassi to be softly attached to the wheels. To accomplish this, we are going to *unlock* one of the `Translate Limits` of the wheels, namely `Translate Limit Y`.

1. Select all 4 wheels
2. Enter a value of `0` for the `Translate Limit Y` attribute

!!! question "What does `0` mean?"
    A value of `0` means disabled, the wheel will be free to move along this axis without disruption. Since the other axes are left at `-1` that means it will only be able to move in a straight line. Like how you might expect suspension to work.

    - See [Limit States](/documentation/constraints/#limit-states) for details

![unlocky](https://user-images.githubusercontent.com/2152766/128631420-b97e9480-1dd5-4c19-9752-81f7ea93c60f.gif)

<br>

#### Suspension - Soft

Now the wheels are free to move along the Y-axis of the chassi. But they are *too* free to move. What we want is for the chassi to bounce back, like a spring.

1. Select all 4 wheels
2. Set `Guide Enabled` to `On`
3. Set `Guide Strength` to `0.3`
3. Set `Translate Guide Damping` to `200`
3. Set `Rotate Guide Stiffness` to `0`
4. Set `Rotate Guide Damping` to `0`

![guide](https://user-images.githubusercontent.com/2152766/128631755-fc38e77d-d2ff-41a4-96ad-9dbd225b7c20.gif)

That's more like it. We aren't interested in having our guide affect rotation, not yet. So we only enable it for translation, such that it will try and keep the wheel where it started.

!!! hint "Tweaks"
    Control how "springy" you want the suspension with the `Stiffness` and `Damping` attributes.

    In real life, "stiffness" is the thickness of the physical spring whereas "damping" is how much resistance there is to it. Like if the spring was made of stainless steel which has a low resistance, or made out of clay which has a very high resistance.

!!! warning "Caution"
    Take care not to leave too much room between the chassi and wheels. The constraints are made to simulate reality, and in reality there cannot be an empty space between two objects that are connected.

    ![gapbetween](https://user-images.githubusercontent.com/2152766/128633016-de216d11-8a0f-48b7-8403-b5a05462ee85.gif)

<br>

### Environment

The wheels are currently unable to roll. To test this, let's put some ground under those wheels.

<br>

#### Set Initial State

Let's move the car to higher ground and set a new "initial state".

1. Move the car along `Translate Y = 10.0`
2. Play

By playing, the initial state is automatically updated to wherever the car was at the time of playing.

![initialstate](https://user-images.githubusercontent.com/2152766/128633156-f53a3f52-692e-436d-b476-d2a570d1b74f.gif)

!!! hint "Alternatively"
    Rather than playing, you can also use the `Set Initial State` command founder under `Ragdoll | Rigging | Set Initial State`

    ![image](https://user-images.githubusercontent.com/2152766/128633220-39579cd5-a35a-42b1-a77d-62cfe04c234d.png)

<br>

#### New Ground

Make a new cube and place it under the car, with some tilt such that the car will naturally roll.

1. Make a new cube
2. Resize it to create a ramp
3. Place it under the car

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128633308-a93d6cac-b789-4f1d-bc27-e2fa981160ba.mp4" type="video/mp4">
</video>

As we can see, the wheels are unable to rotate! Let's fix this.

<br>

#### Roll

The wheels cannot rotate because they are limited along every rotate axis.

1. Select each wheel
2. Set `Rotate Limit X = 0`, zero meaning "free to move"

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128633521-20b44246-0eba-435f-8a9a-3bf0a6a402a0.mp4" type="video/mp4">
</video>

!!! info "Remember"
    - A limit of `-1` means "locked", it cannot change.
    - A limit of `0` means "free", it is *unlimited*
    - A limit greater than `0` means it can change within the specified range

    See [Limit States](/documentation/constraints/#limit-states) for details.

<br>

### Finalise

We've got our car! From here you can tweak the shapes, tweak the stiffness and damping, add some more tracks, you name it!

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128634585-6307feca-ae56-4811-b90f-0334f54fbbc8.mp4" type="video/mp4">
</video>

**You have learnt**

- ✔️ How to make geometry *dynamic*
- ✔️ How to *constrain* two rigids
- ✔️ How to make wheels with translate and rotate "*limits*"
- ✔️ How to build a *static environment*

<br>

#### Engine

Now let's put some *horsepower* into those wheels.

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128640777-39848d86-3468-4cf7-8053-fc1a3e96f340.mp4" type="video/mp4">
</video>

<br>

##### Animation Constraint

To make the wheels spin, we'll apply an `Animation Constraint`.

1. Select one of the rear wheels
2. Run `Animation Constraint`

!!! question "Animation Constraint"
    A special constraint used to *transfer keyframes* into the simulation. In this case, what we're looking for is to rotate each wheel along the `X` axis.

    <img width=200 src=https://user-images.githubusercontent.com/2152766/128985917-b1962a33-3c58-4ccf-936f-9ea816e0bbae.png>

![animconstraint](https://user-images.githubusercontent.com/2152766/128984218-ec671541-c1bb-4ddc-9b68-34dbc90683ce.gif)

<br>

##### Rotation Only

Next, disable the `Translation` of the animation constraint, since the wheels are already held in place with the suspension we put in place earlier.

1. Select both Animation Constraints via the Outliner
2. Set `Translate Guide Stiffness` to `0`
2. Set `Translate Guide Damping` to `0`

![animconstraint2](https://user-images.githubusercontent.com/2152766/128984226-355b0212-1a98-4750-898b-7c718dc1c762.gif)

!!! warning "Caution"
    Take care not to disable the `Translation` of the first `Parent Constraint` we made earlier.

    The safest way to modify both Animation Constraints at the same time is by selecting them in the Outliner. If you instead select the wheels and modify them via the `Shapes` section, then Maya will kindly go ahead and modify both the `Animation Constraint` *and* the `Parent Constraint`.

<br>

##### Ready, Set, Animate!

Ok, great. We're all set to animate!

1. Select both rear wheels
2. Set some keys on `Rotate X`
3. Watch it go

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128984231-4b2d8839-afe9-41db-bfce-d458e3184d63.mp4" type="video/mp4">
</video>

!!! warning "Caution"
    The faster you try and spin the wheels, at some point you may encounter this.

    ![carfaster](https://user-images.githubusercontent.com/2152766/128987436-8569936a-8e42-43a8-9214-65ff7153e04f.gif)

    That's because at some point your *animation* will be greater than 180 degrees away from where the **simulation** is, and the simulation cannot distinguish between an angle of `180` and `-180`.

    By providing an exact angle in this way, we are able to reach specific positions with the car in a very reliable way, but do have to pay attention to special cases like these.

    To solve this, you can increase the `Stiffness` of the `Animation Constraint` to effectively give the needed horsepower required to meet your animation requirements. If you need it to go even faster, you may also need to increase the `Iterations` and `Substeps` on the `rScene`, for helicopter-speeds or greater.

<br>

#### Accurate Roll

If you let the wheels spin slowly, you'll notice how the resolution isn't quite enough.

1. Select the original wheel
2. Set `Subdivision Axis = 50` on the `polyCylinder2` shape

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128634278-6146ad9d-bc14-4923-a632-3f69aba3895f.mp4" type="video/mp4">
</video>

That's more like it, but what about the other wheels? Because we duplicated them, they no longer retain the history of this `polyCylinder` node.

To solve this, let's *replace* the mesh used for collisions by the other wheels such that they all use this one wheel.

- Read about [Replace Mesh](/documentation/active_rigid/#replace-mesh)

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128675467-d99ceadb-e34f-4dcf-ab08-2b17e11f44d7.mp4" type="video/mp4">
</video>

!!! warning "Important"
    Make sure the `Maintain Offset` is *unchecked*, since we want the local position of the wheel for each wheel.

    ![image](https://user-images.githubusercontent.com/2152766/128634388-cdd31dd8-7a3e-4601-9a45-f95006006ada.png)

<br>

#### Suspension Range

In a more realistic example, your vehicle model will have natural limits to how tall the suspension can be. For example in this truck example, there is a ceiling to the rear wheels.

![image](https://user-images.githubusercontent.com/2152766/128977415-e4a89832-8946-479c-8051-dff41b1e671f.png)

We can let the suspension remain soft and springy until a certain point, by providing a range of allowed Y values. The range is given by a value of `Translate Y Limit` that is greater than `0`, the amount being how many Maya units the wheel is allowed to move (typically centimeters).

!!! warning "Start Time"
    Keep in mind that any of the `Limit` attributes can only be changed on the start of your simulation. The start frame can be adjusted using the `Start Time` attribute on the `rScene` node.

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128637863-83560d01-9c5a-45c7-8c83-64f8fc0abf6b.mp4" type="video/mp4">
</video>

<br>

#### Race Track

Let's use the `Duplicate` command to lay some more track.

In my case, I found that the suspension was too loose, so I increased the `Guide Strength` to `0.4`.

- 👉 You can also lower with the `Friction` on the ground, to allow for the chassi to slide on contact.<br>
- 👉 You can also experiment with the chassi `Shape Extents` to make a more narrow vehicle<br>
- 👉 You can also experiment with the `Shape Offset` to raise the chassie higher off the ground (like a monster truck!)

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128634787-e11c84f9-a26b-4019-9c6e-70b8371c953f.mp4" type="video/mp4">
</video>

Combined with the engine, you can now make a proper race track!

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128640779-272f1953-f32e-488b-908e-5d4040605c33.mp4" type="video/mp4">
</video>

<br>

#### Bevelled Wheels

The wheels are currently very *sharp*. Once you add more detail to your environment, you may find that a bevelled wheel behaves more predictably and doesn't get stuck on equally sharp corners.

Since all wheels use the same geometry as one of the polyCylinders, all we need to do is bevel one of them.

<video controls autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128634875-89ab407a-ad5e-42fb-be2c-c4b8e040d8f2.mp4" type="video/mp4">
</video>

<br>

### Homework

Here are some suggestions for how to take the results of this tutorial further.

<br>

#### Mecabricks

A fantastic resource with *tons* of mechanical contraptions, ready to be turned into mechadolls and ragcars!

- https://www.mecabricks.com/en/library/selection

![image](https://user-images.githubusercontent.com/2152766/128638116-b9bfe6ce-12cd-4050-909a-308ae46187fc.png)

<br>

#### High-Resolution Model

Find any vehicle model and either parent the geometry directly to the chassi and wheels, or use Maya's Parent Constraint to keep things clean.

<br>

#### Steering

Given what you've learnt, how would you enable steering? How does it work on a real car?

??? tip "Click to reveal a hint"
    Is there a part missing between the chassi and wheel?
