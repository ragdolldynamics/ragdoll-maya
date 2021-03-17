"""Recreate Maya scene from Ragdoll dump

# Usage Example
import json
dump = cmds.ragdollDump()
dump = json.loads(dump)
dedump(dump)

"""

from maya import cmds
from ragdoll.vendor import cmdx


class Component(dict):
    """Simplified access to component members"""

    def __getattr__(self, key):
        value = self["members"][key]

        if not isinstance(value, dict):
            return value

        if value["type"] == "Vector3":
            return cmdx.Vector(value["values"])

        elif value["type"] == "Color3":
            return cmdx.Color(value["values"])

        elif value["type"] == "Matrix44":
            return cmdx.Matrix4(value["values"])

        elif value["type"] == "Quaternion":
            return cmdx.Quaternion(*value["values"])

        else:
            raise TypeError("Unsupported type: %s" % value)


def dedump(dump):
    """Recreate Maya scene from `dump`"""

    with cmdx.DagModifier() as mod:
        root = mod.createNode("transform", name="dump")

    for entity, data in dump["entities"].items():
        comps = data["components"]

        if "RigidComponent" not in comps:
            continue

        name = Component(comps["NameComponent"])

        if not name.path:
            # Bad export
            continue

        joint = name.path.rsplit("|", 3)[-2]

        scale = Component(comps["ScaleComponent"])
        rest = Component(comps["RestComponent"])
        desc = Component(comps["GeometryDescriptionComponent"])

        # Establish rigid transformation
        tm = cmdx.TransformationMatrix(rest.matrix)

        # Establish shape
        if desc.type in ("Cylinder", "Capsule"):
            radius = desc.radius * scale.absolute.x
            length = desc.length * scale.absolute.y
            geo, _ = cmds.polyCylinder(axis=(1, 0, 0),
                                       radius=radius,
                                       height=length,
                                       roundCap=True,
                                       subdivisionsCaps=5)

        elif desc.type == "Box":
            extents = desc.extents
            extents.x *= scale.absolute.x
            extents.y *= scale.absolute.y
            extents.z *= scale.absolute.z
            geo, _ = cmds.polyCube(width=extents.x,
                                   height=extents.y,
                                   depth=extents.z)

        elif desc.type == "Sphere":
            radius = desc.radius * scale.absolute.x
            geo, _ = cmds.polySphere(radius=radius)

        else:
            print(
                "Unsupported shape type: %s.type=%s"
                % (name.path, desc.type)
            )
            continue

        with cmdx.DagModifier() as mod:
            transform = mod.createNode("transform", name=joint, parent=root)
            transform["translate"] = tm.translation()
            transform["rotate"] = tm.rotation()

        # Establish shape transformation
        offset = desc.offset
        offset.x *= scale.absolute.x
        offset.y *= scale.absolute.y
        offset.z *= scale.absolute.z

        geo = cmdx.encode(geo)
        geo["translate"] = offset
        geo["rotate"] = desc.rotation

        transform.addChild(geo)
