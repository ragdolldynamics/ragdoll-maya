---
hidden: true
title: New Tutorials
description: All new and important information about the basic tools and workflows for Ragdoll
---

Highlight for this release is **new tutorials!**

- [**ADDED** Tutorials](#tutorials) Three new tutorials covering basics up to anatomical correctness!
- [**ADDED** Pivot Editor](#pivot-editor) Faster wheels and knees with this new UI
- [**ADDED** Personal UI](#personal-ui) More accurate licence information in the Ragdoll UI
- [**ADDED** Social Media](#social-media) We're everywhere now!
- [**FIXED** Worldspace Trajectories](#worldspace-trajectories) Now drawn correctly, in worldspace
- [**FIXED** Sphere Rendering](#sphere-rendering) Minor tweak to the look of the `Sphere` shape type
- [**FIXED** Floating Server Details](#floating-server-details) Minor bug fix for floating licence users

<br>

### New Tutorials

Three new tutorials from basics to intermediate, with more to come!

<br>

#### Bouncing Ball

Learn the fundamentals of Ragdoll in this classic animation tutorial. 

https://user-images.githubusercontent.com/2152766/130355317-1874d90b-c366-43bc-a803-18467b9dc3bf.mp4

<div class="hboxlayout">
<a href="/tutorials/bouncing_ball" class="button blue"><b>View Tutorial</b></a>
</div>

<br>

#### Rally Car

Build upon the skills learnt with a bouncing ball to combine several rigids into a car (with an engine!)

https://user-images.githubusercontent.com/2152766/130355317-1874d90b-c366-43bc-a803-18467b9dc3bf.mp4

<div class="hboxlayout">
<a href="/tutorials/rally_car" class="button blue"><b>View Tutorial</b></a>
</div>

<br>

#### Manikin

Construct a full ragdoll from any rig, even your own custom one!

https://user-images.githubusercontent.com/2152766/130355301-d1e45c50-045c-4f9e-9394-6e665ac770b2.mp4

<div class="hboxlayout">
<a href="/tutorials/manikin" class="button blue"><b>View Tutorial</b></a>
</div>

<br>

### Personal UI

The Licence Window at the bottom of the Ragdoll menu now accurately displays your current licence, including Personal, Complete, Unlimited and Batch, along with the licence type - `Floating` or `Node Locked`.

<img class="poster no-radius" src=https://user-images.githubusercontent.com/2152766/129899581-cec76be1-9761-40db-add5-bb1a7dfe688e.png>

<br>

### Social Media

Can you believe it. A clear sign of success, not everyone is on Twitter! If you're one of the lucky few, you can now follow along with updates to the project, documentation and general company news from there!

- https://twitter.com/ragdolldynamics
- https://facebook.com/ragdolldynamics
- https://reddit.com/user/ragdolldynamics
- https://youtube.com/c/RagdollDynamics
<!-- - https://instagram.com/ragdolldynamics -->

The only question is, who's going to be the *first* to follow? 😱

[![image](https://user-images.githubusercontent.com/2152766/129900266-790ab8f1-8858-44ee-9e15-e49eb368de85.png)](https://twitter.com/ragdolldynamics)

<br>

### Pivot Editor

In making he tutorials, the main bottleneck in terms of time taken was editing constraints. They are both complex and difficult to manage.

This release addresses this problem with the Pivot Editor GUI.

**Basics**

Here's how to use it to tune a broken knee.

https://user-images.githubusercontent.com/2152766/130945904-77eb1ad2-faa3-40a4-8fb1-e3afe473c7f4.mp4

**Spin & Swap**

One of the main reasons to want to edit constraint pivots is to align the Twist axis with the main rotation of a knee or elbow. 

https://user-images.githubusercontent.com/2152766/130945895-8236baea-7b4e-433c-8884-ce32b9668581.mp4

**Mirror**

If the pivots face in opposite directions, orientations can be un-mirrored with the `Mirror` option.

https://user-images.githubusercontent.com/2152766/130945889-dbf282ec-04fb-4780-8b63-9d7fb67f37d4.mp4

**Channel Box Co-op**

Tuning limits alongside pivots works well too, middle-click drag attributes from the Channel Box like you normally would, whilst dragging in the UI to compensate.

https://user-images.githubusercontent.com/2152766/130945899-62abade5-b96f-4555-bae1-f94c0e351c1c.mp4

**Snap**

Use the snap option to make precise adjustment to specific angles.

https://user-images.githubusercontent.com/2152766/130946210-40fc287f-f773-4df1-86e9-764db9e2d05f.mp4

<br>

### Worldspace Trajectories

Trajectories used to follow the scene wherever it went. Now they'll stay put, where they belong.

**Before**

https://user-images.githubusercontent.com/2152766/130568171-133ad45d-7844-4332-9d4b-1fa2091558c5.mp4

**After**

https://user-images.githubusercontent.com/2152766/130568174-c56d1553-237b-45b6-89e9-cc4d28b23dcd.mp4

<br>

### Sphere Rendering

This fixes a minor annoyance you may have noticed, of the outline of spheres visible in shaded mode.

**Before**

https://user-images.githubusercontent.com/2152766/129890945-77f94738-5917-4513-8d08-0936f5b3584c.mp4

**After**

https://user-images.githubusercontent.com/2152766/129890952-19894406-99cf-4d42-88ff-4c1777a40295.mp4

<br>

### Floating Server Details

When you first lease a licence from your licence server, the IP and port details are stored on the local machine for quicker access the next time.

However, if you then later needed to change those details, then any local machine previously leasing a licence would not be able to update their details.

This has now been fixed!
