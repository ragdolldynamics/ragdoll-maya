"""Ragdoll upgrade mechanism

Whenever a Ragdoll node is created, the current version of Ragdoll is
stored in the `.version` attribute of that node. When that node is later
found in a scene using a newer version of Ragdoll, this module manages
the transition between what was and what it.

In some cases, it's adding missing values and in others it's undoing new
default values, such as moving from the PGS to TGS solver in 2020.10.15

Each upgradable version is updated in turn, such that we can apply upgrades
from a really really old version and thus maintain a complete backwards
compatibility path for all time.

"""

import logging
from maya import cmds
from . import commands

log = logging.getLogger("ragdoll")


def has_upgrade(node, from_version):
    if node.type() == "rdScene":
        return from_version < 20201015

    if node.type() == "rdRigid":
        return from_version < 20201016


def scene(node, from_version, to_version):
    if from_version <= 0:
        # Saved with a development version
        return

    if from_version < 20201015:
        _scene_00000000_20201015(node)

    node["version"] = to_version


def rigid(node, from_version, to_version):
    if from_version <= 0:
        # Saved with a development version
        return

    if from_version < 20201015:
        _rigid_00000000_20201015(node)

    if from_version < 20201016:
        _rigid_20201015_20201016(node)

    node["version"] = to_version


def _scene_00000000_20201015(node):
    """TGS was introduced, let's maintain backwards compatibility though"""
    log.info("Upgrading %s to 2020.10.15" % node)
    node["solverType"] = commands.PGSSolverType


def _rigid_00000000_20201015(node):
    """Introduced the .restMatrix"""
    log.info("Upgrading %s to 2020.10.15" % node)
    rest = node["inputMatrix"].asMatrix()
    cmds.setAttr(node["restMatrix"].path(), tuple(rest), type="matrix")


def _rigid_20201015_20201016(node):
    """Introduced .color"""
    log.info("Upgrading %s to 2020.10.16" % node)
    node["color"] = commands._random_color()
