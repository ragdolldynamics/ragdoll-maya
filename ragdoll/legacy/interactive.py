import os
import copy
import json
import logging
import functools

from PySide2 import QtWidgets
from maya import cmds

from . import dump, ui
from .. import options, __
from ..vendor import cmdx, qargparse

log = logging.getLogger("ragdoll")


def import_physics_from_file(selection=None, **opts):
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
        return log.error("Could not read from %s" % fname)

    method = _opt("importMethod", opts)

    try:
        if method == "Load":
            merge = _opt("importMergePhysics", opts)
            loader.load(merge=merge)
        else:
            loader.reinterpret()

    except Exception:
        return log.error("Could not load %s" % fname)

    options.write("importPath", fname)
    log.info("Successfully imported %s" % fname)

    return True


def import_physics_options(*args):
    from .legacy import ui
    win = None

    def import_physics():
        return win.do_import()

    win = _Window("importPhysics", import_physics, cls=ui.ImportOptions)
    ui.center_window(win)

    return win


def _opt(key, override=None):
    override = override or {}
    return override.get(key, options.read(key))


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def export_physics(selection=None, **opts):

    # Initialise start and next frames of each scene
    current_time = cmds.currentTime(query=True)
    for scene in cmdx.ls(type="rdScene"):
        start_time = scene["startTime"].asTime().value
        cmds.currentTime(start_time)
        cmds.currentTime(start_time + 1)
    cmds.currentTime(current_time)

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
        return log.warning("Could not export %s" % fname)

    # Update any currently opened Import UI
    for title, widget in __.widgets.items():
        if not isinstance(widget, ui.ImportOptions):
            continue

        if not ui.isValid(widget):
            continue

        log.warning("Updating currently opened Import UI")
        widget.on_path_changed(force=True)

    options.write("exportPath", fname)
    log.info(
        "Successfully exported to %s in %.2f ms"
        % (fname, data["info"]["serialisationTimeMs"])
    )

    return True


def export_physics_options(*args):
    return _Window("exportPhysics", export_physics)


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


def _last_command():
    _last_command._func()


def repeatable(func):
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
