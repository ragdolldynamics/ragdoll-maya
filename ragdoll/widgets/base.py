
import logging
import traceback
import shiboken2
import webbrowser
from functools import partial
from datetime import datetime
from collections import defaultdict
from PySide2 import QtCore, QtWidgets, QtGui
from maya.OpenMayaUI import MQtUtil

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


class TimelineInterface(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(TimelineInterface, self).__init__(parent=parent)

        self._dot_radius = 8
        self._inner_radius = 3
        self._time_frame = 0
        self._remains = 0
        self._date_start = None
        self._date_end = None
        self._milestone = dict()
        self._stone_dict = defaultdict(list)
        self._rect_list = list()  # type: list[QtCore.QRect]
        self._sect_list = list()  # type: list[QtCore.QRect]
        self._sect_name = list()  # type: list[str]
        self._cur_str = ""
        self._cur_days = 0

        self.min_width = 200
        self.min_height = int(self._dot_radius * 3.5)

    def minimumSizeHint(self):
        return QtCore.QSize(self.min_width, self.min_height)

    def mouseMoveEvent(self, event):
        self.update()

    def paintEvent(self, event):
        self.draw_timeline()

    def set_data(self, data):
        self._milestone = data["versions"]
        self._time_frame = (data["end"] - data["start"]).days + 1
        self._remains = (data["end"] - datetime.now()).days + 1
        self._date_start = data["start"]
        self._date_end = data["end"]
        self._cur_days, self._cur_str = data["current"] or (0, "")
        self.update()

    def draw_timeline(self):
        if not self._time_frame:
            return

        self._rect_list.clear()
        self._sect_list.clear()
        self._stone_dict.clear()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        cursor = self.mapFromGlobal(QtGui.QCursor.pos())

        width, height = self.size().toTuple()
        line_pos = int(height / 2)
        unit = width / self._time_frame
        eta = int(unit * self._remains)
        dot_r = self._dot_radius
        _r = self._inner_radius
        _thick = _r * 2

        fg_color = QtGui.QColor("#568c50")
        bg_color = QtGui.QColor.fromHsv(
            fg_color.hue(),
            int(fg_color.saturation() * 0.5),
            int(fg_color.value() * 0.6),
        )
        dot_color = QtGui.QColor("#d2d2d2")
        latest_color = QtGui.QColor("magenta")

        # timeline base
        #
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(bg_color))
        rect = QtCore.QRect(0, line_pos - dot_r, width, dot_r * 2)
        painter.drawRoundedRect(rect, dot_r, dot_r)
        painter.restore()

        # remaining time
        #
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(fg_color))
        rect = QtCore.QRect(width - eta, line_pos - _r, eta - _thick, _thick)
        painter.drawRoundedRect(rect, _r, _r)
        painter.restore()

        # merge milestones if the distance between them gets too close
        #
        index = 0
        last = 0
        for stone in sorted(self._milestone.keys()):
            if last and unit * (stone - last) > dot_r * 2:
                index += 1
            self._stone_dict[index].append(stone)
            last = stone

        # draw milestones
        #
        for stones in self._stone_dict.values():
            painter.save()

            if len(stones) > 1:
                p1 = QtCore.QPoint(int(unit * stones[0]), line_pos)
                p2 = QtCore.QPoint(int(unit * stones[-1]), line_pos)

                _offset = QtCore.QPoint(_r, _r)
                rect = QtCore.QRect(p1 - _offset, p2 + _offset)

                _offset = QtCore.QPoint(dot_r, dot_r)
                bbox = QtCore.QRect(p1 - _offset, p2 + _offset)
            else:
                p1 = QtCore.QPoint(int(unit * stones[0]), line_pos)
                _offset = QtCore.QPoint(_r, _r)
                rect = QtCore.QRect(p1 - _offset, p1 + _offset)

                _offset = QtCore.QPoint(dot_r, dot_r)
                bbox = QtCore.QRect(p1 - _offset, p1 + _offset)

            if bbox.contains(cursor):
                painter.setPen(dot_color)
                painter.setBrush(QtGui.QBrush(dot_color))
                painter.drawRoundedRect(rect, _r, _r)
            elif last in stones:
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(latest_color))
                painter.drawRoundedRect(rect, _r, _r)
            else:
                painter.setPen(QtCore.Qt.NoPen)
                painter.setBrush(QtGui.QBrush(bg_color.darker(130)))
                painter.drawRoundedRect(rect, _r, _r)

            if self._cur_days in stones:
                painter.setPen(dot_color)
                painter.setBrush(QtCore.Qt.NoBrush)
                painter.drawRoundedRect(bbox, dot_r, dot_r)

            painter.restore()
            self._rect_list.append(bbox)

        # chop timeline into sections
        #
        if self._time_frame <= 35:
            # Monthly Subscription
            pass
        else:
            # Yearly AUP
            step = self._date_start.replace(day=1)
            while step < self._date_end:
                try:
                    next_month = step.replace(month=step.month + 1)
                except ValueError:
                    next_month = step.replace(year=step.year + 1, month=1)

                if step <= self._date_start:
                    # first section
                    days = (next_month - self._date_start).days
                    dot_left = QtCore.QPoint(0, line_pos)
                    dot_right = QtCore.QPoint(int(unit * days), line_pos)
                    rect = QtCore.QRect(
                        dot_left.x(),
                        dot_left.y() - dot_r,
                        dot_right.x() - dot_left.x(),
                        dot_r * 2
                    )
                elif next_month >= self._date_end:
                    # last section
                    days = (step - self._date_start).days
                    dot_left = QtCore.QPoint(int(unit * days), line_pos)
                    dot_right = QtCore.QPoint(width, line_pos)
                    rect = QtCore.QRect(
                        dot_left.x(),
                        dot_left.y() - dot_r,
                        dot_right.x() - dot_left.x(),
                        dot_r * 2
                    )
                else:
                    days = (step - self._date_start).days
                    dot_left = QtCore.QPoint(int(unit * days), line_pos)
                    days = (next_month - self._date_start).days
                    dot_right = QtCore.QPoint(int(unit * days), line_pos)
                    rect = QtCore.QRect(
                        dot_left.x(),
                        dot_left.y() - dot_r,
                        dot_right.x() - dot_left.x(),
                        dot_r * 2
                    )

                if rect.contains(cursor):
                    painter.save()
                    painter.setPen(fg_color)
                    offset = QtCore.QPoint(0, -px(2))
                    p1 = rect.topLeft() + offset
                    p2 = rect.topRight() + offset
                    painter.drawLine(p1, p2)
                    painter.restore()

                self._sect_list.append(rect)
                self._sect_name.append(step.strftime("%Y.%b"))
                step = next_month


class TimelineMenu(QtWidgets.QMenu):
    mouse_released = QtCore.Signal(QtGui.QMouseEvent)
    mouse_deviated = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, parent=None):
        super(TimelineMenu, self).__init__(parent=parent)
        self._bbox = None

    def show_upward(self, anchor, offset_y):
        self.show()
        rect = self.rect()
        anchor.setX(anchor.x() - int(rect.width() / 2))
        anchor.setY(anchor.y() - rect.height() - offset_y)
        self.move(anchor)

        rect = self.rect()
        self._bbox = QtCore.QRect(
            rect.topLeft(),
            QtCore.QPoint(
                rect.bottomRight().x(),
                rect.bottomRight().y() + offset_y,
            ),
        )

    def mouseReleaseEvent(self, event):
        super(TimelineMenu, self).mouseReleaseEvent(event)
        self.mouse_released.emit(event)

    def mouseMoveEvent(self, event):
        if (self._bbox or self.rect()).contains(event.pos()):
            super(TimelineMenu, self).mouseMoveEvent(event)
        else:
            self.mouse_deviated.emit(event)


class TimelineWidget(TimelineInterface):

    def __init__(self, parent=None):
        super(TimelineWidget, self).__init__(parent=parent)
        self.setMouseTracking(True)
        self.__menu = None
        self.__index = None
        self.__mouse_pressed = False

    def mousePressEvent(self, event):
        self.__mouse_pressed = True
        index = self.get_hovered_index(event)
        if index is not None:
            self.show_menu(index)
        self.grabMouse()

    def mouseReleaseEvent(self, event):
        self.__mouse_pressed = False
        self.close_menu()
        self.releaseMouse()

    def mouseMoveEvent(self, event):
        super(TimelineWidget, self).mouseMoveEvent(event)

        index = self.get_hovered_index(event)
        if self.__mouse_pressed and index is not None:
            if self.__index is not None and self.__index != index:
                self.close_menu()
            self.show_menu(index)
        else:
            self.close_menu()

        if not self.__mouse_pressed:
            index = self.get_hovered_hint(event)
            if index is not None:
                self.show_hint(index)

    def get_hovered_index(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        for index, rect in enumerate(self._rect_list):
            if rect.contains(pos):
                return index

    def get_hovered_hint(self, event):
        pos = self.mapFromGlobal(event.globalPos())
        for index, rect in enumerate(self._sect_list):
            if rect.contains(pos):
                return index

    def close_menu(self):
        if self.__menu is not None:
            self.__menu.close()
            self.__menu.deleteLater()
            self.__menu = None
            self.__index = None

    def show_menu(self, index):
        if self.__menu is not None:
            return

        menu = TimelineMenu(self)
        self.__menu = menu
        self.__index = index

        for stone in self._stone_dict[index]:
            label = self._milestone[stone]
            if label == self._cur_str:
                label += " (current)"

            action = QtWidgets.QAction(label, menu)
            menu.addAction(action)

            def open_release_note(_label):
                webbrowser.open(
                    "https://learn.ragdolldynamics.com/releases/" + _label
                )

            action.triggered.connect(partial(open_release_note, label))

        menu.mouse_released.connect(self.mouseReleaseEvent)
        menu.mouse_deviated.connect(self.mouseMoveEvent)

        rect = self._rect_list[index]
        menu.show_upward(
            anchor=self.mapToGlobal(rect.center()),
            offset_y=self.min_height,
        )

    def show_hint(self, index):
        rect = self._sect_list[index]
        pos = rect.center()
        pos.setX(pos.x() - px(22))
        pos.setY(pos.y() + px(5))
        pos = self.mapToGlobal(pos)
        QtWidgets.QToolTip.showText(pos, self._sect_name[index], self)
