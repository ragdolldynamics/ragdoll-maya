import os
import sys
import json
import logging

from maya import cmds
from maya.api import OpenMaya as om
from maya.OpenMayaUI import MQtUtil
from PySide2 import QtCore, QtWidgets, QtGui

from .. import (
    options,
    internal,
    ui,
)

from . import dump
from ..vendor import qargparse

log = logging.getLogger("ragdoll")

self = sys.modules[__name__]
self._maya_window = None

px = MQtUtil.dpiScale

EntityRole = QtCore.Qt.UserRole + 0
TransformRole = QtCore.Qt.UserRole + 1
OptionsRole = QtCore.Qt.UserRole + 2
OccupiedRole = QtCore.Qt.UserRole + 3
HintRole = QtCore.Qt.UserRole + 4
PathRole = QtCore.Qt.UserRole + 5


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _scaled_stylesheet(style):
    """Replace any mention of <num>px with scaled version

    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.

    """

    output = []
    for line in style.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            key, value = line.rsplit(" ", 1)
            value = px(int(value[:-3]))
            line = "%s %dpx;" % (key, value)
        output += [line]
    result = "\n".join(output)
    result = result % {"res": _resource().replace("\\", "/")}
    return result


class DumpView(QtWidgets.QTreeView):
    mouseMoved = QtCore.Signal(QtCore.QPoint)  # Pos

    def __init__(self, parent=None):
        super(DumpView, self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.mouseMoved.emit(event.pos())
        return super(DumpView, self).mouseMoveEvent(event)


class DumpWidget(QtWidgets.QWidget):
    hinted = QtCore.Signal(str)  # Hint

    def __init__(self, loader, parent=None):
        super(DumpWidget, self).__init__(parent)

        panels = {
            "Body": QtWidgets.QWidget(),
        }

        widgets = {
            "TargetView": DumpView(),
        }

        models = {
            "TargetModel": qargparse.GenericTreeModel(),
        }

        for name, wid in panels.items():
            wid.setObjectName(name)

        for name, wid in widgets.items():
            wid.setObjectName(name)

        # Setup

        widgets["TargetView"].mouseMoved.connect(self.on_mouse_moved)

        widgets["TargetView"].setModel(models["TargetModel"])
        widgets["TargetView"].setSelectionBehavior(
            QtWidgets.QTreeView.SelectRows)

        # Layout

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(widgets["TargetView"])
        layout.setContentsMargins(0, 0, 0, 0)

        selection_model = widgets["TargetView"].selectionModel()
        selection_model.currentRowChanged.connect(self.on_target_changed)

        timer = QtCore.QTimer(parent=self)
        timer.setInterval(50.0)  # ms
        timer.setSingleShot(True)
        timer.timeout.connect(self._reset)

        self._reset_timer = timer
        self._widgets = widgets
        self._panels = panels
        self._models = models
        self._loader = loader

        self.setStyleSheet(_scaled_stylesheet("""
            QTreeView {
                outline: none;
            }

            QTreeView::item {
                border: 0px;
                padding-left: 0px;
                padding-right: 10px;
            }

            QTreeView::item:selected {
                background: #5285a6;
            }
        """))

    def leaveEvent(self, event):
        self.hinted.emit("")  # Clear
        return super(DumpWidget, self).leaveEvent(event)

    def on_mouse_moved(self, pos):
        index = self._widgets["TargetView"].indexAt(pos)
        tooltip = index.data(HintRole)
        self.hinted.emit(tooltip or "")

    def on_target_changed(self, current, previous):
        pass

    def reset(self):
        # Reset after a given time period.
        # This allows reset to get called frequently, without
        # actually incuring the cost of resetting the model each
        # time. It keeps the user interactivity swift and clean.
        self._reset_timer.start()

    def _reset(self):
        def _transform(data, entity):
            Name = self._loader.component(entity, "NameComponent")

            alignment = (
                QtCore.Qt.AlignLeft,
                QtCore.Qt.AlignLeft,
                QtCore.Qt.AlignLeft,
            )

            shape_icon = None
            rigid_entity = entity

            # Borrow a shape icon from whatever rigid this constraint applies
            if self._loader.has(entity, "JointComponent"):
                Joint = self._loader.component(entity, "JointComponent")

                # Protect against possible (but improbable) invalid reference
                if Joint["child"]:
                    rigid_entity = Joint["child"]

            if self._loader.has(rigid_entity, "RigidUIComponent"):
                rigid_ui = self._loader.component(rigid_entity,
                                                  "RigidUIComponent")

                # TODO: Replace .get with []
                shape_icon = rigid_ui.get("shapeIcon")
                shape_icon = {
                    "joint": "maya_joint.png",
                    "mesh": "maya_mesh.png",
                    "nurbsCurve": "maya_curve.png",
                    "nurbsSurface": "maya_surface.png",
                }.get(shape_icon, "maya_transform.png")

                shape_icon = _resource("icons", shape_icon)
                shape_icon = QtGui.QIcon(shape_icon)

            try:
                transform = analysis["transforms"][entity]

            except KeyError:

                # Dim any transform that isn't getting imported
                color = self.palette().color(self.foregroundRole())
                color.setAlpha(100)
                grayed_out = (color, color, color)

                try:
                    # Is there a transform, except it's occupied?
                    occupied = analysis["occupied"][entity]

                except KeyError:
                    # No, there isn't a transform for this entity
                    icon = _resource("icons", "questionmark.png")
                    icon = QtGui.QIcon(icon)
                    tooltip = "No transform could be found for this rigid"

                    data[QtCore.Qt.DecorationRole] += [shape_icon, icon]
                    data[QtCore.Qt.TextAlignmentRole] = alignment
                    data[QtCore.Qt.ForegroundRole] = grayed_out

                    data[OccupiedRole] = False
                    data[HintRole] += (
                        Name["path"],
                        tooltip
                    )

                else:
                    icon = _resource("icons", "check.png")
                    icon = QtGui.QIcon(icon)
                    path = occupied.shortestPath()

                    data[QtCore.Qt.DisplayRole] += [path]
                    data[QtCore.Qt.DecorationRole] += [shape_icon, icon]
                    data[QtCore.Qt.ForegroundRole] = (color, color)
                    data[QtCore.Qt.TextAlignmentRole] = alignment

                    data[TransformRole] = occupied
                    data[OccupiedRole] = True
                    data[HintRole] += (
                        occupied.path(),
                        "%s already has a rigid" % path
                    )
            else:
                icon = _resource("icons", "right.png")
                icon = QtGui.QIcon(icon)

                data[QtCore.Qt.DecorationRole] += [shape_icon, icon]
                data[QtCore.Qt.DisplayRole] += [transform.shortestPath()]
                data[QtCore.Qt.TextAlignmentRole] = alignment

                data[TransformRole] = transform
                data[HintRole] += (
                    Name["path"],
                    transform.path()
                )

        def _rigid_icon(data, entity):
            Desc = self._loader.component(
                entity, "GeometryDescriptionComponent"
            )

            icon = {
                "Box": "box.png",
                "Capsule": "capsule.png",
                "Cylinder": "cylinder.png",
                "Sphere": "sphere.png",
                "ConvexHull": "mesh.png",
            }.get(
                Desc["type"],

                # In case the format is all whack
                "rigid.png"
            )

            icon = _resource("icons", icon)
            icon = QtGui.QIcon(icon)

            data[QtCore.Qt.DecorationRole] += [icon]

        def _default_data():
            return {
                QtCore.Qt.DisplayRole: [],
                QtCore.Qt.DecorationRole: [],
                QtCore.Qt.TextAlignmentRole: [],

                HintRole: [],
                TransformRole: None,
                EntityRole: None,
                OptionsRole: None,
            }

        def _add_scenes(root_item):
            for scene in analysis["scenes"]:
                entity = scene["entity"]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "scene.png")
                icon = QtGui.QIcon(icon)

                transform_data = _default_data()
                transform_data[QtCore.Qt.DisplayRole] += ["Scene", label]
                transform_data[QtCore.Qt.DecorationRole] += [icon]
                transform_data[HintRole] += ["Scene Command"]
                transform_data[EntityRole] = entity
                transform_data[OptionsRole] = scene["options"]

                _transform(transform_data, entity)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += [Name["value"],
                                                Name.get("shortestPath", "")]
                data[EntityRole] = entity

                _rigid_icon(data, entity)
                _transform(data, entity)

                transform_item = qargparse.GenericTreeModelItem(transform_data)
                entity_item = qargparse.GenericTreeModelItem(data)

                root_item.addChild(transform_item)
                transform_item.addChild(entity_item)

        def _add_chains(root_item):
            for chain in analysis["chains"]:
                entity = chain["rigids"][0]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "chain.png")
                icon = QtGui.QIcon(icon)

                transform_data = _default_data()
                transform_data[QtCore.Qt.DisplayRole] += ["Chain", label]
                transform_data[QtCore.Qt.DecorationRole] += [icon]
                transform_data[HintRole] += ["Chain Command"]

                transform_data[EntityRole] = entity
                transform_data[OptionsRole] = chain["options"]

                _transform(transform_data, entity)

                chain_item = qargparse.GenericTreeModelItem(transform_data)
                root_item.addChild(chain_item)

                for entity in chain["rigids"]:
                    Name = self._loader.component(entity, "NameComponent")
                    label = Name["path"].rsplit("|", 1)[-1]
                    icon = _resource("icons", "rigid.png")
                    icon = QtGui.QIcon(icon)

                    data = _default_data()
                    data[EntityRole] = entity
                    data[HintRole] += ["Rigid"]
                    data[QtCore.Qt.DisplayRole] += [
                        Name["value"], Name.get("shortestPath", "")
                    ]

                    _rigid_icon(data, entity)
                    _transform(data, entity)

                    chain_item.addChild(qargparse.GenericTreeModelItem(data))

                for entity in chain["constraints"]:
                    icon = _resource("icons", "constraint.png")
                    icon = QtGui.QIcon(icon)

                    Name = self._loader.component(entity, "NameComponent")

                    data = _default_data()
                    data[HintRole] += ["Constraint"]
                    data[QtCore.Qt.DecorationRole] += [icon]
                    data[QtCore.Qt.DisplayRole] += [
                        Name["value"], Name.get("shortestPath", "")
                    ]

                    data[EntityRole] = entity

                    _transform(data, entity)

                    chain_item.addChild(qargparse.GenericTreeModelItem(data))

        def _add_rigids(root_item):
            for rigid in analysis["rigids"]:
                entity = rigid["entity"]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "rigid.png")
                icon = QtGui.QIcon(icon)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += ["Rigid", label]
                data[QtCore.Qt.DecorationRole] += [icon]
                data[HintRole] += ["Rigid Command"]

                data[EntityRole] = entity
                data[OptionsRole] = rigid["options"]

                _transform(data, entity)

                item = qargparse.GenericTreeModelItem(data)
                root_item.addChild(item)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += [Name["value"],
                                                Name.get("shortestPath", "")]
                data[QtCore.Qt.DecorationRole] += []
                data[EntityRole] = entity

                _rigid_icon(data, entity)
                _transform(data, entity)

                child = qargparse.GenericTreeModelItem(data)
                item.addChild(child)

        def _add_constraints(root_item):
            for constraint in analysis["constraints"]:
                entity = constraint["entity"]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "constraint.png")
                icon = QtGui.QIcon(icon)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += ["Constraint", label]
                data[QtCore.Qt.DecorationRole] += [icon]
                data[HintRole] += ["Constraint Command"]
                data[EntityRole] = entity
                data[OptionsRole] = constraint["options"]

                _transform(data, entity)

                item = qargparse.GenericTreeModelItem(data)
                root_item.addChild(item)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += [Name["value"],
                                                Name.get("shortestPath", "")]
                data[EntityRole] = entity
                data[QtCore.Qt.DecorationRole] += [icon]

                _transform(data, entity)

                child = qargparse.GenericTreeModelItem(data)
                item.addChild(child)

        def _add_rigid_multipliers(root_item):
            for mult in analysis["rigidMultipliers"]:
                entity = mult["entity"]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "rigid_multiplier.png")
                icon = QtGui.QIcon(icon)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += ["Rigid Multiplier", label]
                data[QtCore.Qt.DecorationRole] += [icon]
                data[HintRole] += ["Rigid Multiplier Command"]
                data[EntityRole] = entity
                data[OptionsRole] = mult["options"]

                _transform(data, entity)

                item = qargparse.GenericTreeModelItem(data)
                root_item.addChild(item)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += [Name["value"],
                                                Name.get("shortestPath", "")]
                data[EntityRole] = entity
                data[QtCore.Qt.DecorationRole] += [icon]

                _transform(data, entity)

                child = qargparse.GenericTreeModelItem(data)
                item.addChild(child)

        def _add_constraint_multipliers(root_item):
            for mult in analysis["constraintMultipliers"]:
                entity = mult["entity"]

                Name = self._loader.component(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "constraint_multiplier.png")
                icon = QtGui.QIcon(icon)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += ["Constraint Multiplier", label]
                data[QtCore.Qt.DecorationRole] += [icon]
                data[HintRole] += ["Constraint Multiplier Command"]
                data[EntityRole] = entity
                data[OptionsRole] = mult["options"]

                _transform(data, entity)

                item = qargparse.GenericTreeModelItem(data)
                root_item.addChild(item)

                data = _default_data()
                data[QtCore.Qt.DisplayRole] += [Name["value"],
                                                Name.get("shortestPath", "")]
                data[EntityRole] = entity
                data[QtCore.Qt.DecorationRole] += [icon]

                _transform(data, entity)

                child = qargparse.GenericTreeModelItem(data)
                item.addChild(child)

        analysis = self._loader.analyse()
        root_item = qargparse.GenericTreeModelItem({
            QtCore.Qt.DisplayRole: ("Command", "Source Node", "Target Node")
        })

        if not self._loader.is_valid():
            icon = _resource("icons", "error.png")
            icon = QtGui.QIcon(icon)
            invalid_item = qargparse.GenericTreeModelItem({
                QtCore.Qt.DisplayRole: "Invalid .rag file",
                QtCore.Qt.DecorationRole: icon,
                QtCore.Qt.ForegroundRole: QtGui.QColor("#F66"),
            })

            root_item.addChild(invalid_item)

            for reason in self._loader.invalid_reasons():
                log.debug("Failure reason: %s" % reason)

            self._widgets["TargetView"].setIndentation(0)

        else:
            self._widgets["TargetView"].setIndentation(30)

            _add_chains(root_item)
            _add_rigids(root_item)
            _add_constraints(root_item)
            _add_rigid_multipliers(root_item)
            _add_constraint_multipliers(root_item)
            _add_scenes(root_item)

        model = self._models["TargetModel"]
        model.reset(root_item)

        # Make sure everything is nice and tight
        self._widgets["TargetView"].resizeColumnToContents(0)
        self._widgets["TargetView"].resizeColumnToContents(1)
        self._widgets["TargetView"].resizeColumnToContents(2)


class ImportOptions(ui.Options):
    def __init__(self, *args, **kwargs):
        super(ImportOptions, self).__init__(*args, **kwargs)
        self.setWindowTitle("Import Options")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        loader = dump.Loader()

        widgets = {
            "DumpWidget": DumpWidget(loader),
            "Thumbnail": QtWidgets.QLabel(),
        }

        # Integrate with other options
        layout = self.parser.layout()
        row = self.parser._row
        alignment = (QtCore.Qt.AlignRight | QtCore.Qt.AlignTop,)

        layout.addWidget(QtWidgets.QLabel("Preview"), row, 0, *alignment)
        layout.addWidget(widgets["DumpWidget"], row, 1)
        layout.setRowStretch(9999, 0)  # Unexpand last row
        layout.setRowStretch(row, 1)  # Expand to fill width

        self.parser._row += 1  # For the next subclass

        # Map known options to this widget
        parser = self._widgets["Parser"]
        import_path = parser.find("importPath")
        import_paths = parser.find("importPaths")
        search_replace = parser.find("importSearchAndReplace")
        use_selection = parser.find("importUseSelection")
        auto_namespace = self.parser.find("importAutoNamespace")
        preserve_attributes = self.parser.find("importPreserveAttributes")

        import_path.changed.connect(self.on_path_changed)
        import_path.browsed.connect(self.on_browsed)
        import_paths.changed.connect(self.on_filename_changed)
        use_selection.changed.connect(self.on_selection_changed)
        auto_namespace.changed.connect(self.on_selection_changed)
        search_replace.changed.connect(self.on_search_and_replace)
        preserve_attributes.changed.connect(self.on_preserve_attributes)

        default_thumbnail = _resource("icons", "no_thumbnail.png")
        default_thumbnail = QtGui.QPixmap(default_thumbnail)
        default_thumbnail = default_thumbnail.scaled(
            px(200), px(128),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        qimport_paths = import_paths.widget()
        qimport_paths.setFixedHeight(px(128))
        layout = qimport_paths.layout()
        layout.setSpacing(px(2))
        layout.addWidget(widgets["Thumbnail"], 1, QtCore.Qt.AlignCenter)
        widgets["Thumbnail"].setAlignment(QtCore.Qt.AlignCenter)
        widgets["Thumbnail"].setFixedWidth(px(200))
        widgets["Thumbnail"].setFixedHeight(px(128))
        widgets["Thumbnail"].setPixmap(default_thumbnail)
        widgets["Thumbnail"].setStyleSheet("""
            QLabel {
                border: 1px solid #555;
                background: #222;
            }
        """)

        widgets["DumpWidget"].hinted.connect(self.on_hinted)

        self._loader = loader
        self._selection_callback = None
        self._previous_dirname = None
        self._default_thumbnail = default_thumbnail

        # Keep superclass informed
        self._widgets.update(widgets)

        # Kick things off, a few ms after opening
        QtCore.QTimer.singleShot(200, self.on_path_changed)

    def on_hinted(self, hint):
        if hint:
            text = hint
        else:
            text = self._widgets["Hint"].property("defaultText")

        # Trim very long instances
        if len(text) > 150:
            text = "..." + text[-147:]

        self._widgets["Hint"].setText(text)

    def do_import(self):
        try:
            if options.read("importMethod") == ui.Load:
                self._loader.load()
            else:
                self._loader.reinterpret()

        except Exception:

            # Keep the technical crowd on-top of what happened
            import traceback
            log.debug(traceback.format_exc())

            # But don't bother the animator
            log.warning("An unexpected error occurred, see Script Editor")

            return False

        finally:
            # Now that new physics has become part of the
            # scene, reset relevant widgets.
            self.reset()

        return True

    @internal.with_timing
    def reset(self):
        search_replace = self.parser.find("importSearchAndReplace")
        preserve = self.parser.find("importPreserveAttributes")
        search, replace = search_replace.read()
        self._loader.set_replace([(search, replace)])
        self._loader.set_preserve_attributes(preserve.read())
        self._widgets["DumpWidget"].reset()

    def load(self, data):
        assert isinstance(data, dict), "data must be a dictionary"

        current_path = self.parser.find("importPath")
        current_path.write("<raw>", notify=False)

        self._loader.read(data)
        self.on_selection_changed()

    def read(self, fname):
        assert isinstance(fname, internal.string_types), "fname must be string"

        current_path = self.parser.find("importPath")
        current_path.write(fname, notify=False)

        self._loader.read(fname)
        self.on_selection_changed()

    def on_selection_changed(self, _=None):
        try:
            self._on_selection_changed()

        # In the off chance that this fails, prevent further failure
        # by removing the callback altogether.
        except Exception:
            # Make note for debugging
            log.debug(
                "Ragdoll Import Options had trouble "
                "with a selection callback, and won't "
                "be using it anymore."
            )

            # This is not allowed to fail
            if self._selection_callback is not None:
                om.MMessage.removeCallback(self._selection_callback)
            self._selection_callback = None

    def _on_selection_changed(self, _=None):
        use_selection = self.parser.find("importUseSelection")
        auto_namespace = self.parser.find("importAutoNamespace")

        if use_selection.read():
            auto_namespace.widget().setEnabled(True)

            roots = cmds.ls(selection=True, type="transform", long=True)

            self._loader.set_namespace(None)
            self._loader.set_roots(roots)

            auto_namespace = self.parser.find("importAutoNamespace")
            if auto_namespace.read():
                namespaces = set()

                for root in roots:
                    namespaces = root.split("|")
                    namespaces = [node.rsplit(":", 1)[0]
                                  for node in namespaces]
                    namespaces = filter(None, namespaces)  # Remove `None`
                    namespaces = tuple(set(namespaces))  # Remove duplicates

                if len(namespaces) > 1:
                    log.debug("Selection had multiple namespaces: %s"
                              % str(namespaces))

                elif len(namespaces) > 0:
                    target_namespace = tuple(namespaces)[0]
                    self._loader.set_namespace(target_namespace)

        else:
            auto_namespace.widget().setEnabled(False)
            self._loader.set_namespace(None)
            self._loader.set_roots([])

        self.reset()

    def on_search_and_replace(self):
        # It'll get fetched during reset
        self.reset()

    def on_preserve_attributes(self):
        self.reset()

    def on_path_changed(self, force=False):
        SUFFIX = ".rag"

        import_paths = self.parser.find("importPaths")
        import_path = self.parser.find("importPath")

        # Could be empty
        if not import_path.read():
            return

        import_path_str = import_path.read()
        dirname, selected_fname = os.path.split(import_path_str)

        # No need to refresh the directory listing if it's the same directory
        if self._previous_dirname != dirname or force:
            self._previous_dirname = dirname

            fnames = []
            try:
                for fname in os.listdir(dirname):
                    if fname.endswith(SUFFIX):
                        fnames += [fname]
            except Exception:
                # Whatever is going on, the user can't do anything about it
                pass

            # TODO: Expose choice of icon to the user during export
            icon = _resource("icons", "logo2.png")
            icon = QtGui.QIcon(icon)

            items = []
            fnames = internal.sort_filenames(fnames)
            for fname in fnames:
                item = {
                    PathRole: fname,

                    QtCore.Qt.DecorationRole: icon,
                    QtCore.Qt.DisplayRole: fname,
                }

                items += [item]

            # A folder path was given, no filename
            if not selected_fname:

                # The folder may be empty
                if fnames:
                    selected_fname = fnames[0]

            if not items:
                items += [{
                    PathRole: None,

                    QtCore.Qt.DisplayRole: "Empty folder",
                    QtCore.Qt.DecorationRole: None,
                }]

            import_paths.reset(items,
                               header=("Filename",),
                               current=selected_fname)

        def read():
            self.read(import_path_str)

        # Give UI a chance to keep up
        QtCore.QTimer.singleShot(200, read)

    def on_filename_changed(self):
        current_paths = self.parser.find("importPaths")
        filename = current_paths.read(PathRole)

        if filename is not None:
            # Swap out the filename from the currently loaded path
            current_path = self.parser.find("importPath")
            original_path = current_path.read()

            dirname, _ = os.path.split(original_path)
            path = os.path.join(dirname, filename)

            # Make it official
            current_path.write(path)

        # Clear any current thumbnail
        qthumbnail = self._default_thumbnail

        # Fetch metadata, like description and thumbnail
        try:
            with open(path) as f:
                data = json.load(f)

        except Exception:
            pass

        else:
            ui = data.get("ui", {})
            thumbnail = ui.get("thumbnail")

            if thumbnail:
                # From JSON's unicode
                thumbnail = thumbnail.encode("ascii")

                # To QPixmap
                qthumbnail = ui.base64_to_pixmap(thumbnail)

                # Fit it to our widget
                qthumbnail = qthumbnail.scaled(
                    px(200), px(128),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )

        self._widgets["Thumbnail"].setPixmap(qthumbnail)

    def on_browsed(self):
        path, suffix = QtWidgets.QFileDialog.getOpenFileName(
            ui.MayaWindow(),
            "Open Ragdoll Scene",
            options.read("lastVisitedPath"),
            "Ragdoll scene files (*.rag)"
        )

        if not path:
            return log.debug("Cancelled")

        path = os.path.normpath(path)
        dirname, fname = os.path.split(path)

        # Update directory listing, even if it's unchanged
        # (in case the contents has actually changed)
        self._previous_dirname = None

        import_path = self.parser.find("importPath")
        import_path.write(path)

    def install_selection_callback(self):
        self._selection_callback = om.MModelMessage.addCallback(
            om.MModelMessage.kActiveListModified,
            self.on_selection_changed
        )

    def uninstall_selection_callback(self):
        if self._selection_callback is not None:
            om.MMessage.removeCallback(self._selection_callback)
        self._selection_callback = None

    def showEvent(self, event):
        # Keep an eye on the current selection
        self.install_selection_callback()
        super(ImportOptions, self).showEvent(event)

    def closeEvent(self, event):
        self.uninstall_selection_callback()

    def __del__(self):
        """This should never really need to be called

        But you can never be too careful with callbacks.

        """

        self.uninstall_selection_callback()
