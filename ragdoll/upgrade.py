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
import traceback

from maya import cmds
from . import constants, internal
from .vendor import cmdx

log = logging.getLogger("ragdoll")

RAGDOLL_PLUGIN = os.getenv("RAGDOLL_PLUGIN", "ragdoll")
RAGDOLL_PLUGIN_NAME = os.path.basename(RAGDOLL_PLUGIN)


def try_it(func):
    # Don't let the failure of one upgrade path
    # hinder the upgrade of subsequent paths.
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()

    return wrapper


@internal.with_undo_chunk
def upgrade_all():
    # Also fetch plug-in version from the same mouth, rather
    # than rely on what's coming out of interactive.py. Since
    # upgrading should work headless too!
    version_str = cmds.pluginInfo(RAGDOLL_PLUGIN_NAME,
                                  query=True, version=True)

    # Debug builds come with a `.debug` suffix, e.g. `2020.10.15.debug`
    current_version = int("".join(version_str.split(".")[:3]))

    nodetype_to_upgrade = (
        ("rdMarker", marker),
        ("rdGroup", group),
        ("rdSolver", solver),
        ("rdCanvas", canvas),
    )

    upgraded_count = 0

    for nodetype, func in nodetype_to_upgrade:
        for node in cmdx.ls(type=nodetype):
            node_version = node["version"].read()

            if node_version >= current_version:
                continue

            try:
                upgraded = func(node, node_version, current_version)

            except Exception as e:
                log.debug(traceback.format_exc())
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
    if node.type() == "rdSolver":
        return from_version < 20211112

    if node.type() == "rdMarker":
        return from_version < 20211129

    if node.type() == "rdGroup":
        return from_version < 20211007

    if node.type() == "rdCanvas":
        return from_version < 20211129


def marker(node, from_version, to_version):
    upgraded = False

    if from_version < 20211007:
        _marker_20210928_20211007(node)
        upgraded = True

    if from_version < 20211129:
        _marker_20211007_20211129(node)
        upgraded = True

    return upgraded


def group(node, from_version, to_version):
    upgraded = False

    if from_version < 20211007:
        _group_20210928_20211007(node)
        upgraded = True

    return upgraded


def solver(node, from_version, to_version):
    upgraded = False

    if from_version < 20211007:
        _solver_20210928_20211007(node)
        upgraded = True

    if from_version < 20211024:
        _solver_20210928_20211024(node)
        upgraded = True

    if from_version < 20211112:
        _solver_20211024_20211112(node)
        upgraded = True

    return upgraded


def canvas(node, from_version, to_version):
    upgraded = False

    return upgraded


"""

Individual upgrade paths

"""


@try_it
def _solver_20210928_20211007(solver):
    log.info("Upgrading %s to 2021.10.07" % solver)

    with cmdx.DagModifier() as mod:
        # Used to be a number, is now an enum
        start_time = solver["startTime"].read()
        start_time = cmdx.om.MTime(start_time, cmdx.TimeUiUnit())
        mod.set_attr(solver["startTimeCustom"], start_time)
        mod.set_attr(solver["startTime"], 2)  # Custom

        # The transform wasn't connected, but now it should be
        transform = solver.parent()
        mod.connect(transform["worldMatrix"][0], solver["inputMatrix"])


@try_it
def _solver_20210928_20211024(solver):
    log.info("Upgrading %s to 2021.10.24" % solver)


@try_it
def _solver_20211024_20211112(solver):
    """rdCanvas node was added"""
    log.info("Upgrading %s to 2021.11.12" % solver)

    with cmdx.DagModifier() as mod:
        parent = solver.parent()
        canvas = mod.create_node("rdCanvas",
                                 name="rCanvasShape",
                                 parent=parent)

        mod.set_attr(canvas["hiddenInOutliner"], True)
        mod.set_attr(canvas["isHistoricallyInteresting"], False)

        mod.connect(solver["ragdollId"], canvas["solver"])


@try_it
def _marker_20210928_20211007(marker):
    log.info("Upgrading %s to 2021.10.07" % marker)

    with cmdx.DagModifier() as mod:
        # driveSpace turned into an enum
        if "driveSpace" in marker:
            custom = marker["driveSpace"].read()
            mod.set_attr(marker["driveSpaceCustom"], custom)

            space = constants.GuideInherit

            if custom < -0.99:
                space = constants.GuideLocal

            if custom > 0.99:
                space = constants.GuideWorld

            mod.set_attr(marker["driveSpace"], space)

        # offsetMatrix was introduced
        if "offsetMatrix" in marker:
            for index, dst in enumerate(marker["dst"]):
                src = marker["src"].input(type=("transform", "joint"))
                dst = dst.input(type=("transform", "joint"))

                if not dst:
                    # An untargeted marker, leave it
                    continue

                if not src:
                    # This would be odd, but technically possible
                    continue

                offset = src["worldMatrix"][0].as_matrix()
                offset *= dst["worldInverseMatrix"][0].as_matrix()
                mod.set_attr(marker["offsetMatrix"][index], offset)


@try_it
def _marker_20211007_20211129(marker):
    """originMatrix was added

    Since we can't go back in time to find out what pose they were
    actually assigned in, we'll grab the next-best thing which is the
    pose at scene open.

    In the case of opening the original rig, this will be accurate.

    """

    log.info("Upgrading %s to 2021.11.29" % marker)

    with cmdx.DagModifier() as mod:
        mod.set_attr(marker["originMatrix"], marker["inputMatrix"].as_matrix())


@try_it
def _group_20210928_20211007(group):
    log.info("Upgrading %s to 2021.10.07" % group)

    with cmdx.DagModifier() as mod:
        for index, oldstart in enumerate(group["inputMarkerStart"]):
            marker = oldstart.input()
            mod.connect(marker["startState"], group["inputStart"][index])
            mod.connect(marker["currentState"], group["inputCurrent"][index])
            mod.disconnect(oldstart)

        for oldcurrent in group["inputMarker"]:
            mod.disconnect(oldcurrent)
