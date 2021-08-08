---
icon: "car_black.png"
---

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/128611375-82a3f65e-7c89-4e42-a40e-3ae1b10c12ce.mp4" type="video/mp4">
</video>

### Rally Car

In this tutorial, we will create the wheels and chassi of a car in a semi-realistic fashion. It will have realistic suspension and limited to spinning along only one axis, but it won't be able to steer.

**You will learn**

- ✔️ How to make geometry *dynamic*
- ✔️ How to *constrain* two rigids
- ✔️ How to make wheels with translate and rotate "*limits*"
- ✔️ How to build a *static environment*

<br>

### Motivation

Before we dive in, let's first consider why would you simulate a car in the first place? To answer this I invite you to take a gander at this clip here.

<video autoplay class="poster" muted="muted" loop="loop" width=100%>
    <source src="https://user-images.githubusercontent.com/2152766/124288785-81b2b400-db49-11eb-8b36-e61e9246ecdb.mp4" type="video/mp4">
</video>

If we ignore that characters for a moment and look at just the car itself; there are a few things going on that would be both challenging and time consuming to animate by hand.

1. Wheel suspension responding realistically to the ground
1. Chassi responding realistically to the wheels
1. Contact with and response to debree on the ground
1. Wheels loosing grip due to on debree
1. Matching the wheel rotation to contact with the ground

The subtle detail alone is enough to make a senior animator sweat, not to mention *changes* to the environment would require an almost complete redo of all of that work.

<br>

### Setup

![image](https://user-images.githubusercontent.com/2152766/128613548-df9b109a-4aeb-4489-ac43-c3428578af09.png)

In the upper-left corner of the above video, you can spot a wireframe of the collision shapes used for the car. We are going to recreate this without the 1 million polygon model to keep things simple, the setup will be near identical with one major difference I'll point out once we get to it.

- Car facing the Z axis
- Wheel along X axis
- X-axis is a good spin axis
- Keeps Y-axis along the world up

