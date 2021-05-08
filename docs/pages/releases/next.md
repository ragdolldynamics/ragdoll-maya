---
title: Mimic
description: Automatically generate a control rig for your simulations to follow; softly, hardly, posely or all together!
---

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/117479428-3cfb0a00-af58-11eb-8ee7-d3a7a1aebd94.mp4" type="video/mp4">
</video>

Highlight for this release is **Mimic**!

- [**ADDED** Mimic](#mimic) Clean separation between simulation and animation
- [**ADDED** Bake Simulation](#bake-simulation) Fresh out the oven!
- [**ADDED** Preserve Attributes](#preserve-attributes) More control over the import process
- [**ADDED** Preserve Roots](#preserve-roots) Original roots are now preserved on export
- [**ADDED** Sleep](#sleep) Greater performance by putting rigids to sleep
- [**ADDED** Textures](#textures) Visualise mass, friction and restitution
- [**IMPROVED** Collide Off](#collide-off) Improved handling of disabled collisions
- [**IMPROVED** Quality of Life](#quality-of-life) Can never have too much of these
- [**FIXED** Startup Crash](#fixed-startup-crash) Were you one of the 2% of users having Maya crash on startup?
- [**FIXED** Scene Drawing in 2018](#scene-drawing-fixed) Maya 2018 and 2019 were acting up, no more!
- [**FIXED** Initial State](#fixed-initial-state) One less thing to worry about
- [**FIXED** Qt](#fixed-qt) Another less to worry about

<br>

Some awesome simulations, courtesy of Jason Snyman, a.k.a. The Wizard. xD

**Facial Rigging**

![konggif3](https://user-images.githubusercontent.com/2152766/117342860-99e4ba80-ae9b-11eb-96c2-32979bcf15fc.gif)

**Ragdolls have feelings too**

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/117312494-fedce800-ae7c-11eb-8abe-84db82ca7412.mp4" type="video/mp4">
</video>

**Wreck-it Zilla**

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/117312506-00a6ab80-ae7d-11eb-85cc-1960ea2e80d6.mp4" type="video/mp4">
</video>

**Wreck-it Warm-up**

Ever wondered how Zilla prepares for world domination?

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/117312500-ff757e80-ae7c-11eb-87a1-5ebe47a4fd6b.mp4" type="video/mp4">
</video>

<br>

## Mimic

Transition in and out of physics, in both pose-space and world-space, with the newly added *Mimic*.

<video autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/117479426-3bc9dd00-af58-11eb-9b5b-d6315240c7b2.mp4" type="video/mp4">
</video>

**Options In-Depth**

A step-by-step guide on what each option mean, there's quite a few of them!

<a href="https://youtu.be/Q84IU6BZJcQ" target="_blank"><img class="boxshadow" style="max-width: 600px;" src=https://user-images.githubusercontent.com/2152766/117536354-8009bb80-aff2-11eb-9b57-1f3e886bc204.png></a>

**Production Rig Example**

A closer look at the Fire Wolf.

> Courtesy of [Truong CG Artist](https://gumroad.com/truongcgartist?sort=page_layout#krsIT)

<a href="https://youtu.be/qS_R8rg9A30" target="_blank"><img class="boxshadow" style="max-width: 600px;" src=https://user-images.githubusercontent.com/2152766/117538190-f7444d00-affc-11eb-9174-f02324837c2f.png></a>

<br>

### Multiple Mimic

Mimic is a replica of your control hierarchy, and there's no limit to the number of replicas you can make. The final force applied to your rigid bodies is the *sum* of constraints applied.

![multimimic](https://user-images.githubusercontent.com/2152766/117537939-d3ccd280-affb-11eb-8a16-0583f3e4e415.gif)


<br>

### Order Independent

The controls in character rigs typically don't form a linear hierarchy. They're in some offset group, or in a different part altogether hanging together with constraints. That are animated, for space switching and what not.

Mimics don't mind.

![mimicorderindependent](https://user-images.githubusercontent.com/2152766/117538067-59508280-affc-11eb-8ba4-85149a189ca6.gif)

<br>

### Partial Chain

Sometimes you only want a *little* bit of control.

![partialmimic](https://user-images.githubusercontent.com/2152766/117538155-c3692780-affc-11eb-956c-7087a5bb441d.gif)

<br>

## Bake Simulation

You can now convert physics into keyframes with `Bake Simulation`.

![bakesimulation](https://user-images.githubusercontent.com/2152766/116553048-9c6e6f80-a8f1-11eb-8c6a-2242b6e67d83.gif)

> I did not edit this GIF, it really was that fast! :D

<br>

**Tutorial**

<a href="https://youtu.be/PN6HaZtAKmQ" target="_blank"><img class="boxshadow" style="max-width: 600px;" src=https://user-images.githubusercontent.com/2152766/117301392-85d89300-ae72-11eb-9073-542929c60483.png></a>

<br>

**Bake Duration**

It'll tell you how much time was spent baking too.

![headsupmessage](https://user-images.githubusercontent.com/2152766/117143200-7db42100-ada8-11eb-8ee7-1894b017e92c.gif)

**Bake Options**

There are a few more options to choose from, with more to come.

![image](https://user-images.githubusercontent.com/2152766/117143294-945a7800-ada8-11eb-8c73-3fe479650a16.png)

<br>

## Preserve Attributes

You now have the option to preserve attributes when importing, for when you'd rather stick with the default values.



<br>

## Preserve Roots

Exported files now remember what their original roots were.

The original root of chains aren't important to Ragdoll. Whether the spine was a chain followed by the left and right arm, or whether the spine and left arm were part of one chain followed by the neck and right arm makes no difference.

Consider these two characters.

![image](https://user-images.githubusercontent.com/2152766/116895992-aa8ef980-ac2b-11eb-87f5-001d20182d6a.png)

Notice how in the front character, one chain starts at the hip and goes out into the arm, whereas in the back character the spine is a single chain as you may expect?

Regardless of how you authored it, to Ragdoll these characters are identical. Ragdoll doesn't bother with hierarchies, everything happens in worldspace. The hierarchy is between you and Maya.

**However**

What if you wanted to *import* just one of the roots? You can import only onto the selected controls, but you can't import *part* of a network of chains like a full ragdoll. It's either a complete character, or no character at all.

In the case of the foreground character, you could import the screen-left arm, but not the screen-right. Not without importing the whole spine.

This release preserves the original root, such that you can isolate an import onto the same chain you originally authored.

<br>

## Sleep

It is now possible to reap additional performance benefits in situations where one or more rigids remain immobile for a given number of frames.

The behavior can be tuned via two attributes on each `rdRigid` node.

| Attribute | Description
|:----------|:----------
| `Wake Counter` | How many frames of inactivity before I fall asleep?
| `Sleep Threshold` | How low of a force should be applied before I start counting?

In practice, you'll likely only want to tweak the Wake Counter to some reasonable value like 5 or 20 frames of immobility. The default value of 0 means they'll never fall asleep. Like a proper insomniac or new parent.

!!! hint "Caveat"
    Currently, the wake counter is not reset when you *rewind*, so it's possible to have them fall asleep on frame 20, rewind to frame 19 and have the counter reset and keep them awake past frame 20. It's unlikely to affect you, and will be addressed in a later release.

![sleep](https://user-images.githubusercontent.com/2152766/117123291-c19a2c80-ad8e-11eb-89d8-d0c1e2418ed1.gif)

<br>

## Textures

As you author your ragdolls, the distribution of mass can play a big role. But it can be tricky to balance something you cannot see, smell or touch.

With this release, you're able to see (but not smell, I promise) the masses in each rigid using the handy new `Texture` attribute and when your viewport is set to Textured mode (the `6` key on your keyboard).

> Thanks to Jason Snyman for the idea!

![massvis1](https://user-images.githubusercontent.com/2152766/117137822-3165e280-ada2-11eb-9a96-2e32d00edac2.gif)

**Normalised Distribution**

Notice how the colors even out to always give you pure white for the maximum weight in any of the rigids in the scene they are part of, and approaching black for anything less. No need to manually specify min/max values!

![massvis2](https://user-images.githubusercontent.com/2152766/117137820-30cd4c00-ada2-11eb-9a07-a4a3373b2781.gif)

**Friction and Restitution**

These can be visualised too.

![massvis3](https://user-images.githubusercontent.com/2152766/117137834-35920000-ada2-11eb-951e-cc3073638352.gif)

!!! info "Maya 2018 Caveat"
    In Maya 2018, consolidation is disabled to facilitate this shader. It shouldn't affect anything of value, you probably don't even know what it is. But if you'd rather it didn't do that, untick the "Maya 2018 Consolidate World Fix" in the Ragdoll Preferences and reload the plug-in or restart Maya.

<br>

## Collide Off

Rigids have always been able to ignore contacts with `Collide: Off`

![disablecollide3](https://user-images.githubusercontent.com/2152766/116609863-ca24da00-a92c-11eb-869e-daf642cdd229.gif)

The problem here is subtle, but has been present since the beginning of Ragdoll. It mostly makes itself known once there is a constraint between a rigid with `Collide: On` and a rigid with `Collide: Off`.

![disablecollide1](https://user-images.githubusercontent.com/2152766/116609454-4e2a9200-a92c-11eb-8587-9dc38ab944c8.gif)

Notice how with `Collide: Off` the upper part of the "creature" is more wobbly? As if the effect of the constraint has somehow dimished? That's not right. Unless there are contacts involved, disabling them shouldn't have an effect on the simulation.

With this release, it behaves as you would expect.

![disablecollide2](https://user-images.githubusercontent.com/2152766/116609556-6b5f6080-a92c-11eb-9443-3a67ea026260.gif)

<br>

## Quality of Life

A number of improvements were made to make working with Ragdoll more pleasant!

<br>

### Translate Limit Rendering

The translate limit is making an appearance!

This should make it just a *tiny bit* easier to work with, now that it's clear which axes are actually free. Letting you see whether they are constrained in 3D, 2D or *1D*. All the D's!

![translatelimit3](https://user-images.githubusercontent.com/2152766/117270305-fa9ad580-ae50-11eb-9258-fbfb08bcbd12.gif)

**Edit Limit**

Using the same method as editing rotate limits, they can be rotated (and moved!).

![linearlimitedit1](https://user-images.githubusercontent.com/2152766/117269728-70eb0800-ae50-11eb-9a25-76654a48a70e.gif)

**Soft Limit**

Like rotate limits, these can also be made soft!

![linearlimitsoft](https://user-images.githubusercontent.com/2152766/117269725-70527180-ae50-11eb-93db-0b95c40feb91.gif)

<br>

### Constraint Rendering

Have you ever noticed constraints looking real nervous?

You now needn't lose any more sleep over it, as they now render flicker-free. :D

**Before**

![aliasingbefore](https://user-images.githubusercontent.com/2152766/116896826-8253ca80-ac2c-11eb-8e41-c1b22f83f388.gif)

**After**

![aliasingafter](https://user-images.githubusercontent.com/2152766/116896832-82ec6100-ac2c-11eb-9026-9e321ade903b.gif)

### Constraint Interactivity

You may also have noticed how when you edit one of two constrained rigids, how things get all whack?

**Before**

![consraintsdrawbefore](https://user-images.githubusercontent.com/2152766/116661205-fface000-a98b-11eb-848a-011e81e1ce19.gif)

Best case you'd at least get constraints to stick together as you make changes.

![constraintsdrawafter](https://user-images.githubusercontent.com/2152766/116661165-f15ec400-a98b-11eb-8b77-4ea040777f80.gif)

**After**

And oh golly how ugly it was. No more! Yay! 🤩

![constraintrendering](https://user-images.githubusercontent.com/2152766/117299037-f92cd580-ae6f-11eb-96e4-7f236e8a92ab.gif)

![perfectconstraints](https://user-images.githubusercontent.com/2152766/116902741-6a337980-ac33-11eb-8a0e-62bbb0909187.gif)

<br>

### Constraint Colors

When rigids have *multiple* constraints, it can be hard to tell them apart visually given they all share the same red/green colors. And if you're amongst the colorblinds things are even more challenging.

This release enables you to give some extra flare to your constriants, by editing the `Twist` (X-axis) and `Swing` (YZ-axes).

![constraintcolors3](https://user-images.githubusercontent.com/2152766/116964947-9dfab780-aca4-11eb-978f-b896756a5731.gif)
![customconstraintcolor2](https://user-images.githubusercontent.com/2152766/116921663-2bf68400-ac4c-11eb-874c-dcfcd3e84597.gif)

<br>

### Trajectory on Selected

There's now an option to isolate trajectories to selected rigids only.

![drawselected](https://user-images.githubusercontent.com/47274066/117424734-030b1300-af1a-11eb-9edd-50b1f500afdf.gif)

<br>

### Load on File Open

There are 3 ways to load Ragdoll.

1. Maya's Plug-in Manager
2. Python's `cmds.loadPlugin("ragdoll")`
3. Opening a file with Ragdoll in it

When Ragdoll is loaded, it appends to a special environment variable Maya uses to look for icons in the Outliner called `XBMLANGPATH`. Because of course that's what it is called, why do you have that look on your face?

Anyway, as it happens, if the Outliner was given a chance to draw icons *before* Ragdoll added this variable then it'd go ahead and draw a generic, non-pleasant-looking icon like this.

This release fixes that. 🥰

| Before | After
|:---|:---
| ![image](https://user-images.githubusercontent.com/2152766/116661797-e5273680-a98c-11eb-867a-950efc7946e3.png) | ![image](https://user-images.githubusercontent.com/2152766/116661953-13a51180-a98d-11eb-8e3b-eada84f1fd7e.png)

<br>

### Upgrade on File Open

Like above, there was another issue when loading the plug-in alonside opening of scenes, which had to do with upgrades.

Normally, what happens is this.

1. Scene is opened
2. Ragdoll checks to see if any nodes are older than the version you use
3. If they are, it then checks to see whether any of them need upgrading
4. If any are, it upgrades those
5. Scene open complete

But since the plug-in is loaded *during* scene open, Ragdoll wasn't given a chance to check it first.

This has now been fixed.

!!! info "Install on Idle"
    This changes the initialisation mechanism somewhat, if this causes any issues for you, set the `RAGDOLL_INSTALL_ON_IDLE` environment variable to revert to the old behavior. It won't be able to upgrade on scene open unless you load the plug-in first, but that's the only thing you're missing out on.

<br>

### Node Editor Icons

Our precious icons now appear in the node editor too!

| Before | After
|:-----|:-------
| ![image](https://user-images.githubusercontent.com/2152766/116910190-26457200-ac3d-11eb-9d96-e120c9331cf5.png) | ![image](https://user-images.githubusercontent.com/2152766/116910200-2a718f80-ac3d-11eb-9511-832c80c10196.png)

<br>

### Passive Initial State

Here's a subtle one.

In previous releases, the initial state is automatically updated on the 2nd frame of the simulation to wherever a rigid was on the 1st frame. Even if you modified the position interactively with manipulators, or via curves in the Graph Editor, or the channel box, and so on.

It even updated when a rigid was affected by passive input, like a Hard Pin, which meant you lost track of the original initial state whenever you disabled the hard pin.

This release addresses that by only automatically updating the initial state if a rigid is active on the start frame.

![initialstatekinematic](https://user-images.githubusercontent.com/2152766/116855122-bdd0a380-abf0-11eb-9d00-aea9328b1d5a.gif)

Notice how I can disable Hard Pin and have the rigids return to where they were before they got pinnned? It's what you would expect.

<br>

### Passive to Active and Back Again

Ragdoll tries to clean up after itself by removing constraints no longer in use. When a rigid is passive, it can no longer be affected by constraints, so those constraints are deleted.

However, active rigids can still be influenced by a passive rigid, and Ragdoll was a little too aggressive in removing those constraints too.

This release fixes that.

![passiveandback](https://user-images.githubusercontent.com/2152766/116859712-5585c000-abf8-11eb-80ce-65e50e1db691.gif)

<br>

### Undo and Attribute Order

Whenever you delete physics and *undo*, the order in which proxy attributes would appear on your controllers would go all whack.

This is basic-Maya, it loves doing this. But now love goes both ways, and we are much happier. 🥰

**Before**

![deleteorderbad](https://user-images.githubusercontent.com/2152766/116973674-c7bbda80-acb4-11eb-9a29-05c4e47a6e71.gif)
![deleteattr](https://user-images.githubusercontent.com/2152766/116973679-c8ed0780-acb4-11eb-940f-0f67badfe7b1.gif)

**After**

![undofixed](https://user-images.githubusercontent.com/2152766/116987783-63eedd00-acc7-11eb-9dea-b5fe663a3cca.gif)

<br>

### Control Rendering

Controls give you a preview of what the rigid they control look like.

These are special in that Maya doesn't actually need them. Ragdoll doesn't actually need them either. They are *exclusively* for-your-eyes-only.

And due to Maya only updating things it absolutely needs to whenever rendering anything, these won't get updated unless Ragdoll explicitly tells them to. So far, they've been told to update whenever the selection changed, which can end up looking bad.

This has now been improved!

**Before**

![controlrenderin](https://user-images.githubusercontent.com/2152766/116987174-a368f980-acc6-11eb-944f-9b8273520687.gif)

**After**

![controlrendering21](https://user-images.githubusercontent.com/2152766/116987318-cdbab700-acc6-11eb-91ed-4f86b3f5058f.gif)

<br>

## Fixed Startup Crash

On plug-in load, Ragdoll would check your licence. Under rare circumstances (2 out of 100 users reported it happening) this would be enough to put Maya under, instantly and without warning.

This has now been fixed.

<br>

## Fixed Initial State

An error was introduced between 2021.04.23 and 2021.04.28 leading to an issue with updating the initial pose via the Channel Box or Graph Editor.

This got addressed on the same day and released unofficially as 2021.04.30, and is now officially part of the latest version.

> Thanks to Niels Dervieux for reporting this bug!

**Before**

![initialstatebug_before](https://user-images.githubusercontent.com/2152766/116550808-19e4b080-a8ef-11eb-86a0-dfc4ec6d49cf.gif)

**After**

![initialstatebug_afte](https://user-images.githubusercontent.com/2152766/116550811-1a7d4700-a8ef-11eb-916c-42eacac59f7a.gif)

<br>

## Fixed Qt

Whenever you clicked `Import Physics` in the Import Physics Option Window, it would needlessly shout at you.

```py
# RuntimeError: Internal C++ object (WidgetHoverFactory) already deleted.
```

No more!

<br>

## Scene Drawing in 2019

Maya was misbehaving in 2018-2019, refused to draw the scene visualisation correctly. No longer!

**Before**

![image](https://user-images.githubusercontent.com/2152766/117452038-33af7480-af3b-11eb-9fcd-97e93678777e.png)

**After**

![image](https://user-images.githubusercontent.com/2152766/117451913-0e226b00-af3b-11eb-90cc-5bfec7f463b8.png)
