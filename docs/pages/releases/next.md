- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync
- [**FIXED** Backwards Compatibility](#backwards-compatibility) Last release broke our precious example scenes!
- [**FIXED** Accurate Gravity](#accurate-gravity) The gravity indicator on the scene is now always truthful

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.

<br>

### Backwards Compatibility

What does breaking backwards compatibility of a dynamics solver look like?

**Original**

![ragdoll20201201_4](https://user-images.githubusercontent.com/2152766/112307337-be445900-8c98-11eb-82a7-30a477947051.gif)

**Last Release**

![bavckwardscomp](https://user-images.githubusercontent.com/2152766/112271306-afe34680-8c72-11eb-8058-94f887cf5581.gif)

He's the same person! Only the circumstances have changed. :D This has now been fixed, and all previous examples now open and run as expected!

<br>

### Accurate Gravity

The indicator used to face in the Y-axis of wherever the node was facing. That wasn't true. It's now accurate no matter how you spin it around, including a potential Z-up axis!

**Before**

![badgravity](https://user-images.githubusercontent.com/2152766/112306957-4d04a600-8c98-11eb-8185-17fc5e38d1a1.gif)

**After**

![accurategravity1](https://user-images.githubusercontent.com/2152766/112306961-4d9d3c80-8c98-11eb-9df8-b0d2c905360a.gif)
