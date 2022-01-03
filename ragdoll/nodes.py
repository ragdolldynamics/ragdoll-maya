from . import internal
from .vendor import cmdx


def create(typ, mod, name, parent=None):
    node = None

    if typ == "rdMarker":
        assert isinstance(mod, cmdx.DGModifier), (
            "rdMarker requires a DGModifier"
        )

        node = mod.create_node(typ, name=name)

        # Avoid markers getting too excited
        mod.set_attr(node["maxDepenetrationVelocity"], 20.0)

    elif typ == "rdGroup":
        node = mod.create_node(typ, name=name, parent=parent)

        time1 = cmdx.encode("time1")
        mod.connect(time1["outTime"], node["currentTime"])

    elif typ in ("rdDistanceConstraint",
                 "rdFixedConstraint",
                 "rdPinConstraint"):
        name = internal.unique_name(name)
        node = mod.create_node(typ, name=name, parent=parent)
        mod.set_attr(node["version"], internal.version())

        return node

    else:
        raise TypeError("Unrecognised Ragdoll type '%s'" % typ)

    mod.set_attr(node["version"], internal.version())

    return node
