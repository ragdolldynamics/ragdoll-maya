from . import internal, constants
from .vendor import cmdx


def create(typ, mod, name, parent=None):
    node = None

    if typ == "rdSolver":
        assert parent is not None, "rdSolver needs a parent"
        name = internal.unique_name(name)
        node = mod.create_node(typ, name=name, parent=parent)

        # Defaults
        up = cmdx.up_axis()
        mod.set_attr(node["positionIterations"], 8)
        mod.set_attr(node["substeps"], 8)
        mod.set_attr(node["gravity"], up * -982)
        mod.set_attr(node["spaceMultiplier"], 0.1)
        mod.set_attr(node["airDensity"], 0.1)
        mod.set_attr(node["frameskipMethod"], constants.FrameskipIgnore)

        # Since 2023.02.xx
        mod.set_attr(node["forceMode"], constants.FieldVelocityChange)
        mod.set_attr(node["drawFieldScale"], 10)

        if up.y:
            mod.set_keyable(node["gravityY"])
        else:
            mod.set_keyable(node["gravityZ"])

        mod.set_attr(node["startTimeCustom"], cmdx.min_time())
        mod.set_attr(node["maxMassRatio"], 0)  # Off

        mod.connect(parent["worldMatrix"][0], node["inputMatrix"])

        node["forceMode"].hide()

    elif typ == "rdMarker":
        assert isinstance(mod, cmdx.DGModifier), (
            "rdMarker requires a DGModifier"
        )

        node = mod.create_node(typ, name=name)

        # Avoid markers getting too excited
        mod.set_attr(node["maxDepenetrationVelocity"], 20.0)

        # This used to be the default
        mod.set_attr(node["capsuleLengthAlongY"], False)
        mod.set_attr(node["convexDecomposition"], 1)

        # Avoid possible crashes due to poor geometry
        mod.set_attr(node["inputGeometryQuantisedCount"], 65535)
        mod.set_attr(node["inputGeometryCheckZeroAreaTriangles"], True)

        # Prefer the simpler visualisation
        mod.set_attr(node["fieldCentroids"], constants.ComCentroid)

        # Deprecated, a custom=0 means "Use Mass"
        mod.set_attr(node["densityType"], constants.DensityCustom)

    elif typ == "rdGroup":
        node = mod.create_node(typ, name=name, parent=parent)

    elif typ == "rdEnvironment":
        node = mod.create_node(typ, name=name)

    elif typ in ("rdDistanceConstraint",
                 "rdFixedConstraint",
                 "rdPinConstraint"):
        name = internal.unique_name(name)
        node = mod.create_node(typ, name=name, parent=parent)

    else:
        raise TypeError("Unrecognised Ragdoll type '%s'" % typ)

    time1 = cmdx.encode("time1")
    mod.set_attr(node["version"], internal.version())

    if node.has_attr("currentTime"):
        mod.connect(time1["outTime"], node["currentTime"])

    return node
