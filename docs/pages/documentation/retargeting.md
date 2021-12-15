---
title: Retargeting
icon: "retarget_black.png"
---

<video autoplay class="poster" muted="muted" loop="loop" width=100% poster="https://user-images.githubusercontent.com/2152766/130401392-0d4549ab-3545-46ec-98d2-6b084b2a8465.jpg">
    <source src="https://user-images.githubusercontent.com/2152766/145724350-8e63a86b-5219-4cc9-b8d7-ecbd1ba474d2.mp4" type="video/mp4">
</video>

Assign to joints, record to controls.

<br>

#### Retarget

Any moderately complex character will have parts better suited for capturing and others for recording onto.

For example, in order to control a simulation with IK controls, we must first assign Markers onto the underlying joints driven by those IK controls. Then, we *retarget* those joints back onto the IK controls.

https://user-images.githubusercontent.com/2152766/145726981-69480bda-62df-475a-87d5-0c243c79be8d.mp4 controls

In this example, markers are assigned to the upper body controls, but then to the joints of the lower body. We don't want keyframes on these joints, so we *retarget* these keyframes onto the IK controls.

https://user-images.githubusercontent.com/2152766/145726993-3bfb60a2-cc13-4b95-b6f2-8fa62f0a1a7e.mp4 controls

<br>

#### Reassign

The opposite of Retarget.

Rather than assigning to joints and retargeting to IK controls, we assign to IK controls and *reassign* to joints. Same coin, different side; which one do you prefer?

<br>

#### Reconnect

Use `Reconnect` when you selected things in the wrong order and want a do-over.

https://user-images.githubusercontent.com/2152766/134465284-f9a3bd04-9392-4f33-a161-390cbe9049d2.mp4 controls

Success!

https://user-images.githubusercontent.com/2152766/134465285-87eacea9-4b93-4526-980e-585bbc92151b.mp4 controls

<br>

#### Untarget

For when you don't want anything recorded for this Marker. Useful for utility Markers, like twist joints or extra spine controls or just Markers without a corresponding control.
