---
title: Cycle Protection
icon: "swirl_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga14.png>
</div>

Guard against cycles during authoring of physics.

<br>

### Usage

From the Ragdoll menu, select `Preferences` under the `System` sub-menu to enable or disable cycle protection.

<br>

### Cycle Protection

Cycle warnings are generally bad but *especially* bad for Ragdoll. Understanding when they happen and where they come from can be difficult, especially in complex setups.

Ragdoll includes **Cycle Protection** to help you spot potential cycles *before they happen*!

![cycleprotection](https://user-images.githubusercontent.com/2152766/115708838-6452b400-a368-11eb-8a4d-8765650e82fe.gif)

Notice how making a passive rigid here would have resulted in it becoming a child of an otherwise active hierarchy. That would have been bad!

#### Protected Commands

These commands will try and protect your from cycles.

- ✔️ Active Rigid
- ✔️ Active Chain
- ✔️ Convert Rigid

All other commands is already safe to use and shouldn't cause any cycles.

#### FAQ

These are some of the things you might want to learn more about.

!!! question "How does it work?"
    Whenever a new Passive Rigid or Active Chain (with passive root) is being created, Ragdoll is asked to evaluate the world transformation of the node you are attempting to make dynamic. The solver should *not* be bothered to simulate anything during this encounter, because if it did then that would mean a cycle is about to happen.

    Why?

    Because passive rigids pass data *into* the solver. Namely, the position and orientation of the node you are attempting to turn into a passive rigid. It cannot both pass and receive data. If it is to *receive* translate/rotate from the solver, then that's an active rigid.

!!! question "Is it accurate?"
    Very.

    Character rigs can get very complex; how can Ragdoll distinguish between an actual *parent* being active, and a node acting like a parent via something like Maya's Parent Constraints (i.e. a "broken rig")?

    The answer is that the feature builds on Maya's own evaluation mechanism to figure out whether a node is dependent on the solver or not. The mechanism is surprisingly simple.

    ```py
    def is_dynamic(transform, scene):
        """Does `transform` in any way affect `scene`?"""
        scene["clean"] = True

        # Pull, but do not bother actually serialising it
        transform["worldMatrix"].pull()

        return not scene["clean"].read()
    ```

    By pulling on `worldMatrix` we ensure all hierarchy and constraints is taken into account, and by not actually retrieving value we limit the computational cost to dirty propagation only - as opposed to actually reading and serialising the 16 values that make up the matrix.

!!! question "Can it be disabled?"
    Yes.

    The protection is only happening when interacting with Ragdoll via the UI menu items. The API remains unaffected and there is an option in the Preferences to disable it in the UI as well.

    ![image](https://user-images.githubusercontent.com/2152766/115709313-007cbb00-a369-11eb-99f2-77dbde3b4d5c.png)
