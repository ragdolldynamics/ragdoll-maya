"""Functionality for menus

This module is where we deal with the messy nature of user
input and try to be as forgiving as possible to what goes in,
and strict as possible about what goes out.

  ________________             _________
 |                |           |         |
 | User Selection |---- + --->|         |
 |________________|           |         |
  __________________          |         |    _______________
 |                  |         |         |   |               |
 | User preferences |-- + --->| Ragdoll |-->| User Feedback |
 |__________________|         |         |   |_______________|
  ____________                |         |
 |            |               |         |
 | Maya state |-------- + --->|         |
 |____________|               |_________|


Each command..

- Takes an optional (selection=) as its first argument
- Use persistent optionVars stored in Maya preferences
- Cannot throw an exception, these must be actionable messages
    for the end-user

These build on functionality found in ragdoll.commands
and can but generally *should not* be used for scripting.

"""

import os
import copy
import json
import errno
import logging
import traceback
import functools
import webbrowser
import contextlib

from maya import cmds
from maya.utils import MayaGuiLogHandler
from maya.api import OpenMaya as om
from .vendor import cmdx, qargparse

from . import (
    commands,
    upgrade,
    ui,
    options,
    dump,
    recording,
    recording_match,
    licence,
    telemetry,
    widgets,
    constants as c,
    internal as i__,
    __
)

log = logging.getLogger("ragdoll")

Warning = ValueError
DoNothing = None
Cancelled = False

kSuccess = True
kFailure = False

# Internal
__.previousvars = dict({
    "MAYA_SCRIPT_PATH": os.getenv("MAYA_SCRIPT_PATH", ""),
    "XBMLANGPATH": os.getenv("XBMLANGPATH", ""),
}, **__.previousvars)  # Keep exising previous vars, if any


def _print_exception():
    log.warning(traceback.format_exc())


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _is_standalone():
    """Is Maya running without a GUI?"""
    return not hasattr(cmds, "about") or cmds.about(batch=True)


def _is_interactive():
    """Is Maya running with a GUI?"""
    return not _is_standalone()


MessageBox = ui.MessageBox


if _is_standalone():
    def MessageBox(*args, **kwargs):
        return kSuccess


def _after_scene_open(*args):
    """Handle upgrades of nodes saved with an older version of Ragdoll"""

    if options.read("upgradeOnSceneOpen"):
        _evaluate_need_to_upgrade()

    uninstall_ui()

    # Grant an initial state to any plan lurking about
    for plan in cmdx.ls(type="rdPlan"):
        plan["startState"].read()

    options.write("viewportGamma", 1.0)

    # lut = cmds.colorManagementPrefs(query=True, renderingSpaceName=True)

    # if lut == "sRGB gamma":
    #     options.write("viewportGamma", 1.8)

    # elif lut.startswith("ACES 1.0 SDR-video"):
    #     options.write("viewportGamma", 1.2)


def _before_scene_open(*args):
    # Let go of all memory, to allow Ragdoll plug-in to be unloaded
    cmdx.uninstall()


def _before_scene_new(*args):
    cmdx.uninstall()
    uninstall_ui()


def requires_ui(func):
    """Wrapper for functions that rely on being displayed

    Mostly for CI. These are simply ignored.

    """

    @functools.wraps(func)
    def requires_ui_wrapper(*args, **kwargs):
        if _is_standalone():
            return kSuccess
        return func(*args, **kwargs)
    return requires_ui_wrapper


def with_exception_handling(func):
    """Turn exceptions into user-facing messages"""

    @functools.wraps(func)
    def format_exception_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except i__.UserWarning as e:
            log.warning(traceback.format_exc())

            MessageBox(
                e.title,
                e.message,
                buttons=ui.OkButton,
                icon=ui.InformationIcon
            )

            return kFailure

        except Exception:
            # Turn this into a friendly warning
            log.warning(traceback.format_exc())
            return kFailure

    return format_exception_wrapper


# Every argument used by UIs
#
# These can be accessed/modified via cmds.optionVar
# as <prefix><name> where <prefix> is "ragdoll" and are
# all stored persistently alongside Maya's native preferences
with open(_resource("options.json")) as f:
    __.optionvars = json.load(f)
    __.optionvars.pop("#", None)  # Exclude comments

    if cmdx.__maya_version__ < 2020:
        __.optionvars["mimicFreezeTransform"]["enabled"] = False
        __.optionvars["mimicFreezeTransform"]["default"] = False


# Every menu item
with open(_resource("menu.json")) as f:
    __.menuitems = json.load(f)
    __.menuitems.pop("#", None)  # Exclude comments


def install():
    if __.installed:
        return

    __.installed = True

    options.install()
    install_logger()
    install_plugin()

    options.write("shaderPath", _resource("shaders"))
    options.write("fontPath", _resource("fonts"))
    options.write("iconPath", _resource("icons"))

    if _is_interactive():
        install_telemetry() if c.RAGDOLL_TELEMETRY else None
        install_callbacks()

        # Give Maya's GUI a chance to boot up
        cmds.evalDeferred(install_menu)

        widgets.WelcomeWindow.preload()

        # 2018 and consolidation doesn't play nicely without animated shaders
        if cmdx.__maya_version__ < 2019:
            def no_consolidate():
                try:
                    render = cmdx.encode("hardwareRenderingGlobals")
                    render["consolidateWorld"] = 0
                except Exception:
                    # Not a big deal, try again next time.
                    pass

            if options.read("maya2018ConsolidateWorldFix"):
                cmds.evalDeferred(no_consolidate)

        if not c.RAGDOLL_NO_STARTUP_DIALOG and options.read("firstLaunch2"):
            cmds.evalDeferred(welcome_user)
            options.write("firstLaunch2", False)

        # Enums were made into integers
        if options.read("firstLaunch3"):

            first_launch2 = options.read("firstLaunch2")
            options.reset()

            # Keep this, to avoid pestering the user with the splash dialog
            options.write("firstLaunch3", False)
            options.write("firstLaunch2", first_launch2)

    cmds.evalDeferred(licence.check_init_status)


def uninstall():
    if not __.installed:
        # May have been uninstalled by either the C++ plug-in,
        # or via the Script Editor or userSetup.py etc.
        return

    uninstall_telemetry() if c.RAGDOLL_TELEMETRY else None
    uninstall_logger()
    uninstall_menu()
    uninstall_ui(force=True)
    options.uninstall()
    cmdx.uninstall()
    licence.uninstall()

    if _is_interactive():
        uninstall_callbacks()

    # Call last, for Maya to properly unload and clean up
    try:
        uninstall_plugin()

    except RuntimeError:
        # This is fine, for development
        traceback.print_exc()

    # Erase all trace
    import sys
    for module in sys.modules.copy():
        if module.startswith("ragdoll"):
            sys.modules.pop(module)

    __.installed = False


class RagdollGuiLogHandler(MayaGuiLogHandler):
    """Gather errors and warnings for the Message Board"""

    history = []

    def emit(self, record):
        if record.levelno > logging.INFO:
            RagdollGuiLogHandler.history.append(record)
            update_menu()

        if record.levelno == logging.WARNING:
            __.telemetry_data["maya"]["warnings"] += 1

        if record.levelno >= logging.ERROR:
            __.telemetry_data["maya"]["errors"] += 1

        return super(RagdollGuiLogHandler, self).emit(record)


def install_logger():
    fmt = logging.Formatter(
        "ragdoll.%(funcName)s() - %(message)s"
    )

    # This one works like logging.StreamHandler,
    # except it also colors the Command Line nicely
    handler = RagdollGuiLogHandler()

    handler.setFormatter(fmt)
    log.addHandler(handler)
    log.propagate = False


def install_telemetry():
    ragdoll_dir = os.path.expanduser("~/.ragdoll")
    crash_fname = os.path.join(
        ragdoll_dir, "ragdollCrashed_%d.txt" % os.getpid()
    )

    try:
        os.makedirs(ragdoll_dir)

    except OSError as e:
        if e.errno == errno.EEXIST:
            # This is fine
            pass

        else:
            # Can't think of a reason why this would ever happen
            log.debug("Could not create ~/.ragdoll user-directory")

    if os.path.exists(crash_fname):
        __.telemetry_data["maya"]["crashed"] = True
        os.remove(crash_fname)
        log.debug("Maya crashed last time, with Ragdoll loaded.")

    with open(crash_fname, "w") as f:
        f.write("Nothing to see here")

    telemetry.install()


def uninstall_telemetry():
    ragdoll_dir = os.path.expanduser("~/.ragdoll")
    crash_fname = os.path.join(
        ragdoll_dir, "ragdollCrashed_%d.txt" % os.getpid()
    )

    try:
        os.remove(crash_fname)
    except OSError as e:
        if e.errno == errno.ENOENT:
            # If it isn't there, it isn't there
            pass
        else:
            # Could be a permission issue, which I don't expect
            # could ever happen.
            log.debug("Could not remove crash file")


def uninstall_logger():
    log.handlers[:] = []
    log.propagate = True  # Defer to root logger


def _on_cycle(clientData=None):
    """The solver is panicking

    This is expected to happen only when there is a cycle,
    but could happen for other reasons too. The result is
    an unexpected dependency graph, where one rigid or scene
    evaluates ahead of another.

    """

    log.warning("Something is not right!")


def _on_licence_expired(clientData=None):
    # Careful not to immediately call Qt,
    # as it may put Maya into an infinite sleep.

    # This event is triggered many times, but we're only really
    # interested in notifying the user about it once.
    if not hasattr(__, "expiry_timer"):
        from PySide2 import QtCore
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(300)
        timer.timeout.connect(welcome_user)

        __.expiry_timer = timer

    __.expiry_timer.start()


def _on_nonkeyable_keyed(clientData=None):
    """Called on attempted keyframining of a non-keyable attribute"""

    cmds.evalDeferred(lambda: ui.notify(
        "Non-keyable Attribute",
        "This attribute cannot be keyframed",
        location="cursor",
        shake=True
    ))


def _on_noncommercial_file(clientData=None):
    """Called on opening a file saved with a non-commercial Ragdoll"""

    msg = (
        "This file was saved using a non-commercial licence of Ragdoll\n"
        "and cannot be opened with a commercial licence.\n"
        "\n"
        "This Ragdoll instance has been converted into a non-commercial\n"
        "licence, reload the plug-in to restore your commercial licence."
    )

    def deferred():
        ui.notify("Non-commercial file", msg, persistent=True, location="menu")
        welcome_user()

    cmds.evalDeferred(deferred)
    log.warning(msg)


def _on_noncommercial_export(clientData=None):
    """Called on attempted export from non-commercial version"""

    msg = (
        "Export is a Ragdoll Unlimited feature, "
        "and is limited to a maximum<br>"
        "of 10 markers with a <b>Complete</b> "
        "and <b>Non-commercial</b> licence."
    )

    def deferred():
        ui.notify(
            "Unlimited export", msg, persistent=True, location="menu"
        )

    cmds.evalDeferred(deferred)
    log.warning(msg)


def _on_recording_limit(clientData=None):
    """Called on attempted recording from non-commercial version"""

    msg = (
        "A non-commercial licence is limited to 100 frames of recorded "
        "and live simulation. To record or transfer more frames, consider "
        "purchasing a Complete or Unlimited licence."
    )

    def deferred():
        log.warning(msg)

        def buy():
            webbrowser.open(
                "https://ragdolldynamics.com/pricing"
            )
            return False

        ui.warn(
            option="validateNonCommercialRecord",
            title="Recording with Ragdoll Non-Commercial",
            message="nc_record.png",
            call_to_action=msg,
            actions=[
                ("Ok", lambda: True),
                ("Pricing", buy)
            ]
        )

    # This event is triggered many times, but we're only really
    # interested in notifying the user about it once.
    if not hasattr(__, "recording_timer"):
        from PySide2 import QtCore
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(1000)
        timer.timeout.connect(deferred)

        __.recording_timer = timer

    __.recording_timer.start()


def _on_locomotion_limit(clientData=None):
    """Called on attempted planning from not-unlimited"""

    msg = (
        "Locomotion is a feature of Ragdoll Unlimited, any other "
        "version is limited to 100 frames of generated motion. "
        "See Pricing for purchase options."
    )

    def deferred():
        log.warning(msg)

        def buy():
            webbrowser.open(
                "https://ragdolldynamics.com/pricing"
            )
            return False

        ui.warn(
            option="validateUnlimitedLocomotion",
            title="Locomotion without Ragdoll Unlimited",
            message="un_locomotion.png",
            call_to_action=msg,
            actions=[
                ("Ok", lambda: True),
                ("Pricing", buy)
            ]
        )

    # This event is triggered many times, but we're only really
    # interested in notifying the user about it once.
    if not hasattr(__, "locomotion_timer"):
        from PySide2 import QtCore
        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(1000)
        timer.timeout.connect(deferred)

        __.locomotion_timer = timer

    __.locomotion_timer.start()


def _fit_to_view():
    manip = json.loads(cmds.ragdollDump(manipulator=True))
    if manip["solverPath"]:
        cmds.viewFit(
            manip["solverPath"],

            # Respect the users global preference
            animate=cmds.optionVar(query="animateRoll")
        )


def _install_fit_to_view():
    from PySide2 import QtWidgets, QtCore

    _uninstall_fit_to_view()

    win = ui.MayaWindow()
    __.shortcut = QtWidgets.QShortcut("F", win)
    __.shortcut.setContext(QtCore.Qt.ApplicationShortcut)
    __.shortcut.activated.connect(_fit_to_view)


def _uninstall_fit_to_view():
    if __.shortcut is not None:
        try:
            # Just deleting this thing is not enough, apparently
            __.shortcut.setEnabled(False)
            __.shortcut.setKey(None)
            __.shortcut.activated.disconnect(_fit_to_view)
            __.shortcut = None

        except Exception as e:
            log.debug("Had trouble uninstalling the Fit to View hotkey")
            log.debug(str(e))


def _on_manipulator_entered(clientData=None):
    """User has entered into the manipulator"""

    if options.read("manipulatorFitToViewOverride"):
        _install_fit_to_view()

    __.panel_states = {}

    # We can't use `cmds.getPanel(type="modelPanel")` as it
    # would return panels that aren't necessarily visible. As it happens,
    # querying invisible panels yields bogus values. We can't store
    # and later restore those, as it would make the Viewport menu `Show`
    # confused about whether the HUD is actually visible or not.

    # So instead, we only worry about currently visible modelPanels
    # The caveat being that if a user displays new panels during
    # manipulator use then those won't be handled here.
    for panel in cmds.getPanel(visiblePanels=True):
        if not cmds.modelPanel(panel, query=True, exists=True):
            continue

        state = cmds.modelEditor(panel, query=True, headsUpDisplay=True)
        cmds.modelEditor(panel, edit=True, headsUpDisplay=False)
        __.panel_states[panel] = state


def _on_manipulator_exited(clientData=None):
    """User has exited the manipulator, restore viewport HUD"""
    for panel, state in __.panel_states.items():
        cmds.modelEditor(panel, edit=True, headsUpDisplay=state)

    if options.read("manipulatorFitToViewOverride"):
        _uninstall_fit_to_view()

    # For recording.transfer_live()
    for marker in cmdx.ls(type="rdMarker"):
        marker.data.pop("previousMatrix", None)
        marker.data.pop("previousTranslate", None)
        marker.data.pop("previousRotate", None)


def _on_plan_complete(clientData=None):
    """User has exited the manipulator, restore viewport HUD"""

    def deferred():
        cmdx.current_time(cmdx.current_time())

    cmds.evalDeferred(deferred)
    log.info("Plan Complete")


def install_callbacks():
    __.callbacks.append(
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kBeforeOpen, _before_scene_open)
    )

    __.callbacks.append(
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterOpen, _after_scene_open)
    )

    __.callbacks.append(
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterLoadReference, _after_scene_open)
    )

    __.callbacks.append(
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kAfterImportReference, _after_scene_open)
    )

    __.callbacks.append(
        om.MSceneMessage.addCallback(
            om.MSceneMessage.kBeforeNew, _before_scene_new)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollCycleEvent", _on_cycle)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollLicenceExpiredEvent", _on_licence_expired)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollNonKeyableEvent", _on_nonkeyable_keyed)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollNonCommercialEvent", _on_noncommercial_file)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollNonCommercialExportEvent", _on_noncommercial_export)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollRecordingLimitEvent", _on_recording_limit)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollLocomotionLimitEvent", _on_locomotion_limit)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollManipulatorEntered", _on_manipulator_entered)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollManipulatorExited", _on_manipulator_exited)
    )

    __.callbacks.append(
        om.MUserEventMessage.addUserEventCallback(
            "ragdollPlanComplete", _on_plan_complete)
    )


def uninstall_callbacks():
    for callback_id in __.callbacks:
        om.MMessage.removeCallback(callback_id)
    __.callbacks[:] = []


def install_plugin():
    os.environ["XBMLANGPATH"] = os.pathsep.join([
        _resource(__.xbmlangpath),
        __.previousvars["XBMLANGPATH"]
    ])

    os.environ["MAYA_SCRIPT_PATH"] = os.pathsep.join([
        _resource(__.aetemplates),
        __.previousvars["MAYA_SCRIPT_PATH"]
    ])

    # Override with RAGDOLL_PLUGIN environment variable
    if not cmds.pluginInfo(c.RAGDOLL_PLUGIN_NAME, query=True, loaded=True):
        # May already have been loaded prior to calling install
        cmds.loadPlugin(c.RAGDOLL_PLUGIN, quiet=True)

    # Required for undo
    cmdx.install()

    # Required by commands.py
    cmds.loadPlugin("matrixNodes", quiet=True)

    __.version_str = cmds.pluginInfo(c.RAGDOLL_PLUGIN_NAME,
                                     query=True, version=True)

    # Debug builds come with a `.debug` suffix, e.g. `2020.10.15.debug`
    __.version = int("".join(__.version_str.split(".")[:3]))


def uninstall_plugin(force=True):
    if cmds.pluginInfo(c.RAGDOLL_PLUGIN_NAME, query=True, loaded=True):
        cmds.unloadPlugin(c.RAGDOLL_PLUGIN_NAME)

    # Restore environment
    os.environ["MAYA_SCRIPT_PATH"] = (
        os.environ["MAYA_SCRIPT_PATH"].replace(
            _resource(__.aetemplates) + os.pathsep, "")
    )
    os.environ["XBMLANGPATH"] = (
        os.environ["XBMLANGPATH"].replace(
            _resource(__.xbmlangpath) + os.pathsep, "")
    )


def uninstall_ui(force=False):
    protected = {}
    for title, widget in __.widgets.items():
        if not force and getattr(widget, "protected", False):
            protected[title] = widget
            continue

        try:
            widget.close()

        except RuntimeError:
            # May already have been deleted, and that's OK
            pass

        except Exception:
            traceback.print_exc()
            log.error(
                "An unexpected error occurred during uninstall of widgets."
            )

    __.widgets.clear()
    __.widgets.update(protected)


def install_menu():
    if __.menu:
        uninstall_menu()

    __.menu = cmds.menu(label="Ragdoll",
                        tearOff=True,
                        parent="MayaWindow")

    def item(key, command=None, option=None, label=None, visible=True):
        menuitem = __.menuitems[key]

        kwargs = {
            "label": label or menuitem.get("label", key),
            "enable": menuitem.get("enable", True),
            "echoCommand": True,
            "image": "bad.png",

            # These show up in the Maya "Help Line" on hover
            "annotation": menuitem.get("summary", ""),
        }

        if command:
            # Store as string instead of Python function,
            # so as to facilitate saving menu items to Shelf
            # via Ctrl + Shift + Click.
            script = "from ragdoll import interactive as ri\n"
            script += "ri.%s()" % command.__name__
            kwargs["command"] = script

            # Create a reverse-mapping for recording
            __.actiontokey[command.__name__] = key

        if "icon" in menuitem:
            icon = _resource(os.path.join("icons", menuitem["icon"]))
            kwargs["image"] = icon

        if "checkbox" in menuitem:
            kwargs["checkBox"] = True

        menuitem["path"] = cmds.menuItem(**kwargs)

        if option:
            cmds.menuItem(command=option, optionBox=True)

        if not visible:
            # The cmds.menuItem(visible=) flag was introduced in Maya 2019
            ui.hide_menuitem(menuitem["path"])

        return menuitem["path"]

    @contextlib.contextmanager
    def submenu(label, icon=None):
        kwargs = {
            "subMenu": True,
            "tearOff": True,
        }

        if icon:
            kwargs["image"] = _resource(os.path.join("icons", icon))

        previous_parent = cmds.setParent(menu=True, query=True)
        cmds.menuItem(label, **kwargs)
        yield
        cmds.setParent(previous_parent, menu=True)

    def divider(label=None):
        cmds.menuItem(divider=True, dividerLabel=label)

    item("markersManipulator", markers_manipulator)

    divider("Markers")

    item("assignMarker", assign_marker, assign_marker_options)
    item("assignGroup", assign_and_connect, assign_and_connect_options)
    item("assignHierarchy")
    item("assignEnvironment", assign_environment, assign_environment_options)

    with submenu("Assign Locomotion", icon="locomotion.png"):
        item("assignPlan", assign_plan, assign_plan_options)
        item("assignTerrain", assign_terrain)
        item("updatePlan", update_plan, update_plan_options)

        divider("Transfer")

        item("bakePlan", plan_to_animation)
        item("bakeTargets", animation_to_plan, animation_to_plan_options)
        item("extractPlan", extract_plan, extract_plan_options),

        divider("Edit")

        item("alignPlans", align_plans, align_plans_options)
        item("resetPlan", reset_plan, reset_plan_options)
        item("resetPlanStepSequence", reset_step_sequence,
             reset_step_sequence_options)
        item("resetPlanTargets", reset_targets, reset_targets_options)
        item("resetPlanOrigin", reset_plan_origin, reset_plan_origin_options)
        item("resetFoot", reset_foot, reset_foot_options)

        divider("System")

        item("deleteLocomotion", delete_all_locomotion,
             label="Delete All Locomotion")
        item("deleteLocomotion", delete_locomotion_from_selection,
             label="Delete Locomotion from Selection")

    divider("Transfer")

    item("recordMarkers", record_markers, record_markers_options)

    item("snapMarkers", snap_markers, snap_markers_options)

    divider("IO")

    item("exportPhysics", export_physics, export_physics_options)
    item("importPhysics", import_physics, import_physics_options)
    item("openPhysics", open_physics, open_physics_options)
    item("updatePhysics", open_physics, open_physics_options)

    divider("Manipulate")

    with submenu("Constrain", icon="constraint.png"):
        item("distanceConstraint",
             create_distance_constraint, label="Distance")
        item("pinConstraint",
             create_pin_constraint, create_pin_constraint_options, label="Pin")
        item("attachConstraint",
             create_attach_constraint, label="Attach")
        item("fixedConstraint",
             create_fixed_constraint, label="Weld")

    with submenu("Edit", icon="kinematic.png"):
        divider("Hierarchy")

        item("reassignMarker", reassign_marker, label="Reassign")
        item("retargetMarker", retarget_marker, retarget_marker_options,
             label="Retarget")
        item("reparentMarker", reparent_marker, label="Reparent")

        divider()

        item("unparentMarker", unparent_marker, label="Unparent")
        item("untargetMarker", untarget_marker, label="Untarget")

        divider("Membership")

        item("groupMarkers", group_markers)
        item("ungroupMarkers", ungroup_markers)
        item("moveToGroup", move_to_group)

        divider("Collisions")

        item("assignCollisionGroup",
             assign_collision_group,
             assign_collision_group_options)

        item("addToCollisionGroup", add_to_collision_group)
        item("removeFromCollisionGroup", remove_from_collision_group)

        divider("Solver")

        item("mergeSolvers", merge_solvers)
        item("extractFromSolver", extract_from_solver)
        item("moveToSolver", move_to_solver)

        divider("Cache")

        item("cacheSolver", cache_all, label="Cache")
        item("uncacheSolver", uncache, label="Uncache")

        divider("Link")

        item("linkSolver", link_solver)
        item("unlinkSolver", unlink_solver)

    with submenu("Fields", icon="force.png"):
        item("airField", air_field)
        item("dragField", drag_field)
        item("gravityField", gravity_field)
        item("newtonField", newton_field)
        item("radialField", radial_field)
        item("turbulenceField", turbulence_field)
        item("uniformField", uniform_field)
        item("vortexField", vortex_field)
        item("volumeAxis", volume_axis)
        item("volumeCurve", volume_curve)

        divider("Source")

        item("useSelectedAsSource", use_selected_as_source)
        item("disconnectSource", disconnect_source)

        divider("Centroids")

        item("comCentroid", field_com_centroid, label="Center of Mass")
        item("volumetricCentroids",
             field_volumetric_centroid,
             label="Volumetric")

    divider("Utilities")

    with submenu("Utilities", icon="magnet.png"):
        item("markerReplaceMesh",
             replace_marker_mesh,
             replace_marker_mesh_options)

        item("convertMesh", convert_to_mesh, convert_to_mesh_options)
        item("bakeMesh", bake_mesh, bake_mesh_options)

        divider()

        item("extractMarkers", extract_markers, extract_markers_options)

        divider()

        item("createLollipop", create_lollipops, create_lollipops_options)

        divider()

        item("toggleChannelBoxAttributes", toggle_channel_box_attributes,
             toggle_channel_box_attributes_options)

        divider()

        item("markersAutoLimit", auto_limit)
        item("resetShape", reset_shape)
        item("resetMarkerConstraintFrames", reset_marker_constraint_frames)
        item("editMarkerConstraintFrames", edit_marker_constraint_frames)

        divider("Time")

        item("warpTime", warp_time, warp_time_options)
        item("restoreTime", restore_time)

    with submenu("Select", icon="select.png"):
        item("selectMarkers", select_markers)
        item("selectGroups", select_groups)
        item("selectSolvers", select_solvers)

        divider()

        item("parentMarker", select_parent_marker, label="Marker Parent")
        item("childMarkers", select_child_markers, label="Marker Children")
        item("selectGroupMembers", select_group_members, label="Group Members")

    with submenu("System", icon="system.png"):
        divider("Scene")

        item("deleteAllPhysics", delete_all_physics, delete_physics_options,
             label="Delete All Physics")
        item("deleteAllPhysics", delete_physics_from_selection,
             delete_physics_options, label="Delete Physics from Selection")

        divider()

        item("explorer", show_explorer)

        divider()

        item("globalPreferences", global_preferences)
        item("savePreferences", save_preferences)
        item("resetPreferences", reset_preferences)

        item("resetTKey", reset_t_key, reset_t_key_options)

        with submenu("Logging Level", icon="logging.png"):
            item("loggingOff", logging_off)
            item("loggingInfo", logging_info)
            item("loggingWarning", logging_warning)
            item("loggingDebug", logging_debug)

    divider()

    label = "Ragdoll %s" % __.version_str

    item("showMessages",
         command=show_messageboard,
         option=show_messageboard_options,

         # Programatically displayed during logging
         visible=False)

    item("ragdoll", welcome_user, label=label)


def logging_debug():
    log.setLevel(logging.DEBUG)
    log.debug("Debug level set")


def logging_info():
    log.setLevel(logging.INFO)
    log.info("Info level set")


def logging_warning():
    log.setLevel(logging.WARNING)
    log.info("Warning level set")


def logging_off():
    log.setLevel(logging.CRITICAL)


def uninstall_menu():
    if __.menu:
        cmds.deleteUI(__.menu, menu=True)

    __.menu = None


def show_messageboard():
    RagdollGuiLogHandler.history[:] = []
    update_menu()


def show_messageboard_options(*args):
    win = ui.MessageBoard(RagdollGuiLogHandler.history, parent=ui.MayaWindow())
    win.show()

    # Auto-clear on show, message has been received
    RagdollGuiLogHandler.history[:] = []
    update_menu()


def update_menu():
    # Only attempt once the menu has actually been installed
    if not __.menu:
        return

    count = len(RagdollGuiLogHandler.history)

    label = (
        "Ragdoll (%d)" % count
        if count else "Ragdoll"
    )

    menu_item = __.menuitems["showMessages"]
    menu_kwargs = {
        "label": "%s (%d)" % (menu_item["label"], count),
        "edit": True,
    }

    try:
        menu_item_path = menu_item["path"]
    except KeyError:
        # The module has been abused in some way, possibly using `reload()`
        # This shouldn't break the plug-in though.
        return

    change_visibility = ui.show_menuitem if count else ui.hide_menuitem
    change_visibility(menu_item_path)

    # Help the user understand there's a problem somewhere
    cmds.menu(__.menu, edit=True, label=label)
    cmds.menuItem(menu_item_path, **menu_kwargs)


"""

# Upgrade Path

This next part is what maintains backwards compatibility when changes
have been made to the plug-in in such a way that it alters the behavior
of your scene. In such cases, an upgrade is performed to convert your
scene into one that behaves identically to before.

"""


def _evaluate_need_to_upgrade():
    oldest, count = upgrade.needs_upgrade()

    if not count:
        return

    saved_version = oldest
    current_version = __.version

    if not _opt("autoUpgrade"):
        message = """\
    This file was created with an older version of Ragdoll %s

    Would you like to convert %d nodes to Ragdoll %s? Not converting \
    may break the behavior from your previous scene.
    """ % (saved_version, count, current_version)

        if not MessageBox("%d Ragdoll nodes can be upgraded" % count, message):
            return

    try:
        count = upgrade.upgrade_all()
    except Exception:
        traceback.print_exc()
        return log.warning(
            "I had trouble upgrading, it should still "
            "work but you may want to consider reopening "
            "the file"
        )

    if count:
        log.debug("%d Ragdoll nodes were upgraded" % count)

        # Synchronise viewport, sometimes it can go stale
        time = cmds.currentTime(query=True)
        cmds.evalDeferred(lambda: cmds.currentTime(time, update=True))

    else:
        log.debug("Ragdoll nodes already up to date!")


@requires_ui
def validate_evaluation_mode():
    if not options.read("validateEvaluationMode"):
        return kSuccess

    mode = cmds.evaluationManager(query=True, mode=True)

    if mode[0] != "off":  # Both Serial and Parallel are OK
        return kSuccess

    def enable_parallel():
        cmds.evaluationManager(mode="parallel")
        log.info("Enabled Parallel Evaluation")
        return kSuccess

    return ui.warn(
        option="validateEvaluationMode",
        title="DG Evaluation Mode Detected",
        message=(
            "Maya is currently evaluating in the old DG mode, "
            "Ragdoll is most optimal with with Parallel Evaluation or "
            "at the very least Serial. If you experience issues with "
            "performance or drawing in the viewport, switch to Parallel."
        ),
        call_to_action="What would you like to do?",
        actions=[
            ("Ignore", lambda: True),
            ("Enable Parallel Evaluation", enable_parallel),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_cached_playback():
    if not cmds.optionVar(query="cachedPlaybackEnable"):
        return kSuccess

    if not options.read("validateCachingMode"):
        return kSuccess

    def disable_cached_playback():
        cmds.optionVar(intValue=("cachedPlaybackEnable", 0))
        log.info("Cached Playback Disabled")
        return kSuccess

    return ui.warn(
        option="validateCachingMode",
        title="Cached Playback Warning",
        message="cachedplayback.png",
        call_to_action=(
            "Ragdoll does not work well with Cached Playback.\n"
            "What would you like to do?"
        ),
        actions=[
            ("Ignore", lambda: True),
            ("Disable Cached Playback", disable_cached_playback),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_playbackspeed():
    if not options.read("validatePlaybackSpeed"):
        return kSuccess

    # 'Real-time playback' is only problematic if frames are skipped
    if options.read("frameskipMethod") == c.FrameskipPause:
        return kSuccess

    playback_speed = cmds.playbackOptions(playbackSpeed=True, query=True)

    if playback_speed == 0.0:

        # Keep this the current option as much as
        # possible, it is the most reliable
        options.write("frameskipMethod", c.FrameskipPause)

        return kSuccess

    def ignore():
        options.write("frameskipMethod", c.FrameskipIgnore)
        return kSuccess

    def fix_it():
        cmds.playbackOptions(playbackSpeed=0.0, maxPlaybackSpeed=1)
        log.info("Playing every frame")
        return kSuccess

    return ui.warn(
        option="validatePlaybackSpeed",
        title="Real-time playback detected",
        message=(
            "Real-time playback is supported, but requires Ragdoll "
            "to ignore frames during simulation which can result "
            "in less predictable results."
        ),
        call_to_action="What would you like to do?",
        actions=[
            ("Ignore Frames", ignore),
            ("Play Every Frame", fix_it),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_layer_override():
    if not options.read("validateLayerOverride"):
        return kSuccess

    layer = cmds.treeView("AnimLayerTabanimLayerEditor",
                          query=True, selectItem=True)

    if not layer or layer == ["BaseAnimation"]:
        return kSuccess

    if cmds.animLayer(layer[0], query=True, override=True):
        return kSuccess

    def fix_it():
        cmds.animLayer(layer[0], edit=True, override=True)
        log.info("%s was set to Override" % layer[0])
        return kSuccess

    return ui.warn(
        option="validateLayerOverride",
        title="Selected Layer",
        message=(
            "The selected layer is set to 'Additive' mode, which is "
            "incompatible with Record Simulation. It must be set to "
            "'Override'"
        ),
        call_to_action="What would you like to do?",
        actions=[
            ("Ignore", lambda: True),
            ("Set to Override", fix_it),
            ("Cancel", lambda: False)
        ]
    )


def _filtered_selection(node_type, selection=None):
    """Interpret user selection

    They should be able to..

    1. Select transforms, even though they meant the shape
    2. Select a transform with *multiple* shapes of a given type
    2. Select the shape
    3. Select multiple shapes
    4. Select multiple shapes *and* transforms

    """

    selection = list(selection or cmdx.selection())

    if not selection:
        return []

    shapes = []
    for node in selection:
        if node.isA(cmdx.kDagNode):
            for shape in node.shapes(node_type):
                if "intermediateObject" in shape and shape["io"]:
                    log.info("Skipped intermediate shape %s" % shape)
                    continue
                shapes += [shape]

    shapes = filter(None, shapes)
    shapes = list(shapes) + selection
    shapes = filter(lambda shape: shape.isA(node_type), shapes)

    return list(shapes)


def _opt(key, override=None):
    override = override or {}
    return override.get(key, options.read(key))


def _rewind(scene):
    start_time = scene["startTime"].as_time()
    cmdx.currentTime(start_time)


def _find_current_solver(solver, show_plugin_shapes=True):
    solver_items = options.items("markersAssignSolver")
    NewSolver = len(solver_items) - 1
    is_new = False

    if solver == NewSolver:
        if not validate_evaluation_mode():
            return None, None

        if not validate_cached_playback():
            return None, None

        solver = commands.create_solver(opts={
            "sceneScale": options.read("markersSceneScale"),
        })
        is_new = True

    else:
        # The UI may have remained open, providing the user with
        # out-of-date options that may no longer exist.
        try:
            solver = solver_items[solver]
            solver = cmdx.encode(solver)

        except (cmdx.ExistError, IndexError):
            options.write("markersAssignSolver", 0)
            return _find_current_solver(NewSolver, show_plugin_shapes)

    if _is_interactive() and show_plugin_shapes:
        # Protect user against Plugin Shapes not being visible
        for panel in cmds.getPanel(visiblePanels=True):
            if not cmds.modelPanel(panel, query=True, exists=True):
                continue

            cmds.modelEditor(panel, edit=True, pluginShapes=True)

    return solver, is_new


def _find_solver_for(marker):
    assert marker and marker.isA("rdMarker"), "%s wasn't a marker" % marker
    output = marker["startState"].output()
    while output and output is not marker and not output.isA("rdSolver"):
        output = output["startState"].output()
    return output


def _add_to_objset(markers):
    objset = cmdx.find("rMarkers")

    if not objset:
        with cmdx.DGModifier() as mod:
            objset = mod.create_node("objectSet", name="rMarkers")

    with cmdx.DGModifier() as mod:
        for marker in markers:
            index = objset["dnSetMembers"].next_available_index()
            mod.connect(marker["message"], objset["dnSetMembers"][index])
            mod.do_it()


@with_exception_handling
def markers_manipulator(selection=None, **opts):
    selection = plans_from_selection(selection)

    if selection:
        return cmds.setToolTo("ShowManips")

    selection = _markers_from_selection(selection)
    if selection:
        solvers = i__.promote_linked_solvers(
            _solvers_from_selection(selection)
        )

        if len(solvers) == 1:
            # all markers in selection belong to a single solver, take one
            #   to manipulate.
            selection = selection[-1:]
        else:
            selection = solvers
    else:
        selection = i__.promote_linked_solvers(
            _solvers_from_selection(selection) or cmdx.ls(type="rdSolver")
        )

    if len(selection) < 1:
        raise i__.UserWarning(
            "No solver found",
            "No solver found to manipulate."
        )

    elif len(selection) == 1:
        cmds.select(str(selection[0]))
        cmds.setToolTo("ShowManips")
        log.info("Manipulating %s" % selection[0])

    else:
        helptext = """\
            <p>
            There are multiple solvers in the scene.
            <br>
            <br>
            Use the <b>"T"</b> keyboard shortcut with
            a solver or marker selected to skip this popup.
            </p>
        """

        def on_picked(solver_name):
            cmds.select(solver_name)
            return markers_manipulator()

        dialog = widgets.SolverSelectorDialog(
            solvers=selection,
            help=helptext,
            best_guess=None,  # todo: best-guess from viewport
            parent=ui.MayaWindow()
        )
        dialog.solver_picked.connect(on_picked)
        dialog.open()

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def assign_marker(selection=None, **opts):
    selection = selection or cmdx.selection()
    selection = cmdx.ls(selection, type=("transform", "joint"))

    if not selection:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one or more controls to assign markers to."
        )

    opts = dict({
        "connect": False,

        "refit": _opt("markersRefit", opts),
        "createGround": _opt("markersCreateGround", opts),
        "createObjectSet": _opt("markersCreateObjectSet", opts),
        "createLollipop": _opt("markersCreateLollipop", opts),
        "group": _opt("markersAssignGroup", opts),
        "solver": _opt("markersAssignSolver", opts),
        "autoLimit": _opt("markersAutoLimit", opts),
        "showPluginShapes": _opt("markersShowPluginShapes", opts),
        "materialInChannelBox": _opt("markersChannelBoxMaterial", opts),
        "shapeInChannelBox": _opt("markersChannelBoxShape", opts),
        "limitInChannelBox": _opt("markersChannelBoxLimit", opts),
        "advancedPoseInChannelBox": _opt(
            "markersChannelBoxAdvancedPose", opts),

        # Lollipop options
        "basicAttributes": _opt("lollipopBasicAttributes", opts),
        "advancedAttributes": _opt("lollipopAdvancedAttributes", opts),
        "groupAttributes": _opt("lollipopGroupAttributes", opts),
        "linearAngularStiffness": _opt("markersLinearAngularStiffness2", opts),

    }, **(opts or {}))

    _update_solver_options()
    _update_group_options()

    solver, is_new = _find_current_solver(
        opts["solver"], opts["showPluginShapes"])

    if not solver:
        # This should never really happen
        log.warning("No solver found")
        return kFailure

    if is_new and opts["createGround"]:
        commands.create_ground(solver)

    owner = solver
    new_group = False

    if opts["group"] == 0:  # No group
        pass

    if opts["group"] == 1 and len(selection) > 1:  # Append to existing
        root_transform = selection[0]
        root_marker = root_transform["message"].output(type="rdMarker")
        existing_group = None

        # Append to this group
        if root_marker is not None:
            existing_group = root_marker["startState"].output(type="rdGroup")

        # Create otherwise make one
        if existing_group is not None:
            owner = existing_group
        else:
            new_group = True

    if opts["group"] == 2:  # New group
        new_group = True

    if opts["group"] > 2:
        try:
            items = options.items("markersAssignGroup")
            owner = cmdx.encode(items[opts["group"]])
        except (cmdx.ExistError, IndexError):
            options.write("markersAssignGroup", 1)

    if new_group:
        root_transform = selection[0]
        name = root_transform.name(namespace=False) + "_rGroup"
        owner = commands.create_group(solver, name, opts={
            "selfCollide": not opts["connect"],
            "linearAngularStiffness": opts["linearAngularStiffness"],
        })

    if owner is None:
        owner = solver

    markers = []

    try:
        markers += commands.assign_markers(selection, owner, opts={
            "refit": opts["refit"],
            "connect": opts["connect"],
            "autoLimit": opts["autoLimit"],
            "linearAngularStiffness": opts["linearAngularStiffness"],
        })

    except RuntimeError as e:
        raise i__.UserWarning("Already assigned", str(e))

    if opts["createLollipop"]:
        commands.create_lollipops(markers, opts={
            "basicAttributes": opts["basicAttributes"],
            "advancedAttributes": opts["advancedAttributes"],
            "groupAttributes": opts["groupAttributes"],
        })

    if opts["createObjectSet"]:
        _add_to_objset(markers)

    channel_box = {
        "materialInChannelBox": False,
        "shapeInChannelBox": False,
        "limitInChannelBox": False,
        "advancedPoseInChannelBox": False,
    }

    for key, value in channel_box.items():
        channel_box[key] = opts[key]

    if any(channel_box.values()):
        commands.toggle_channel_box_attributes(markers, opts={
            "materialAttributes": channel_box["materialInChannelBox"],
            "shapeAttributes": channel_box["shapeInChannelBox"],
            "limitAttributes": channel_box["limitInChannelBox"],
            "advancedPoseAttributes": channel_box["advancedPoseInChannelBox"],
        })

    cmds.select(list(t.shortest_path() for t in selection))
    cmds.refresh()

    return kSuccess


def assign_and_connect(selection=None, **opts):
    return assign_marker(selection, **dict({
        "connect": True,
    }, **opts))


@i__.affects_initial_state
def assign_environment(selection=None, **opts):
    opts = dict({
        "solver": _opt("markersAssignSolver", opts),
        "visualise": _opt("visualiseEnvironment", opts),
        "showPluginShapes": _opt("markersShowPluginShapes", opts),
    })

    _update_solver_options()

    solver, is_new = _find_current_solver(
        opts["solver"], opts["showPluginShapes"])

    if not solver:
        return kFailure

    for mesh in cmdx.selection():
        if not mesh.isA(cmdx.kShape):
            mesh = mesh.shape(type="mesh")

        if not (mesh and mesh.isA(cmdx.kMesh)):
            raise i__.UserWarning(
                "Bad Selection",
                "Select a polygon mesh to use for an environment."
            )

        commands.assign_environment(mesh, solver, opts={
            "visualise": opts["visualise"]
        })

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def assign_collision_group(selection=None, **opts):
    groups = shapes_from_selection(selection, type="rdCollisionGroup")
    markers = list(_markers_from_selection(selection))

    group = None

    # Permit merging of collision groups
    if groups and len(groups) == 1:
        group = groups[0]

    elif groups and len(groups) > 1:
        for group in groups:
            existing = group["collisionGroup"].outputs(type="rdMarker")

            for marker in existing:
                markers.append(marker)

    if not markers:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one or more markers to assign a collision group to."
        )

    group = commands.assign_collision_group(markers, group)
    cmds.select(str(group.parent()))

    log.info("Created collision group for %s" % (
        ", ".join(str(m) for m in markers))
    )

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def add_to_collision_group(selection=None, **opts):
    groups = shapes_from_selection(selection, type="rdCollisionGroup")

    if not groups or len(groups) > 1:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one collision group, along with one or more Markers"
        )

    group = groups[0]
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one or more markers to assign a collision group to."
        )

    commands.add_to_collision_group(markers, group)
    cmds.select(str(group.parent()))

    log.info("Added %s to %s" % (
        ", ".join(str(m) for m in markers), group)
    )

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def remove_from_collision_group(selection=None, **opts):
    groups = shapes_from_selection(selection, type="rdCollisionGroup")

    if not groups or len(groups) > 1:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one collision group, along with one or more Markers"
        )

    group = groups[0]
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "Bad Selection",
            "Select one or more markers to assign a collision group to."
        )

    commands.remove_from_collision_group(markers, group)
    cmds.select(str(group.parent()))

    log.info("Removed %s from %s" % (
        ", ".join(str(m) for m in markers), group),
    )

    return kSuccess


def _solvers_from_selection(selection=None):
    """Find solvers from selection

    Examples:
        >>> ctrl, _ = cmds.polyCube()
        >>> cmds.select(ctrl)
        >>> _ = assign_marker()

        # Initialise solver
        >>> _ = cmds.getAttr(cmds.ls(type="rdSolver")[0] + ".startState")
        >>> _ = cmds.getAttr(cmds.ls(type="rdSolver")[0] + ".currentState")

        # Select transform
        >>> cmds.select(ctrl)
        >>> len(_solvers_from_selection())
        1

        # Select marker
        >>> cmds.select(cmds.ls(type="rdMarker"))
        >>> len(_solvers_from_selection())
        1

        # Select group
        >>> _ = group_markers()
        >>> cmds.select(cmds.ls(type="rdGroup"))
        >>> len(_solvers_from_selection())
        1

        # Select group transform
        >>> cmds.select(str(cmdx.ls(type="rdGroup")[0].parent()))
        >>> len(_solvers_from_selection())
        1

        # Select solver transform
        >>> cmds.select(str(cmdx.ls(type="rdSolver")[0].parent()))
        >>> len(_solvers_from_selection())
        1

        # Select grouped marker
        >>> cmds.select(cmds.ls(type="rdMarker"))
        >>> len(_solvers_from_selection())
        1

        # Select multiple
        >>> cmds.select(cmds.ls(type=("rdMarker", "rdGroup", "rdSolver")))
        >>> len(_solvers_from_selection())
        1

    """

    solvers = set()
    selection = selection or cmdx.selection()

    ragdoll_nodes = []
    ragdoll_types = (
        "rdSolver",
        "rdMarker",
        "rdGroup",
        "rdFixedConstraint",
        "rdPinConstraint",
        "rdDistanceConstraint",
    )

    for selected in selection:
        if selected.isA(cmdx.kTransform):
            selected = selected["message"].output(type=ragdoll_types)

        if selected and selected.isA(ragdoll_types):
            ragdoll_nodes += [selected]

    for node in ragdoll_nodes:
        if node.isA("rdSolver"):
            solvers.add(node)
        else:
            other = node["startState"].output()

            if other:
                if other.isA("rdSolver"):
                    solvers.add(other)
                elif other.isA("rdGroup"):
                    other = other["startState"].output(type="rdSolver")
                    if other:
                        solvers.add(other)

    return tuple(solvers)


def _markers_from_selection(selection=None):
    """Find markers from selection

    Examples:
        >>> ctrl1, _ = cmds.polyCube()
        >>> ctrl2, _ = cmds.polyCube()
        >>> cmds.select(ctrl1, ctrl2)
        >>> _ = assign_marker()

        # Select transform
        >>> cmds.select(ctrl1)
        >>> len(_markers_from_selection())
        1

        # Select markers, including ground
        >>> cmds.select(cmds.ls(type="rdMarker"))
        >>> len(_markers_from_selection())
        3

    """

    markers = list()

    for selected in selection or cmdx.selection():
        if selected.isA(cmdx.kDagNode):
            selected = selected["message"].output(type="rdMarker")

        if selected and selected.isA("rdMarker"):
            if selected in markers:
                continue

            markers.append(selected)

    return tuple(markers)


def plans_from_selection(selection=None):
    """Find plans from selection"""

    plans = list()

    for selected in selection or cmdx.selection():
        plan = None

        if selected.is_a("rdFoot"):
            plan = selected["startState"].output(type="rdPlan")

        if selected.is_a(cmdx.kDagNode):
            plan = selected.shape(type="rdPlan")

            if not plan:
                plan = selected["message"].output(type="rdPlan")

            if not plan:
                foot = selected["message"].output(type="rdFoot")

                if foot:
                    plan = foot["startState"].output(type="rdPlan")

        if plan and plan.is_a("rdPlan") and plan not in plans:
            plans.append(plan)

    return tuple(plans)


def shapes_from_selection(selection, type):
    """Find shapes of type `type` from selection"""

    shapes = list()

    for selected in selection or cmdx.selection():
        if selected.isA(cmdx.kDagNode):
            selected = selected.shape(type=type)

        if selected and selected.isA(type):
            if selected in shapes:
                continue

            shapes.append(selected)

    return tuple(shapes)


@with_exception_handling
@i__.with_undo_chunk
def merge_solvers(selection=None, **opts):
    solvers = _filtered_selection("rdSolver", selection)

    if not solvers:
        raise i__.UserWarning(
            "No solvers found",
            "Select one or more solvers to group."
        )

    if len(solvers) != 2:
        raise i__.UserWarning(
            "Invalid Selection",
            "Select 2 solvers, the latter will contain the former."
        )

    commands.merge_solvers(solvers[0], solvers[1])

    return True


@with_exception_handling
@i__.with_undo_chunk
def extract_from_solver(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to group."
        )

    commands.extract_from_solver(markers)

    return True


@with_exception_handling
@i__.with_undo_chunk
def group_markers(selection=None, **opts):

    # Let the user merge groups
    groups = []
    for group in cmdx.selection() or selection:
        if group.is_a(cmdx.kTransform):
            group = group.shape(type="rdGroup")

        if group and group.is_a("rdGroup"):
            groups.append(group)

    markers = []
    for group in groups:
        for element in group["inputStart"]:
            marker = element.input(type="rdMarker")
            if marker:
                markers.append(marker)

    markers += _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to group."
        )

    group = commands.group_markers(markers)
    cmds.select(str(group.parent()))

    return True


@with_exception_handling
@i__.with_undo_chunk
def move_to_group(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to group."
        )

    groups = _filtered_selection("rdGroup", selection)

    if len(groups) < 1:
        raise i__.UserWarning(
            "No group found",
            "Select some markers and a group to add things together."
        )

    if len(groups) > 1:
        log.warning("Multiple groups selected, using %s" % groups[0])

    group = groups[0]
    for marker in markers:
        commands.move_to_group(marker, group)

    return True


@with_exception_handling
@i__.with_undo_chunk
def move_to_solver(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to group."
        )

    solvers = _filtered_selection("rdSolver", selection)

    if len(solvers) < 1:
        raise i__.UserWarning(
            "No group found",
            "Select some markers and a group to add things together."
        )

    if len(solvers) > 1:
        log.warning("Multiple solvers selected, using %s" % solvers[0])

    solver = solvers[0]
    for marker in markers:
        commands.move_to_solver(marker, solver)

    return True


@with_exception_handling
@i__.with_undo_chunk
def ungroup_markers(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to group."
        )

    commands.ungroup_markers(markers)

    return True


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def create_distance_constraint(selection=None, **opts):
    try:
        a, b = _markers_from_selection(selection)
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select two markers to constrain."
        )

    con = commands.create_distance_constraint(a, b)
    cmds.select(str(con.parent()))

    return True


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def create_fixed_constraint(selection=None, **opts):
    try:
        a, b = _markers_from_selection(selection)
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select two markers to constrain."
        )

    con = commands.create_fixed_constraint(a, b)
    cmds.select(str(con.parent()))

    return True


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def create_pin_constraint(selection=None, **opts):
    opts = dict({
        "location": _opt("pinLocation", opts),
    })

    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "Selection Problem",
            "Select one or more markers to pin"
        )

    cons = []
    for a in markers:
        con = commands.create_pin_constraint(a, opts=opts)
        cons += [con.parent().path()]

    cmds.select(cons)

    return True


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def create_attach_constraint(selection=None, **opts):
    selection = selection or cmdx.sl()

    try:
        a, b = _markers_from_selection(selection)
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select two markers to constrain."
        )

    transform = selection[1] if selection[1].is_a(cmdx.kTransform) else None
    con = commands.create_pin_constraint(a, b, transform=transform)
    cmds.select(str(con.parent()))

    return True


@contextlib.contextmanager
def progressbar(status="Progress.. ", max_value=100):
    if _is_interactive():
        import maya.mel
        progress_bar = maya.mel.eval('$tmp = $gMainProgressBar')

        cmds.progressBar(progress_bar,
                         edit=True,
                         beginProgress=True,
                         isInterruptable=True,
                         status=status,
                         maxValue=max_value)

        try:
            yield progress_bar

        finally:
            cmds.progressBar(progress_bar, edit=True, endProgress=True)

    else:
        yield


@i__.with_undo_chunk
@with_exception_handling
def snap_markers(selection=None, **opts):
    opts = dict({
        "useSelection": _opt("markersSnapUseSelection", opts),
        "ignoreJoints": _opt("markersIgnoreJoints", opts),
        "maintainOffset": _opt("markersRecordMaintainOffset2", opts),
    }, **(opts or {}))

    solvers = _filtered_selection("rdSolver", selection)
    include = []

    if len(solvers) < 1:
        solvers = cmdx.ls(type="rdSolver")

    if opts["useSelection"]:
        include += _filtered_selection(cmdx.kDagNode, selection)

    for solver in solvers:
        recording.snap(solver, {
            "include": include,
            "ignoreJoints": opts["ignoreJoints"],
            "maintainOffset": opts["maintainOffset"],
        })


@i__.with_undo_chunk
@with_exception_handling
def record_markers(selection=None, **opts):
    opts = dict({
        "method": _opt("markersRecordMethod", opts),
        "recordRange": _opt("markersRecordRange", opts),
        "recordCustomStartTime": _opt("markersRecordCustomStartTime", opts),
        "recordCustomEndTime": _opt("markersRecordCustomEndTime", opts),
        "recordKinematic": _opt("markersRecordKinematic", opts),
        "toLayer": _opt("markersRecordToLayer", opts),
        "setInitialKey": _opt("markersRecordInitialKey", opts),
        "useSelection": _opt("markersRecordUseSelection", opts),
        "ignoreJoints": _opt("markersIgnoreJoints", opts),
        "recordReset": _opt("markersRecordReset", opts),
        "recordSimplify": _opt("markersRecordSimplify", opts),
        "recordFilter": _opt("markersRecordFilter", opts),
        "accumulateByLayer": _opt("markersRecordAccumulateByLayer", opts),
        "autoCache": _opt("markersRecordAutoCache", opts),
        "recordMaintainOffset": _opt("markersRecordMaintainOffset2", opts),
        "closedLoop": _opt("markersRecordClosedLoop", opts),
        "minIterationCount": _opt("markersSnapMinIterations", opts),
        "maxIterationCount": _opt("markersSnapMaxIterations", opts),
        "updateViewport": _opt("markersRecordUpdateViewport", opts),
        "include": None,
        "exclude": None,
        "mode": _opt("markersRecordMode", opts),
        "protectOriginalInput": _opt(
            "markersRecordProtectOriginalInput", opts),
    }, **(opts or {}))

    solvers = _solvers_from_selection(selection)

    if not solvers:
        solvers = cmdx.ls(type="rdSolver")

    if not solvers or len(solvers) > 1:
        raise i__.UserWarning(
            "No solver selected",
            "Select a solver to record."
        )

    solver = solvers[0]

    # Remove linked solvers, we'll record those from the main solver
    if solver["startState"].output(type="rdSolver") is not None:
        log.warning("Selected solver is linked")
        return kFailure

    if opts["useSelection"]:
        opts["include"] = _filtered_selection(cmdx.kDagNode, selection)

    if opts["recordRange"] == 0:
        start_time = cmdx.animation_start_time()
        end_time = cmdx.animation_end_time()

    elif opts["recordRange"] == 1:
        start_time = cmdx.min_time()
        end_time = cmdx.max_time()

    else:
        start_time = opts["recordCustomStartTime"]
        end_time = opts["recordCustomEndTime"]

    if isinstance(start_time, int):
        start_time = cmdx.time(start_time)

    if isinstance(end_time, int):
        end_time = cmdx.time(end_time)

    # A selected time overrides it all
    if _is_interactive():
        a, b = cmdx.selected_time()

        # Returns a single frame if nothing was selected
        if (b.value - a.value) > 2:
            start_time, end_time = a, b

    opts["startFrame"] = int(start_time.value)
    opts["endFrame"] = int(end_time.value)

    with refresh_suspended(not opts["updateViewport"]):
        if opts["method"] == c.RecordConstraintMethod:
            return _constraint_record_markers(solver, **opts)
        else:
            return _match_record_markers(solver, **opts)


def _constraint_record_markers(solver, **opts):
    cached = {}

    with cmdx.DagModifier() as mod:
        cached[solver] = solver["cache"].read()
        mod.try_set_attr(solver["cache"], c.StaticCache)

    total_frames = 0
    timer = i__.Timer("record")
    with timer as duration, progressbar() as p:
        op = {
            "startTime": opts["startFrame"],
            "endTime": opts["endFrame"],
            "include": opts["include"],
            "exclude": opts["exclude"],
            "accumulateByLayer": opts["accumulateByLayer"],
            "includeKinematic": opts["recordKinematic"],
            "maintainOffset": opts["recordMaintainOffset"],
            "simplifyCurves": opts["recordSimplify"],
            "rotationFilter": opts["recordFilter"],
            "toLayer": opts["toLayer"],
            "setInitialKey": opts["setInitialKey"],
            "ignoreJoints": opts["ignoreJoints"],
            "closedLoop": opts["closedLoop"],
            "mode": opts["mode"],
        }

        instance = recording._Recorder(solver, op)

        previous_progress = 0
        for step, progress in instance.record():
            progress = int(progress)

            if progress % 5 == 0 and progress != previous_progress:
                log.info("%.1f%% (%s)" % (progress, step.title()))
                previous_progress = progress

            # Allow the user to cancel with the ESC key
            if _is_interactive():
                if cmds.progressBar(p, query=True, isCancelled=True):
                    break

                cmds.progressBar(p, edit=True, step=1)

        total_frames = opts["endFrame"] - opts["startFrame"]

    stats = (duration.s, total_frames / max(0.00001, duration.s))
    log.info("Recorded markers in %.2fs (%d fps)" % stats)

    cmds.inViewMessage(
        amg="Recorded markers in <hl>%.2fs</hl> (%d fps)" % stats,
        pos="topCenter",
        fade=True
    )

    # The native recorded nodes aren't updated for some reason
    if _is_interactive():
        cmds.currentTime(cmds.currentTime(query=True))

    # Turn off auto-cache after recording, so as to let the viewport
    # show the cached simulation while it's baking to keyframes. And
    # to also not re-simulate during baking, that would be a waste.
    if not opts["autoCache"]:
        with cmdx.DagModifier() as mod:
            mod.set_attr(solver["cache"], cached[solver])

    return kSuccess


def _match_record_markers(solver, **opts):
    timer = i__.Timer("match_record")
    with timer as duration, progressbar() as p:
        it = recording_match.record_simulation(solver, opts)

        previous_progress = 0
        for step, progress in it:
            progress = int(progress)

            if progress % 5 == 0 and progress != previous_progress:
                log.info("%.1f%% (%s)" % (progress, step.title()))
                previous_progress = progress

            # Allow the user to cancel with the ESC key
            if _is_interactive():
                if cmds.progressBar(p, query=True, isCancelled=True):
                    break

                cmds.progressBar(p, edit=True, step=1)

    total_frames = opts["endFrame"] - opts["startFrame"]
    stats = (duration.s, total_frames / max(0.00001, duration.s))
    log.info("Recorded markers in %.2fs (%d fps)" % stats)

    cmds.inViewMessage(
        amg="Recorded markers in <hl>%.2fs</hl> (%d fps)" % stats,
        pos="topCenter",
        fade=True
    )

    # The native recorded nodes aren't updated for some reason
    if _is_interactive():
        cmds.currentTime(cmds.currentTime(query=True))

    return True


@i__.with_undo_chunk
@with_exception_handling
def extract_markers(selection=None, **opts):
    opts = dict({
        "extractAndAttach": _opt("markersExtractAndAttach", opts)
    }, **(opts or {}))

    solvers = _filtered_selection("rdSolver", selection)

    if len(solvers) < 1:
        solvers = cmdx.ls(type="rdSolver")

    if len(solvers) < 1:
        raise i__.UserWarning(
            "Nothing to extract",
            "Ensure there is at least 1 marker in the "
            "scene along with a solver."
        )

    # Remove linked solvers, we'll record those from the main solver
    for solver in solvers[:]:
        if solver["startState"].output(type="rdSolver") is not None:
            solvers.remove(solver)

    end_time = cmdx.max_time()

    total_frames = 0
    timer = i__.Timer("record")

    for solver in solvers:
        with timer as duration, progressbar() as p, refresh_suspended():
            start_time = solver["_startTime"].as_time()
            instance = recording._Recorder(solver, {
                "startTime": start_time,
                "endTime": end_time,
                "extractAndAttach": opts["extractAndAttach"],
            })

            previous_progress = 0
            for status in instance.extract():
                step, progress = status
                progress = int(progress)

                if progress % 5 == 0 and progress != previous_progress:
                    log.info("%.1f%% (%s)" % (progress, step.title()))
                    previous_progress = progress

                # Allow the user to cancel with the ESC key
                if _is_interactive():
                    if cmds.progressBar(p, query=True, isCancelled=True):
                        break

                    cmds.progressBar(p, edit=True, step=1)

            total_frames += int((end_time - start_time).value)

    stats = (duration.s, total_frames / max(0.00001, duration.s))
    log.info("Extracted markers in %.2fs (%d fps)" % stats)

    cmds.inViewMessage(
        amg="Extracted markers in <hl>%.2fs</hl> (%d fps)" % stats,
        pos="topCenter",
        fade=True
    )

    return kSuccess


def _last_command():
    """Store repeatable command at module-level

    This assumes no threading happens.

    """

    _last_command._func()


def repeatable(func):
    """Make `func` repeatable in Maya

    See https://groups.google.com/g/python_inside_maya
               /c/2GO5PGD6Q6w/m/U-97zyB_DAAJ

    """

    @functools.wraps(func)
    def repeatable_wrapper(*args, **kwargs):
        _last_command._func = func

        command = 'python("import {0};{0}._last_command()")'.format(__name__)
        result = func(*args, **kwargs)

        try:
            cmds.repeatLast(
                addCommand=command,
                addCommandLabel=func.__name__
            )
        except Exception:
            pass

        return result
    return repeatable_wrapper


@repeatable
def transfer_live(selection=None, **opts):
    manip = json.loads(cmds.ragdollDump(manipulator=True))

    if not manip["solverPath"]:
        return kFailure

    solver = cmdx.encode(manip["solverPath"])
    keyframe = opts.get("keyframe", False)

    if not solver:
        raise i__.UserWarning(
            "Internal Error",
            "Could not find currently active solver, this is a bug."
        )

    with i__.Timer("transfer") as duration:
        recording.transfer_live(solver, keyframe=keyframe, opts=opts)

    if keyframe:
        log.info("Keyframed animation in %.1f ms" % duration.ms)

    else:
        log.info("Transferred animation in %.1f ms" % duration.ms)

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def retarget_marker(selection=None, **opts):
    opts = dict({
        "append": _opt("markersAppendTarget", opts),
    }, **(opts or {}))

    try:
        a, b = selection or cmdx.sl()
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select an existing marker along with "
            "where you would like it reassigned."
        )

    if a.isA(cmdx.kDagNode):
        a = a["message"].output(type="rdMarker")

    if not (a and a.type() == "rdMarker"):
        raise i__.UserWarning(
            "No marker found",
            "The first selection should have a marker assigned."
        )

    if not (b and b.isA(cmdx.kDagNode)):
        raise i__.UserWarning(
            "No suitable target found",
            "The second selection should be a suitable target, a DAG node. "
            "'%s' was <b>not</b> a DAG node" % b
        )

    commands.retarget_marker(a, b, opts)

    Window = widgets.RetargetWindow
    if Window.instance and ui.isValid(Window.instance):
        try:
            Window.instance.refresh_if_outdated()
        except Exception:
            # This can fail, it's OK
            pass

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def reparent_marker(selection=None, **opts):
    markers = _markers_from_selection(selection)

    try:
        children, parent = markers[:-1], markers[-1]
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select any number of child markers "
            "along with the new parent."
        )

    for child in children:
        commands.reparent_marker(child, parent)
        log.info("Parented %s -> %s" % (child, parent))

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def unparent_marker(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to unparent."
        )

    for marker in markers:
        commands.unparent_marker(marker)
        log.info("Unparented %s" % (marker))

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def untarget_marker(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if not markers:
        raise i__.UserWarning(
            "No markers found",
            "Select one or more markers to remove the target(s) from."
        )

    for marker in markers:
        commands.untarget_marker(marker)

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def reassign_marker(selection=None, **opts):
    try:
        a, b = selection or cmdx.sl()
    except ValueError:
        raise i__.UserWarning(
            "Selection Problem",
            "Select an existing marker along with "
            "where you would like it reassigned."
        )

    if a.isA(cmdx.kDagNode):
        a = a["message"].output(type="rdMarker")

    if not (a and a.type() == "rdMarker"):
        raise i__.UserWarning(
            "No marker found",
            "The first selection should have a marker assigned."
        )

    if not (b and b.isA(cmdx.kDagNode)):
        raise i__.UserWarning(
            "No suitable target found",
            "The second selection should be a suitable target, a DAG node. "
            "'%s' was <b>not</b> a DAG node" % b
        )

    commands.reassign_marker(a, b)

    return kSuccess


def _selection(selection=None):
    result = []
    for node in selection or cmdx.selection():
        if isinstance(node, str):
            node = cmdx.encode(node)

        result.append(node)
    return result


@i__.with_undo_chunk
@with_exception_handling
def toggle_channel_box_attributes(selection=None, **opts):
    opts = dict({
        "materialAttributes": _opt("markersChannelBoxMaterial", opts),
        "shapeAttributes": _opt("markersChannelBoxShape", opts),
        "limitAttributes": _opt("markersChannelBoxLimit", opts),
        "advancedPoseAttributes": _opt("markersChannelBoxAdvancedPose", opts),
    }, **(opts or {}))

    markers = cmdx.ls(type="rdMarker")

    if not markers:
        raise i__.UserWarning(
            "No Markers Found",
            "No markers were found to toggle attributes on."
        )

    visible = commands.toggle_channel_box_attributes(markers, opts=opts)

    log.info("Successfully %s attributes for %d markers" % (
        ("hid" if visible else "showed"), len(markers)
    ))


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def reset_marker_constraint_frames(selection=None, **opts):
    for node in _selection(selection):
        marker = node

        if marker.isA(cmdx.kDagNode):
            marker = node["message"].output(type="rdMarker")

        if not (marker and marker.type() == "rdMarker"):
            continue

        with cmdx.DGModifier() as mod:
            commands.reset_constraint_frames(mod, marker)

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def reset_shape(selection=None, **opts):
    markers = _markers_from_selection(selection)

    for marker in markers:
        commands.reset_shape(marker)

    return kSuccess


@i__.with_undo_chunk
def select_parent_marker(selection=None, **opts):
    parent = None

    for marker in selection or cmdx.sl():
        if marker.isA(cmdx.kDagNode):
            marker = marker["message"].output(type="rdMarker")

        if not marker or marker.type() != "rdMarker":
            continue

        marker = marker["parentMarker"].input(type="rdMarker")
        if not marker:
            continue

        parent = marker["sourceTransform"].input()

    if not parent:
        cmds.warning("No parent found")
        cmds.select(deselect=True)
    else:
        cmds.select(parent.shortest_path())

    return kSuccess


@i__.with_undo_chunk
def select_child_markers(selection=None, **opts):
    children = list()

    for marker in selection or cmdx.sl():
        if marker.isA(cmdx.kDagNode):
            marker = marker["message"].output(type="rdMarker")

        if not marker or marker.type() != "rdMarker":
            continue

        plug = marker["ragdollId"].output(type="rdMarker", plug=True)
        if not plug or plug.name() != "parentMarker":
            continue

        child = plug.node()
        child = child["sourceTransform"].input()

        if child:
            children += [child]

    if not children:
        cmds.warning("No markers selected")
    else:
        cmds.select([c.shortest_path() for c in children])
    return kSuccess


@i__.with_undo_chunk
def snap_to_sim(selection=None, **opts):
    selection = selection or cmdx.sl()
    selection = cmdx.ls(selection, type=("transform", "joint"))
    recording.snap(selection)
    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def create_lollipops(selection=None, **opts):
    opts = dict({
        "basicAttributes": _opt("lollipopBasicAttributes", opts),
        "advancedAttributes": _opt("lollipopAdvancedAttributes", opts),
        "groupAttributes": _opt("lollipopGroupAttributes", opts),
    }, **(opts or {}))

    selection = selection or cmdx.sl()
    markers = set()

    for marker in selection:
        if marker.isA(cmdx.kDagNode):
            marker = marker["message"].output(type="rdMarker")

        if marker and marker.type() == "rdMarker":
            markers.add(marker)

    if not markers:
        raise i__.UserWarning(
            "No markers",
            "Select one or more markers to assign a lollipop to."
        )

    commands.create_lollipops(markers, opts=opts)

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def auto_limit(selection=None, **opts):
    selection = selection or cmdx.sl()
    markers = set()

    for marker in selection:
        if marker.isA(cmdx.kDagNode):
            marker = marker["message"].output(type="rdMarker")

        if marker and marker.isA("rdMarker"):
            markers.add(marker)

    if not markers:
        raise i__.UserWarning(
            "No markers",
            "Select one or more markers to automatically find limits for."
        )

    with cmdx.DagModifier() as mod:
        for marker in markers:
            commands.auto_limit(mod, marker)

    log.info(
        "Successfully transferred locked channels "
        "into %d markers" % len(markers)
    )

    return kSuccess


@i__.with_refresh_suspended
def cache_all(selection=None, **opts):
    solvers = _filtered_selection("rdSolver", selection)
    solvers = solvers or cmdx.ls(type="rdSolver")
    solvers = [s for s in solvers if s["startState"].output() is None]

    total_solvers = len(solvers)
    log.info("Caching %d solver%s" % (
        total_solvers, "s" if total_solvers > 1 else "")
    )

    total_frames = 0
    with i__.Timer() as duration, progressbar() as p:
        it = commands.cache(solvers)

        previous_progress = 0
        for progress in it:
            progress = int(progress)
            if progress % 5 == 0 and progress != previous_progress:
                log.info("%.1f%%" % progress)
                previous_progress = progress

            # Allow the user to cancel with the ESC key
            if cmds.progressBar(p, query=True, isCancelled=True):
                break

            total_frames += 1
            cmds.progressBar(p, edit=True, step=1)

    stats = (duration.s, total_frames / max(0.00001, duration.s))
    log.info("Cached %d frames for %d solvers in %.1fs (%d fps)" % (
        total_frames, total_solvers, stats[0], stats[1]
    ))

    cmds.inViewMessage(
        amg="Cached in <hl>%.2fs</hl> (%d fps)" % stats,
        pos="topCenter",
        fade=True
    )

    return True


@i__.affects_initial_state
def uncache(selection=None, **opts):
    solvers = _filtered_selection("rdSolver", selection)
    solvers = solvers or cmdx.ls(type="rdSolver")
    solvers = [s for s in solvers if s["startState"].output() is None]

    with cmdx.DagModifier() as mod:
        for solver in solvers:
            mod.set_attr(solver["cache"], 0)


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def link_solver(selection=None, **opts):
    try:
        a, b = selection or cmdx.selection()
    except ValueError:
        raise i__.UserWarning(
            "Select two solvers",
            "Select a solver <b>(a)</b> to link with another solver "
            "<b>(b)</b>.<br>"
            "Solver <b>(b)</b> will participate in Solver <b>(a)</b>."
        )

    if a.isA(cmdx.kTransform):
        a = a.shape(type="rdSolver")

    if b.isA(cmdx.kTransform):
        b = b.shape(type="rdSolver")

    if not a or not b:
        raise i__.UserWarning(
            "Bad selection",
            "%s or %s was not two solvers." % (a, b)
        )

    commands.link_solver(a, b)

    # Trigger a draw refresh
    cmds.select(cmds.ls(selection=True))

    log.info("Successfully linked %s -> %s" % (a, b))
    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def unlink_solver(selection=None, **opts):
    solvers = _solvers_from_selection(selection)

    for solver in solvers:
        commands.unlink_solver(solver)
        log.info("Successfully unlinked %s" % solver)

    # Trigger a draw refresh
    cmds.select(cmds.ls(selection=True))
    cmds.refresh()

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def update_plan(selection=None, **opts):
    opts = dict({
        "forceUpdate": _opt("planForceUpdate", opts),
    }, **(opts or {}))

    sel = cmdx.ls(type="rdPlan")

    if len(sel) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Select a plan to update."
        )

    for plan in sel:

        # Recompute the plan even when nothing has changed
        # Can be necessary as it sometimes fails for no obvious reason
        if opts["forceUpdate"]:
            plan["enabled"] = True

        plan["startState"].read()

    cmds.refresh()

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def assign_plan(selection=None, **opts):
    opts = dict({
        "useTransform": False,  # deprecated option
        "preset": _opt("planPreset", opts),
        "increment": _opt("planFromAnimIncrementalSampling", opts),
        "duration": _opt("planDuration", opts),
        "interactive": _opt("planInteractive", opts),
    }, **(opts or {}))

    sel = selection or cmdx.selection()

    if len(sel) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Select one body and 1 or more feet"
        )

    body, feet = sel[0], sel[1:]
    plan = commands.assign_plan(body, feet, opts)

    # Show user the Press T notification
    cmds.select(str(plan.parent()))

    if _is_interactive() and opts["useTransform"]:
        # Make sure user can actually see the handles
        for panel in cmds.getPanel(visiblePanels=True):
            if not cmds.modelPanel(panel, query=True, exists=True):
                continue

            cmds.modelEditor(panel, edit=True, handles=True)

    # Compute initial plan
    update_plan([plan], forceUpdate=True)

    return kSuccess


@with_exception_handling
def plan_to_animation(selection=None, **opts):
    plans = plans_from_selection(selection) or cmdx.ls(type="rdPlan")

    if not plans:
        raise i__.UserWarning(
            "No plans",
            "Found no plans to bake"
        )

    with i__.Timer("planToAnimation") as duration:
        start, end, dsts = recording.plans_to_animation(plans)

    stats = (duration.s, (end - start) / max(0.00001, duration.s))
    log.info("Recorded plan in %.2fs (%d fps)" % stats)

    cmds.inViewMessage(
        amg="Recorded plan in <hl>%.2fs</hl> (%d fps)" % stats,
        pos="bottomCenter",
        fade=True
    )

    return kSuccess


@with_exception_handling
def align_plans(selection=None, **opts):
    opts = dict({
        "includePlanAttributes": _opt("planAlignPlanAttributes", opts),
        "includeFootAttributes": _opt("planAlignFootAttributes", opts),
    }, **(opts or {}))

    plans = plans_from_selection(selection) or cmdx.ls(type="rdPlan")

    if not plans:
        raise i__.UserWarning(
            "No plans",
            "Found no plans to bake"
        )

    if len(plans) != 2:
        raise i__.UserWarning(
            "Bad Selection",
            "Select two plans, a starting plan and one to follow it."
        )

    commands.align_plans(plans, opts)
    update_plan(plans, forceUpdate=True)

    log.info("Aligned %s -> %s" % (str(plan) for plan in plans))

    return kSuccess


@i__.with_undo_chunk
def animation_to_plan(selection=None, **opts):
    opts = dict({
        "increment": _opt("planFromAnimIncrementalSampling", opts),
    }, **(opts or {}))

    plans = plans_from_selection(selection)

    if not plans:
        raise i__.UserWarning(
            "No plan selected",
            "Select one or more plans to bake"
        )

    for plan in plans:
        commands.animation_to_plan(plan, opts["increment"])

    update_plan(plans, forceUpdate=True)

    return kSuccess


@i__.with_undo_chunk
def extract_plan(selection=None, **opts):
    plans = plans_from_selection(selection) or cmdx.ls(type="rdPlan")

    if not plans:
        raise i__.UserWarning(
            "No plan selected",
            "Select one or more plans to extract"
        )

    recording.extract_plans(plans)

    log.info("Successfully extracted %s plans" % len(plans))

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def assign_terrain(selection=None, **opts):
    sel = selection or cmdx.selection()

    if len(sel) != 2:
        raise i__.UserWarning(
            "Bad selection",
            "Select terrain and plan"
        )

    mesh, plan = sel[0], sel[1]

    if plan.is_a(cmdx.kTransform):
        plan = plan.shape(type="rdPlan")

    if mesh.is_a(cmdx.kTransform):
        mesh = mesh.shape(type="mesh")

    if not (plan and plan.is_a("rdPlan")) and (mesh and mesh.is_a("mesh")):
        raise i__.UserWarning(
            "Terrain must be a 'mesh'",
            "Select the plan, followed by a mesh to use for a terrain."
        )

    with cmdx.DagModifier() as mod:
        mod.set_attr(plan["heightmapEnabled"], True)
        mod.connect(mesh["outMesh"], plan["heightmapGeometry"])
        mod.connect(mesh["worldMatrix"][0], plan["heightmapGeometryMatrix"])

    update_plan()

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def reset_foot(selection=None, **opts):
    sel = selection or cmdx.selection()

    if len(sel) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Select one body and 1 or more feet"
        )

    with cmdx.DagModifier() as mod:
        for foot in cmdx.ls(type="rdFoot"):
            plan = foot["currentState"].output(type="rdPlan")
            if not plan:
                continue

            mtx = foot["targets"][0].as_matrix()
            mtx *= plan["targets"][0].as_matrix().inverse()
            mod.set_attr(foot["nominalMatrix"], mtx)

    # Trigger a draw refresh
    cmds.select(cmds.ls(selection=True))

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def reset_plan(selection=None, **opts):
    if reset_step_sequence(selection, **opts):
        return reset_targets(selection, **opts)
    return kFailure


@i__.with_undo_chunk
@with_exception_handling
def reset_step_sequence(selection=None, **opts):
    plans = plans_from_selection(selection)

    if len(plans) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Could not find a plan from the selection."
        )

    for plan in plans:
        commands.reset_step_sequence(plan)

    update_plan()

    log.info("Successfully reset %d step sequences" % len(plans))

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def reset_targets(selection=None, **opts):
    plans = plans_from_selection(selection)

    if len(plans) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Could not find a plan from the selection."
        )

    for plan in plans:
        commands.reset_plan_targets(plan)

    update_plan()

    log.info("Successfully reset %d targets" % len(plans))

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def reset_plan_origin(selection=None, **opts):
    plans = plans_from_selection(selection)

    if len(plans) < 1:
        raise i__.UserWarning(
            "Bad selection",
            "Select one body and 1 or more feet"
        )

    for plan in plans:
        commands.reset_plan_origin(plan)

    update_plan()

    log.info("Successfully reset %d target origins" % len(plans))

    return kSuccess


def air_field(selection=None, **opts):
    _field("airField", opts={
        "directionX": 10.0,
        "speed": 0.1,
        "magnitude": 1,
    })
    return kSuccess


def drag_field(selection=None, **opts):
    _field("dragField", opts={
        "magnitude": 0.1,
        "directionY": 1,
    })
    return kSuccess


def gravity_field(selection=None, **opts):
    up = cmdx.up_axis()

    _field("gravityField", {
        "directionY": up.y,
        "directionZ": up.z,
        "magnitude": -0.982,
    })

    return kSuccess


def newton_field(selection=None, **opts):
    _field("newtonField", opts={
        "magnitude": 1,
    })

    return kSuccess


def radial_field(selection=None, **opts):
    _field("radialField", opts={
        "magnitude": 1,
    })

    return kSuccess


def turbulence_field(selection=None, **opts):
    _field("turbulenceField", opts={
        "magnitude": 5,
        "frequency": 0.1,
    })

    return kSuccess


def uniform_field(selection=None, **opts):
    _field("uniformField", opts={
        "directionX": 1.0,
        "magnitude": 1,
    })

    return kSuccess


def vortex_field(selection=None, **opts):
    up = cmdx.up_axis()

    _field("vortexField", opts={
        "axisY": -up.y,
        "axisZ": -up.z,
        "magnitude": 10,
        "attenuation": 1.0,
    })

    return kSuccess


def volume_axis(selection=None, **opts):
    _field("volumeAxisField", opts={
        "magnitude": 1.0,
        "volumeShape": 1,  # Cube
    })

    return kSuccess


def volume_curve(selection=None, **opts):
    field = _field("volumeAxisField", opts={
        "volumeShape": 7,  # Curve
        "magnitude": 1.0,
        "sectionRadius": 2,
        "awayFromAxis": 0,
        "alongAxis": 1,
    })

    # Generate the default curve
    with cmdx.DagModifier() as mod:
        name = i__.unique_name("volumeAxisFieldCurve")
        shape_name = i__.shape_name(name)
        parent = mod.create_node("transform", name=name)
        shape = mod.create_node("nurbsCurve", name=shape_name, parent=parent)
        mod.set_attr(shape["cached"], cmdx.NurbsCurveData(
            points=((0, 0, 0), (1, 1, 0), (0, 2, 0)),
            degree=2
        ))

        mod.connect(shape["worldSpace"][0], field["inputCurve"])

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def _field(typ, opts=None):
    field = commands.create_field(typ, opts)

    for solver in cmdx.ls(type="rdSolver"):
        commands.affect_solver(field, solver)

    cmds.select(str(field))

    return field


@i__.with_undo_chunk
@with_exception_handling
def use_selected_as_source(selection=None, **opts):
    markers = _markers_from_selection()

    if len(markers) < 1:
        raise i__.UserWarning(
            "No marker selected",
            "Select both a marker and a field"
        )

    if len(markers) > 1:
        log.warning("Multiple markers selected, using %s" % markers[0])

    fields = selection or cmdx.sl(type="field", selection=True)

    if len(fields) < 1:
        raise i__.UserWarning(
            "No field selected",
            "Select both a marker and a field"
        )

    marker = markers[0]
    with cmdx.DGModifier() as mod:
        for field in fields:
            decompose = mod.create_node("decomposeMatrix")
            mod.connect(marker["outputMatrix"], decompose["inputMatrix"])
            mod.connect(decompose["outputTranslate"], field["translate"])

            commands._take_ownership(mod, marker, decompose)

    return field


@i__.with_undo_chunk
@with_exception_handling
def disconnect_source(selection=None, **opts):
    fields = selection or cmdx.sl(type="field", selection=True)

    if len(fields) < 1:
        raise i__.UserWarning(
            "No field selected",
            "Select a field to disconnect a source from"
        )

    with cmdx.DGModifier() as mod:
        for field in fields:
            decompose = field["translate"].input(type="decomposeMatrix")

            if not decompose:
                continue

            mod.delete_node(decompose)


@i__.with_undo_chunk
@with_exception_handling
def field_com_centroid(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if len(markers) < 1:
        raise i__.UserWarning(
            "No marker(s) selected",
            "Select one or more markers to edit."
        )

    with cmdx.DGModifier() as mod:
        for marker in markers:
            mod.set_attr(marker["fieldCentroids"], c.ComCentroid)

    return kSuccess


@i__.with_undo_chunk
@with_exception_handling
def field_volumetric_centroid(selection=None, **opts):
    markers = _markers_from_selection(selection)

    if len(markers) < 1:
        raise i__.UserWarning(
            "No marker(s) selected",
            "Select one or more markers to edit."
        )

    with cmdx.DGModifier() as mod:
        for marker in markers:
            mod.set_attr(marker["fieldCentroids"], c.VolumetricCentroids)

    return kSuccess


@contextlib.contextmanager
def refresh_suspended(suspend=True):
    cmds.refresh(suspend=suspend)

    try:
        yield
    finally:
        cmds.refresh(suspend=False)


@contextlib.contextmanager
def isolate_select(nodes):
    isolated_panel = cmds.paneLayout("viewPanes", query=True, pane1=True)

    previous_selection = cmds.ls(selection=True)
    cmds.select(nodes)
    cmds.editor(isolated_panel,
                edit=True,
                lockMainConnection=True,
                mainListConnection="activeList")
    cmds.isolateSelect(isolated_panel, state=True)

    try:
        yield
    finally:
        cmds.isolateSelect(isolated_panel, state=False)
        cmds.select(previous_selection)


@with_exception_handling
def bake_mesh(selection=None, **opts):
    markers = _markers_from_selection(selection)

    for marker in markers:
        commands.bake_mesh(marker)

    log.info("Successfully baked %d markers" % len(markers))
    return kSuccess


@with_exception_handling
def convert_to_mesh(selection=None, **opts):
    markers = _markers_from_selection(selection)

    meshes = []
    for marker in markers:
        meshes += [commands.marker_to_mesh(marker)]

    cmds.select(list(str(mesh.parent()) for mesh in meshes))
    log.info("Successfully converted %d markers" % len(meshes))

    return kSuccess


@i__.with_undo_chunk
@i__.affects_initial_state
@with_exception_handling
def replace_marker_mesh(selection=None, **opts):
    opts = {
        "exclusive": _opt("replaceMeshExclusive", opts),
        "maintainOffset": _opt("replaceMeshMaintainOffset", opts),
        "maintainHistory": _opt("replaceMeshMaintainHistory", opts),
    }

    meshes = (
        _filtered_selection("mesh", selection) +
        _filtered_selection("nurbsCurve", selection) +
        _filtered_selection("nurbsSurface", selection)
    )

    markers = _markers_from_selection(selection)

    if len(markers) < 1:
        raise i__.UserWarning(
            "Selection Problem",
            "No marker selected. Select 1 mesh and 1 marker, in any order."
        )

    if len(markers) > 1:
        raise i__.UserWarning(
            "Selection Problem",
            "2 or more markers selected. Pick one."
        )

    if len(meshes) < 1:
        raise i__.UserWarning(
            "Selection Problem",
            "No meshes selected. Select 1 mesh and 1 marker."
        )

    if len(meshes) > 1:
        existing_geo = markers[0]["inputGeometry"].input()

        if existing_geo in meshes:
            meshes.remove(existing_geo)

    # Still got more?
    if len(meshes) > 1:
        if all(mesh.is_a("mesh") for mesh in meshes):
            commands.replace_meshes(markers[0], meshes, opts=opts)

        else:
            log.warning(
                "%s are all selected"
                % ", ".join(str(m) for m in meshes)
            )

            raise i__.UserWarning(
                "Selection Problem",
                "2 or more geometries were selected, but not "
                "all of them were polygonal meshes."
            )
    else:
        commands.replace_mesh(markers[0], meshes[0], opts=opts)

    return kSuccess


def edit_marker_constraint_frames(selection=None):
    frames = []
    markers = set()

    for node in selection or cmdx.selection():
        marker = node

        if marker.isA(cmdx.kDagNode):
            marker = marker["message"].output(type="rdMarker")

        if not (marker and marker.isA("rdMarker")):
            raise i__.UserWarning(
                "No marker found",
                "%s was not a marker." % node
            )

        markers.add(marker)

    for marker in markers:
        frames.extend(commands.edit_constraint_frames(marker))

    log.info("Created %d pivots" % len(frames))
    cmds.select(list(map(str, frames)))
    return kSuccess


@with_exception_handling
def warp_time(selection=None, **opts):
    opts = dict({
        "on": _opt("warpTimeOn", opts),
    }, **(opts or {}))

    solvers = _solvers_from_selection(selection)

    if not solvers:
        raise i__.UserWarning(
            "No solver",
            "Select one or more solvers to animate the time of."
        )

    solver = solvers[0]

    if opts["on"] == 0:
        selection = selection or cmdx.selection()

        if not selection or len(selection) > 1:
            raise i__.UserWarning(
                "Bad selection",
                "Select 1 animated control, I'll simulate "
                "alongside each keyframe on this control."
            )

        transform = selection[0]

        try:
            commands.simulate_based_on(solver, transform)
        except AssertionError:
            raise i__.UserWarning(
                "Missing animation",
                "I tried simulating based on '%s'\n"
                "but it does not appear to be animated." % transform
            )

    else:
        commands.simulate_on(solver, opts["on"])

    cmds.select(str(solver.parent()))

    log.info("%s is now animated in time." % solver)

    return kSuccess


def restore_time(selection=None, **opts):
    solvers = _solvers_from_selection(selection)

    if not solvers:
        log.warning("No solvers to restore time for")

    for solver in solvers:
        commands.restore_time(solver)

        log.info("Successfully restored time for %s" % solver)

    return kSuccess


def delete_all_physics(selection=None, **opts):
    options.write("deleteFromSelection", False)
    delete_physics(selection, **opts)


def delete_physics_from_selection(selection=None, **opts):
    options.write("deleteFromSelection", True)
    delete_physics(selection, **opts)


@i__.with_undo_chunk
@with_exception_handling
def delete_physics(selection=None, **opts):
    if cmds.about(apiVersion=True) == 20220000:
        MessageBox(
            "Warning",
            "Maya 2022.0 has a critical bug leading to a crash "
            "when running this command. You will need the "
            "service pack 2022.1 or greater."
        )

        return kFailure

    delete = commands.delete_all_physics

    if _opt("deleteFromSelection", opts):
        selection = selection or cmdx.selection()

        if selection:
            def delete():
                return commands.delete_physics(selection)

    result = delete()

    any_node = cmds.ls()[0]
    cmds.select(any_node)  # Trigger a change to selection
    cmds.select(deselect=True)

    if any(result.values()):
        log.info(
            "Deleted {deletedRagdollNodeCount} Ragdoll nodes and "
            "{deletedOwnedNodeCount} owned nodes".format(**result)
        )
        return kSuccess

    else:
        return log.warning("Nothing deleted")


def delete_all_locomotion(selection=None, **opts):
    options.write("deleteFromSelection", False)
    delete_locomotion(selection, **opts)


def delete_locomotion_from_selection(selection=None, **opts):
    options.write("deleteFromSelection", True)
    delete_locomotion(selection, **opts)


@i__.with_undo_chunk
@with_exception_handling
def delete_locomotion(selection=None, **opts):
    delete = commands.delete_all_locomotion

    if _opt("deleteFromSelection", opts):
        selection = selection or cmdx.selection()

        if selection:
            def delete():
                return commands.delete_locomotion(selection)

    result = delete()

    any_node = cmds.ls()[0]
    cmds.select(any_node)  # Trigger a change to selection
    cmds.select(deselect=True)

    if any(result.values()):
        log.info(
            "Deleted {deletedRagdollNodeCount} Ragdoll nodes and "
            "{deletedOwnedNodeCount} owned nodes".format(**result)
        )
        return kSuccess

    else:
        return log.warning("Nothing deleted")


def select_type(typ):
    def select(selection=None, **opts):
        use_selection = _opt("selectUseSelection", opts)
        if use_selection:
            cmds.select(
                cmds.ls(selection=True, type=typ) or
                cmds.ls(type=typ)
            )
        else:
            cmds.select(cmds.ls(type=typ))

        return kSuccess

    return select


def select_markers(selection=None, **opts):
    return select_type("rdMarker")(selection, **opts)


def select_groups(selection=None, **opts):
    return select_type("rdGroup")(selection, **opts)


def select_solvers(selection=None, **opts):
    return select_type("rdSolver")(selection, **opts)


def select_group_members(selection=None, **opts):
    groups = _filtered_selection("rdGroup", selection)

    members = set()
    for group in groups:
        for el in group["inputStart"]:
            member = el.input()

            if member is None:
                continue

            members.add(member)

    cmds.select(list(map(str, members)))
    return kSuccess


#
# User Interface
#


def reset_t_key(selection=None, **opts):
    opts = dict({
        "hotkey": _opt("manipulatorHotkey", opts),
    }, **(opts or {}))

    cmds.hotkey(keyShortcut=opts["hotkey"], name="ShowManipulatorsNameCommand")
    log.info(
        "Success, use %s to activate the Manipulator" % opts["hotkey"].upper()
    )

    return kSuccess


def reset_t_key_options(*args):
    return _Window("resetTKey", reset_t_key)


def show_explorer(selection=None):
    if not json.loads(cmds.ragdollDump()):
        return

    def get_fresh_dump(*args, **kwargs):
        return json.loads(cmds.ragdollDump(*args, **kwargs))

    if ui.Explorer.instance and ui.isValid(ui.Explorer.instance):
        return ui.Explorer.instance.show()

    win = ui.Explorer(parent=ui.MayaWindow())
    win.load(get_fresh_dump)
    win.show(dockable=True)


@i__.with_timing
def welcome_user(*args):
    LegacyWindow = ui.SplashScreen
    welcome_window_ref = widgets.WelcomeWindow.instance_weak

    if os.getenv("RAGDOLL_LEGACY_GREETS"):
        if welcome_window_ref and ui.isValid(welcome_window_ref()):
            welcome_window_ref().close()
        if LegacyWindow.instance and ui.isValid(LegacyWindow.instance):
            return LegacyWindow.instance.show()

        parent = ui.MayaWindow()
        win = LegacyWindow(parent)

    else:
        if LegacyWindow.instance and ui.isValid(LegacyWindow.instance):
            LegacyWindow.instance.close()
        if welcome_window_ref and ui.isValid(welcome_window_ref()):
            return welcome_window_ref().show()

        parent = ui.MayaWindow()
        win = widgets.WelcomeWindow(parent)

        def on_licence_data_requested():
            licence.uninstall()
            licence.install()

            data = licence.data()
            data["currentVersion"] = ".".join(__.version_str.split(".")[:3])
            try:
                data["ip"], port = licence._parse_server_from_environment()
                data["port"] = str(port)
            except AttributeError:
                data["ip"], data["port"] = "", ""  # env not set
            except ValueError as e:
                data["ip"], data["port"] = "", ""
                log.error(e)

            win.on_licence_data_requested(data)

        def _is_succeed(status):
            return status == licence.STATUS_OK

        def on_node_activated(key_or_fname):
            """If STATUS_INET returned, switch to offline mode"""
            is_file = os.path.isfile(key_or_fname)
            func = licence.activate_from_file if is_file else licence.activate
            status = func(key_or_fname)

            if status == licence.STATUS_INET:
                log.info("Switching to offline activation mode.")
                key = key_or_fname  # should be key
                win.node_activate_inet_returned.emit(key)
            else:
                _is_succeed(status)
                win.licence_data_requested.emit()

        def on_node_deactivated():
            """If STATUS_INET returned, switch to offline mode"""
            status = licence.deactivate()

            if status == licence.STATUS_INET:
                log.info("Switching to offline deactivation mode.")
                win.node_deactivate_inet_returned.emit()
            else:
                _is_succeed(status)
                win.licence_data_requested.emit()

        def on_float_requested():
            _is_succeed(licence.request_lease())
            win.licence_data_requested.emit()

        def on_float_dropped():
            _is_succeed(licence.drop_lease())
            win.licence_data_requested.emit()

        def on_offline_activate_requested(key, fname):
            if _is_succeed(licence.activation_request_to_file(key, fname)):
                win.on_offline_activate_requested()

        def on_offline_deactivate_requested(fname):
            if _is_succeed(licence.deactivation_request_to_file(fname)):
                win.on_offline_deactivate_requested()

        def on_asset_opened(file_path):
            win.hide()

            # Let the UI disappear first
            cmds.evalDeferred(lambda: _open_physics(file_path))

        win.licence_data_requested.connect(on_licence_data_requested)
        win.node_activated.connect(on_node_activated)
        win.node_deactivated.connect(on_node_deactivated)
        win.float_requested.connect(on_float_requested)
        win.float_dropped.connect(on_float_dropped)
        win.offline_activate_requested.connect(on_offline_activate_requested)
        win.offline_deactivate_requested.connect(
            on_offline_deactivate_requested
        )
        win.asset_opened.connect(on_asset_opened)

    win.show()
    win.activateWindow()

    # Maya automatically centers new windows,
    # sometimes. On some platforms. Trust no one.
    ui.center_window(win)

    return win


def _Arg(var, label=None, callback=None):
    var = __.optionvars[var]
    var = copy.deepcopy(var)  # Allow edits to internal lists etc.

    # Special case
    if var["name"] == "solver":
        scenes = [n.shortestPath() for n in cmdx.ls(type="rdScene")]
        var["items"] = scenes + ["Create new solver"]
        var["default"] = 0
        var["initial"] = None  # Always prefer the latest created scene

        __.solvers = scenes

        options.write(var)  # Update this whenever the window is shown

    if label is not None:
        var["label"] = label

    # Restore persistent values, from Maya preferences
    optionvar = options.read(var)
    if optionvar is not None:
        var["initial"] = optionvar

    # Used elsewhere
    _ = var.pop("arg", var["name"])
    _ = var.pop("originalItems", None)

    depends = var.pop("depends", [])
    for dependency in depends:
        pass

    cls = getattr(qargparse, var.pop("type"))
    arg = cls(**var)

    if callback is not None:
        arg.changed.connect(callback)

    return arg


def _Window(key, command=None, cls=None):
    parent = ui.MayaWindow()
    menuitem = __.menuitems[key]
    args = map(_Arg, menuitem.get("options", []))

    win = (cls or ui.Options)(
        key,
        args,
        command=repeatable(command) if command else None,
        icon=_resource("icons", menuitem["icon"]),
        description=menuitem["summary"],
        media=menuitem.get("media", []),
        parent=parent
    )

    # On Windows, windows typically spawn in the
    # center of the screen. On Linux? Flip a coin.
    ui.center_window(win)

    win.show()

    return win


def global_preferences(*args):
    def callback():
        from maya import cmds
        cmds.evalDeferred(lambda: cmds.refresh(force=True))

    def global_preferences():
        pass

    window = _Window("globalPreferences", global_preferences)

    # Update viewport immediately whenever this changes
    for opt in ("scale", "resolutionScaleFactor"):
        scale = window.parser.find(opt)
        scale.changed.connect(callback)

    return window


def save_preferences(*args):
    options.save()
    log.info("Successfully saved Ragdoll preferences")


def reset_preferences(*args):
    options.reset()
    log.info("Successfully reset Ragdoll preferences")


def assign_plan_options(*args):
    return _Window("assignPlan", assign_plan)


def extract_plan_options(*args):
    return _Window("extractPlan", extract_plan)


def update_plan_options(*args):
    return _Window("updatePlan", update_plan)


def animation_to_plan_options(*args):
    return _Window("bakeTargets", animation_to_plan)


def bake_mesh_options(selection=None, **opts):
    return _Window("bakeMesh", bake_mesh)


def convert_to_mesh_options(selection=None, **opts):
    return _Window("convertMesh", convert_to_mesh)


def replace_marker_mesh_options(*args):
    return _Window("markerReplaceMesh", replace_marker_mesh)


def extract_markers_options(*args):
    return _Window("extractMarkers", extract_markers)


def create_lollipops_options(*args):
    return _Window("createLollipop", create_lollipops)


def align_plans_options(*args):
    return _Window("alignPlans", align_plans)


def reset_plan_options(*args):
    return _Window("resetPlan", reset_plan)


def reset_step_sequence_options(*args):
    return _Window("resetPlanStepSequence", reset_step_sequence)


def reset_plan_origin_options(*args):
    return _Window("resetPlanOrigin", reset_plan_origin)


def reset_targets_options(*args):
    return _Window("resetPlanTargets", reset_targets)


def reset_foot_options(*args):
    return _Window("resetFoot", reset_foot)


def _update_solver_options():
    if "originalItems" not in __.optionvars["markersAssignSolver"]:
        items = __.optionvars["markersAssignSolver"]["items"][:]
        __.optionvars["markersAssignSolver"]["originalItems"] = items

    solvers = cmdx.ls(type="rdSolver")
    solvers = [solver.shortestPath() for solver in solvers]
    items = solvers + __.optionvars["markersAssignSolver"]["originalItems"]

    __.optionvars["markersAssignSolver"]["items"] = items


def _update_group_options():
    if "originalItems" not in __.optionvars["markersAssignGroup"]:
        items = __.optionvars["markersAssignGroup"]["items"][:]
        __.optionvars["markersAssignGroup"]["originalItems"] = items

    groups = cmdx.ls(type="rdGroup")
    groups = [group.shortestPath() for group in groups]
    items = __.optionvars["markersAssignGroup"]["originalItems"] + groups
    __.optionvars["markersAssignGroup"]["items"] = items


def assign_marker_options(*args):
    _update_solver_options()
    _update_group_options()
    return _Window("assignMarker", assign_marker)


def assign_and_connect_options(*args):
    _update_solver_options()
    _update_group_options()
    return _Window("assignGroup", assign_and_connect)


def assign_environment_options(*args):
    _update_solver_options()
    return _Window("assignEnvironment", assign_environment)


def assign_collision_group_options(*args):
    return _Window("assignCollisionGroup", assign_collision_group)


def record_markers_options(*args):
    start = int(cmdx.animation_start_time().value)
    end = int(cmdx.animation_end_time().value)

    __.optionvars["markersRecordCustomStartTime"]["default"] = start
    __.optionvars["markersRecordCustomStartTime"]["min"] = start
    __.optionvars["markersRecordCustomStartTime"]["max"] = end
    __.optionvars["markersRecordCustomEndTime"]["default"] = end
    __.optionvars["markersRecordCustomEndTime"]["min"] = start
    __.optionvars["markersRecordCustomEndTime"]["max"] = end

    win = _Window("recordMarkers", record_markers)

    record_range = win.parser.find("markersRecordRange")
    start = win.parser.find("markersRecordCustomStartTime")
    end = win.parser.find("markersRecordCustomEndTime")

    def update_start_end():
        start.setEnabled(record_range.read() == 2)
        end.setEnabled(record_range.read() == 2)

    update_start_end()
    record_range.changed.connect(update_start_end)

    return win


def warp_time_options(*args):
    return _Window("warpTime", warp_time)


def snap_markers_options(*args):
    return _Window("snapMarkers", snap_markers)


def retarget_marker_options(*args):
    return _Window("retargetMarker",
                   retarget_marker,
                   cls=widgets.RetargetWindow)


def create_pin_constraint_options(*args):
    return _Window("pinConstraint", create_pin_constraint)


def toggle_channel_box_attributes_options(*args):
    return _Window("toggleChannelBoxAttributes", toggle_channel_box_attributes)


def delete_physics_options(*args):
    return _Window("deleteAllPhysics", delete_physics)


# Let the Import UI initialise these, and then reuse it for
# any subsequent imports without a UI. To mimic the behavior
# of other menu items that don't *require* a UI.
_singleton_import_loader = None
_singleton_export_loader = None


def _import_physics_wrapper():
    override_solver = None
    if options.read("importSolver") == c.ImportSolverFromScene:
        existing_solvers = cmdx.ls(type="rdSolver")

        if existing_solvers:
            override_solver = existing_solvers[0].path()

    _singleton_import_loader.edit({
        "overrideSolver": override_solver,
    })

    try:
        with i__.Timer("importPhysics") as t:
            _singleton_import_loader.reinterpret()

    except Exception:
        log.warning(traceback.format_exc())
        log.warning("An unexpected error occurred, see Script Editor")
        return False

    else:
        stats = (_singleton_import_loader.count(), t.ms)
        cmds.inViewMessage(
            amg="Imported %d markers in <hl>%.2f ms</hl>" % stats,
            pos="topCenter",
            fade=True
        )

        log.info("Successfully imported %d markers in %.2f ms" % stats)

    return True


def _export_physics_wrapper(thumbnail=None):
    try:
        with i__.Timer("exportPhysics") as t:
            data = _singleton_export_loader.dump()

            if not data["entities"]:
                return log.error("Nothing to export")

            if not thumbnail:
                # Call this *before* opening up the dialog,
                # to ensure we don't mess up the active 3d viewport
                thumbnail = ui.view_to_pixmap()

            if "ui" not in data:
                data["ui"] = {}

            b64 = ui.pixmap_to_base64(thumbnail)
            data["ui"]["thumbnail"] = b64.decode("ascii")

            fname = options.read("exportPath")
            fname = os.path.normpath(fname)
            fname = fname.replace("\\", "/")  # Safe for all platforms

            try:
                dump.export(fname, data=data)
            except Exception:
                _print_exception()
                return log.warning("Could not export %s" % fname)

            # Update any currently opened Import UI
            for title, widget in __.widgets.items():
                if not isinstance(widget, ui.ImportOptions):
                    continue

                if not ui.isValid(widget):
                    continue

                log.warning("Updating currently opened Import UI")
                widget.on_path_changed(force=True)

    except Exception:
        log.warning(traceback.format_exc())
        log.warning("An unexpected error occurred, see Script Editor")
        return False

    stats = (_singleton_export_loader.count(), t.ms)
    cmds.inViewMessage(
        amg="Exported %d markers in <hl>%.2f ms</hl>" % stats,
        pos="topCenter",
        fade=True
    )

    log.info("Successfully exported %d markers in %.2f ms to %s" % (
        stats[0], stats[1], fname)
    )

    return True


def _open_physics(path):
    with i__.Timer("openPhysics") as duration:
        created = dump.load(path)

    log.info("Successfully opened %s.." % path)
    log.info("..in %.1f ms" % duration.ms)

    stats = (len(created["markers"]), duration.ms)
    cmds.inViewMessage(
        amg="Opened %d markers in <hl>%.2f ms</hl>" % stats,
        pos="topCenter",
        fade=True
    )


def open_physics(selection=None, **opts):
    from PySide2 import QtWidgets
    path, _ = QtWidgets.QFileDialog.getOpenFileName(
        ui.MayaWindow(),
        "Open Ragdoll File",
        options.read("lastVisitedPath"),
        "Ragdoll scene files (*.rag)"
    )

    if not path:
        return log.debug("Cancelled")

    if not path.endswith(".rag"):
        path += ".rag"

    path = os.path.normpath(path)
    _open_physics(path)

    return kSuccess


def open_physics_options(*args):
    return open_physics(*args)


def import_physics(selection=None, **opts):
    return import_physics_options()


def export_physics(selection=None, **opts):
    return export_physics_options()


def import_physics_options(*args):
    global _singleton_import_loader
    _singleton_import_loader = dump.Loader()

    #
    win = None

    def _on_selection_changed():
        use_selection = win.parser.find("importUseSelection")

        if use_selection.read():
            roots = cmds.ls(selection=True, type="transform", long=True)

            _singleton_import_loader.edit({"roots": roots})

        else:
            _singleton_import_loader.edit({"roots": []})

        win.reset()

    def on_selection_changed(clientData=None):
        try:
            _on_selection_changed()

        except Exception:
            # One the window is closed, this will cease to matter
            uninstall_selection_callback()

    def uninstall_selection_callback():
        from maya.api import OpenMaya as om
        callback = getattr(on_selection_changed, "_callback", None)
        if callback is not None:
            om.MMessage.removeCallback(callback)
            on_selection_changed._callback = None

    def install_selection_callback():
        uninstall_selection_callback()

        # Store callback on called function, it'll survive
        # any eventual module reloads too.
        from maya.api import OpenMaya as om
        on_selection_changed._callback = om.MModelMessage.addCallback(
            om.MModelMessage.kActiveListModified,
            on_selection_changed
        )

    def on_use_selection_changed():
        _on_selection_changed()

    def before_reset():
        """The UI was reset, for whatever reason"""
        _singleton_import_loader.edit({
            "matchBy": options.read("importMatchBy"),
            "searchAndReplace": options.read("importSearchAndReplace"),
            "preserveAttributes": options.read("importPreserveAttributes"),
            "namespace": options.read("importNamespaceCustom"),
            "createMissingTransforms": options.read(
                "importCreateMissingTransforms"
            ),
        })

    def import_physics():
        result = _import_physics_wrapper()
        win.reset()
        return result

    # Initialise namespaces
    namespaces = cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True)
    namespaces = namespaces or []  # There may not be any

    for default_namespace in ("UI", "shared"):
        try:
            namespaces.remove(default_namespace)
        except ValueError:
            pass

    items = ["Off", "From File"]
    items.extend(namespaces)
    items.append("Custom")

    __.optionvars["importNamespace"]["items"] = items

    win = _Window("importPhysics", import_physics, cls=ui.ImportOptions)
    win.init(_singleton_import_loader)

    win.before_reset.connect(before_reset)
    use_selection = win.parser.find("importUseSelection")
    use_selection.changed.connect(on_use_selection_changed)

    ui.center_window(win)
    win.resize(ui.px(1100), ui.px(575))

    install_selection_callback()

    return win


def export_physics_options(*args):
    global _singleton_export_loader
    _singleton_export_loader = dump.Loader()

    def export_physics():
        thumbnail = win.parser.find("exportThumbnail")
        thumbnail = thumbnail.pixmap()
        result = _export_physics_wrapper(thumbnail)
        return result

    win = _Window("exportPhysics", export_physics, cls=ui.ExportOptions)

    def loader_factory(*args, **kwargs):
        data = dump.export()
        _singleton_export_loader.read(data)

        return _singleton_export_loader

    win.init(loader_factory)
    ui.center_window(win)
    win.resize(ui.px(1100), ui.px(410))

    return win


# Backwards compatibility
assign_single = assign_marker
assign_group = assign_and_connect
