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
import logging
import traceback
import functools
import contextlib

from maya import cmds, mel
from maya.utils import MayaGuiLogHandler
from maya.api import OpenMaya as om
from .vendor import cmdx, qargparse
from . import (
    commands,
    upgrade,
    ui,
    options,
    licence,
    dump,
    tools,
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
__.previousvars = {
    "MAYA_SCRIPT_PATH": os.getenv("MAYA_SCRIPT_PATH", ""),
    "XBMLANGPATH": os.getenv("XBMLANGPATH", ""),
}


# Recording-related data
_recorded_actions = []


def _print_exception():
    log.debug(traceback.format_exc())


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _is_standalone():
    """Is Maya running without a GUI?"""
    return not hasattr(cmds, "about") or cmds.about(batch=True)


MessageBox = ui.MessageBox


if _is_standalone():
    def MessageBox(*args, **kwargs):
        return True


def _after_scene_open(*args):
    """Handle upgrades of nodes saved with an older version of Ragdoll"""

    if options.read("upgradeOnSceneOpen"):
        _evaluate_need_to_upgrade()

    # Update known solvers
    __.solvers = [n.shortestPath() for n in cmdx.ls(type="rdScene")]


def _before_scene_open(*args):
    # Let go of all memory, to allow Ragdoll plug-in to be unloaded
    cmdx.uninstall()


def _before_scene_new(*args):
    cmdx.uninstall()


def requires_ui(func):
    """Wrapper for functions that rely on being displayed

    Mostly for CI. These are simply ignored.

    """

    @functools.wraps(func)
    def requires_ui_wrapper(*args, **kwargs):
        if _is_standalone():
            return True
        return func(*args, **kwargs)
    return requires_ui_wrapper


def _format_exception(func):
    """Turn exceptions into user-facing messages"""

    @functools.wraps(func)
    def format_exception_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Turn this into a friendly warning
            _print_exception()
            log.warning(str(e))
            return kFailure
    return format_exception_wrapper


def _selected_channels():
    """Get currently selected attributes from the channelbox

    Reference: http://forums.cgsociety.org/showthread.php
                      ?f=89&t=892246&highlight=main+channelbox

    """

    channel_box = mel.eval(
        "global string $gChannelBoxName; $temp=$gChannelBoxName;"
    )

    attrs = cmds.channelBox(channel_box,
                            selectedMainAttributes=True,
                            query=True) or []

    attrs += cmds.channelBox(channel_box,
                             selectedShapeAttributes=True,
                             query=True) or []

    attrs += cmds.channelBox(channel_box,
                             selectedHistoryAttributes=True,
                             query=True) or []

    attrs += cmds.channelBox(channel_box,
                             selectedOutputAttributes=True,
                             query=True) or []

    # Returned attributes are shortest possible,
    # e.g. 'tx' instead of 'translateX'
    return attrs


# Every argument used by UIs
#
# These can be accessed/modified via cmds.optionVar
# as <prefix><name> where <prefix> is "ragdoll" and are
# all stored persistently alongside Maya's native preferences
with open(_resource("options.json")) as f:
    __.optionvars = json.load(f)
    __.optionvars.pop("#", None)  # Exclude comments


# Every menu item
with open(_resource("menu.json")) as f:
    __.menuitems = json.load(f)
    __.menuitems.pop("#", None)  # Exclude comments


def install():
    if __.installed:
        return

    install_logger()
    install_plugin()
    licence.install(c.RAGDOLL_AUTO_SERIAL)
    options.install()

    if not _is_standalone():
        install_callbacks()

        # Give Maya's GUI a chance to boot up
        cmds.evalDeferred(install_menu)

        # Temporarily work around incompatibility with pre-popupalated
        # controllers. This is the option from the Maya Preferences
        # called "Include controllers in evaluation graph"
        cmds.optionVar(iv=("prepopulateController", 0))

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

    __.installed = True


def uninstall():
    if not __.installed:
        # May have been uninstalled by either the C++ plug-in,
        # or via the Script Editor or userSetup.py etc.
        return

    uninstall_logger()
    uninstall_callbacks()
    uninstall_menu()
    uninstall_ui()
    options.uninstall()
    cmdx.uninstall()

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
    welcome_user()


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

    # Required by tools.py
    cmds.loadPlugin("matrixNodes", quiet=True)

    __.version_str = cmds.pluginInfo(c.RAGDOLL_PLUGIN_NAME,
                                     query=True, version=True)

    # Debug builds come with a `.debug` suffix, e.g. `2020.10.15.debug`
    __.version = int("".join(__.version_str.split(".")[:3]))


def uninstall_plugin(force=True):
    cmds.file(new=True, force=force)

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


def uninstall_ui():
    for title, widget in __.widgets.items():
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

    item("showMessages",
         command=show_messageboard,

         # Programatically displayed during logging
         visible=False)

    divider("Create")

    item("activeRigid", create_active_rigid, create_rigid_options)
    item("activeChain", create_active_chain, create_chain_options)
    item("passiveRigid", create_passive_rigid, create_passive_options)
    item("tissue")
    item("cloth")
    item("muscle", create_muscle, create_muscle_options)
    item("fluid")

    with submenu("Character", icon="ragdoll.png"):
        item("character", create_character, create_character_options,
             label="New")

        divider()

        item("trajectory")
        item("momentOfInertia")
        item("centerOfMass")

    divider("Manipulate")

    with submenu("Constraints", icon="constraint.png"):
        item("point", create_point_constraint, _constraint_options("Point"))
        item("orient", create_orient_constraint, _constraint_options("Orient"))
        item("parent", create_parent_constraint, _constraint_options("Parent"))
        item("hinge", create_hinge_constraint, _constraint_options("Hinge"))
        item("socket", create_socket_constraint, _constraint_options("Socket"))

        divider()

        item("animationConstraint", create_animation_constraint,
             create_animation_constraint_options)

        divider()

        item("editConstraintFrames",
             edit_constraint_frames,
             label="Edit Pivots")

    with submenu("Controls", icon="control.png"):
        item("kinematic", create_kinematic_control,
             create_kinematic_control_options)
        item("guide", create_driven_control,
             create_driven_control_options)
        item("motor")
        item("actuator")
        item("trigger")

    with submenu("Forces", icon="turbulence.png"):
        item("push", create_push_force, create_push_force_options)
        item("pull", create_pull_force, create_pull_force_options)
        item("directional", create_uniform_force, create_uniform_force_options)
        item("wind", create_turbulence_force, create_turbulence_force_options)

        divider()

        item("visualiser", create_slice)
        item("assignToSelected", assign_force)

    divider("Utilities")

    with submenu("Animation", icon="animation.png"):
        item("bakeSimulation")

        divider()

        item("exportPhysics", export_physics, export_physics_options)
        item("importPhysics", import_physics_from_file, import_physics_options)

        divider()

        item("createDynamicControl",
             create_dynamic_control,
             create_dynamic_control_options)

        item("multiplyRigids",
             multiply_rigids,
             multiply_rigids_options)
        item("multiplyConstraints",
             multiply_constraints,
             multiply_constraints_options)

    with submenu("Rigging", icon="rigging.png"):
        item("editShape", edit_shape, edit_shape_options)
        item("editConstraintFrames", edit_constraint_frames)

        divider()

        item("duplicateSelected", duplicate_selected)
        item("transferAttributes", transfer_selected)

        if c.RAGDOLL_DEVELOPER:
            item("convertToPolygons", convert_to_polygons)
            item("normaliseShapes", normalise_shapes)

        item("setInitialState", set_initial_state,
             set_initial_state_options)
        item("clearInitialState", clear_initial_state,
             clear_initial_state_options)

    with submenu("System", icon="system.png"):
        item("deleteAllPhysics", delete_physics, delete_physics_options)

        divider()

        item("explorer", show_explorer)

        divider()

        item("globalPreferences", global_preferences)
        item("savePreferences", save_preferences)
        item("resetPreferences", reset_preferences)

        with submenu("Logging Level", icon="logging.png"):
            item("loggingOff", logging_off)
            item("loggingInfo", logging_info)
            item("loggingWarning", logging_warning)
            item("loggingDebug", logging_debug)

    with submenu("Select", icon="select.png"):
        item("selectRigids", select_rigids, select_rigids_options)
        item("selectConstraints",
             select_constraints,
             select_constraints_options)
        item("selectControls", select_controls, select_controls_options)
        item("selectScenes", select_scenes, select_scenes_options)

    divider()

    item("ragdoll", welcome_user, label="Ragdoll %s" % __.version_str)


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

    change_visibility = ui.show_menuitem if count else ui.hide_menuitem
    change_visibility(menu_item["path"])

    # Help the user understand there's a problem somewhere
    cmds.menu(__.menu, edit=True, label=label)
    cmds.menuItem(menu_item["path"], **menu_kwargs)


"""

# Upgrade Path

This next part is what maintains backwards compatibility when changes
have been made to the plug-in in such a way that it alters the behavior
of your scene. In such cases, an upgrade is performed to convert your
scene into one that behaves identically to before.

"""


def _evaluate_need_to_upgrade():
    oldest, count = upgrade.needs_upgrade(__.version)

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
        log.info("%d Ragdoll nodes were upgraded" % count)

        # Synchronise viewport, sometimes it can go stale
        time = cmds.currentTime(query=True)
        cmds.evalDeferred(lambda: cmds.currentTime(time, update=True))

    else:
        log.debug("Ragdoll nodes already up to date!")


def _find_current_scene(autocreate=True):
    scene = options.read("solver")

    try:
        # Enum -> String
        scene = __.solvers[scene]

    except IndexError:
        # No questions asked, just make a new one
        scene = create_scene()

    else:
        # The one stored persistently may not actually exist,
        # it may come from another scene or at a time when it
        # did exist but got deleted
        try:
            scene = cmdx.encode(scene)

        except cmdx.ExistError:
            # Ok, no persistent clue or request for a new scene
            try:
                scene = cmdx.ls(type="rdScene")[0]

            # Nothing in sight, now it's up to the function
            except IndexError:
                if autocreate:
                    scene = create_scene()
                else:
                    raise cmdx.ExistError("No Ragdoll scene was found")

    if scene is not None:
        # Use this from now on
        current = __.solvers.index(scene.shortestPath())
        options.write("solver", current)

    return scene


@requires_ui
def validate_evaluation_mode():
    if not options.read("validateEvaluationMode"):
        return True

    mode = cmds.evaluationManager(query=True, mode=True)

    if mode[0] != "off":  # Both Serial and Parallel are OK
        return True

    def ignore():
        return True

    def enable_parallel():
        cmds.evaluationManager(mode="parallel")
        log.info("Enabled Parallel Evaluation")
        return True

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
            ("Ignore", ignore),
            ("Enable Parallel Evaluation", enable_parallel),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_cached_playback():
    if not cmds.optionVar(query="cachedPlaybackEnable"):
        return True

    if not options.read("validateCachingMode"):
        return True

    if cmds.optionVar(query="cachePreferenceDynamicsSupportEnabled"):
        return True

    def ignore():
        return True

    def enable_caching():
        cmds.optionVar(intValue=("cachePreferenceDynamicsSupportEnabled", 1))
        log.info("Cached Playback Enabled")
        return True

    return ui.warn(
        option="validateCachingMode",
        title="Cached Playback Detected",
        message=(
            "Ragdoll works with Cached Playback, but needs Maya to allow "
            "for dynamics to be cached also."
        ),
        call_to_action="What would you like to do?",
        actions=[
            ("Ignore", ignore),
            ("Enable Cached Dynamics", enable_caching),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_playbackspeed():
    if not options.read("validatePlaybackSpeed"):
        return True

    playback_speed = cmds.playbackOptions(playbackSpeed=True, query=True)

    if playback_speed == 0.0:
        return True

    def fix_it():
        cmds.playbackOptions(playbackSpeed=0.0)
        log.info("Playing every frame")
        return True

    return ui.warn(
        option="validatePlaybackSpeed",
        title="Play every frame",
        message=(
            "Ensure your playback speed is set to 'Play every frame' "
            "to avoid frame drops, these can break a simulation and "
            "generally causes odd things to happen."
        ),
        call_to_action="What would you like to do?",
        actions=[
            ("Ignore", lambda: True),
            ("Play Every Frame", fix_it),
            ("Cancel", lambda: False)
        ]
    )


@requires_ui
def validate_legacy_opengl():
    if not options.read("validateLegacyOpenGL"):
        return True

    opengl_legacy = cmds.optionVar(query="vp2RenderingEngine") == "OpenGL"

    if not opengl_legacy:
        return True

    def fix_it():
        cmds.optionVar(stringValue=("vp2RenderingEngine",
                                    "OpenGLCoreProfileCompat"))
        log.warning(
            "OpenGL Core Compatibility Profile "
            "enabled, restart required."
        )
        return False

    return ui.warn(
        option="validate_legacy_opengl",
        title="Legacy OpenGL Detected",
        message=(
            "Your viewport is set to render in Legacy OpenGL, which is "
            "incompatible with the Ragdoll renderer. Changing renderer "
            "requires a restart of Maya."
        ),
        call_to_action="Go to Maya Preferences to change this.",
        actions=[
            ("Ignore", lambda: True),
            ("Play Every Frame", fix_it),
            ("Cancel", lambda: False)
        ]
    )


def _filtered_selection(node_type):
    """Interpret user selection

    They should be able to..

    1. Select transforms, even though they meant the shape
    2. Select a transform with *multiple* shapes of a given type
    2. Select the shape
    3. Select multiple shapes
    4. Select multiple shapes *and* transforms

    """

    selection = list(cmdx.selection())

    if not selection:
        return []

    shapes = []
    for node in selection:
        shapes += node.shapes(node_type)

    shapes = filter(None, shapes)
    shapes = list(shapes) + selection
    shapes = filter(lambda shape: shape.type() == node_type, shapes)

    return list(shapes)


@i__.with_undo_chunk
def create_scene(selection=None):
    if not validate_evaluation_mode():
        return

    if not validate_cached_playback():
        return

    if not validate_playbackspeed():
        return

    if not validate_legacy_opengl():
        return

    # Update known solvers
    __.solvers = [n.shortestPath() for n in cmdx.ls(type="rdScene")]

    scene = commands.create_scene()

    # Use last-created scene per default
    __.solvers.insert(0, scene.shortestPath())

    return scene


@requires_ui
def is_valid_transform(transform):
    """Ragdoll currently does not support any custom pivot or axis"""

    if options.read("validateScalePivot"):
        nonzero = []
        tolerance = 0.01
        for attr in ("scalePivot",
                     "scalePivotTranslate"):
            for axis in "XYZ":
                plug = transform[attr + axis]
                if abs(plug.read()) > tolerance:
                    nonzero.append(plug)

        if nonzero:
            for plug in nonzero:
                log.warning("%s was not zero" % plug.path())

            return ui.warn(
                option="validateScalePivot",
                title="Custom Scale Pivot Not Supported",
                message=(
                    "Non-zero scale pivot was found. These are currently "
                    "unsupported and need to be zeroed out, "
                    "see Script Editor for details."
                ),
                call_to_action="What would you like to do?",
                actions=[

                    # Happens automatically by commands.py
                    # Take it or leave it, doesn't work otherwise
                    ("Zero out scalePivot", lambda: True),

                    ("Cancel", lambda: False)
                ]
            )

    return True


def _opt(key, override=None):
    override = override or {}
    return override.get(key, options.read(key))


@i__.with_undo_chunk
def create_active_rigid(selection=None, **opts):
    """Create a new rigid from selection"""

    created = []
    selection = selection or cmdx.selection(type="dagNode")

    if not selection:

        # Make a new rigid from scratch
        with cmdx.DagModifier() as mod:
            name = i__.unique_name("rigid")
            transform = mod.create_node("transform", name=name)

        selection = [transform]

    # Based on the first selection, determine
    # whether to convert or create something new.
    if selection[0].isA(cmdx.kShape):
        if selection[0].type() == "rdRigid":
            # The user meant to convert the selection
            return convert_rigid(selection, **opts)

    elif selection[0].isA(cmdx.kTransform):
        if selection[0].shape("rdRigid"):
            # The user meant to convert the selection
            return convert_rigid(selection, **opts)

    if not _validate_transforms(selection):
        return

    # Pre-flight check
    for node in selection:
        transform = node.parent() if node.isA(cmdx.kShape) else node
        if not is_valid_transform(transform):
            return

        # Rigid bodies must have translate and rotate channels
        if not transform.isA(cmdx.kTransform):
            log.warning("%s is not a transform node", transform.path())
            return

    select = _opt("rigidSelect", opts)
    passive = _opt("createRigidType", opts) == c.CreatePassive
    scene = _find_current_scene()

    # Cancelled by user
    if not scene:
        return

    if passive and _opt("cycleProtection", opts):
        def will_cycle(root):
            rigid = root.shape(type="rdRigid")

            # Passive or active, this is fine
            if rigid:
                return False

            # This is not fine
            return i__.is_dynamic(root, scene)

        for node in selection:
            transform = node.parent() if node.isA(cmdx.kShape) else node

            if not will_cycle(transform):
                continue

            log.warning("%s cannot be made passive" % transform)
            MessageBox("Cycle Warning", (
                "**Passive Child, Active Parent**\n\n"
                "Cannot make *passive* rigid the "
                "child of an *active* hierarchy. "
                "This would have caused a cycle.\n\n"
                "Ensure no parent is already being simulated."
            ), buttons=ui.OkButton, icon=ui.InformationIcon)

            return kFailure

    if _opt("autoReturnToStart", opts):
        start_time = scene["startTime"].asTime()
        cmdx.currentTime(start_time)

    for index, node in enumerate(selection):
        transform = node.parent() if node.isA(cmdx.kShape) else node

        # Check *before* it becomes rigid
        translate_animated = any(
            transform[attr].connected for attr in ("tx", "ty", "tz")
        )
        rotate_animated = any(
            transform[attr].connected for attr in ("rx", "ry", "rz")
        )

        opts_ = {
            "computeMass": _opt("computeMass", opts),
            "passive": passive,
            "defaults": {}
        }

        # Translate UI options into attribute defaults
        initial_shape = _opt("initialShape", opts)
        if initial_shape != c.InitialShapeAuto:
            opts_["defaults"]["shapeType"] = {
                # UI -> API
                c.InitialShapeBox: c.BoxShape,
                c.InitialShapeSphere: c.SphereShape,
                c.InitialShapeCapsule: c.CapsuleShape,
                c.InitialShapeMesh: c.MeshShape,
            }[initial_shape]

        try:
            rigid = commands.create_rigid(node, scene,
                                          opts=opts_)
        except Exception as e:
            _print_exception()
            log.error(str(e))
            continue

        # There may have been an error
        if not rigid:
            continue

        created += [rigid]

        # Preserve animation, if any, as soft constraints
        follow = _opt("existingAnimation", opts) == c.ExistingFollow
        if not passive and follow and (translate_animated or rotate_animated):
            subopts = {"defaults": {"driveStrength": 1.0}}

            if not translate_animated:
                subopts["defaults"]["linearDriveStiffness"] = 0
                subopts["defaults"]["linearDriveDamping"] = 0

            if not rotate_animated:
                subopts["defaults"]["angularDriveStiffness"] = 0
                subopts["defaults"]["angularDriveDamping"] = 0

            con = commands.animation_constraint(rigid, opts=subopts)
            created += [con]

    if created:
        new_rigids = [n for n in created if n.type() == "rdRigid"]

        if select:
            all_rigids = [r.parent() for r in new_rigids]
            cmds.select(list(map(str, all_rigids)), replace=True)

        log.info("Created %d rigid bodies", len(new_rigids))
        return kSuccess

    else:
        return log.warning("Nothing happened, that was unexpected")


@i__.with_undo_chunk
def create_passive_rigid(selection=None, **opts):
    # Special case of nothing selected, just make a default sphere
    if not selection and not cmdx.selection():
        with cmdx.DagModifier() as mod:
            name = i__.unique_name("rPassive")
            transform = mod.create_node("transform", name=name)

        cmds.select(transform.path())

    opts["createRigidType"] = c.CreatePassive
    opts["convertRigidType"] = c.ConvertPassive
    return create_active_rigid(selection, **opts)


@i__.with_undo_chunk
@_format_exception
def create_active_chain(selection=None, **opts):
    links = selection or cmdx.selection(type="transform")

    # This is no chain
    if len(links) < 2:
        return create_rigid(selection, **opts)

    if not links:
        return log.warning(
            "Select two or more transforms "
            "in the order they should be connected. "
            "The first selection will be passive (i.e. animated)."
        )

    for link in links:
        if not is_valid_transform(link):
            return

    # Protect against accidental duplicates
    for link in links[1:]:
        if link.shape("rdRigid") is not None:
            return log.warning("Already dynamic: '%s'" % link)

    opts = {
        "autoMultiplier": _opt("chainAutoMultiplier", opts),
        "autoLimits": _opt("chainAutoLimits", opts),
        "passiveRoot": _opt("chainPassiveRoot", opts),
    }

    defaults = {
        "drawShaded": False
    }

    shape_type = _opt("chainShapeType", opts)
    if shape_type != c.Auto:
        defaults["shapeType"] = shape_type

    scene = _find_current_scene()

    # Cancelled by user
    if not scene:
        return

    def cycle_protection():
        root = links[0]
        rigid = root.shape(type="rdRigid")

        # Passive or active, this is fine
        if rigid:
            return True

        # This is not fine
        return not i__.is_dynamic(root, scene)

    if _opt("cycleProtection", opts) and not cycle_protection():
        if opts["passiveRoot"]:
            log.warning("%s cannot be made passive" % links[0])
            MessageBox("Passive Child, Active Parent", (
                "Cannot make *passive* rigid the "
                "child of an *active* hierarchy."
            ), buttons=ui.OkButton, icon=ui.InformationIcon)

            return kFailure

    tools.create_chain(links, scene, opts=opts, defaults=defaults)

    root = links[0]
    cmds.select(str(root))

    return kSuccess


@i__.with_undo_chunk
def create_link(*args):
    links = []

    scene = _find_current_scene()
    for node in cmdx.selection():
        if not node.isA(cmdx.kJoint):
            return log.error("%s must be a joint" % node)

        link = commands.create_link(node, scene)
        links += [link]

    cmds.select(map(str, links))
    return kSuccess


def _axis_to_vector(axis="x"):
    return {
        "x": cmdx.Vector(1, 0, 0),
        "y": cmdx.Vector(0, 1, 0),
        "z": cmdx.Vector(0, 0, 1),
        0: cmdx.Vector(1, 0, 0),
        1: cmdx.Vector(0, 1, 0),
        2: cmdx.Vector(0, 0, 1),
    }[axis]


@i__.with_undo_chunk
def create_muscle(selection=None, **opts):
    try:
        a, b = selection or cmdx.selection()
    except ValueError:
        return log.warning("Select root and tip anchors of new muscle")

    if not all(node.isA(cmdx.kTransform) for node in (a, b)):
        return log.error(
            "Select two transforms for root and tip anchors of muscle"
        )

    if not all(node.parent() for node in (a, b)):
        return log.error(
            "Anchors must have a parent, see muscle documentation for details"
        )

    new_scene = not cmdx.ls(type="rdScene")
    scene = _find_current_scene()

    # Cancelled by user
    if not scene:
        return

    if _opt("autoReturnToStart", opts):
        start_time = scene["startTime"].asTime()
        cmdx.currentTime(start_time)

    if new_scene:
        # Muscles work best with the PGS solver, fow now
        log.info("Swapping TGS for PGS for better muscle simulation results")
        with cmdx.DagModifier() as mod:
            mod.set_attr(scene["solverType"], c.PGSSolverType)
            mod.set_attr(scene["gravity"], 0)

    kwargs = {
        "up_axis": _axis_to_vector(_opt("muscleUpAxis", opts)),
        "aim_axis": _axis_to_vector(_opt("muscleAimAxis", opts)),
        "flex": _opt("muscleFlex", opts),
        "radius": _opt("muscleRadius", opts),
    }

    muscle, root, tip = tools.create_muscle(a, b, scene, **kwargs)

    cmds.select(muscle.parent().path())
    return kSuccess


def _validate_transforms(nodes, tolerance=0.01):
    """Check for unsupported features in nodes of `root`"""
    negative_scaled = []
    positive_scaled = []
    issues = []

    for node in nodes:
        if not node.isA(cmdx.kTransform):
            continue

        tm = node.transform(cmdx.sWorld)
        if any(value < 0 - tolerance for value in tm.scale()):
            negative_scaled += [node]

        if any(value > 1 + tolerance for value in tm.scale()):
            positive_scaled += [node]

    if negative_scaled and options.read("validateScale"):
        issues += [
            "%d node(s) has negative scale\n%s" % (
                len(negative_scaled),
                "\n".join(" - %s" % node for node in negative_scaled),
            )
        ]

    if issues:
        for issue in issues:
            log.warning(issue)

        log.warning("%d %s" % (
            len(issues),
            "issue was found" if len(issues) == 1 else
            "issues were found"
        ))

    return False if issues else True


@i__.with_undo_chunk
def create_character(selection=None, **opts):
    scene = _find_current_scene()

    # Cancelled by user
    if not scene:
        return

    root = selection or cmdx.selection(type="joint")

    if not root or root[0].type() != "joint":
        return log.warning("Select root joint from which to create character")

    if len(root) > 1:
        return log.warning(
            "Multiple roots selected, select the root of 1 hierarchy"
        )

    # Operate only on first selected joint, to avoid
    # the tragic fate of accidentally making 100 ragdolls
    # (Could still be done via scripting)
    root = root[0]

    hierarchy = [root]
    hierarchy += [
        joint for joint in root.descendents(type="joint")
        if joint.child(type="joint")
    ]

    if not _validate_transforms(hierarchy):
        return

    if _opt("autoReturnToStart", opts):
        start_time = scene["startTime"].asTime()
        cmdx.currentTime(start_time)

    kwargs = {
        "copy": _opt("characterCopy", opts),
        "control": _opt("characterControl", opts),
        "normalise_shapes": _opt("characterNormalise", opts),
    }

    print(options.read("characterCopy"))

    tools.create_character(root, scene, **kwargs)

    cmds.select(str(root))
    log.info("Successfully created character from %s", root)
    return kSuccess


def _find_rigid(node, autocreate=False):
    if node.type() == "rdRigid":
        pass

    elif node.type() in ("transform", "joint"):
        shape = node.shape(type="rdRigid")

        # Automatically convert selection to rigid for the constraints
        if not shape and not node.shape(type="rdLink"):
            if autocreate:
                scene = _find_current_scene(autocreate=autocreate)

                # Cancelled by user
                if not scene:
                    return

                shape = commands.create_active_rigid(node, scene)
            else:
                return log.warning(
                    "%s did not have a rdRigid shape" % node.path()
                )

        node = shape

    return node


@i__.with_undo_chunk
def create_constraint(selection=None, **opts):
    select = _opt("constraintSelect", opts)
    constraint_type = _opt("constraintType", opts)
    selection = selection or cmdx.selection()

    if selection and selection[0].type() == "rdConstraint":
        # The user meant to convert/restore a constraint
        return convert_constraint(selection, **opts)

    try:
        parent, child = selection
    except ValueError:
        return log.warning(
            "Select parent and child rigids, "
            "these will become constrained to each other"
        )

    scene = _find_current_scene(autocreate=True)

    # Cancelled by user
    if not scene:
        return

    parent = _find_rigid(parent) or scene
    child = _find_rigid(child)

    if any(node is None for node in (parent, child)):
        return log.warning("Must select two rigids")

    opts = {
        "maintainOffset": _opt("maintainOffset", opts),
        "useRotatePivot": _opt("constraintUseRotatePivot", opts),
        "standalone": _opt("constraintStandalone", opts),
    }

    if constraint_type == c.PointConstraint:
        con = commands.point_constraint(parent, child, opts=opts)

    elif constraint_type == c.OrientConstraint:
        con = commands.orient_constraint(parent, child, opts=opts)

    elif constraint_type == c.HingeConstraint:
        con = commands.hinge_constraint(parent, child, opts=opts)

    elif constraint_type == c.SocketConstraint:
        con = commands.socket_constraint(parent, child, opts=opts)

    elif constraint_type == c.ParentConstraint:
        con = commands.parent_constraint(parent, child, opts=opts)

    else:
        return log.warning(
            "Unrecognised constraint type '%s'" % constraint_type
        )

    guide_strength = _opt("constraintGuideStrength", opts)
    if guide_strength > 0:
        with cmdx.DagModifier() as mod:
            mod.set_attr(con["driveStrength"], guide_strength)

    if select:
        cmds.select(con.path(), replace=True)

    log.info("Constrained %s to %s" % (child, parent))
    return kSuccess


@i__.with_undo_chunk
def convert_constraint(selection=None, **opts):
    converted = []

    select = _opt("constraintSelect", opts)
    constraint_type = _opt("constraintType", opts)

    if constraint_type is None:
        constraint_type = options.read("convertConstraintType")

    for node in selection or cmdx.selection():
        con = node

        if not node.type() == "rdConstraint":
            con = node.shape(type="rdConstraint")

        if not con:
            log.warning("No constraint found for %s", node)
            continue

        if constraint_type == c.PointConstraint:
            converted += [commands.convert_to_point(con)]

        elif constraint_type == c.OrientConstraint:
            converted += [commands.convert_to_orient(con)]

        elif constraint_type == c.ParentConstraint:
            converted += [commands.convert_to_parent(con)]

        elif constraint_type == c.HingeConstraint:
            converted += [commands.convert_to_hinge(con)]

        elif constraint_type == c.SocketConstraint:
            converted += [commands.convert_to_socket(con)]

        else:
            # Raise errors, instead of logging directly, such that the
            # error message references the calling function instead of this,
            # helper-level function
            log.warning("Unrecognised constraint type '%s'", constraint_type)
            break

    if not converted:
        return log.warning("Nothing converted")

    elif select:
        cmds.select(map(str, converted), replace=True)

    log.info("Converted %d constraints" % len(converted))
    return kSuccess


@i__.with_undo_chunk
def convert_rigid(selection=None, **opts):
    selection = selection or cmdx.selection()
    converted = []
    typ = _opt("convertRigidType", opts)

    rigids = []
    for node in selection:
        rigid = node

        if node.isA(cmdx.kTransform):
            rigid = node.shape(type="rdRigid")

        if not rigid or rigid.type() != "rdRigid":
            log.warning("Couldn't convert %s" % node)
            continue

        # Toggle between kinematic and dynamic
        if typ == c.ConvertOpposite:
            passive = not rigid["kinematic"].read()
        else:
            passive = typ == c.ConvertPassive

        if _opt("cycleProtection", opts) and passive:
            scene = rigid["nextState"].connection(type="rdScene")

            if scene is None:
                # This rigid isn't even part of a scene
                pass

            transform = rigid.parent()
            parent = transform.parent()

            if parent and i__.is_dynamic(parent, scene):
                log.warning("%s cannot be made passive" % transform)
                MessageBox("Cycle Warning", (
                    "**Passive Child, Active Parent**\n\n"
                    "Cannot make *passive* rigid the "
                    "child of an *active* hierarchy. "
                    "This would have caused a cycle.\n\n"
                    "Ensure the parent of the selected node is "
                    "not already being affected by the simulation."
                ), buttons=ui.OkButton, icon=ui.InformationIcon)

                return kFailure

        rigids += [(rigid, passive)]

    for rigid, passive in rigids:
        commands.convert_rigid(rigid, opts={"passive": passive})
        converted.append(rigid)

    if not converted:
        return log.debug("Nothing converted")

    log.info("%d rigids converted", len(converted))
    return kSuccess


@i__.with_undo_chunk
def convert_to_socket(node):
    con = node.shape(type="rdConstraint")

    if con is None:
        return log.warning(
            "Couldn't find an existing constraint to convert, "
            "did you mean to select parent and child?"
        )

    commands.convert_to_socket(con)
    log.info("Converted %s -> Socket", con.path())
    return kSuccess


@i__.with_undo_chunk
def create_point_constraint(selection=None, **opts):
    opts = dict(opts, **{"constraintType": c.PointConstraint})
    return create_constraint(selection, **opts)


@i__.with_undo_chunk
def create_orient_constraint(selection=None, **opts):
    opts = dict(opts, **{"constraintType": c.OrientConstraint})
    return create_constraint(selection, **opts)


@i__.with_undo_chunk
def create_parent_constraint(selection=None, **opts):
    opts = dict(opts, **{"constraintType": c.ParentConstraint})
    return create_constraint(selection, **opts)


@i__.with_undo_chunk
def create_hinge_constraint(selection=None, **opts):
    opts = dict(opts, **{"constraintType": c.HingeConstraint})
    return create_constraint(selection, **opts)


@i__.with_undo_chunk
def create_socket_constraint(selection=None, **opts):
    opts = dict(opts, **{"constraintType": c.SocketConstraint})
    return create_constraint(selection, **opts)


@i__.with_undo_chunk
def create_animation_constraint(selection=None, **opts):
    selection = selection or cmdx.selection()

    created = []
    for node in selection:
        rigid = _find_rigid(node)

        if not rigid:
            continue

        opts = {
            "strength": _opt("constraintGuideStrength", opts),
        }

        con = commands.animation_constraint(rigid, opts=opts)
        created += [con]

    log.info("Successfully created %s" % ", ".join(str(c) for c in created))
    return kSuccess


@i__.with_undo_chunk
def set_initial_state(selection=None, **opts):
    selection = selection or cmdx.selection()
    use_selection = _opt("initialStateUseSelection", opts)

    if not use_selection:
        selection = cmdx.ls(type="rdRigid")

    rigids = []
    for rigid in selection:
        if rigid.isA(cmdx.kTransform):
            rigid = rigid.shape(type="rdRigid")

        if rigid and rigid.type() == "rdRigid":
            rigids += [rigid]

    if not rigids:
        return log.warning("No rigids found to set initial state for")

    commands.set_initial_state(rigids)

    log.info(
        "Successfully set initial state for %d rigid bodies.", len(rigids)
    )
    return kSuccess


@i__.with_undo_chunk
def clear_initial_state(selection=None, **opts):
    selection = selection or cmdx.selection()
    use_selection = _opt("initialStateUseSelection", opts)

    if not use_selection:
        selection = cmdx.ls(type="rdRigid")

    rigids = []
    for rigid in selection:
        if rigid.isA(cmdx.kTransform):
            rigid = rigid.shape(type="rdRigid")

        if rigid and rigid.type() == "rdRigid":
            rigids += [rigid]

    if not rigids:
        return log.warning("No rigids found to clear initial state for")

    commands.clear_initial_state(rigids)

    log.info(
        "Successfully cleared initial state for %d rigid bodies.", len(rigids)
    )
    return kSuccess


@i__.with_undo_chunk
def create_driven_control(selection=None, **opts):
    controls = []
    selection = selection or cmdx.selection()

    if len(selection) == 1:
        actor = selection[0]

        if actor.isA(cmdx.kTransform):
            actor = selection[0].shape(type="rdRigid")

        if not actor:
            return log.warning("%s was not a Ragdoll Rigid", selection[0])

        _, ctrl, _ = commands.create_absolute_control(actor)
        controls += [ctrl.parent().path()]

    elif len(selection) == 2:
        reference, actor = selection

        if actor.isA(cmdx.kTransform):
            actor = selection[1].shape(type="rdRigid")

        if not actor:
            return log.warning("%s was not a Ragdoll Rigid", selection[1])

        if actor.sibling(type="rdConstraint"):
            ctrl = commands.create_active_control(reference, actor)
        else:
            _, ctrl, _ = commands.create_absolute_control(actor, reference)

        controls += [reference.path()]

    else:
        return log.warning(
            "Select one rigid, or one rigid and a reference transform"
        )

    cmds.select(controls)
    return kSuccess


@i__.with_undo_chunk
def create_kinematic_control(selection=None, **opts):
    controls = []

    for node in selection or cmdx.selection():
        actor = node

        if actor.isA(cmdx.kTransform):
            actor = node.shape(type="rdRigid")

        if not actor:
            log.warning("%s was not an Ragdoll Rigid", node)
            continue

        con = commands.create_kinematic_control(actor)
        controls += [con.path()]

    if not controls:
        return log.warning("Nothing happened, did you select a rigid?")
    else:
        cmds.select(controls)
        return kSuccess


@i__.with_undo_chunk
def transfer_selected(selection=None):
    try:
        a, b = selection or cmdx.selection()
    except ValueError:
        return log.warning(
            "Select source and destination rigids, in that order"
        )

    commands.transfer_attributes(a, b, opts={"mirror": True})

    log.info("Transferred attributes from %s -> %s", a, b)
    return kSuccess


def edit_constraint_frames(selection=None):
    frames = []

    for node in selection or cmdx.selection():
        con = node

        if con.isA(cmdx.kTransform):
            cons = list(node.shapes(type="rdConstraint"))

            if cons:
                # Last created constraint
                con = cons[-1]

        if not con:
            log.warning("%s had no constraint", node)
            continue

        frames.extend(commands.edit_constraint_frames(con))

    log.info("Created %d frames", len(frames))
    cmds.select(map(str, frames))
    return kSuccess


def edit_shape(selection=None):
    editors = []

    for node in selection or cmdx.selection():
        rigid = node

        if rigid.isA(cmdx.kTransform):
            rigid = node.shape(type="rdRigid")

        if rigid is None:
            log.warning("No rigid found for %s" % node)
            continue

        if rigid.type() != "rdRigid":
            log.warning("%s was not a rigid" % rigid)
            continue

        if not rigid:
            log.warning("%s had no constraint", node)
            continue

        editors.append(commands.edit_shape(rigid))

    log.info("Created %d shape editors", len(editors))
    cmds.select(map(str, editors))
    return kSuccess


def _create_force(selection=None, force_type=None):
    # To specific rigids, or all of them
    selection = cmdx.selection() or cmdx.ls(type="rdRigid")

    rigids = []
    for node in selection:
        rigid = node

        if rigid.isA(cmdx.kTransform):
            rigid = node.shape(type="rdRigid")

        if not rigid:
            log.warning("%s was not an Ragdoll Rigid", node)
            continue

        rigids += [rigid]

    if not rigids:
        return log.warning("No rigids found")

    scene = _find_current_scene(autocreate=False)

    # Cancelled by user
    if not scene:
        return

    force = commands.create_force(force_type, scene)

    for rigid in rigids:
        commands.assign_force(rigid, force)

    cmds.select(force.parent().path())
    return kSuccess


@i__.with_undo_chunk
def create_push_force(selection=None):
    return _create_force(selection, c.PushForce)


@i__.with_undo_chunk
def create_pull_force(selection=None):
    return _create_force(selection, c.PullForce)


@i__.with_undo_chunk
def create_uniform_force(selection=None):
    return _create_force(selection, c.UniformForce)


@i__.with_undo_chunk
def create_turbulence_force(selection=None):
    return _create_force(selection, c.TurbulenceForce)


@i__.with_undo_chunk
def create_slice(selection=None):
    scene = _find_current_scene(autocreate=False)

    # Cancelled by user
    if not scene:
        return

    slice = commands.create_slice(scene)
    cmds.select(slice.parent().path())
    log.info("Created %s", slice)
    return kSuccess


@i__.with_undo_chunk
def assign_force(selection=None):
    sel = selection or cmdx.selection()

    if len(sel) < 2:
        return log.warning(
            "Select rigid body followed by one or more forces to assign"
        )

    force, targets = sel[0], sel[1:]

    if force.isA(cmdx.kTransform):
        force = force.shape(type="rdForce")

    if not force or force.type() != "rdForce":
        return log.warning("%s was not a force", sel[0])

    assignments = []
    for node in targets:
        target = node

        if target.isA(cmdx.kTransform):
            target = node.shape(type="rdRigid")

        if not target or target.type() != "rdRigid":
            log.warning("%s was not a rigid body", node)
            continue

        if commands.assign_force(target, force):
            assignments += [force]

    if assignments:
        return log.info("Assigned %s to %d rigids", force, len(assignments))
    else:
        log.warning("No forces assigned")
        return kSuccess


@i__.with_undo_chunk
def duplicate_selected(selection=None, **opts):
    selection = cmdx.selection()
    cmds.select(deselect=True)

    duplicates = []
    for node in selection:
        rigid = node

        if rigid.isA(cmdx.kTransform):
            rigid = node.shape(type="rdRigid")

        if not rigid:
            log.warning("%s skipped, not a rigid", node)
            continue

        log.info("Duplicating %s", rigid)

        dup = commands.duplicate(rigid)
        duplicates += [dup]

        cmds.select(dup.parent().path(), add=True)

    if duplicates:
        log.info("Duplicated %d rigids", len(duplicates))
        return kSuccess
    else:
        return log.warning("Nothing duplicated")


@i__.with_undo_chunk
def delete_physics(selection=None, **opts):
    if _opt("deleteFromSelection", opts):
        selection = selection or cmdx.selection(type="dagNode")

        if not selection:
            result = commands.delete_all_physics()

        else:
            result = commands.delete_physics(selection)

    else:
        result = commands.delete_all_physics()

    any_node = cmds.ls()[0]
    cmds.select(any_node)  # Trigger a change to selection
    cmds.select(deselect=True)

    if any(result.values()):
        log.info(
            "Deleted {deletedRagdollNodeCount} Ragdoll nodes, "
            "{deletedExclusiveNodeCount} exclusive nodes and "
            "{deletedUserAttributeCount} user attributes".format(**result)
        )
        return kSuccess

    else:
        return log.warning("Nothing deleted")


@requires_ui
def create_dynamic_control(selection=None, **opts):
    message = """\
Dynamic Control has been updated and renamed Active Chain
"""

    MessageBox(
        "Command Renamed",
        message,
        buttons=ui.OkButton,
        icon=ui.InformationIcon
    )

    return kSuccess


@i__.with_undo_chunk
def convert_to_polygons(selection=None):
    meshes = []

    for node in cmdx.selection(type=("transform", "rdRigid", "rdControl")):
        actor = node

        if actor.isA(cmdx.kTransform):
            actor = node.shape(type=("rdRigid", "rdControl"))

        if not actor:
            log.warning("%s was not a rdRigid or rdControl" % node)
            continue

        mesh = commands.convert_to_polygons(actor)
        meshes += [mesh.parent().path()]

    if meshes:
        cmds.select(meshes)
        log.info("Converted %d rigids to polygons" % len(meshes))
        return kSuccess
    else:
        return log.warning("Nothing converted")


def normalise_shapes(selection=None):
    selection = selection or cmdx.selection()

    if not selection:
        return log.warning("Select root of hierarchy to normalise it")

    root = selection[0]

    if root.isA(cmdx.kShape):
        root = root.parent()

    commands.normalise_shapes(root)

    return True


def multiply_rigids(selection=None):
    rigids = _filtered_selection("rdRigid")

    if not rigids:
        return False

    selected_channels = _selected_channels()
    mult = commands.multiply_rigids(
        rigids, channels=selected_channels
    )

    cmds.select(str(mult))

    return True


def multiply_constraints(selection=None):
    constraints = _filtered_selection("rdConstraint")

    if not constraints:
        return False

    selected_channels = _selected_channels()

    mult = commands.multiply_constraints(
        constraints, channels=selected_channels
    )

    cmds.select(str(mult))

    return True


def select_type(typ):
    def select(selection=None):
        selection = cmds.ls(selection=True)

        if selection:
            cmds.select(cmds.ls(selection, type=typ))
        else:
            cmds.select(cmds.ls(type=typ))
    return select


def select_rigids(selection=None):
    return select_type("rdRigid")(selection)


def select_constraints(selection=None):
    return select_type("rdConstraint")(selection)


def select_controls(selection=None):
    return select_type("rdControl")(selection)


def select_scenes(selection=None):
    return select_type("rdScene")(selection)


def show_explorer(selection=None):
    def get_fresh_dump(*args, **kwargs):
        return json.loads(cmds.ragdollDump(*args, **kwargs))

    if ui.Explorer.instance and ui.isValid(ui.Explorer.instance):
        return ui.Explorer.instance.show()

    win = ui.Explorer(parent=ui.MayaWindow())
    win.load(get_fresh_dump)
    win.show(dockable=True)


#
# User Interface
#


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
        result = func()

        try:
            cmds.repeatLast(
                addCommand=command,
                addCommandLabel=func.__name__
            )
        except Exception:
            pass

        return result
    return repeatable_wrapper


def welcome_user(*args):
    parent = ui.MayaWindow()
    win = ui.SplashScreen(parent)
    win.show()
    win.activateWindow()

    # Maya automatically centers new windows,
    # sometimes. On some platforms. Trust no one.
    ui.center_window(win)

    return win


@_format_exception
def export_physics(selection=None, **opts):
    data = cmds.ragdollDump()
    data = json.loads(data)

    if not data["entities"]:
        return log.error("Nothing to export")

    from PySide2 import QtWidgets
    fname, suffix = QtWidgets.QFileDialog.getSaveFileName(
        ui.MayaWindow(),
        "Export Ragdoll Scene",
        os.path.dirname(options.read("exportPath")),
        "Ragdoll scene files (*.rag)"
    )

    if not fname:
        return cmds.warning("Cancelled")

    fname = os.path.normpath(fname)

    # Include optional thumbnail
    data["ui"] = {

        # Guarantee forward-slash for paths, on all OSes
        "filename": fname.replace("\\", "/"),

        "description": "",
    }

    if _opt("exportIncludeThumbnail", opts):
        thumbnail = ui.view_to_pixmap()
        b64 = ui.pixmap_to_base64(thumbnail)
        data["ui"]["thumbnail"] = b64.decode("ascii")

    try:
        dump.export(fname, data=data)
    except Exception:
        _print_exception()
        return log.warning("Could not export %s" % fname)

    options.write("exportPath", fname)
    log.info(
        "Successfully exported to %s in %.2f ms"
        % (fname, data["info"]["serialisationTimeMs"])
    )


@_format_exception
def import_physics_from_file(selection=None, **opts):
    from PySide2 import QtWidgets
    fname, suffix = QtWidgets.QFileDialog.getOpenFileName(
        ui.MayaWindow(),
        "Import Ragdoll Scene",
        os.path.dirname(options.read("importPath")),
        "Ragdoll scene files (*.rag)"
    )

    if not fname:
        return cmds.warning("Cancelled")

    fname = os.path.normpath(fname)
    loader = dump.Loader()

    try:
        loader.read(fname)
    except Exception:
        _print_exception()
        return log.error("Could not read from %s" % fname)

    method = _opt("importMethod", opts)

    try:
        if method == "Load":
            merge = _opt("importMergePhysics", opts)
            loader.load(merge=merge)
        else:
            loader.reinterpret()

    except Exception:
        _print_exception()
        return log.error("Could not load %s" % fname)

    options.write("importPath", fname)
    log.info("Successfully imported %s" % fname)


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
        ctime = cmds.currentTime(query=True)
        cmds.evalDeferred(lambda: cmds.currentTime(ctime, update=True))

    def global_preferences():
        pass

    window = _Window("globalPreferences", global_preferences)

    # Update viewport immediately whenever this changes
    scale = window.parser.find("scale")
    scale.changed.connect(callback)

    return window


def save_preferences(*args):
    options.save()
    log.info("Successfully saved Ragdoll preferences")


def reset_preferences(*args):
    options.reset()
    log.info("Successfully reset Ragdoll preferences")


def create_rigid_options(*args):
    window = _Window("activeRigid", create_active_rigid)
    return window


def create_chain_options(*args):
    window = _Window("activeChain", create_active_chain)
    return window


def create_passive_options(selection=None):
    window = _Window("passiveRigid", create_passive_rigid)
    return window


def convert_constraint_options(*args):
    window = _Window("convertConstraint", convert_constraint)
    return window


def convert_rigid_options(*args):
    window = _Window("convertRigid", convert_rigid)
    return window


def _constraint_options(typ):
    def _create_constraint_options(*args):
        # Preselect whatever the user picked
        options.write("constraintType", typ)
        window = _Window("constraint", create_constraint)
        return window

    return _create_constraint_options


def create_kinematic_control_options(*args):
    return _Window("kinematic", create_kinematic_control)


def create_driven_control_options(*args):
    return _Window("guide", create_driven_control)


def create_push_force_options(*args):
    return _Window("push", create_push_force)


def create_pull_force_options(*args):
    return _Window("pull", create_pull_force)


def create_uniform_force_options(*args):
    return _Window("directional", create_uniform_force)


def create_turbulence_force_options(*args):
    return _Window("wind", create_turbulence_force)


def multiply_rigids_options(*args):
    return _Window("multiplyRigids", multiply_rigids)


def edit_shape_options(*args):
    return _Window("editShape", edit_shape)


def multiply_constraints_options(*args):
    return _Window("multiplyConstraints", create_turbulence_force)


def create_animation_constraint_options(selection=None, **opts):
    return _Window("animationConstraint", create_animation_constraint)


def create_character_options(*args):
    window = _Window("character", create_character)

    # Create dependencies between arguments
    control = window.parser.find("characterControl")
    copy = window.parser.find("characterCopy")
    control["condition"] = copy.read

    return window


def create_muscle_options(*args):
    return _Window("muscle", create_muscle)


def create_dynamic_control_options(*args):
    return create_chain_options()


def set_initial_state_options(*args):
    return _Window("setInitialState", set_initial_state)


def clear_initial_state_options(*args):
    return _Window("clearInitialState", clear_initial_state)


def _st_options(key, typ):
    def select(*args):
        return _Window(key, select_type(typ))
    return select


select_rigids_options = _st_options("selectRigids", "rdRigid")
select_constraints_options = _st_options("selectConstraints", "rdControl")
select_scenes_options = _st_options("selectScenes", "rdScene")
select_controls_options = _st_options("selectControls", "rdControl")


def delete_physics_options(*args):
    return _Window("deleteAllPhysics", delete_physics)


def import_physics_options(*args):
    win = None

    def import_physics():
        return win.do_import()

    win = _Window("importPhysics", import_physics, cls=ui.ImportOptions)
    win.resize(win.width(), ui.px(750))
    ui.center_window(win)
    return win


def export_physics_options(*args):
    return _Window("exportPhysics", export_physics)


# Backwards compatibility
create_rigid = create_active_rigid
create_collider = create_passive_rigid
