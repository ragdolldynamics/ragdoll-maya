Highlight for this release is **Automatic Initial State**!

- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync
- [**FIXED** Animated Rigid Attributes](#animated-rigid-attributes)
- [**FIXED** Pre-Start Frame](#pre-start-frame) Pose is now reset prior to hitting the solver start frame
- [**FIXED** Explosion on Initial State](#explosion-on-initial-state) More robust detection of when to actually update the initial state

<br>

## Animated Rigid Attributes

The previous release broke your ability to animate anything on a rigid, e.g. `rdRigid.linearDamping`. That's been all patched up!

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.

<br>

## Pre-Start Frame

A bug in a prior version caused frames ahead of the start frame to not reset correctly, unless you explicitly visited the start frame. E.g. skipping from frame 100 directly to 1 rather than from 2 to 1 wouldn't look right. Coupled with the next auto-initial-state feature, this could break a pose. This has now been patched up!

<br>

## Explosion on Initial State

Ragdoll could mistakenly treat a broken simulated first frame as the new and correct initial state. Detecting that stuff is hard! Now it's doing a better job, but keep an eye out for when your start pose breaks, that should never happen.

Also don't forget that this fancy new shiny feature can be disabled under Ragdoll -> System -> Ragdoll Preferences.

<br>

## Shear

The enemy of any animation, shear is scale's ugly brother. Ragdoll now accounts for shear, even though you are strongly advised never to introduce it willingly.