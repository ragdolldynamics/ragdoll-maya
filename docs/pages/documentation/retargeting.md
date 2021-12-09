---
title: Retargeting
icon: "retarget_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=/car12.png>
</div>

The fundamental building block to Ragdoll, for "reverse motion capture" or Animation Capture.

<br>

#### Retarget

We've talked a lot about "retargeting". But what *is* that?

Per default, markers are recorded onto the controls you assigned, this is called `Rig to Rig`.

![image](https://user-images.githubusercontent.com/2152766/134169658-39590bbf-bbca-41dc-af3b-de20e69e9aed.png)

But often times, rigs are more complicated and what you want is for the simulation to look at one set of nodes, but record onto another. This is called `Joint to Rig`, but can be from any source. Even other controls (like FK to IK).

![image](https://user-images.githubusercontent.com/2152766/134169635-e0a751c8-f06b-4dac-a459-50118d04821f.png)

!!! info "The Old Days"
    Think about how you would accomplish this using the `Active Rigid` or `Active Chain` commands. That would be a *huge* pain, but not with markers!

<br>

#### Reassign

Over in [Demo 2 - Ragdoll](#demo-2---ragdoll) we "reassigned" already marked controls. What does that mean?

In that example, we've assigned our FK controls directly, which means Ragdoll would grab the translation and rotation from those controls during simulation. But what we really wanted was the IK controls.

But! We couldn't just assign to the IK controls directly, since they are *indirectly* rotating a characters limbs. So instead, we `Reassign` the markers previously made onto the underlying joints that follow IK around.

We then also `Retarget` them, since they would have otherwise been recorded onto the original FK controls.

<br>

#### Reparent

Sometimes, you change your mind.

https://user-images.githubusercontent.com/2152766/134465284-f9a3bd04-9392-4f33-a161-390cbe9049d2.mp4 controls

Success!

https://user-images.githubusercontent.com/2152766/134465285-87eacea9-4b93-4526-980e-585bbc92151b.mp4 controls
