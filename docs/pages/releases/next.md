
- [**ADDED** JSON Export](#json-export) Run your ragdolls in Unreal, Unity or your own custom game engine
- [**ADDED** Replay](#replay) Animator-friendly automation of Ragdoll setuport going out of sync

<br>

## JSON Export

In 2021.03.04 we introduced `cmds.ragdollDump` to get a copy of all rigids in the form of a JSON dictionary.

```py
import json
from maya import cmds
from ragdoll.vendor import cmdx

cmds.file(new=True, force=True)

rd = r"C:\Users\marcus\Downloads\ragdoll.json"
with open(rd) as f:
    rd = json.load(f)

joints = ["pelvis1", "spine_01", "spine_02"]

for uid, data in rd["entities"].items():
    comps = data["components"]
    
    if "NameComponent" not in comps:
        continue
    
    if not "RigidComponent" in comps:
        continue

    name = comps["NameComponent"]
    path = name["members"]["path"]

    if not path:
        # What's this? :O
        continue

    joint = path.rsplit("|", 3)[-2]

    scale = comps["ScaleComponent"]["members"]["absolute"]["values"]
    scale = cmdx.Vector(scale)
    matrix = comps["RestComponent"]["members"]["matrix"]["values"]
    matrix = cmdx.Matrix4(matrix)
    tm = cmdx.Tm(matrix)

    transform = cmdx.createNode("transform", name=joint)
    transform["translate"] = tm.translation()
    transform["rotate"] = tm.rotation()

    desc = comps["GeometryDescriptionComponent"]["members"]
    if desc["type"] == "Capsule":
        radius = desc["radius"] * scale.x
        length = desc["length"] * scale.y
        geo, _ = cmds.polyCylinder(axis=(1, 0, 0),
                                   radius=radius,
                                   height=length,
                                   roundCap=True,
                                   subdivisionsCaps=5)

    elif desc["type"] == "Box":
        extents = cmdx.Vector(desc["extents"]["values"])
        extents.x *= scale.x
        extents.y *= scale.y
        extents.z *= scale.z
        geo, _ = cmds.polyCube(width=extents.x,
                            height=extents.y,
                            depth=extents.z)

    elif desc["type"] == "Sphere":
        radius = desc["radius"] * scale.x
        geo, _ = cmds.polySphere(radius=radius)

    else:
        print("Unsupported shape type: %s" % desc["type"])
        continue

    offset = cmdx.Vector(desc["offset"]["values"])
    offset.x *= scale.x
    offset.y *= scale.y
    offset.z *= scale.z

    geo = cmdx.encode(geo)
    geo["translate"] = offset
    geo["rotate"] = cmdx.Quaternion(desc["rotation"]["values"])

    transform.addChild(geo)


```

<br>

## Replay

Ever set-up a character with physics, only to have to do it all over again on some other shot or character? With **Replay** this can be a thing of the past! :)

If you've ever worked with Photoshop and it's "Actions" panel, you'll know what to expect. It'll record the things you do, such that you can replay them later. For every recorded action, selection and preferences are stored. You can edit the names of selected nodes with *wildcards* to support alternative naming conventions, for example if a control has a different namespace than originally recorded at. Preferences can be manipulated post-recording as well, such as the initial shapes of things.
