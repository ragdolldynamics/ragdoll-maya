---
icon: "hardpin_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga12.png>
</div>

Tell a rigid *exactly* where to be.

<br>

### Usage

From the Ragdoll menu, select the `Hard Pin` option in the `Control` sub-menu.

![hardpin2](https://user-images.githubusercontent.com/2152766/127813976-aff21ea1-12e9-4ac4-9f67-7bcf3293e360.gif)

<br>

### Troubleshooting

Let's look at how things can go wrong when using Hard Pin.

<br>

#### Hard Conflict

Unlike a [Soft Pin](/guides/soft_pin), a Hard Pin will respect your command even it means disobeying physics.

In this example, two hard pins are asking for an impossible pose with limbs also being asked to stick together.

![hardpincaution](https://user-images.githubusercontent.com/2152766/127813952-e53d3b72-75c8-4bdb-a8aa-4ab5504a359d.gif)

A translate limit of `-1` means you want the limb to stick together *no matter what*. To apply an infinitely strong force to respect this relationship. The problem is that a Hard Pin is also an infinitely strong force, respecting a different relationship.

It's what happens when an unstoppable force meets an unbreakable object.

One possible solution to this is to make one of them soft, such as the translate limit.

![hardpinsoftlimits](https://user-images.githubusercontent.com/2152766/127814630-ef6b674c-86be-4be8-8e70-88c745907ebf.gif)

But be careful not to make it *too* soft, as you probably do want limbs to stick together most of the time.

![softtoolow](https://user-images.githubusercontent.com/2152766/127814636-735f730d-db7c-4bd7-9c18-5794f3c1b4da.gif)

<br>

### Limitations

What *can't* you do with Hard Pin?

- A rigid can currently have 1 Hard Pin each. This will be addressed in a future release.
- These cannot currently be exported, they are primarily intended for use interactively by the animator
