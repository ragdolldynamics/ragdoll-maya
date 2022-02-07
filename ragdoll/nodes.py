from . import internal
from .vendor import cmdx


def create(typ, mod, name, parent=None):
    node = None

    if typ == "rdSolver":
        assert parent is not None, "rdSolver needs a parent"
        name = internal.unique_name(name)
        node = mod.create_node(typ, name=name, parent=parent)

        # Auxilliary node, hidden from view and not relevant to the user
        canvas = mod.create_node("rdCanvas",
                                 name="rCanvasShape",
                                 parent=parent)

        # Hide in outliner and channel box
        mod.set_attr(canvas["hiddenInOutliner"], True)
        mod.set_attr(canvas["isHistoricallyInteresting"], 0)

        # Defaults
        up = cmdx.up_axis()
        mod.set_attr(node["positionIterations"], 4)
        mod.set_attr(node["gravity"], up * -982)
        mod.set_attr(node["spaceMultiplier"], 0.1)

        if up.y:
            mod.set_keyable(node["gravityY"])
        else:
            mod.set_keyable(node["gravityZ"])

        mod.set_attr(node["startTimeCustom"], cmdx.min_time())
        mod.set_attr(node["maxMassRatio"], 1)  # 10 ^ 1

        mod.connect(node["ragdollId"], canvas["solver"])
        mod.connect(parent["worldMatrix"][0], node["inputMatrix"])

        time1 = cmdx.encode("time1")
        mod.connect(time1["outTime"], node["currentTime"])

    elif typ == "rdMarker":
        assert isinstance(mod, cmdx.DGModifier), (
            "rdMarker requires a DGModifier"
        )

        node = mod.create_node(typ, name=name)

        time1 = cmdx.encode("time1")
        mod.connect(time1["outTime"], node["currentTime"])

        # Avoid markers getting too excited
        mod.set_attr(node["maxDepenetrationVelocity"], 20.0)

        # This used to be the default
        mod.set_attr(node["capsuleLengthAlongY"], False)

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

        time1 = cmdx.encode("time1")
        mod.connect(time1["outTime"], node["currentTime"])

        return node

    else:
        raise TypeError("Unrecognised Ragdoll type '%s'" % typ)

    mod.set_attr(node["version"], internal.version())

    return node
