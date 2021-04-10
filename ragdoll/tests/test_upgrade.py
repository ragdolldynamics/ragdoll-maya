from . import _scene, _open
from .. import upgrade

from maya import cmds

from nose.tools import (
    assert_equals,
)


def test_upgrade_dynamiccontrol():
    scenename = _scene("dynamiccontrol.mb")
    _open(scenename)
    count = upgrade.upgrade_all()

    assert_equals(count, 3)


def test_upgrade_multipliers():
    scenename = _scene("multipliers_pre20210411.ma")
    _open(scenename)
    count = upgrade.upgrade_all()

    assert_equals(count, 2)
