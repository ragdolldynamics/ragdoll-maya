from nose.tools import (
    assert_equals,
    assert_less,
)

from . import _new

from maya import cmds
from ragdoll.vendor import cmdx
from ragdoll import licence, constants, api


if constants.RAGDOLL_FLOATING:

    def setup():
        # Make sure we don't already have a lease
        licence.drop_lease()

    def teardown():
        # Make sure the remaining tests aren't interrupted by lack of a lease
        if not cmds.ragdollLicence(hasLease=True, query=True):

            # Behind an if-statement in case a test fails, at which point
            # we can't be sure what state we are in.
            licence.request_lease()

    def test_request_lease():
        assert_equals(licence.request_lease(), 0)
        assert_equals(licence.drop_lease(), 0)

    def test_lease_on_simulation():
        box, _ = cmds.polyCube()
        cmds.move(0, 5, 0)

        solver = api.create_solver()
        marker = api.assign_marker(box, solver)

        # There are Ragdoll nodes in the scene, but no simulation has
        # yet taken place. So we shouldn't have a lease yet.
        assert not cmds.ragdollLicence(hasLease=True, query=True)

        cmds.playbackOptions(minTime=1)
        cmds.playbackOptions(maxTime=5)
        api.record_physics(solver)

        # Simulation has begun, a lease should have been aquired
        assert cmds.ragdollLicence(hasLease=True, query=True)

        assert_equals(licence.drop_lease(), 0)

        tm = cmdx.Tm(cmdx.Mat4(cmds.getAttr(marker + ".outputMatrix")))
        assert_less(tm.translation().y, 5.0)

    def test_drop_on_unload():
        _new()

        assert_equals(licence.request_lease(), 0)
        assert cmds.ragdollLicence(hasLease=True, query=True)
        cmds.unloadPlugin("ragdoll")
        cmds.loadPlugin("ragdoll")

        # Lease was dropped on unload, and not requested again
        # until simulation starts.
        assert not cmds.ragdollLicence(hasLease=True, query=True)
