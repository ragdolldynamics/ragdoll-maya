from . import _scene
from .. import upgrade

from maya import cmds

from nose.tools import (
    assert_equals,
)


def test_upgrade_dynamiccontrol():
    scenename = _scene("dynamiccontrol.mb")
    cmds.file(scenename, open=True, force=True)
    count = upgrade.upgrade_all()

    assert_equals(count, 3)


def test_upgrade_multipliers():
    scenename = _scene("multipliers_pre20210411.ma")
    cmds.file(scenename, open=True, force=True)
    count = upgrade.upgrade_all()

    assert_equals(count, 2)
