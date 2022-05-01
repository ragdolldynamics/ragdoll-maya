import shiboken2

from PySide2 import QtCore, QtWidgets, QtGui
from maya.OpenMayaUI import MQtUtil

px = MQtUtil.dpiScale

try:
    long  # noqa
except NameError:
    # Python 3 compatibility
    long = int


def is_filtering_recursible():
    """Does Qt binding support recursive filtering for QSortFilterProxyModel?

    (NOTE) Recursive filtering was introduced in Qt 5.10.

    """
    return hasattr(QtCore.QSortFilterProxyModel,
                   "setRecursiveFilteringEnabled")


def qt_wrap_instance(ptr, base=None):
    assert isinstance(ptr, long), "Argument 'ptr' must be of type <long>"
    assert (base is None) or issubclass(base, QtCore.QObject), (
        "Argument 'base' must be of type <QObject>")

    func = shiboken2.wrapInstance

    if base is None:
        q_object = func(long(ptr), QtCore.QObject)
        meta_object = q_object.metaObject()

        while True:
            class_name = meta_object.className()
            try:
                base = getattr(QtWidgets, class_name)
            except AttributeError:
                try:
                    base = getattr(QtCore, class_name)
                except AttributeError:
                    meta_object = meta_object.superClass()
                    continue
            break

    return func(long(ptr), base)


class ToggleButton(QtWidgets.QPushButton):
    """A QPushButton subclass that allows to change icon on check state

    This is for Qt version that prior to 5.15 (like Maya<=2020), where
    "icon" property isn't yet exists in QPushButton stylesheet.

    With Qt version 5.15+, you can simply do so with following stylesheet
    setup:
        ```
        QPushButton:checked {
            icon: url(":/checked.svg");
        }
        QPushButton:!checked {
            icon: url(":/unchecked.svg");
        }
        ```

    """

    def __init__(self, *args, **kwargs):
        super(ToggleButton, self).__init__(*args, **kwargs)
        self._checked_icon = None
        self._unchecked_icon = None
        self.setCheckable(True)
        self.toggled.connect(self._on_toggled)

    def setIcon(self, icon):
        super(ToggleButton, self).setIcon(icon)
        self._unchecked_icon = icon

    def set_unchecked_icon(self, icon):
        self.setIcon(icon)

    def set_checked_icon(self, icon):
        assert isinstance(icon, QtGui.QIcon), "icon must be QtGui.QIcon"
        self._checked_icon = icon

    def _on_toggled(self, state):
        if not self._checked_icon:
            return
        if state:
            super(ToggleButton, self).setIcon(self._checked_icon)
        else:
            super(ToggleButton, self).setIcon(self._unchecked_icon)


class StateRotateButton(QtWidgets.QPushButton):
    """A QPushButton subclass that rotates on a list of linked state
    """
    stateChanged = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(StateRotateButton, self).__init__(*args, **kwargs)
        self._states = list()
        self._block = set()
        self._current = None
        self.setCheckable(True)

    def add_state(self, name, icon, text=None):
        """Register new state

        New added state will be linked with last added state.
        For example:
            foo -> bar -> foo (a circular chain with two states)
            foo -> bar -> new -> foo (new state inserted into the last)

        Args:
            name: state name
            icon: button icon
            text: button text, if given

        Returns:
            None
        """
        if not name:
            raise Exception("State name cannot be empty.")
        if any(s["name"] == name for s in self._states):
            raise Exception("Already have same named state %r." % name)

        after = self._states[-1] if self._states else None

        state = {
            "name": name,
            "icon": icon,
            "text": text or "",
            "next": None,
        }
        self._states.append(state)

        if after is None:
            state["next"] = state
            self._current = state  # first state, init
        else:
            state["next"] = after["next"]
            after["next"] = state

    def set_state(self, name):
        """Set current state by name"""
        for state in self._states:
            if state["name"] == name:
                self._current = state
                break
        else:
            raise Exception("No matched state found.")
        self.checkStateSet()

    def state(self):
        """Get current state name"""
        if self._current is None:
            raise Exception("Not initialized.")
        return self._current["name"]

    def block(self, name):
        """Block a state, blocked state will be skipped to it's next"""
        self._block.add(name)

    def unblock(self, name):
        """Unblock a state"""
        self._block.remove(name)

    def nextCheckState(self):
        self._current = self._current["next"]
        if self._current["name"] in self._block:
            self.nextCheckState()
        else:
            self.checkStateSet()

    def checkStateSet(self):
        state = self._current
        self.setText(state["text"])
        self.setIcon(state["icon"])
        self.stateChanged.emit(state["name"])

    def showEvent(self, event):
        super(StateRotateButton, self).showEvent(event)
        # init text and icon without emitting signal
        self.blockSignals(True)
        self.checkStateSet()
        self.blockSignals(False)


class FramelessDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(FramelessDialog, self).__init__(parent=parent)
        self.setWindowFlags(
            self.windowFlags() |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowSystemMenuHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        fx = QtWidgets.QGraphicsDropShadowEffect(self)
        fx.setBlurRadius(px(32))
        fx.setOffset(0)
        fx.setColor(QtGui.QColor("#55000000"))  # ARGB
        self.setGraphicsEffect(fx)

        self._wrapped = False
        self._dragging = False
        self._last_pos = None

    def showEvent(self, event):
        # type: (QtGui.QShowEvent) -> None

        widget = None
        if not self._wrapped:
            widget = QtWidgets.QWidget()
            widget.setAttribute(QtCore.Qt.WA_StyledBackground)
            widget.setObjectName("_FramelessDialog")
            widget.setLayout(self.layout())

            layout = QtWidgets.QVBoxLayout(self)
            layout.setMargin(32)
            layout.addWidget(widget)
            self._wrapped = True

        super(FramelessDialog, self).showEvent(event)

        if widget:
            r = px(10)
            color = widget.palette().color(QtGui.QPalette.Background)
            widget.setStyleSheet("""
            #%s {
                background: %s;
                border-radius: %dpx;
            }
            """ % (widget.objectName(), color.name(), r))

    def mousePressEvent(self, event):
        # type: (QtGui.QMouseEvent) -> None
        self._dragging = True
        self._last_pos = event.globalPos()
        super(FramelessDialog, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # type: (QtGui.QMouseEvent) -> None
        self._dragging = False
        super(FramelessDialog, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # type: (QtGui.QMouseEvent) -> None
        _current_pose = event.globalPos()
        if self._dragging and self._last_pos:
            _delta_pos = _current_pose - self._last_pos
            self.move(self.pos() + _delta_pos)
        self._last_pos = _current_pose
        super(FramelessDialog, self).mouseMoveEvent(event)


class BaseItemModel(QtGui.QStandardItemModel):
    Headers = []

    def __init__(self, *args, **kwargs):
        super(BaseItemModel, self).__init__(*args, **kwargs)
        self.setColumnCount(len(self.Headers))

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and section < len(self.Headers):
            return self.Headers[section]
        return super(BaseItemModel, self).headerData(
            section, orientation, role)

    def reset(self):
        """Remove all rows and set row count to zero
        This doesn't clear header.
        """
        self.removeRows(0, self.rowCount())
        self.setRowCount(0)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


def sibling_at_column(index, column):
    """An alternative of QModelIndex.siblingAtColumn() for Qt version < 5.11
    """
    model = index.model()
    parent = index.parent()
    return model.index(index.row(), column, parent)
