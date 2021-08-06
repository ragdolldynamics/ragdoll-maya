---
icon: "convert_black.png"
---

<div class="hero-container">
    <img class="hero-image" src=https://user-images.githubusercontent.com/2152766/128189396-55382975-a4b9-4c8b-9204-a4cd6b2fa1a6.png>
</div>

Some tips and tricks on how to debug your simulations.

<br>

### Debugging Tips

Running into trouble? Can't figure out why something happens the way it does? Try these tips one by one, in the order they're written.

<br>

### Test Ragdoll

For any of these tips to help you, we need to make sure Ragdoll is to blame.

![debugscene](https://user-images.githubusercontent.com/2152766/128197952-2e857e68-4b7e-49a7-99ce-67928ee6f501.gif)

**Python Script**

```py
from maya import cmds

for scene in cmds.ls(type="rdScene"):
    cmds.setAttr(scene + ".enabled", False)
```

This disables all Ragdoll scenes and should result in a non-simulated, clean version of your scene. If the problem persists, the problem is *unlikely* related to Ragdoll.

!!! info "Still a chance"
    Your controls are still plugged into Ragdoll, and it's unlikely but possible that the problem isn't with the simulation but with the non-simulated parts of Ragdoll, like custom rotation orders, rotate pivots, *scale* and so forth. So keep an eye out for that!

<br>

### Test Everything

Make sure no funny business is happening, this should result in in *nothing* happening when you press play.

1. Disable `Gravity`
1. Disable `Collide` on all Rigids
1. Disable `Limit Enabled` on all Constraints
1. Disable `Guide Enabled` on all Constraints
1. Re-enable things, one by one until you find the culprit

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128201443-9a968f3d-3465-463a-a371-8bc1046a758a.mp4" type="video/mp4">
</video>

**Python Script**

```py
from maya import cmds

def set_attr(attr, value):
    """Some attributes are driven by another"""
    inputs = cmds.listConnections(attr, plugs=True, destination=False)
    while inputs:
        attr = inputs[0]

        # Keep walking until you find one that can be set
        inputs = cmds.listConnections(attr, plugs=True, destination=False)

    try:
        cmds.setAttr(attr, value)
    except Exception:
        print("Could not set %s" % attr)

for scene in cmds.ls(type="rdScene"):
    set_attr(scene + ".gravityY", 0.0)
    set_attr(scene + ".gravityZ", 0.0)

for rigid in cmds.ls(type="rdRigid"):
    set_attr(rigid + ".collide", False)

for constraint in cmds.ls(type="rdConstraint"):
    set_attr(constraint + ".limitEnabled", False)
    set_attr(constraint + ".driveEnabled", False)  # Another name for "guide"
```

<br>

### Test Shapes

Overlapping shapes on the start frame can be a headache. Here's a quick and easy way of seeing whether that's a problem.

1. Disable `Gravity`
1. Disable `Collide` on all Rigids
1. Re-enable things, one by one until you find the culprit

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128171367-8bacc3ef-aa1e-45ba-924a-0265dfa64b10.mp4" type="video/mp4">
</video>

**Python Script**

```py
from maya import cmds

def set_attr(attr, value):
    """Some attributes are driven by another"""
    inputs = cmds.listConnections(attr, plugs=True, destination=False)
    while inputs:
        attr = inputs[0]

        # Keep walking until you find one that can be set
        inputs = cmds.listConnections(attr, plugs=True, destination=False)

    try:
        cmds.setAttr(attr, value)
    except Exception:
        print("Could not set %s" % attr)

for scene in cmds.ls(type="rdScene"):
    set_attr(scene + ".gravityY", 0.0)
    set_attr(scene + ".gravityZ", 0.0)

for rigid in cmds.ls(type="rdRigid"):
    set_attr(rigid + ".collide", False)
```

<br>

### Test Limits

Sometimes, limbs can begin *outside* of a permitted limit.

![testlimits](https://user-images.githubusercontent.com/2152766/128196875-0f5c6c4b-6b5f-4709-aa64-c05b1e9d9901.gif)

**Python Script**

```py
from maya import cmds

def set_attr(attr, value):
    """Some attributes are driven by another"""
    inputs = cmds.listConnections(attr, plugs=True, destination=False)
    while inputs:
        attr = inputs[0]

        # Keep walking until you find one that can be set
        inputs = cmds.listConnections(attr, plugs=True, destination=False)

    try:
        cmds.setAttr(attr, value)
    except Exception:
        print("Could not set %s" % attr)

for constraint in cmds.ls(type="rdConstraint"):
    set_attr(constraint + ".limitEnabled", False)
```

<br>

### Test Guides

Sometimes, guides are responsible. They can be especial
ly treacherous if you ask it to reach an angle exactly 180 degrees away from where it starts.

<video controls autoplay="autoplay" loop="loop" width="100%">
   <source src="https://user-images.githubusercontent.com/2152766/128197714-b7e15c52-3bc1-4c71-a146-c80c6428a547.mp4" type="video/mp4">
</video>

**Python Script**

```py
from maya import cmds

def set_attr(attr, value):
    """Some attributes are driven by another"""
    inputs = cmds.listConnections(attr, plugs=True, destination=False)
    while inputs:
        attr = inputs[0]

        # Keep walking until you find one that can be set
        inputs = cmds.listConnections(attr, plugs=True, destination=False)

    try:
        cmds.setAttr(attr, value)
    except Exception:
        print("Could not set %s" % attr)

for scene in cmds.ls(type="rdScene"):
    set_attr(scene + ".gravityY", 0.0)
    set_attr(scene + ".gravityZ", 0.0)

for rigid in cmds.ls(type="rdRigid"):
    set_attr(rigid + ".collide", False)

for constraint in cmds.ls(type="rdConstraint"):
    set_attr(constraint + ".limitEnabled", False)
    set_attr(constraint + ".driveEnabled", False)  # Another name for "guide"
```
