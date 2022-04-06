
import shiboken2
from PySide2 import QtCore, QtWidgets, QtGui
from . import px

try:
    long  # noqa
except NameError:
    # Python 3 compatibility
    long = int


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
