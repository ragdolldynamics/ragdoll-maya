---
title: Level of Detail
icon: "hair2_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=https://user-images.githubusercontent.com/2152766/148948560-aee1dae3-4844-4dcd-bc36-274d0b263f48.png>
</div>

Light-weight or heavy-duty? How about both!

<br>

### Level of Detail

Setup your character once with all bells-and-whistles, and interactively pick which level of detail to use for your simulation in a given situation.

**Usecases**

1. Body at `Level 0`, fingers at `Level 1`
2. Props at `Level 1`, muscles at `Level 2`
3. Major masses at `Level 0`, extremities at `Level 1` and `Level 2`

For example, here's a Wasp character with 3 levels of increasing detail.

https://user-images.githubusercontent.com/2152766/148215131-87811017-307a-4363-9ba8-a9a7d816f29b.mp4 controls

As you'd expect, it'll record only the currently active markers.

https://user-images.githubusercontent.com/2152766/148215124-5a937bec-0c34-4fbb-83b0-54b09646ae1e.mp4 controls

<br>

#### Workflow

Here's how it works.

1. Give each marker a "level", such as `1`
2. Tell solver which "level" to solve at, such as `1`

https://user-images.githubusercontent.com/2152766/148227206-42a1e54b-6185-46c2-9d90-0d720c657add.mp4 controls

And that's it! Any marker with a matching level is simulated and recorded.

<br>

#### Operators

What does each level mean? The answer lies in the "operator".

| Operator  | Description
|:----------|:-----------
| `Less Than` | If the `Marker Level` is less than (or equal) to the `Solver Level`, simulate it.
| `Greater Than` | If the `Marker Level` is greater than (or equal) to the `Solver Level`, simulate it.
| `Equal` | If the `Marker Level` is *equal* to the `Solver Level`, simulate it.
| `NotEqual` | If the `Marker Level` is *not equal* to the `Solver Level`, simulate it.

With these, you can use each level for..

1. An increasing amount of detail
2. An increasing amount of *reduction*
3. Something completely custom

With `Equal` and `NotEqual` operators, you can have some markers appear or disappear on particular levels, enabling endless combinations.

**Roadmap**

This should cover a majority of cases, but there are things you cannot yet do, but will be able to in the future.

1. `Capsule` on one level, `Mesh` on another. For higher-resolution contacts.
2. Dense hierarchy of controls at one level, sparse at another. For e.g. twist joints versus a simple 2-joint chain, or a densely packed spine versus just hip and torso controls.

<br>

#### Algorithm

For the geeks out there, here's what the underlying algorithm looks like in Python.

```py
# Membership types
Minimum = 1  # Present at this level and higher
Maximum = 3  # Present at this level and lower
Only = 4     # Only present at this level
Not = 5      # Present at all levels *except* this one

markers = [
    {"name": "hip", "level": 0, "membership": Minimum},
    {"name": "spine", "level": 0, "membership": Minimum},
    {"name": "neck", "level": 0, "membership": Minimum},
    {"name": "head", "level": 0, "membership": Minimum},
    {"name": "L_upper_leg", "level": 0, "membership": Minimum},
    {"name": "L_lower_leg", "level": 0, "membership": Minimum},
    {"name": "R_hand", "level": 1, "membership": Minimum},
    {"name": "L_foot_box", "level": 1, "membership": Maximum},
    {"name": "L_foot_convex", "level": 2, "membership": Minimum},
    {"name": "R_toe_capsule", "level": 2, "membership": Not},
    {"name": "R_toe_convex", "level": 2, "membership": Only},
]

def resolve(level):
    print("Level %d" % level)
    for marker in markers:
        if marker["membership"] == Minimum and marker["level"] <= level:
            print(" - {name} ({level})".format(**marker))

        if marker["membership"] == Maximum and marker["level"] >= level:
            print(" - {name} ({level})".format(**marker))

        if marker["membership"] == Only and marker["level"] == level:
            print(" - {name} ({level})".format(**marker))

        if marker["membership"] == Not and marker["level"] != level:
            print(" - {name} ({level})".format(**marker))

resolve(0)
resolve(1)
resolve(2)
```

Run this, and this is what you'll find.

```bash
Level 0
 - hip (0)
 - spine (0)
 - neck (0)
 - head (0)
 - L_upper_leg (0)
 - L_lower_leg (0)
 - L_foot_box (1)
 - R_toe_capsule (2)
Level 1
 - hip (0)
 - spine (0)
 - neck (0)
 - head (0)
 - L_upper_leg (0)
 - L_lower_leg (0)
 - R_hand (1)
 - L_foot_box (1)
 - R_toe_capsule (2)
Level 2
 - hip (0)
 - spine (0)
 - neck (0)
 - head (0)
 - L_upper_leg (0)
 - L_lower_leg (0)
 - R_hand (1)
 - L_foot_convex (2)
 - R_toe_convex (2)
```
