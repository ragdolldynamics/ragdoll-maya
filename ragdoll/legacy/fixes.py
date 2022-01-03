from maya import mel


def paint_skin_weights():

    # Augment original implementation with this:
    #
    # if (`nodeType $item` == "joint") {
    #     $object = {};
    # }
    #
    # So as to support the right-click context menu
    #
    # Note: This has no uninstall equivalent
    command = """\

proc string getControlledHandle(string $item)
{
    string $handle;
    if (size(`ls ($item+".ikBlend")`)) {
        string $connHandles[] =
            `listConnections -type ikHandle ($item+".ikBlend")`;
        if (size($connHandles)) {
            $handle = $connHandles[0];
        }
    }
    return $handle;
}

proc int isIKcontroller(string $item)
{
    string $handle = getControlledHandle($item);
    return (size($handle) > 0);
}


global proc string[] objectSelectMasks(string $item)
// Returns the component selection masks that apply to this object
{
    string $maskList[];
    string $shape = $item;
    int $i;

    // Look at the shape child of this object
    //
    string $object[] = `listRelatives -path -s $item`;
    if (`nodeType $item` == "joint") {
        $object = {};
    }

    int $gotVisible = 0;

    for ($i = 0; $i < size($object); ++$i) {
        if( (0 == getAttr($object[$i] + ".io")) &&
            getAttr($object[$i] + ".v") ) {
            $shape = $object[$i];
            $gotVisible = 1;
            break;
        }
    }

    if( !$gotVisible ) {
        for ($i = 0; $i < size($object); ++$i)
        {
            if (getAttr($object[$i] + ".io") == 0)
            {
                $shape = $object[$i];
                break;
            }
        }
    }

    string $nt = `nodeType $shape`;

    switch ($nt) {
        case "lattice":
            $maskList[0] = "latticePoint";
            break;
        case "locator":
            $maskList[0] = "locator";
            break;
        case "nurbsCurve":
            $maskList[0] = "curveParameterPoint";
            $maskList[1] = "controlVertex";
            $maskList[2] = "editPoint";
            $maskList[3] = "hull";
            break;
        case "bezierCurve":
            $maskList[0] = "curveParameterPoint";
            $maskList[1] = "bezierAnchor";
            $maskList[2] = "editPoint";
            $maskList[3] = "hull";
            break;
        case "nurbsSurface":
            $maskList[0] = "isoparm";
            $maskList[1] = "controlVertex";
            $maskList[2] = "surfaceParameterPoint";
            $maskList[3] = "hull";
            $maskList[4] = "surfaceFace";
            $maskList[5] = "surfaceUV";
            if (objectIsTrimmed($shape)) {
                $maskList[6] = "surfaceEdge";
            }
            break;
        case "mesh":
            $maskList[0] = "edge";
            $maskList[1] = "vertex";
            $maskList[2] = "facet";
            $maskList[3] = "puv";
            $maskList[4] = "pvf";
            $maskList[5] = "meshComponents";
            break;
        case "joint":
        case "hikFKJoint":
            $maskList[0] = "joint";     // special case
            break;
        case "ikHandle":
            $maskList[0] = "ikHandle";  // special case
            break;
        case "hikEffector":
        case "hikIKEffector":
        // fall through
        case "hikFloorContactMarker":
            $maskList[0] = "hikEffector";   // special case
            break;
        case "motionTrailShape":
            $maskList[0] = "motionTrail";
            break;
        case "particle":
            $maskList[0] = "particle";  // only one choice
            break;
        case "nParticle":
            $maskList[0] = "particle";  // only one choice
            break;
        case "spring":
            $maskList[0] = "springComponent";   // only one choice
            break;
        case "subdiv":
            $maskList[0] = "subdivMeshPoint";
            $maskList[1] = "subdivMeshEdge";
            $maskList[2] = "subdivMeshFace";
            $maskList[3] = "subdivMeshUV";
            break;
    }

    if (isIKcontroller($item)) {
        $maskList[size($maskList)] = "ikfkHandle";
    }

    return $maskList;
}
"""

    mel.eval(command)
