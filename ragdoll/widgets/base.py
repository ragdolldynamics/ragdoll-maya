
import os
import re
import sys
import json
import logging
import weakref
import hashlib
import traceback
import threading
import shiboken2
import subprocess
import webbrowser
from functools import partial
from collections import defaultdict
from datetime import datetime, timedelta, date as date_
from PySide2 import QtCore, QtWidgets, QtGui
from maya.OpenMayaUI import MQtUtil

try:
    import queue
except ImportError:
    import Queue as queue  # py2

try:
    from urllib import request
except ImportError:
    import urllib as request  # py2

from .. import __, constants, options, ui

RAGDOLL_DYNAMICS_VERSIONS_URL = "https://ragdolldynamics.com/version"
RAGDOLL_DYNAMICS_RELEASES_URL = "https://learn.ragdolldynamics.com/news"
WYDAY_URL = "https://wyday.com"

NO_INTERNET = bool(os.getenv("RAGDOLL_SKIP_UPDATE_CHECK"))
NO_WORKER_THREAD_QT = bool(os.getenv("RAGDOLL_SINGLE_THREADED_QT"))
NO_WORKER_THREAD_INTERNET = bool(os.getenv("RAGDOLL_SINGLE_THREADED_INTERNET"))

log = logging.getLogger("ragdoll")
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


def write_clipboard(text):
    app = QtWidgets.QApplication.instance()
    app.clipboard().setText(text)


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


class FlowLayout(QtWidgets.QLayout):
    """
    """

    def __init__(self, parent=None):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(0, 0, 0, 0)
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(),
                             2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton,
                QtWidgets.QSizePolicy.PushButton,
                QtCore.Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint())
                )

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class OverlayWidget(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent=None):
        super(OverlayWidget, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.new_parent()

    def new_parent(self):
        if self.parent():
            self.parent().installEventFilter(self)
            self.raise_()

    def eventFilter(self, watched, event):
        """
        Args:
            watched (QtCore.QObject):
            event (QtCore.QEvent):

        Returns:
            bool
        """
        if watched == self.parent():
            if event.type() == event.Resize:
                self.resize(event.size())
            elif event.type() == event.ChildAdded:
                self.raise_()
            elif event.type() == event.Move:  # e.g. when QListView updates
                self.raise_()
        return super(OverlayWidget, self).eventFilter(watched, event)

    def event(self, event):
        """
        Args:
            event (QtCore.QEvent):

        Returns:
            bool
        """
        if event.type() == event.ParentAboutToChange:
            if self.parent():
                self.parent().removeEventFilter(self)
        elif event.type() == event.ParentChange:
            self.new_parent()
        return super(OverlayWidget, self).event(event)


class SizeAdjustedStackedWidget(QtWidgets.QStackedWidget):
    SizeIgnored = QtWidgets.QSizePolicy.Ignored
    SizePreferred = QtWidgets.QSizePolicy.Preferred

    def addWidget(self, w):
        w.setSizePolicy(self.SizeIgnored, self.SizeIgnored)
        return super(SizeAdjustedStackedWidget, self).addWidget(w)

    def setCurrentWidget(self, w):
        self.currentWidget().setSizePolicy(self.SizeIgnored, self.SizeIgnored)
        w.setSizePolicy(self.SizePreferred, self.SizePreferred)
        super(SizeAdjustedStackedWidget, self).setCurrentWidget(w)
        self.adjustSize()

    def setCurrentIndex(self, i):
        self.currentWidget().setSizePolicy(self.SizeIgnored, self.SizeIgnored)
        self.widget(i).setSizePolicy(self.SizePreferred, self.SizePreferred)
        super(SizeAdjustedStackedWidget, self).setCurrentIndex(i)
        self.adjustSize()


class SingletonMainWindow(QtWidgets.QMainWindow):
    instance_weak = None
    protected = False  # set to True if only closed on plugin unloaded

    def __init__(self, parent=None):
        super(SingletonMainWindow, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.__class__.instance_weak = weakref.ref(self)
        # For uninstall
        __.widgets[self.__class__.__name__] = self

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)


class Thread(QtCore.QThread):
    result_ready = QtCore.Signal(tuple)

    def __init__(self, func, args=None, kwargs=None, parent=None):
        super(Thread, self).__init__(parent=parent)
        self._func = func
        self._args = args or ()
        self._kwargs = kwargs or {}

    def on_quit(self):
        self.requestInterruption()
        self.wait()

    def run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
        except Exception as e:
            message = "\n{trace}\n{err}".format(
                trace=traceback.format_exc(),
                err=str(e),
            )
            log.critical(message)
        else:
            self.result_ready.emit(result)


class TimelineItem(QtWidgets.QGraphicsItem):
    DateRole = QtCore.Qt.UserRole
    DateListRole = QtCore.Qt.UserRole + 1
    VersionRole = QtCore.Qt.UserRole + 2
    MessageRole = QtCore.Qt.UserRole + 3

    @staticmethod
    def compute_fg(bg):
        return bg.lighter(800) if bg.value() < 200 else bg.darker(800)

    def __init__(self, w, h, r, color, text=None):
        super(TimelineItem, self).__init__()
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.hover_parent = None
        self.hover_children = list()
        self._w = w
        self._h = h
        self._r = r
        self._bg = color
        self._fg = self.compute_fg(color)
        self._text = text
        self._hovered = False
        self._bg_hov = None
        self._fg_hov = None

    def hoverEnterEvent(self, event):
        self._hovered = True
        if self.data(self.MessageRole):
            self.scene().message_set.emit(self.data(self.MessageRole))
        super(TimelineItem, self).hoverEnterEvent(event)

        if self.hover_parent:
            self.hover_parent.set_hovered(True)
        for child in self.hover_children:
            child.set_hovered(True)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        if self.data(self.MessageRole):
            self.scene().message_unset.emit()
        super(TimelineItem, self).hoverLeaveEvent(event)

        if self.hover_parent:
            self.hover_parent.set_hovered(False)
        for child in self.hover_children:
            child.set_hovered(False)

    def mousePressEvent(self, event):
        pass  # reimplement this so the release event can be received

    def mouseReleaseEvent(self, event):
        super(TimelineItem, self).mouseReleaseEvent(event)
        if self.boundingRect().contains(event.pos()):
            ver = self.data(self.VersionRole)
            if ver:
                url = "https://learn.ragdolldynamics.com/releases/" + ver
                webbrowser.open(url)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self._w, self._h)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(self.boundingRect(), self._r, self._r)
        return path

    def paint(self, painter, option, widget=None):
        bg = self._bg_hov if self._hovered else self._bg
        fg = self._fg_hov if self._hovered else self._fg

        painter.setRenderHint(painter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(bg)
        painter.drawPath(self.shape())
        if self._text:
            fr = painter.fontMetrics().boundingRect(self._text)
            fr.moveCenter(self.boundingRect().center().toPoint())
            painter.setPen(fg)
            painter.drawText(fr, self._text)

    def set_message(self, text):
        self.setData(self.MessageRole, text)

    def is_hovered(self):
        return self._hovered

    def set_hovered(self, value):
        self._hovered = value
        self.update()

    def enable_hover(self, bg_color, fg_color=None):
        self.setAcceptHoverEvents(True)
        self._bg_hov = QtGui.QColor(bg_color)
        self._fg_hov = QtGui.QColor(fg_color or "white")


class ProductTimelineGraphicsScene(QtWidgets.QGraphicsScene):
    message_set = QtCore.Signal(str)
    message_unset = QtCore.Signal()


class ProductTimelineGraphicsView(QtWidgets.QGraphicsView):

    def enterEvent(self, event):
        super(ProductTimelineGraphicsView, self).enterEvent(event)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)


class ProductTimelineModel(QtCore.QObject):

    def __init__(self, parent=None):
        super(ProductTimelineModel, self).__init__(parent)
        self.expiry_date = None
        self.current = None
        self.first = None
        self.versions = None
        self.latest_update = None
        self.correction = dict()
        self.max_gap = 7 * 4  # don't visualize release gap over 4 weeks

    def set_data(self, released_versions, current_ver, expiry_date):
        current_ver = datetime(*map(int, current_ver.split(".")))
        released_versions = sorted(released_versions)
        released_dates = [
            datetime(*map(int, v.split("."))) for v in released_versions
            if int(v[:4]) < 2077  # internal dev version
        ]
        # merge release if the distance between them gets too close
        merged_releases = defaultdict(list)
        unit = ProductTimelineBase.DayWidth
        dot_r = ProductTimelineView.DotRadius
        first_date = released_dates[0]
        threshold = dot_r * 6
        index = 0
        previous = 0

        def avoid_gap(_days_after_v0):
            if _days_after_v0 - previous >= self.max_gap:
                offset = _days_after_v0 - previous - self.max_gap
                self.correction[_days_after_v0] = offset

        incidents = [datetime.today(), expiry_date]

        for date in sorted(released_dates + incidents):
            days_after_v0 = (date - first_date).days

            if date not in incidents:
                if previous and unit * (days_after_v0 - previous) > threshold:
                    index += 1
                merged_releases[index].append(date)

            avoid_gap(days_after_v0)
            previous = days_after_v0

            if date < expiry_date:
                self.latest_update = date

        self.expiry_date = expiry_date
        self.current = current_ver
        self.first = first_date
        self.versions = merged_releases


class ProductTimelineBase(QtWidgets.QWidget):
    message_sent = QtCore.Signal(str)

    DayWidth = px(3)
    DayPadding = 45  # how many days before first release and after today

    def __init__(self, parent=None):
        super(ProductTimelineBase, self).__init__(parent)

        scene = ProductTimelineGraphicsScene()
        view = ProductTimelineGraphicsView()

        view.setScene(scene)
        view.setDragMode(view.ScrollHandDrag)
        view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # NOTE
        # The direction of timeline is as follows.
        # | Past <-> Present |
        # And the scrollBar value ramp direction is as follows.
        # | Min <-> Maximum |
        # So by default, when we scroll down mouse wheel, it slides the
        # timeline toward the present.
        # But what we want is opposite, hence we set this to False.
        view.horizontalScrollBar().setInvertedControls(False)

        # signals
        scene.message_set.connect(self.on_item_message_set)
        scene.message_unset.connect(self.on_item_message_unset)

        self.view = view
        self.scene = scene
        self._today = datetime.now()
        self._days = 0
        self._expiry_days = 0
        self._expiry_date = None
        self._expiry_shown = False
        self._view_len = 0
        self._current = None
        self._first = None
        self._versions = None
        self._latest_update = None
        self._correction = None

    def set_data_from_model(self, model):
        """
        Args:
            model (ProductTimelineModel):
        """
        current_ver = model.current
        first_date = model.first
        expiry_date = model.expiry_date

        self._days = self.DayPadding + (self._today - first_date).days
        self._expiry_days = self.DayPadding + (expiry_date - first_date).days
        self._expiry_shown = self._expiry_days - self._days < self.DayPadding
        self._expiry_date = expiry_date
        self._view_len = (self._days + self.DayPadding) * self.DayWidth
        self._current = current_ver
        self._first = first_date
        self._versions = model.versions
        self._latest_update = model.latest_update
        self._correction = model.correction

        self._view_len -= sum(self._correction.values()) * self.DayWidth

    def compute_x(self, date):
        days_after_v0 = (date - self._first).days

        total_offset = 0
        for checkpoint, offset in self._correction.items():
            if days_after_v0 >= checkpoint:
                total_offset += offset
        days_after_v0 -= total_offset

        days_after_v0 += self.DayPadding
        return days_after_v0 * self.DayWidth

    def draw_item(self, x, y, w, h, r, color, text=None, z=0):
        item = TimelineItem(w, h, r, QtGui.QColor(color), text)
        item.setX(x)
        item.setY(y)
        item.setZValue(z)
        self.scene.addItem(item)
        return item

    def on_item_message_set(self, text):
        self.message_sent.emit(text)

    def on_item_message_unset(self):
        self.message_sent.emit("")


class ProductTimelineView(ProductTimelineBase):
    ViewHeight = px(20)
    LineThick = px(5)
    DotRadius = px(5)

    def __init__(self, parent=None):
        super(ProductTimelineView, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor("#5F000000"))  # ARGB
        self.setGraphicsEffect(shadow)
        self.setStyleSheet("border: none; background: transparent;")
        self.setFixedHeight(self.ViewHeight)

    def draw(self):
        self.scene.clear()
        top_left = QtCore.QPoint(0, 0)
        bottom_right = QtCore.QPoint(self._view_len, self.ViewHeight)
        self.scene.setSceneRect(QtCore.QRectF(top_left, bottom_right))

        self.draw_timeline()
        for index, dates in self._versions.items():
            self.draw_highlight(dates)
        if self._expiry_shown:
            it = self.draw_incident(self._expiry_date, 1.2, "#e96868")
            it.set_message("Licence/AUP/Trial expired after: %s"
                           % self._expiry_date.strftime("%b.%d.%Y"))
        it = self.draw_incident(self._today, 0.5, "#dfdfdf")
        it.set_message("Today: %s" % self._today.strftime("%Y %b %d"))

    def draw_timeline(self):
        h = self.LineThick
        r = int(h / 2)
        y = (self.view.height() / 2) - (h / 2)

        if self._expiry_shown:
            x = 0
            w = self.compute_x(self._expiry_date)
            self.draw_item(x=x, y=y, z=1, w=w, h=h, r=r, color="#445442")

            x = w
            w = self._view_len - w
            self.draw_item(x=x, y=y, z=1, w=w, h=h, r=r, color="#967100")
        else:
            x = 0
            w = self._view_len
            self.draw_item(x=x, y=y, z=1, w=w, h=h, r=r, color="#445442")

    def draw_highlight(self, dates):
        color = "#d4ac20" if dates[-1] > self._expiry_date else "#92d453"
        r = self.DotRadius
        x = self.compute_x(dates[0]) - r
        y = (self.view.height() / 2) - r
        w = self.compute_x(dates[-1]) - r - x + (r * 2)
        h = r * 2
        it = self.draw_item(x=x, y=y, z=2, w=w, h=h, r=r, color=color)
        it.setData(it.DateListRole, dates)
        it.enable_hover("#7399ce")

    def draw_incident(self, date, scale, color):
        z = 3 if scale < 1 else 2
        r = self.DotRadius * scale
        x = self.compute_x(date) - r
        y = (self.view.height() / 2) - r
        w = h = r * 2
        it = self.draw_item(x=x, y=y, z=z, w=w, h=h, r=r, color=color)
        it.enable_hover("#7399ce")
        return it


class ProductReleasedView(ProductTimelineBase):
    ViewHeight = px(84)
    ButtonWidth = px(68)
    ButtonHeight = px(18)

    def __init__(self, parent=None):
        super(ProductReleasedView, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        self.setFixedHeight(self.ViewHeight + px(12))  # + scrollbar height
        self.setStyleSheet("""
        background: #202020;
        border: none;
        border-radius: 0;
        border-bottom-right-radius: {radius}px;
        border-bottom-left-radius: {radius}px;
        """.format(radius=px(8)))

    def draw(self):
        self.scene.clear()
        top_left = QtCore.QPoint(0, 0)
        bottom_right = QtCore.QPoint(self._view_len, self.ViewHeight)
        self.scene.setSceneRect(QtCore.QRectF(top_left, bottom_right))

        self.draw_time(self._current, "#8d8d8d")
        self.draw_time(self._expiry_date, "#e96868")

        row_count = int(self.ViewHeight / self.ButtonHeight)
        row_count -= 1  # for footer overlaying
        prev_items = [None] * row_count  # for collision check
        reversed_dates = [
            self._versions[i]
            for i in sorted(self._versions.keys(), reverse=True)
        ]
        for i, dates in enumerate(reversed_dates):
            prev_items = self.draw_releases(reversed(dates), prev_items)

    def draw_releases(self, dates, prev_items):
        last_row = len(prev_items) - 1
        y_base = -(self.ButtonHeight / 2) + px(4)
        gap = px(4)

        def get_rightest_row():
            # get row that has the most clearance for overflowed item
            rx = max(p.x() for p in prev_items)
            return next(i for i, p in enumerate(prev_items) if p.x() == rx)

        for date in dates:
            it = self._draw_button(date, y_base)
            # check collision with previous item in each row
            for row, prev in enumerate(prev_items):
                if prev and it.collidesWithItem(prev):
                    if row != last_row:
                        it.setY(it.y() + gap + self.ButtonHeight)
                    else:
                        rr = get_rightest_row()
                        it.setY(prev_items[rr].y())
                        while it.collidesWithItem(prev_items[rr]):
                            it.setX(it.x() - gap)
                        prev_items[rr] = it
                else:
                    prev_items[row] = it
                    break

        return prev_items

    def _draw_button(self, date, y_base):
        cl = ("#1953be" if date == self._current else
              "#f8d803" if date == self._latest_update else "#101010")
        ver = date.strftime("%Y.%m.%d")
        tx = ver + " "  # a trailing space for better width
        w, h = self.ButtonWidth, self.ButtonHeight
        r = int(h / 2)
        x = self.compute_x(date) - (w / 2)
        y = y_base
        it = self.draw_item(x=x, y=y, z=0, w=w, h=h, r=r, color=cl, text=tx)
        it.setData(it.DateRole, date)
        it.setData(it.VersionRole, ver)
        it.enable_hover("#a4a4a4", "#1c1c1c")
        msg = "Ragdoll version (click to read more) - %s" % ver
        if date == self._current:
            it.set_message("Your current " + msg)
        elif date == self._latest_update:
            it.set_message("Latest " + msg)
        else:
            it.set_message("Previous " + msg)
        return it

    def draw_time(self, date, color):
        x = self.compute_x(date)
        y1 = self.view.mapToScene(0, 0).y() + 2
        y2 = self.ViewHeight - self.ButtonHeight  # for footer
        line = QtCore.QLineF(x, y1, x, y2)

        gradient = QtGui.QLinearGradient()
        gradient.setStart(0, 0)
        gradient.setFinalStop(0, y2 - y1)
        gradient.setColorAt(0.25, color)
        gradient.setColorAt(0.90, QtGui.QColor("transparent"))

        self.scene.addLine(line, QtGui.QPen(QtGui.QBrush(gradient), 1))

    def connect_timeline(self, timeline):
        items = self.scene.items()
        for dot in timeline.scene.items():
            for date in dot.data(TimelineItem.DateListRole) or []:
                for item in items:
                    if item.data(TimelineItem.DateRole) == date:
                        dot.hover_children.append(item)
                        item.hover_parent = dot
                        items.remove(item)
                        break


class ProductTimelineWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ProductTimelineWidget, self).__init__(parent)

        model = ProductTimelineModel()
        widgets = {
            "Timeline": ProductTimelineView(),
            "Released": ProductReleasedView(),
            "Message": QtWidgets.QLabel(),
            "Update": QtWidgets.QPushButton(),
        }
        overlays = {
            "Message": OverlayWidget(parent=widgets["Released"]),
            "Update": OverlayWidget(parent=widgets["Released"]),
        }
        overlays["Update"].setAttribute(
            QtCore.Qt.WA_TransparentForMouseEvents, False)
        # set to False for update button click

        widgets["Message"].setStyleSheet("color: #4a4a4a;")
        widgets["Update"].setFixedHeight(px(20))

        # timeline has shadow fx + transparent bg,
        # so we need another container for transparent gradient bg
        time_container = QtWidgets.QWidget()
        time_container.setStyleSheet("""
        border: none;
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1, stop:0.5 transparent, stop:0.51 #202020);
        """)
        layout = QtWidgets.QVBoxLayout(time_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Timeline"])

        layout = QtWidgets.QVBoxLayout(overlays["Message"])
        layout.setContentsMargins(px(6), 0, 0, px(6))
        layout.addStretch(1)
        layout.addWidget(widgets["Message"], alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout(overlays["Update"])
        layout.setContentsMargins(0, 0, px(6), px(6))
        layout.addStretch(1)
        layout.addWidget(widgets["Update"], alignment=QtCore.Qt.AlignRight)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(time_container)
        layout.addWidget(widgets["Released"])

        # scroll sync
        t_w = widgets["Timeline"]
        r_w = widgets["Released"]
        t_bar = t_w.view.horizontalScrollBar()
        r_bar = r_w.view.horizontalScrollBar()

        t_bar.valueChanged.connect(
            lambda v: r_w.view.horizontalScrollBar().setValue(v))
        r_bar.valueChanged.connect(
            lambda v: t_w.view.horizontalScrollBar().setValue(v))
        r_bar.rangeChanged.connect(
            lambda m, x: t_w.view.horizontalScrollBar().setMaximum(x))

        def cleanup(obj):
            t_w.view.horizontalScrollBar().valueChanged.disconnect()
            r_w.view.horizontalScrollBar().valueChanged.disconnect()
            r_w.view.horizontalScrollBar().rangeChanged.disconnect()

        self.destroyed.connect(cleanup)
        widgets["Timeline"].message_sent.connect(self.on_message_sent)
        widgets["Released"].message_sent.connect(self.on_message_sent)

        def on_clicked():
            webbrowser.open("https://learn.ragdolldynamics.com/download/")
        widgets["Update"].clicked.connect(on_clicked)

        self._model = model
        self._widgets = widgets
        self._overlays = overlays
        # init
        self.on_message_sent("")

    def resizeEvent(self, event):
        super(ProductTimelineWidget, self).resizeEvent(event)
        self._mask_indicator()

    def minimumHeight(self):
        return (
            self._widgets["Timeline"].ViewHeight +
            self._widgets["Released"].ViewHeight
        )

    def on_message_sent(self, text):
        text = text or "Drag to navigate, or scroll with Alt key pressed"
        self._widgets["Message"].setText(text)

    def set_data(self, released_versions, current_ver, expiry_date):
        self._model.set_data(released_versions, current_ver, expiry_date)

        self._widgets["Timeline"].set_data_from_model(self._model)
        self._widgets["Released"].set_data_from_model(self._model)
        self._update_button(self._model)
        # to trigger indicator region masking...
        self.adjustSize()

    def draw(self):
        self._widgets["Timeline"].draw()
        self._widgets["Released"].draw()
        self._widgets["Released"].connect_timeline(self._widgets["Timeline"])
        # slide to present day
        bar = self._widgets["Released"].view.horizontalScrollBar()
        bar.setValue(bar.maximum())

    def _mask_indicator(self):
        # we need to mask out the overlay widget so the underlying timeline
        # widget can receive mouse events that happened outside the button.
        w = self._widgets["Update"]
        over = self._overlays["Update"]
        p = w.mapTo(over, w.rect().topLeft())
        over.setMask(QtCore.QRect(p.x(), p.y(), w.width(), w.height()))

    def _update_button(self, model):
        btn = self._widgets["Update"]
        up_to_date = model.latest_update == model.current
        btn.setText(
            "Current Version: %s" % model.current.strftime("%Y.%m.%d")
            if up_to_date else "Download Latest"
        )
        fg = "#ffffff" if up_to_date else "#000000"
        bg = "#1953be" if up_to_date else "#f8d803"

        if not up_to_date:
            icon = ui._resource("icons", "download_black.png")
            icon = QtGui.QIcon(icon)
            btn.setIcon(icon)
        else:
            btn.setIcon(QtGui.QIcon())

        bgc = QtGui.QColor(bg)
        btn.setStyleSheet(
            """QPushButton {
                padding: %dpx %dpx;
                border-radius: %dpx;
                background: %s; color: %s; }
            QPushButton:hover { background: %s; }
            QPushButton:pressed { background: %s; }
            """ % (px(2), px(8), px(9.5), bg, fg,
                   bgc.lighter().name(), bgc.darker().name())
        )
        btn.setEnabled(not up_to_date)


class ProductStatus(object):

    def __init__(self):
        self._data = dict()

    @property
    def data(self):
        return self._data.copy()

    @data.setter
    def data(self, data):
        self._data = data.copy()
        # In case any licencing issue,
        # run log.setLevel(logging.DEBUG) to print out
        log.debug("Licencing data:")
        for k, v in self._data.items():
            log.debug("|    %s: %s" % (k, v))

    def name(self):
        name = self.data["product"]
        if name == "unknown" and self.is_expired():
            name = "complete"

        return {
            "enterprise": "Unlimited",
            "educational": "Educational",
            "freelancer": "Freelancer",
            "headless": "Batch",
            "personal": "Personal",
            "complete": "Complete",
            "trial": "Trial",
        }.get(name) or name

    def current_version(self):
        return self.data["currentVersion"]

    def key(self):
        if self.data["key"] == "HIDDEN":
            return ""  # this happens when RAGDOLL_FLOATING is set
        else:
            return self.data["key"]

    def is_non_commercial(self):
        return self.data["isNonCommercial"]

    def is_floating(self):
        return self.data["isFloating"] and constants.RAGDOLL_FLOATING

    def has_lease(self):
        return self.data["hasLease"]

    def licence_server(self):
        return self.data["ip"], self.data["port"]

    def is_activated(self):
        return (
            (self.key() and self.data["isActivated"]) or
            (self.key() and self.is_expired())
        )

    def is_perpetual(self):
        return (
            not self.data["expires"] and
            not self.is_trial()
        )

    def is_subscription(self):
        return not self.is_perpetual() and not self.is_trial()

    def is_trial(self):
        return self.data["isTrial"] or self.data["product"] == "trial"

    def is_trial_errored(self):
        return self.is_trial() and self.data["trialError"] != 0

    def is_expired(self):
        if self.is_trial():
            return self.data["trialDays"] == 0
        else:
            if self.data["expires"]:
                # The exact way how internal licencing module computed
                dt = self.expiry_date()
                expiry_date = date_.fromordinal(dt.toordinal())
                return expiry_date < date_.today()
            else:
                return False

    def is_updatable(self):
        if self.is_trial() or self.is_subscription():
            return not self.is_expired()
        else:
            return self.aup_date() > datetime.now()

    def expiry_date(self):
        if self.is_trial():
            return datetime.now() + timedelta(days=self.data["trialDays"])
        else:
            if self.data["expires"]:
                return datetime.strptime(
                    self.data["expiry"], "%Y-%m-%d %H:%M:%S")
            else:
                return None  # perpetual

    def aup_date(self):
        if self.is_trial():
            return None
        else:
            try:
                return datetime.strptime(
                    self.data["annualUpgradeProgram"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Sometimes we get invalid date string for reasons, e.g.
                # licence changed without plugin reload, or floating
                # server is not available. Here we just return present
                # time as expired to indicate something went wrong.
                return datetime.now()

    def trial_error_msg(self):
        error = self.data["trialError"]

        if error == 0:
            return ""

        elif error == 4:
            return "Ragdoll requires internet to start trial."

        else:
            return "Ragdoll failed to start trial: Error %d" % error


class InternetRequestHandler(object):
    """A class for processing internet connection required requests

    All request object should be an instance of `RequestBaseCls` subclass
    and submit by calling `submit()`.

    After submission, call `process()` to run all requests. All request
    function will run in worker thread, unless env var
    `RAGDOLL_SINGLE_THREADED_INTERNET` is set.

    Finally, call `fetch()` to pass the results to callbacks. If the job
    is still running, then the results will be passed once done.

    If env var `RAGDOLL_SKIP_UPDATE_CHECK` is set, no internet connection
    should be made and `RequestBaseCls.default()` will be called instead
    even if the internet is actually available.

    IMPORTANT:
        Remember to check the request receiver, e.g. Qt widgets, is still
        alive or not when the callback is being called.

    """

    def __init__(self):
        self._requests = set()
        self._workers = weakref.WeakKeyDictionary()
        self._promise = weakref.WeakSet()

    def submit(self, request_obj):
        assert isinstance(request_obj, RequestBaseCls), (
            "Must be an instance of 'RequestBaseCls' subclass."
        )
        self._requests.add(request_obj)

    def fetch(self):
        for request_obj in self._requests:
            worker = self._workers.get(request_obj)

            if worker and hasattr(worker, "cache"):
                # Already completed.
                request_obj.callback(worker.cache)

            elif not NO_WORKER_THREAD_INTERNET:
                self._promise.add(request_obj)

            else:  # Should not happen in single thread mode.
                log.error("Internal Error: Failed to complete request.")

    def process(self):
        def _process():
            log.debug("Processing internet requests...")
            if self._preflight():
                self._run()
            else:
                self._default()

        if NO_WORKER_THREAD_INTERNET:
            _process()
        else:  # Run _preflight() in thread
            threading.Thread(target=_process).start()

    def _preflight(self):
        return (not NO_INTERNET
                and self.__is_ssl_cert_file_exists()
                and not self.__has_open_ssl_bug())

    def _run(self):
        if NO_WORKER_THREAD_INTERNET:
            for request_obj in self._requests:
                result = request_obj.run()

                worker = type("Worker", (), dict(cache=result))()
                self._workers[request_obj] = worker

        else:
            for request_obj in self._requests:

                worker = threading.Thread()
                self._workers[request_obj] = worker

                def run(request_obj_, worker_):
                    setattr(worker_, "cache", request_obj_.run())
                    self._on_promised(request_obj_)

                worker.run = partial(run, request_obj, worker)
                worker.start()

        log.debug("Internet requests completed.")

    def _default(self):
        # The `default()` runs without internet and should be fast, so
        # no worker thread for each of them.
        for request_obj in self._requests:
            result = request_obj.default()

            worker = type("Worker", (), dict(cache=result))()
            self._workers[request_obj] = worker
            self._on_promised(request_obj)

        log.debug("Internet blocked, local resource used.")

    def _on_promised(self, request_obj):
        if request_obj in self._promise:
            worker = self._workers.get(request_obj)
            if worker and hasattr(worker, "cache"):
                self._promise.remove(request_obj)
                request_obj.callback(worker.cache)

    def __has_open_ssl_bug(self):
        """Return True if OpenSSL bug found
        https://support.foundry.com/hc/en-us/articles/360012750300-Q100573
        """
        if os.name != "nt":
            return False

        try:
            OPENSSL_VERSION_INFO = __import__("ssl").OPENSSL_VERSION_INFO
        except ImportError:
            return True  # no ssl, proceed as bugged and without internet.

        has_ssl_bug = (1, 0, 2, 7) <= OPENSSL_VERSION_INFO < (1, 0, 2, 9)
        has_workaround = os.getenv("OPENSSL_ia32cap") == "~0x200000200000000"
        cpu_ident = os.getenv("PROCESSOR_IDENTIFIER", "")
        is_intel = "GenuineIntel" in cpu_ident

        if not (is_intel and has_ssl_bug and not has_workaround):
            return False

        # a way to bypass subprocess checking.
        manual_over = os.getenv("RAGDOLL_OVER_OPENSSL_CHECK", "").lower()
        if manual_over.isdigit():
            return int(manual_over)
        elif manual_over in ["y", "yes"]:
            return False  # yes, proceed as no-bug.
        elif manual_over in ["n", "no"]:
            return True  # no, proceed as bugged and without internet.

        exe = sys.executable
        if exe.endswith("maya.exe"):
            exe = os.path.join(os.path.dirname(exe), "mayapy.exe")

        cmd = "import ssl;ssl.get_server_certificate(('www.google.com',443))"
        p = subprocess.Popen(
            [exe, "-c", cmd],
            stdout=subprocess.PIPE,
            creationflags=0x08000000  # no window
        )
        _, _ = p.communicate()
        unsafe = p.wait() != 0
        if unsafe:
            log.debug("OpenSSL connection issue detected, "
                      "please refer to this article for detail: "
                      "https://support.foundry.com/hc/en-us/articles/"
                      "360012750300-Q100573")
        return unsafe

    def __is_ssl_cert_file_exists(self):
        ssl_cert_file = os.getenv("SSL_CERT_FILE")
        if ssl_cert_file:
            if os.path.isfile(ssl_cert_file):
                return True
            else:
                log.debug('Invalid SSL certificate file: Environment variable'
                          '"SSL_CERT_FILE" is set but file path not exists: '
                          '%s' % ssl_cert_file)
                return False
        else:
            return True  # Env not set, take it as valid setup


def _ping(url):
    try:
        response = request.urlopen(url)
        return response.code == 200
    except Exception as e:
        log.debug(e)
        return False


class RequestBaseCls(object):
    """Base class of internet request
    Args:
        callback (func): A function that gets called by the
            `InternetRequestHandler.fetch()` when the job function
            is finished. The argument(s) of the callback will be the
            return value(s) of the job function, `run()` or `default()`.
    """

    def __init__(self, callback):
        self.callback = callback

    def run(self):
        """The job function that runs on internet"""
        raise NotImplementedError

    def default(self):
        """The other job function when there is no internet, as fallback"""
        raise NotImplementedError


class RequestVersionHistory(RequestBaseCls):

    def run(self):
        released = []

        def parsed_versions(lines):
            p = r'.*<a href="/releases/(\d{4}\.\d{2}\.\d{2}).*">'
            p = re.compile(p.encode())
            return [
                matched.group(1).decode()
                for matched in [p.match(ln) for ln in lines] if matched
            ]

        url = RAGDOLL_DYNAMICS_RELEASES_URL
        try:
            response = request.urlopen(url)
            if response.code == 200:
                released = parsed_versions(response.readlines())
            else:
                raise Exception("%s returned: %d" % (url, response.code))

        except Exception as e:
            log.debug(e)
        else:
            log.debug("Release history fetched from %s" % url)

        return released or self.default()

    def default(self):
        released = []

        root = os.path.dirname(constants.__file__)
        cache = os.path.join(root, "resources", "versioninfo.json")
        if os.path.isfile(cache):
            with open(cache) as f:
                released = json.load(f)
                log.debug("Release history loaded from %s" % cache)

        return released


class RequestRagdollWebsite(RequestBaseCls):
    """Check the connectivity with Ragdoll website

    The result will ONLY be used as a condition for displaying update
    checking ability on GUI. The result will NOT be used as a condition
    of any kind of operation.

    """

    def run(self):
        return _ping(RAGDOLL_DYNAMICS_VERSIONS_URL)  # type: bool

    def default(self):
        # This fallback function gets used either because of OpenSSL bug or
        # env var `RAGDOLL_SKIP_UPDATE_CHECK` is set.
        # (see `InternetRequestHandler._preflight()`)
        # We don't want to bother users about this on GUI if above case met,
        # so just returning `True` here.
        return True


def text_to_color(text):
    """Hashing arbitrary string into QColor
    Same string can be hashed to same color in different Python versions
    """
    seed = text.encode("utf-8")
    code = int(hashlib.sha1(seed).hexdigest(), base=16)
    return QtGui.QColor.fromHsv(
        (code & 0xFF0000) >> 16,
        (code & 0x00FF00) >> 8,
        180,
    ).name()


class AssetLibrary(object):

    def __init__(self):
        self._status = dict()
        self._stop = threading.Event()
        self._queue = queue.Queue()
        self._cache = []
        self._worker = None

    def get_user_path(self):
        return options.read("extraAssets")

    def set_user_path(self, path):
        if not any(self._iter_rag_files(path)):
            path = ""
        options.write("extraAssets", path)

    def search_paths(self):
        paths = [ui._resource("assets")]
        paths += os.getenv("RAGDOLL_ASSETS", "").split(os.pathsep)
        paths += [self.get_user_path()]
        paths = list(filter(None, paths))
        return reversed(paths)

    def attach_consumer(self, model):
        model.attach_library(self._queue)

    def reload(self):
        self.stop()
        self._cache = []
        self._stop.clear()
        self._status.clear()

        if NO_WORKER_THREAD_QT:
            self._produce()
        else:
            self._worker = threading.Thread(target=self._produce)
            self._worker.start()

    def stop(self):
        self._stop.set()
        if self._worker is not None:
            self._worker.join()
        self._queue.queue.clear()

    def terminate(self):
        self.stop()
        self._queue.put({"type": "terminate"})

    def rewind(self):
        produced = self._cache and self._cache[-1]["type"] == "finish"
        if produced and self._queue.empty():
            for job in self._cache:
                self._queue.put(job)

    def _send_job(self, type_, payload):
        job = {"type": type_, "payload": payload}
        self._queue.put(job)
        self._cache.append(job)

    def _produce(self):
        rag_files = list()
        self._send_job("start", None)

        for lib_path in self.search_paths():
            for rag_path in self._iter_rag_files(lib_path):
                if self._stop.is_set():
                    return
                _stat = os.stat(rag_path)
                mtime = _stat.st_mtime
                data = {"path": rag_path, "_mtime": mtime}
                self._send_job("create", data)
                # group by size (5MB) and then sort by mtime
                fsize = int(_stat.st_size / 1048576 / 5)
                rag_files.append((-fsize, mtime, rag_path))

        # sort processing order by file size and modified time
        rag_files.sort(reverse=True)

        for _, mtime, rag_path in rag_files:
            if self._stop.is_set():
                return
            log.debug("Loading: %s" % rag_path)
            data = self._load_rag_file(rag_path) or {}
            data = self._refine_rag_data(rag_path, data)
            self._send_job("update", data)

        self._send_job("finish", None)

        # report
        total = 0
        valid = {k: v for k, v in self._status.items() if v}
        for p, count in valid.items():
            log.debug("%d assets were found from: %s" % (count, p))
            total += count
        log.debug("Total: %d asset from %d valid dir." % (total, len(valid)))

    def _iter_rag_files(self, lib_path):
        status = self._status

        if not os.path.isdir(lib_path):
            status[lib_path] = None
            return

        status[lib_path] = 0
        for item in os.listdir(lib_path):
            path = os.path.join(lib_path, item)

            if item.endswith(".rag") and os.path.isfile(path):
                status[lib_path] += 1
                yield path

    def _load_rag_file(self, file_path):
        try:
            return self._load_rag_file_fast(file_path)
        except Exception as e:
            log.debug(e)
            with open(file_path) as _f:
                try:
                    rag = json.load(_f)
                except ValueError as e:
                    log.debug(e)
                    return None
            return rag.get("ui") or {}

    def _load_rag_file_fast(self, file_path):
        # File read and json.load doesn't release GIL until job done,
        #   so if the file is big enough, everyone has to wait for it.
        #
        # To work around this, we take only what we need from the file,
        #   which is the "ui" field. So we read the file backward and
        #   find the keyword and ignore the rest.
        #
        # See link below for detail (it's a work journal)
        # https://gitlab.ragdolldynamics.com/-/snippets/302
        #
        lines = []
        for line in reverse_readline(file_path):
            lines.append(line)
            if b'"ui": {' in line:
                lines.append(b"{")
                break
        lines.reverse()
        try:
            rag = json.loads(b"\n".join(lines))
        except ValueError as e:
            log.debug(e)
            return None
        return rag.get("ui") or {}

    def _refine_rag_data(self, file_path, data):
        lib_path, fname = os.path.split(file_path)
        fname = fname.rsplit(".", 1)[0]
        _d = {
            "name": fname,
            "video": fname + ".webm",
            "thumbnail": "",
            "tags": {},
        }
        _d.update(data)

        poster = ui.base64_to_pixmap(_d["thumbnail"].encode("ascii"))
        if not poster.isNull():
            poster = poster.scaled(
                px(217), px(122),
                QtCore.Qt.KeepAspectRatioByExpanding,
                QtCore.Qt.SmoothTransformation
            )

        if isinstance(_d["tags"], dict):
            # A dict of name and color pairs.
            tags = _d["tags"]

        elif isinstance(_d["tags"], list):
            # A list of tag names. Hashing color from name.
            tags = {tag: text_to_color(tag) for tag in set(_d["tags"])}

        else:
            log.debug('Invalid value type: "tags" field should be a list of'
                      'tag names, or a dict mapping tag name and color.')
            tags = {}

        _d.update({
            "path": file_path,
            "thumbnail": poster,
            "tags": tags,
        })

        return _d


def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order
    https://stackoverflow.com/a/23646049/4145300
    """
    with open(filename, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        segment = None
        offset = 0
        file_size = remaining_size = fh.tell()

        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split(b"\n")
            # The first line of the buffer is probably not a complete line,
            # so we'll save it and append it to the last line of the next
            # buffer we read.
            if segment is not None:
                # If the previous chunk starts right from the beginning of
                # line do not concat the segment to the last line of new
                # chunk. Instead, yield the segment first
                if buffer[-1] != b"\n":
                    lines[-1] += segment
                else:
                    yield segment

            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]

        # Don't yield None if the file was empty
        if segment is not None:
            yield segment
