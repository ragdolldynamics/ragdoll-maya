"""Ragdoll upgrade mechanism

Whenever a Ragdoll node is created, the current version of Ragdoll is
stored in the `.version` attribute of that node. When that node is later
found in a scene using a newer version of Ragdoll, this module manages
the transition between what was and what is.

In some cases, it's adding missing values and in others it's undoing new
default values, such as moving from the PGS to TGS solver in 2020.10.15

Each upgradable version is updated in turn, such that we can apply upgrades
from a really really old version and thus maintain a complete backwards
compatibility path for all time.

"""

import os
import logging

from maya import cmds
from . import constants, internal
from .vendor import cmdx

log = logging.getLogger("ragdoll")

RAGDOLL_PLUGIN = os.getenv("RAGDOLL_PLUGIN", "ragdoll")
RAGDOLL_PLUGIN_NAME = os.path.basename(RAGDOLL_PLUGIN)


@internal.with_undo_chunk
def upgrade_all():

    # Fetch node types from the horses mouth
    all_nodetypes = cmds.pluginInfo("ragdoll", query=True, dependNode=True)

    # Also fetch plug-in version from the same mouth, rather
    # than rely on what's coming out of interactive.py. Since
    # upgrading should work headless too!
    version_str = cmds.pluginInfo(RAGDOLL_PLUGIN_NAME,
                                  query=True, version=True)

    # Debug builds come with a `.debug` suffix, e.g. `2020.10.15.debug`
    current_version = int("".join(version_str.split(".")[:3]))

    nodetype_to_upgrade = {
        "rdScene": scene,
        "rdRigid": rigid,
        "rdRigidMultiplier": rigid_multiplier,
        "rdConstraintMultiplier": constraint_multiplier,
    }

    upgraded_count = 0

    for node in cmdx.ls(type=all_nodetypes):
        node_version = node["version"].read()

        func = nodetype_to_upgrade.get(node.type())
        if func is None:
            continue

        if node_version >= current_version:
            continue

        try:
            upgraded = func(node, node_version, current_version)

        except Exception as e:
            log.warning(e)
            log.warning("Bug, had trouble upgrading")
            continue

        else:
            if upgraded:
                upgraded_count += 1
                with cmdx.DGModifier() as mod:
                    mod.set_attr(node["version"], current_version)

    return upgraded_count


def needs_upgrade():
    version_str = cmds.pluginInfo(constants.RAGDOLL_PLUGIN_NAME,
                                  query=True, version=True)

    # Debug builds come with a `.debug` suffix, e.g. `2020.10.15.debug`
    version = int("".join(version_str.split(".")[:3]))

    needs_upgrade = 0
    oldest_version = version

    # Evaluate all node types defined by Ragdoll
    all_nodetypes = cmds.pluginInfo("ragdoll", query=True, dependNode=True)

    for node in cmdx.ls(type=all_nodetypes):
        node_version = node["version"].read()

        if has_upgrade(node, node_version):
            needs_upgrade += 1

        if node_version < oldest_version:
            oldest_version = node_version

    return oldest_version, needs_upgrade


def has_upgrade(node, from_version):
    if node.type() == "rdScene":
        return from_version < 20210313

    if node.type() == "rdRigid":
        return from_version < 20210308

    if node.type() == "rdRigidMultiplier":
        return from_version < 20210411

    if node.type() == "rdConstraintMultiplier":
        return from_version < 20210411


def scene(node, from_version, to_version):
    if from_version <= 0:
        # Saved with a development version
        return

    upgraded = False

    if from_version < 20201015:
        _scene_00000000_20201015(node)
        upgraded = True

    if from_version < 20210228:
        _scene_20201016_20210228(node)
        upgraded = True

    if from_version < 20210313:
        _scene_20201015_20210313(node)
        upgraded = True

    return upgraded


def rigid(node, from_version, to_version):
    if from_version <= 0:
        # Saved with a development version
        return

    upgraded = False

    if from_version < 20201015:
        _rigid_00000000_20201015(node)
        upgraded = True

    elif from_version < 20201016:
        _rigid_20201015_20201016(node)
        upgraded = True

    if from_version < 20210228:
        _rigid_20201016_20210228(node)
        upgraded = True

    if from_version < 20210308:
        _rigid_20210228_20210308(node)
        upgraded = True

    if from_version < 20210423:
        _rigid_20210423_20210427(node)
        upgraded = True

    return upgraded


def rigid_multiplier(node, from_version, to_version):
    upgraded = False

    if from_version < 20210411:
        _rigid_multiplier_20210308_20210411(node)
        upgraded = True

    return upgraded


def constraint_multiplier(node, from_version, to_version):
    upgraded = False

    if from_version < 20210411:
        _constraint_multiplier_20210308_20210411(node)
        upgraded = True

    return upgraded


"""

Individual upgrade paths

"""


def _scene_00000000_20201015(node):
    """TGS was introduced, let's maintain backwards compatibility though"""
    log.info("Upgrading %s to 2020.10.15" % node)
    node["solverType"] = constants.PGSSolverType


def _scene_20201015_20210313(node):
    """Support for Z-up got added"""
    log.info("Upgrading %s to 2021.03.13" % node)

    up = cmdx.up_axis()

    with cmdx.DagModifier() as mod:
        if up.y:
            mod.set_nice_name(node["gravityY"], "Gravity")
            mod.set_keyable(node["gravityY"])
        else:
            mod.set_nice_name(node["gravityZ"], "Gravity")
            mod.set_keyable(node["gravityZ"])


def _rigid_00000000_20201015(node):
    """Introduced the .restMatrix"""
    log.info("Upgrading %s to 2020.10.15" % node)

    if "restMatrix" in node and node["restMatrix"].editable:
        rest = node["inputMatrix"].asMatrix()
        cmds.setAttr(node["restMatrix"].path(), tuple(rest), type="matrix")


def _rigid_20201015_20201016(node):
    """Introduced .color"""
    log.info("Upgrading %s to 2020.10.16" % node)
    node["color"] = internal.random_color()


def _scene_20201016_20210228(scene):
    """Array indices are automatically removed since 02-28

    There remains support for unconnected indices with references to
    non-existent entities, but not for long.

    """

    log.info("Upgrading %s to 2021.02.28" % scene)

    array_attributes = [
        "inputActive",
        "inputActiveStart",
        "inputConstraint",
        "inputConstraintStart",
        "inputLink",
        "inputLinkStart",
        "inputSlice",
        "inputSliceStart",
    ]

    with cmdx.DGModifier() as mod:
        for attr in array_attributes:
            for element in scene[attr]:
                if element.connected:
                    continue

                mod._modifier.removeMultiInstance(element._mplug, True)


def _rigid_20201016_20210228(rigid):
    """Introduced .cachedRestMatrix"""
    log.info("Upgrading %s to 2021.02.28" % rigid)

    with cmdx.DagModifier() as mod:
        rest = rigid["restMatrix"].asMatrix()
        mod.set_attr(rigid["cachedRestMatrix"], rest)

        if not rigid["restMatrix"].connected:
            parent = rigid.parent()
            mod.connect(parent["worldMatrix"][0],
                        rigid["restMatrix"])


def _rigid_20210228_20210308(rigid):
    """Introduced .startTime"""
    log.info("Upgrading %s to 2021.03.08" % rigid)

    scene = rigid["nextState"].connection(type="rdScene")

    with cmdx.DagModifier() as mod:
        mod.connect(scene["startTime"], rigid["startTime"])


def _rigid_20210423_20210427(rigid):
    """Introduced .startTime"""
    log.info("Upgrading %s to 2021.04.27" % rigid)

    with cmdx.DagModifier() as mod:
        mod.set_attr(rigid["creationMatrix"],
                     rigid["cachedRestMatrix"].as_matrix())


def _constraint_multiplier_20210308_20210411(mult):
    log.info("Upgrading %s to 2021.04.11" % mult)

    with cmdx.DagModifier() as mod:
        others = mult["message"].connections(type="rdConstraint",
                                             source=False,
                                             plugs=True)
        for index, other in enumerate(others):
            mod.connect(mult["ragdollId"], other)


def _rigid_multiplier_20210308_20210411(mult):
    log.info("Upgrading %s to 2021.04.11" % mult)

    with cmdx.DagModifier() as mod:
        others = mult["message"].connections(type="rdRigid",
                                             source=False,
                                             plugs=True)
        for index, other in enumerate(others):
            mod.connect(mult["ragdollId"], other)
