
import re
import logging
import traceback
import shiboken2
import webbrowser
from datetime import datetime, timedelta
from collections import defaultdict
from PySide2 import QtCore, QtWidgets, QtGui
from maya.OpenMayaUI import MQtUtil

try:
    from urllib import request
except ImportError:
    import urllib as request  # py2

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


class Thread(QtCore.QThread):
    result_ready = QtCore.Signal(tuple)

    def __init__(self, func, parent=None):
        super(Thread, self).__init__(parent=parent)
        self._func = func
        self._args = None
        self._kwargs = None

    def on_quit(self):
        self.requestInterruption()
        self.wait()

    def start(self,
              args=None,
              kwargs=None,
              priority=QtCore.QThread.InheritPriority):
        self._args = args or ()
        self._kwargs = kwargs or {}
        super(Thread, self).start(priority)

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

    def __init__(self, w, h, r, color, text=None):
        super(TimelineItem, self).__init__()
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.hover_parent = None
        self.hover_children = list()
        self._w = w
        self._h = h
        self._r = r
        self._color = color
        self._text = text
        self._hovered = False
        self._color_hov = None
        self._text_hov = None

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
        bg = self._color_hov if self._hovered else self._color
        fg = self._text_hov if self._hovered else self._color.lighter(800)

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
        self._color_hov = QtGui.QColor(bg_color)
        self._text_hov = QtGui.QColor(fg_color or "white")


class ProductTimelineGraphicsScene(QtWidgets.QGraphicsScene):
    message_set = QtCore.Signal(str)
    message_unset = QtCore.Signal()


class ProductTimelineGraphicsView(QtWidgets.QGraphicsView):

    def enterEvent(self, event):
        super(ProductTimelineGraphicsView, self).enterEvent(event)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)


class ProductTimelineBase(QtWidgets.QWidget):
    message_sent = QtCore.Signal(str)

    DayWidth = px(3)
    DayPadding = 45

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

    def set_data(self, released_versions, current_ver, expiry_date):
        current_ver = datetime(*map(int, current_ver.split(".")))
        released_versions = sorted(released_versions)
        released_dates = [
            datetime(*map(int, v.split("."))) for v in released_versions
        ]
        # merge release if the distance between them gets too close
        merged_releases = defaultdict(list)
        unit = ProductTimelineBase.DayWidth
        dot_r = ProductTimelineView.DotRadius
        first_date = released_dates[0]
        threshold = dot_r * 6
        index = 0
        previous = 0
        for date in released_dates:
            days = (date - first_date).days
            if previous and unit * (days - previous) > threshold:
                index += 1
            merged_releases[index].append(date)
            previous = days

            if date < expiry_date:
                self._latest_update = date

        self._days = self.DayPadding + (self._today - first_date).days
        self._expiry_days = self.DayPadding + (expiry_date - first_date).days
        self._expiry_shown = self._expiry_days - self._days < self.DayPadding
        self._expiry_date = expiry_date
        self._view_len = (self._days + self.DayPadding) * self.DayWidth
        self._current = current_ver
        self._first = first_date
        self._versions = merged_releases

    def compute_x(self, date):
        days_after_v0 = self.DayPadding + (date - self._first).days
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
            it = self.draw_incident(self._expiry_date, 2 / 3, "#e96868")
            it.set_message("Licence/AUP/Trial expired after: %s"
                           % self._expiry_date.strftime("%b.%d.%Y"))
        it = self.draw_incident(self._today, 1 / 2, "#dfdfdf")
        it.set_message("Today: %s" % self._today.strftime("%b.%d.%Y"))

    def draw_timeline(self):
        h = self.LineThick
        r = int(h / 2)
        y = (self.view.height() / 2) - (h / 2)

        if self._expiry_shown:
            x = 0
            w = self._expiry_days * self.DayWidth
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
    ViewHeight = px(80)
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
        gap = px(2)

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
        cl = ("#344527" if date == self._current else
              "#101010" if date != self._latest_update else "#1953be")
        tx = date.strftime("%Y.%m.%d ")
        w, h = self.ButtonWidth, self.ButtonHeight
        r = int(h / 2)
        x = self.compute_x(date) - (w / 2)
        y = y_base
        it = self.draw_item(x=x, y=y, z=0, w=w, h=h, r=r, color=cl, text=tx)
        it.setData(it.DateRole, date)
        it.setData(it.VersionRole, tx.strip())
        it.enable_hover("#a4a4a4", "#1c1c1c")
        if date == self._current:
            it.set_message("Current Ragdoll version.")
        elif date == self._latest_update:
            it.set_message("Latest updatable Ragdoll version. Go get it!")
        else:
            it.set_message("Old Ragdoll release, click to open release note "
                           "in web browser.")
        return it

    def draw_time(self, date, color):
        x = self.compute_x(date)
        y1 = self.view.mapToScene(0, 0).y() + 2
        y2 = self.ViewHeight - self.ButtonHeight  # for footer
        line = QtCore.QLineF(x, y1, x, y2)
        self.scene.addLine(line, QtGui.QPen(QtGui.QColor(color)))

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


class ProductTimelineFooter(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ProductTimelineFooter, self).__init__(parent)

        widgets = {
            "Message": QtWidgets.QLabel(),
            "Version": QtWidgets.QLabel(),
        }

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Message"], stretch=1)
        layout.addWidget(widgets["Version"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        widgets["Message"].setStyleSheet("color: #4a4a4a;")
        widgets["Version"].setStyleSheet("color: #8b8b8b;")

        self._widgets = widgets
        self.set_message("")

    def set_message(self, text):
        if text:
            self._widgets["Message"].setText(text)
        else:
            self._widgets["Message"].setText(
                "Drag, or scroll with Alt key pressed to navigate.")

    def set_version(self, ver_str):
        self._widgets["Version"].setText("Current Version: %s" % ver_str)


class ProductTimelineWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ProductTimelineWidget, self).__init__(parent)

        widgets = {
            "Timeline": ProductTimelineView(),
            "Released": ProductReleasedView(),
            "Footer": ProductTimelineFooter(),
        }

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

        overlay = OverlayWidget(parent=widgets["Released"])  # for overlay
        layout = QtWidgets.QVBoxLayout(overlay)
        layout.setContentsMargins(px(12), 0, px(12), px(4))
        layout.addStretch(1)  # for overlay
        layout.addWidget(widgets["Footer"])

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
        widgets["Timeline"].message_sent.connect(widgets["Footer"].set_message)
        widgets["Released"].message_sent.connect(widgets["Footer"].set_message)

        self._widgets = widgets

    def minimumHeight(self):
        return (
            self._widgets["Timeline"].ViewHeight
            + self._widgets["Released"].ViewHeight
        )

    def set_data(self, released_versions, current_ver, expiry_date):
        _args = released_versions, current_ver, expiry_date
        self._widgets["Timeline"].set_data(*_args)
        self._widgets["Released"].set_data(*_args)
        self._widgets["Footer"].set_version(current_ver)

    def draw(self):
        self._widgets["Timeline"].draw()
        self._widgets["Released"].draw()
        self._widgets["Released"].connect_timeline(self._widgets["Timeline"])
        # slide to present day
        bar = self._widgets["Released"].view.horizontalScrollBar()
        bar.setValue(bar.maximum())


class ProductStatus(object):

    def __init__(self):
        self._data = dict()
        self._conn = dict()
        self._released = None

    @property
    def data(self):
        return self._data.copy()

    @data.setter
    def data(self, data):
        self._data = data.copy()

    def name(self):
        name = self.data["product"]
        if name == "unknown" and self.is_expired():
            name = "complete"

        return {
            "enterprise": "Unlimited",
            "educational": "Educational",
            "freelance": "Freelance",
            "headless": "Batch",
            "personal": "Personal",
            "complete": "Complete",
            "trial": "Trial",
        }.get(name) or name

    def current_version(self):
        return self.data["currentVersion"]

    def key(self):
        return self.data["key"]

    def is_non_commercial(self):
        return self.data["isNonCommercial"]

    def is_floating(self):
        return self.data["isFloating"]

    def has_lease(self):
        return self.data["hasLease"]

    def licence_server(self):
        return self.data["ip"], self.data["port"]

    def is_activated(self):
        return (
            self.data["isActivated"]
            or (self.data["key"] and self.is_expired())
        )

    def is_perpetual(self):
        return (
            not self.data["expires"]
            and not self.is_trial()
        )

    def is_subscription(self):
        return not self.is_perpetual() and not self.is_trial()

    def is_trial(self):
        return self.data["isTrial"] or self.data["product"] == "trial"

    def is_expired(self):
        if self.is_trial():
            return self.data["trialDays"] < 1
        else:
            if self.data["expires"]:
                return self.data["expiryDays"] < 1
            else:
                return False

    def is_updatable(self):
        if self.is_trial() or self.is_subscription():
            return not self.is_expired()
        else:
            return self.aup_date() > datetime.now()

    def start_date(self):
        if self.is_trial():
            return datetime.now() - timedelta(days=30 - self.data["trialDays"])
        else:
            aup = self.aup_date()
            return aup.replace(year=aup.year - 1)

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
            return datetime.strptime(
                self.data["annualUpgradeProgram"], "%Y-%m-%d %H:%M:%S")

    def release_history(self, refresh=False):
        if not refresh and self._released is not None:
            return self._released

        if self.has_ragdoll():
            url = "https://learn.ragdolldynamics.com/news"
            with request.urlopen(url) as r:
                if r.code == 200:
                    self._released = list(
                        self._iter_parsed_versions(r.readlines())
                    )
                else:
                    self._released = []

            return self._released[:]
        else:
            return []
            # TODO: read history from distribution cache for offline users

    def has_ragdoll(self, refresh=False):
        return self._ping("https://ragdolldynamics.com/version", refresh)

    def has_wyday(self, refresh=False):
        return self._ping("https://wyday.com", refresh)

    def _iter_parsed_versions(self, lines):
        pattern = re.compile(
            rb'.*<a href="/releases/(\d{4}\.\d{2}\.\d{2}).*">'
        )
        for line in lines:
            matched = pattern.match(line)
            if matched:
                yield matched.group(1).decode()

    def _ping(self, url, refresh):
        status = self._conn.get(url)
        if not refresh and status is not None:
            return status

        with request.urlopen(url) as r:
            self._conn[url] = r.code == 200

        return self._conn[url]
