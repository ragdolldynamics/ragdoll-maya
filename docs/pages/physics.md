## Constraint

Every object in the real world can move along 6 different axes, or 6 "degrees of freedom".

- Translate X
- Translate Y
- Translate Z
- Rotate X
- Rotate Y
- Rotate Z

A constraint limits one or more of these axes.

In Maya, the most typical form of constraint is locking a channel. This prevents this axis from changing.

- A value < 0 means `LOCKED`, meaning it may *not* move along this axis
- A value = 0 means `FREE`, meaning it *may* freely move along this axis
- A value > 0 means `LIMITED`, meaning it *may* move within the limited range of this axis

<br>

## Soft Constraints

Limits above 0 are referred to as "soft", because their amount of influence can be tuned using the `Stiffness` and `Damping` attributes. These can safely flex and can approach that of a hard constraint given enough stiffness and damping, but would struggle to reach a given target 100%.

<br>

## Hard Constraints

Limits *below* 0, typically -1, are referred to as "hard", because their influence is infinite. These should never flex, as even the slightest amount of flex means the constraint has *broken*. Leaving the solver in a poor state, struggling to keep up.
