---
title: Constraints
icon: "constraint_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/yoga12.png>
</div>

Establish a relationship between two markers.

<br>

### Constraints

You can constrain one marker to another!

| Constraint Type | Description
|:----------------|:-------------
| Weld Constraint | Simplest of constraints, welds two markers together; no change to their distance or relative orientation is allowed. This is akin to the Maya `Parent Constraint`
| Distance Constraint | Maintain a minimum, maximum or total distance between two markers.
| Pin Constraint | Match a position and orientation in worldspace, similar to `Drive Space = World`.

https://user-images.githubusercontent.com/2152766/138263114-b9a9e3a8-230c-4676-a757-073cfc42af70.mp4 controls

<br>

#### Weld

Maintain the position and orientation of one marker relative another from the first frame onwards.

https://user-images.githubusercontent.com/2152766/138453515-936e7297-b40e-46bf-a63e-bb1153f8f166.mp4 controls


https://user-images.githubusercontent.com/2152766/138267073-dfd2e913-9a92-437b-8ba3-b99fe24223b4.mp4 controls

<br>

#### Distance

A simple but versatile constraint with animatable distance.

**Maintain Start Distance**

Whatever the distance between two markers, it will be maintained throughout a simulation.

https://user-images.githubusercontent.com/2152766/138162535-8bc269cf-e0f0-47d6-8bf2-ec124b1a62f0.mp4 controls

**Minimum Distance**

Alternatively, only respond to when two controls get too close.

https://user-images.githubusercontent.com/2152766/138162536-a208a381-d7c1-4f0d-821e-a1e93b95a24d.mp4 controls

**Maximum Distance**

Conversely, keep markers from getting too far *away* from each other.

https://user-images.githubusercontent.com/2152766/138162537-ce2ed22b-5f1c-4565-80e9-f24f51776950.mp4 controls

**Custom Distance**

Or go all-in, with both a minimum *and* maximum distance, for the most complex behavior.

https://user-images.githubusercontent.com/2152766/138162542-572f72e1-6420-46be-852c-092352a267e6.mp4 controls

**Offsets**

Control at which point on a control to measure the distance.

https://user-images.githubusercontent.com/2152766/138123321-31dadba0-175b-46f9-8116-e3b6416c4fca.mp4 controls

**Animated Distance**

Both min and max distance, along with stiffness and damping, can be animated for some pretty rad effects.

https://user-images.githubusercontent.com/2152766/138125038-390d999d-dad3-474d-92b9-83be7f5fbea1.mp4 controls

**Hard Distance**

A `Stiffness = -1` means the constraint is "hard". It will not accept any slack or "springiness".

In this example, the distance is animated whilst soft, and transitioned into a hard constraint. Notice how it snaps into place once hard.

https://user-images.githubusercontent.com/2152766/138226874-2fafa5c1-f8c3-4143-b6f4-e18a3b77fe87.mp4 controls

!!! hint "Limitation"
    A limitation of a hard constraint is that the distance cannot be animated whilst hard. You can however animate it between values of -1 and above, to transition to and from hard to soft.

<br>

#### Pin

Pin the translation and/or rotation of a Marker in worldspace.

https://user-images.githubusercontent.com/2152766/138454713-ceaedf52-3777-4af8-81de-e543318316f5.mp4 controls
