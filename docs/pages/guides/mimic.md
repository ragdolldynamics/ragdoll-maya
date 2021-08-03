<div class="hero-container">
    <img class="hero-image" src=/car14.png>
</div>

Generate an animator-friendly control rig from a rigid chain or tree.

<br>

### Usage

From the Ragdoll menu, select the `Mimic` option in the `Controls` sub-menu.

![mimic2](https://user-images.githubusercontent.com/2152766/127834132-5184b423-d930-48b7-8843-c83e6f2c2b49.gif)

<br>

### Mimic

Transition in and out of physics, in both pose-space and world-space, with *Mimic*.

<video autoplay="autoplay" loop="loop" width="100%">
    <source src="https://user-images.githubusercontent.com/2152766/117479426-3bc9dd00-af58-11eb-9b5b-d6315240c7b2.mp4" type="video/mp4">
</video>

**Options In-Depth**

A step-by-step guide on what each option mean, there's quite a few of them!

<a href="https://youtu.be/EJmWCQ3n5e4" target="_blank"><img class="boxshadow" style="max-width: 450px;" src=https://user-images.githubusercontent.com/2152766/117536354-8009bb80-aff2-11eb-9b57-1f3e886bc204.png></a>

**Production Rig Example**

A closer look at the Fire Wolf.

> Courtesy of [Truong CG Artist](https://gumroad.com/truongcgartist?sort=page_layout#krsIT)

<a href="https://youtu.be/LezmVuIEDaw" target="_blank"><img class="boxshadow" style="max-width: 450px;" src=https://user-images.githubusercontent.com/2152766/117538190-f7444d00-affc-11eb-9174-f02324837c2f.png></a>

<br>

#### Multiple Mimics

The Mimic is a replica of your control hierarchy, and there's no limit to the number of replicas you can make. The final pose is then the *sum* of all mimics.

![multimimic](https://user-images.githubusercontent.com/2152766/117537939-d3ccd280-affb-11eb-8a16-0583f3e4e415.gif)

<br>

#### Order Independent

The controls in character rigs typically don't form a linear hierarchy. They may be in some "offset group", or in a different location altogether connected with constraints that are animated for space switching and what not.

Mimics don't mind.

![mimicorderindependent](https://user-images.githubusercontent.com/2152766/117538067-59508280-affc-11eb-8ba4-85149a189ca6.gif)

<br>

#### Partial Chain

Sometimes you only want a *little* bit of control.

![partialmimic](https://user-images.githubusercontent.com/2152766/117538155-c3692780-affc-11eb-956c-7087a5bb441d.gif)

!!! hint "Pro tip"
    You can also *delete* and *reparent* the resulting hierarchy of mimics, if all you wanted was for example the first few rigids in a hierarchy.
