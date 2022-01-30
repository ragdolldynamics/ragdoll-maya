import os
import re
import sys
import time
import json
import ctypes
import logging
import datetime
import webbrowser
import tempfile

from maya.api import OpenMaya as om, OpenMayaUI as omui
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets, QtGui
import shiboken2

from . import (
    options,
    licence,
    dump,
    constants as c,
    internal as i__,
    __,
)

from .vendor import qargparse, markdown, qjsonmodel

log = logging.getLogger("ragdoll")

self = sys.modules[__name__]
self._maya_window = None

px = MQtUtil.dpiScale

# Expose some utility to interactive.py
isValid = shiboken2.isValid


def camel_to_title(text):
    """Convert camelCase `text` to Title Case

    Example:
        >>> camel_to_title("mixedCase")
        "Mixed Case"
        >>> camel_to_title("myName")
        "My Name"
        >>> camel_to_title("you")
        "You"
        >>> camel_to_title("You")
        "You"
        >>> camel_to_title("This is That")
        "This Is That"

    """

    return re.sub(
        r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))",
        r" \1", text
    ).title()


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


with open(_resource("ui", "style.css")) as f:
    stylesheet = f.read()


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


def _with_entered_exited_signals(cls):
    class WidgetHoverFactory(cls):
        entered = QtCore.Signal()
        exited = QtCore.Signal()

        def enterEvent(self, event):
            self.entered.emit()
            return super(WidgetHoverFactory, self).enterEvent(event)

        def leaveEvent(self, event):
            self.exited.emit()
            return super(WidgetHoverFactory, self).leaveEvent(event)

    return WidgetHoverFactory


def hide_menuitem(item):
    ptr = MQtUtil.findMenuItem(item)
    item = shiboken2.wrapInstance(i__.long(ptr), QtWidgets.QAction)
    item.setVisible(False)


def show_menuitem(item):
    ptr = MQtUtil.findMenuItem(item)
    item = shiboken2.wrapInstance(i__.long(ptr), QtWidgets.QAction)
    item.setVisible(True)


def MayaWindow():
    """Fetch Maya window, along with whatever DPI it's got cooking"""

    # This will never change during the lifetime of this Python session
    if not self._maya_window:
        ptr = MQtUtil.mainWindow()

        if ptr is not None:
            self._maya_window = shiboken2.wrapInstance(
                i__.long(ptr), QtWidgets.QMainWindow
            )

        else:

            # Running standalone
            return None

    return self._maya_window


class Player(QtWidgets.QWidget):
    frame_changed = QtCore.Signal(int)

    def __init__(self, media, parent=None):
        super(Player, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        panels = {
            "overlay": QtWidgets.QWidget(self),
            "video": QtWidgets.QStackedWidget()
        }

        widgets = {
            "background": QtWidgets.QWidget(),
            "title": QtWidgets.QLabel("Title"),
            "description": QtWidgets.QLabel("Description here")
        }

        effects = {
            "background": (
                QtWidgets.QGraphicsOpacityEffect(widgets["background"])
            ),
            "title": (
                QtWidgets.QGraphicsOpacityEffect(widgets["title"])
            ),
            "description": (
                QtWidgets.QGraphicsOpacityEffect(widgets["description"])
            ),
        }

        animation = {
            "overlay": (
                QtCore.QPropertyAnimation(self, b"overlay_height")
            ),
            "background": (
                QtCore.QPropertyAnimation(effects["background"], b"opacity")
            ),
            "title": (
                QtCore.QPropertyAnimation(effects["title"], b"opacity")
            ),
            "description": (
                QtCore.QPropertyAnimation(effects["description"], b"opacity")
            ),
        }

        for key in ("background", "title", "description"):
            effect = effects[key]
            widgets[key].setGraphicsEffect(effect)
            effect.setOpacity(0.0)

        for name, obj in widgets.items():
            obj.setObjectName(name)

        for name, obj in panels.items():
            obj.setObjectName(name)

        widgets["description"].setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(panels["overlay"])
        layout.addWidget(widgets["title"], QtCore.Qt.AlignVCenter)
        layout.addWidget(widgets["description"], QtCore.Qt.AlignVCenter)
        layout.addWidget(QtWidgets.QWidget(), 1)  # Push up

        widgets["background"].setParent(panels["overlay"])
        widgets["background"].setAttribute(QtCore.Qt.WA_StyledBackground)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(panels["video"])

        for anim in animation.values():
            anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        animation["title"].setDuration(100)
        animation["background"].setDuration(100)
        animation["description"].setDuration(100)
        animation["overlay"].setDuration(50)

        self._panels = panels
        self._widgets = widgets
        self._effects = effects
        self._animation = animation
        self._clips = []

        self._offset = 0
        self._frame_to_index = []

        t0 = time.time()

        for clip in media:
            self.add_clip(clip)

        t1 = time.time()
        ms = (t1 - t0) * 1000
        log.debug("Created player in %.2f ms" % ms)

    def add_clip(self, clip):
        fname = _resource("gif", clip["fname"])
        movie = QtGui.QMovie(parent=self)
        movie.setFileName(fname)

        # Cache all frames in advance, for blissful scrubbing
        if options.read("cacheMedia") == c.All:
            # Unfortunately, every frame takes ~1.5 mb of memory
            # and 1,000 frames is not uncommon!
            movie.setCacheMode(movie.CacheAll)
            movie.jumpToFrame(movie.frameCount() - 1)

        # Fit the 480p video to a 570px wide UI
        movie.setScaledSize(QtCore.QSize(px(570), px(320)))

        widget = QtWidgets.QLabel()
        widget.setMovie(movie)

        video = self._panels["video"]
        video.addWidget(widget)

        # Maintain reference to stack index for each frame
        new_index = video.count() - 1
        offset = len(self._frame_to_index)
        for frame in range(movie.frameCount()):
            self._frame_to_index.append((new_index, offset))

        movie.frameChanged.connect(self.on_frame_changed)

        self._clips.append(clip)

    def on_frame_changed(self, frame):
        self.frame_changed.emit(frame + self._offset)

    def index_at(self, frame):
        """Find index at which player is at from a global time"""
        return self._frame_to_index[frame]

    def set_current_index(self, index):
        # Update help card
        clip = self._clips[index]

        self._widgets["title"].setText(clip["label"])
        self._widgets["description"].setText(clip["description"])

        # Update offset
        offset = 0

        for i in range(index):
            video = self.video(i)
            offset += video.movie().frameCount()

        self._offset = offset

        video = self._panels["video"]
        return video.setCurrentIndex(index)

    def current_index(self):
        return self._panels["video"].currentIndex()

    def current_video(self):
        return self._panels["video"].currentWidget()

    def video(self, index):
        return self._panels["video"].widget(index)

    def jump_to(self, frame=0):
        index, offset = self.index_at(frame)

        # From global to local frame number
        frame = frame - offset

        if index != self.current_index():
            self.set_current_index(index)

        player = self.current_video()
        movie = player.movie()

        # If media is cached, then jumping to
        # any frame from any frame is possible.
        if options.read("cacheMedia") == c.All:
            movie.jumpToFrame(frame)

        elif options.read("cacheMedia") == c.On:

            # Caching is much preferred, but if memory
            # is an issue then we haven't got much choice.
            current = movie.currentFrameNumber()

            # I.e. the user scrubs backwards
            # The QMovie apparently doesn't scrub that way
            if frame < current:
                current = 0

            # A QMovie that isn't cached must be jumped
            # one frame at a time, in the order they appear
            for f in range(current, frame):
                movie.jumpToFrame(f)

        else:
            return movie.jumpToFrame(0)

    def play(self):
        video = self.current_video()

        if not video:
            return

        video.movie().setPaused(False)

    def pause(self):
        video = self.current_video()

        if not video:
            return

        video.movie().setPaused(True)

    def start(self, index=0):
        self.set_current_index(index)
        video = self.current_video()

        if not video:
            return

        video.movie().start()

    def stop(self):
        video = self.current_video()

        if not video:
            return

        video.movie().stop()

    def enterEvent(self, event):
        """Animate overlay transition on entering and leaving"""
        anim = self._animation["background"]
        anim.setStartValue(0.0)
        anim.setEndValue(0.9)
        anim.start()

        # anim = self._animation["overlay"]
        # anim.setStartValue(px(50))
        # anim.setEndValue(px(80))
        # anim.start()

        for text in ("title", "description"):
            anim = self._animation[text]
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()

        super(Player, self).enterEvent(event)

    def leaveEvent(self, event):
        anim = self._animation["background"]
        anim.setStartValue(0.9)
        anim.setEndValue(0.0)
        anim.start()

        # anim = self._animation["overlay"]
        # anim.setStartValue(px(80))
        # anim.setEndValue(px(50))
        # anim.start()

        for text in ("title", "description"):
            anim = self._animation[text]
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.start()

        super(Player, self).leaveEvent(event)

    def _get_overlay_height(self):
        if not hasattr(self, "_panels"):
            return 0.0

        return self._panels["overlay"].height()

    def _set_overlay_height(self, height):
        if not hasattr(self, "_panels"):
            return

        overlay = self._panels["overlay"]
        overlay.setFixedHeight(height)
        overlay.move(0, self.size().height() - height)

    overlay_height = QtCore.Property(
        float, _get_overlay_height, _set_overlay_height)

    def resizeEvent(self, event):
        """Fit widgets without layout"""
        self._widgets["background"].resize(event.size())

        overlay = self._panels["overlay"]
        overlay_size = QtCore.QSize(event.size().width(), px(80))
        overlay.resize(overlay_size)

        height = px(80)
        overlay.setFixedHeight(height)
        overlay.move(0, self.size().height() - height)

        super(Player, self).resizeEvent(event)

    def showEvent(self, event):
        super(Player, self).showEvent(event)

        self._widgets["background"].lower()
        self._widgets["background"].show()
        self._panels["overlay"].raise_()
        self._panels["overlay"].show()


class DirectJumpSlider(QtWidgets.QSlider):
    """Slider with support for clicking anywhere to scrubbing

    From: https://stackoverflow.com/questions/11132597
                /qslider-mouse-direct-jump

    """

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.orientation() == QtCore.Qt.Horizontal:
                self.setValue(
                    self.minimum() + (self.maximum() - self.minimum() + 1) *
                    float(event.x()) / float(self.width())
                )
            else:
                self.setValue(
                    self.minimum() + (
                        (self.maximum() - self.minimum()) * event.x()
                    ) / self.width()
                )

            event.accept()

        return super(DirectJumpSlider, self).mousePressEvent(event)


class Clip(QtWidgets.QWidget):
    def __init__(self, fname, parent=None):
        super(Clip, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        movie = QtGui.QMovie(fname, parent=self)
        movie.jumpToFrame(0)
        image = movie.currentImage()

        # Fit more pixels in each thumbnail
        image = image.scaledToHeight(
            px(image.height()) * 0.25,
            QtCore.Qt.SmoothTransformation
        )

        self._label = QtWidgets.QLabel(self)
        self._length = movie.frameCount()
        self._fname = fname
        self._movie = movie
        self._image = image
        self._scale = 1.0
        self._height = px(75)

        self._label.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.fit()

        anim = QtCore.QPropertyAnimation(self, b"animated_height")
        anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        anim.setDuration(200)

        self._height_anim = anim

        self.animate_height()

    def showEvent(self, event):
        self._label.show()
        super(Clip, self).showEvent(event)

    def animate_height(self, height=None):
        height = height or self._height
        current = self._height_anim.currentValue()
        self._height_anim.setStartValue(current)
        self._height_anim.setEndValue(height)
        self._height_anim.start()

    def _get_animated_height(self):
        return self._height

    def _set_animated_height(self, height):
        self._height = height
        self._label.setFixedHeight(height)

        # Centered motion
        center = self.size().height() / 2.0
        height_delta = height / 2.0
        center_delta = height - center
        y = height_delta - center_delta
        self._label.move(0, y)

    # PySide's properties have garbage syntax
    animated_height = QtCore.Property(
        float, _get_animated_height, _set_animated_height)

    def fit(self, scale=1.0):
        """Fit thumbnail inside of clip

        Scale is whatever the parent container needs it
        to be in order to fill a complete with of many clips.

        """

        image = self._image

        original_width = image.width()
        scaled_width = self._length * scale

        # Ensure we've got enough pixels to fill the width
        if original_width < scaled_width:
            scale = scaled_width / float(original_width)
            image = image.scaledToWidth(
                original_width * scale, QtCore.Qt.SmoothTransformation
            )

        rect = image.rect()
        rect.setHeight(px(80))  # Crop from bottom
        rect.setWidth(scaled_width)  # Crop from right
        image = image.copy(rect)

        self._label.setPixmap(QtGui.QPixmap.fromImage(image))
        self._label.setFixedWidth(scaled_width)
        self.setFixedWidth(scaled_width)

    @property
    def length(self):
        return self._length

    @property
    def movie(self):
        return self._movie

    @property
    def image(self):
        return self._image


class Timeline(QtWidgets.QWidget):
    pressed = QtCore.Signal()
    moved = QtCore.Signal(int)
    released = QtCore.Signal()

    def __init__(self, media, parent=None):
        super(Timeline, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setCursor(QtCore.Qt.SizeHorCursor)

        background = QtWidgets.QWidget(self)
        background.setObjectName("background")
        background.setAttribute(QtCore.Qt.WA_StyledBackground)

        layout = QtWidgets.QHBoxLayout(background)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        slider = DirectJumpSlider(self)
        slider.setOrientation(QtCore.Qt.Horizontal)

        slider.sliderMoved.connect(self.on_slider_moved)
        slider.sliderPressed.connect(self.on_slider_pressed)
        slider.sliderReleased.connect(self.on_slider_released)
        slider.valueChanged.connect(self.on_slider_changed)

        self._slider = slider
        self._background = background
        self._clips = []
        self._frame_to_index = []
        self._current_index = 0

        for clip in media or []:
            self.add_clip(clip)

        if media:
            self.on_index_changed(0)

    def index_at(self, frame):
        """Find index at which player is at from a global time"""
        return self._frame_to_index[frame]

    def jump_to(self, frame):
        self.blockSignals(True)
        self._slider.setValue(frame)
        self.blockSignals(False)

    def on_slider_changed(self, frame):
        index = self.index_at(frame)
        if index != self._current_index:
            self.on_index_changed(index)
            self._current_index = index

    def on_index_changed(self, index):
        for clip in self._clips:
            clip.animate_height(px(55))
            clip.setProperty("playing", False)
            clip.setStyleSheet("")  # Respond to edited attributes

        clip = self._clips[index]
        clip.animate_height(px(60))
        clip.setProperty("playing", True)
        clip.setStyleSheet("")

    def on_slider_pressed(self,):
        frame = self._slider.value()
        self.pressed.emit()
        self.moved.emit(frame)

    def on_slider_moved(self, frame):
        self.moved.emit(frame)

    def on_slider_released(self):
        self.released.emit()

    def add_clip(self, clip):
        fname = _resource("gif", clip["fname"])

        assert os.path.exists(fname), "'%s' could not be found" % fname
        assert fname.endswith(".gif"), "'%s' was not a gif" % fname

        clip = Clip(fname)
        clip.setProperty("scaledLength", -1)
        clip.setProperty("scale", 1.0)

        layout = self._background.layout()
        layout.addWidget(clip)

        self._clips.append(clip)

        total_count = 0
        for clip in self._clips:
            total_count += clip.length

        self._slider.setRange(0, total_count - 1)

        # Maintain reference to stack index for each frame
        for frame in range(clip.length):
            self._frame_to_index.append(len(self._clips) - 1)

    def showEvent(self, event):
        """Give it a little push

        Without this, the timeline can appear at 0 height
        when used in a layout. There's probably a more correct
        solution to this, if you spot it do something about it.

        """

        self.on_index_changed(0)

        return super(Timeline, self).showEvent(event)

    def resizeEvent(self, event):
        """Keep clips proportionally sized to the overall timeline"""
        self._slider.resize(event.size())
        self._background.resize(event.size())

        scale = event.size().width() / float(self._slider.maximum())

        for clip in self._clips:
            clip.fit(scale)

        return super(Timeline, self).resizeEvent(event)


class HelpPage(QtWidgets.QWidget):
    """The widget showing up when the user clicked Help

     _____________________________________
    |      _                              |
    | <-- |_| Active Rigid       Options  |
    |         ----------------   o ----   |
    |                            o ----   |
    |         ----------------   o ----   |
    |         ---------------             |
    |         -------------      Media    |
    |         --------------     o ----   |
    |         ---------------    o ----   |
    |                            o ----   |
    |                            o ----   |
    |                                     |
    |_____________________________________|

    """

    back = QtCore.Signal()

    def __init__(self, parent=None):
        super(HelpPage, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        widgets = {
            "background": QtWidgets.QLabel(),
            "body": QtWidgets.QWidget(),
            "scroll": QtWidgets.QScrollArea(),

            "back": QtWidgets.QPushButton(),
            "title": QtWidgets.QLabel("Label"),
            "icon": QtWidgets.QLabel(),
            "summary": QtWidgets.QLabel(),
            "description": QtWidgets.QLabel(),

            "sidebar": QtWidgets.QWidget(),
            "mediaTitle": QtWidgets.QLabel("Media"),
            "media": QtWidgets.QWidget(),
            "optionsTitle": QtWidgets.QLabel("Options"),
            "options": QtWidgets.QWidget(),

            "logo": QtWidgets.QLabel(),
        }

        widgets["background"].setPixmap(_resource("ui", "background1.png"))
        widgets["background"].setScaledContents(True)
        widgets["background"].setParent(self)

        widgets["title"].setAlignment(QtCore.Qt.AlignLeft)

        opacity = QtWidgets.QGraphicsOpacityEffect(widgets["background"])
        opacity.setOpacity(0.5)
        widgets["background"].setGraphicsEffect(opacity)

        icon = _resource("icons", "back.png")
        icon = QtGui.QIcon(icon)
        widgets["back"].setIcon(icon)
        widgets["back"].clicked.connect(self.on_back)

        widgets["icon"].setFixedWidth(px(20))
        widgets["icon"].setAlignment(QtCore.Qt.AlignHCenter)

        font = widgets["summary"].font()
        font.setWeight(font.Bold)

        layout = QtWidgets.QVBoxLayout(widgets["media"])
        layout.addWidget(widgets["mediaTitle"])
        layout.addWidget(QtWidgets.QWidget(), 1)  # Push everything up
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(widgets["options"])
        layout.addWidget(widgets["optionsTitle"])
        layout.addWidget(QtWidgets.QWidget(), 1)  # Push everything up
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(widgets["sidebar"])
        layout.addWidget(widgets["media"])
        layout.addWidget(widgets["options"])
        layout.addWidget(QtWidgets.QWidget(), 1)  # Push everything up
        layout.setSpacing(px(20))

        pixmap = _resource("ui", "ragdoll_silhouette_white_128.png")
        pixmap = QtGui.QPixmap(pixmap)
        pixmap = pixmap.scaledToWidth(
            px(32), QtCore.Qt.SmoothTransformation
        )
        widgets["logo"].setPixmap(pixmap)

        for label in (widgets["summary"], widgets["description"]):
            label.setWordWrap(True)
            label.setAlignment(QtCore.Qt.AlignTop)
            label.setTextInteractionFlags(
                QtCore.Qt.TextBrowserInteraction
            )

        for name, obj in widgets.items():
            obj.setObjectName(name)

        layout = QtWidgets.QGridLayout(widgets["body"])
        layout.addWidget(widgets["back"], 0, 0, QtCore.Qt.AlignCenter)
        layout.addWidget(widgets["icon"], 0, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(widgets["title"], 0, 2)
        layout.addWidget(widgets["summary"], 1, 1, 1, 2)
        layout.addWidget(widgets["description"], 2, 1, 1, 2)
        layout.addWidget(widgets["sidebar"], 0, 3, 3, 1)
        layout.addWidget(widgets["logo"], 10, 3, QtCore.Qt.AlignRight)
        layout.setRowStretch(2, 1)  # Push summary upwards
        layout.setColumnStretch(2, 1)  # Push icon leftwards
        layout.setVerticalSpacing(px(5))
        layout.setHorizontalSpacing(px(10))
        layout.setContentsMargins(px(10), px(10), px(10), px(10))

        widgets["scroll"].setWidgetResizable(True)
        widgets["scroll"].setFrameShape(QtWidgets.QFrame.NoFrame)
        widgets["scroll"].setWidget(widgets["body"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(widgets["scroll"])
        layout.setContentsMargins(0, 0, 0, 0)

        self._widgets = widgets
        self.setStyleSheet(_scaled_stylesheet(stylesheet))

    def showEvent(self, event):
        self._widgets["background"].show()
        return super(HelpPage, self).showEvent(event)

    def resizeEvent(self, event):
        self._widgets["background"].resize(event.size())
        return super(HelpPage, self).resizeEvent(event)

    def on_back(self):
        self.back.emit()

    def load(self, key):
        item = __.menuitems[key]

        # Use a fallback in case there isn't an icon
        label = item.get("label", camel_to_title(key))
        icon = item.get("icon", "system.png")
        summary = item.get("summary", "")
        description = item.get("description", "")
        options = item.get("options", [])
        media = item.get("media", [])

        # Pre-process any contained markdown
        summary = markdown.markdown(summary)
        description = markdown.markdown(description)

        pixmap = QtGui.QPixmap(_resource("icons", icon))
        pixmap = pixmap.scaledToWidth(
            px(20), QtCore.Qt.SmoothTransformation
        )

        self._widgets["title"].setText(label)
        self._widgets["icon"].setPixmap(pixmap)
        self._widgets["summary"].setText(summary)
        self._widgets["description"].setText(description)

        def clear(layout):
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()

                if widget:
                    widget.deleteLater()
                del item

        options_layout = self._widgets["options"].layout()
        media_layout = self._widgets["media"].layout()

        self._widgets["optionsTitle"].setText("Options (%d)" % len(options))
        self._widgets["mediaTitle"].setText("Media (%d)" % len(media))

        clear(options_layout)
        clear(media_layout)

        if options:
            for option in options:
                option = QtWidgets.QLabel("- " + option)
                options_layout.addWidget(option)
        else:
            options_layout.addWidget(QtWidgets.QLabel("- No options"))

        if media:
            for med in media:
                med = QtWidgets.QLabel("- " + med["label"])
                media_layout.addWidget(med)
        else:
            media_layout.addWidget(QtWidgets.QLabel("- No media"))


class Options(QtWidgets.QMainWindow):
    instance = None

    def __init__(self,
                 key,
                 args,
                 command,
                 icon,
                 description,
                 media=None,
                 parent=None):

        super(Options, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMouseTracking(True)  # For helptext
        self.setMinimumWidth(px(570))
        self.setMaximumWidth(px(570))
        self.setMinimumHeight(px(395))

        # Infer name from command
        command_name = " ".join(command.__name__.split("_")).title()
        self.setWindowTitle(command_name + " options")

        panels = {
            "Central": QtWidgets.QWidget(),
            "Body": QtWidgets.QStackedWidget(),
            "Buttons": QtWidgets.QWidget(),
            "Footer": QtWidgets.QWidget(),
            "Timeline": QtWidgets.QWidget(),
        }

        panels["Body"].setFixedWidth(px(570))

        _Button = _with_entered_exited_signals(QtWidgets.QPushButton)

        widgets = {
            "Confirm": _Button(command_name),
            "Apply": _Button("Apply"),
            "Close": _Button("Close"),
            "Hint": QtWidgets.QLabel(),
            "PlayerButton": _Button(),
            "TimelineButton": _Button(),
            "TimelineSpacing": QtWidgets.QWidget(),
            "Player": Player(media, self),
            "Help": HelpPage(),
            "Options": QtWidgets.QWidget(),
            "ScrollArea": QtWidgets.QScrollArea(),
            "Timeline": Timeline(media),
            "Background": QtWidgets.QLabel(),
            "Foreground": QtWidgets.QLabel(),

            "Parser": qargparse.QArgumentParser(args, style={
                "comboboxFillWidth": False,

                # We'll defer these to the footer
                "useTooltip": False,
            }),
        }

        effects = {
            "Foreground": QtWidgets.QGraphicsOpacityEffect(
                widgets["Foreground"]),
        }

        keys = {
            "Escape": QtWidgets.QShortcut(self)
        }

        for name, obj in widgets.items():
            obj.setObjectName(name)
            obj.setAttribute(QtCore.Qt.WA_StyledBackground)

        for name, obj in panels.items():
            obj.setObjectName(name)

        player_icon = QtGui.QPixmap(_resource("icons", "play.png"))
        widgets["PlayerButton"].setCheckable(True)
        widgets["PlayerButton"].setIcon(player_icon)
        widgets["PlayerButton"].setIconSize(QtCore.QSize(px(20), px(20)))

        pause_icon = QtGui.QPixmap(_resource("icons", "pause.png"))
        widgets["TimelineButton"].setIcon(pause_icon)
        widgets["TimelineButton"].setIconSize(QtCore.QSize(px(20), px(20)))
        widgets["TimelineButton"].setCheckable(True)
        widgets["TimelineButton"].setChecked(True)

        helptext = "Hover over an option to read more about it"
        widgets["Hint"].setProperty("defaultText", helptext)
        widgets["Hint"].setText(helptext)

        widgets["Confirm"].clicked.connect(self.on_confirm_clicked)
        widgets["Apply"].clicked.connect(self.on_apply_clicked)
        widgets["Close"].clicked.connect(self.on_close_clicked)

        pixmap = QtGui.QPixmap(_resource("ui", "option_header.png"))
        pixmap = pixmap.scaledToWidth(px(570), QtCore.Qt.SmoothTransformation)
        widgets["Background"].setPixmap(pixmap)
        widgets["Background"].setFixedHeight(px(75))
        widgets["Background"].setFixedWidth(px(570))

        panels["Timeline"].setFixedHeight(px(75))
        panels["Footer"].setFixedHeight(px(75))

        widgets["Background"].setParent(self)

        widgets["Hint"].setParent(panels["Footer"])
        widgets["Hint"].move(px(80), px(9))
        widgets["Hint"].setFixedWidth(px(350))
        widgets["Hint"].setFixedHeight(px(75))
        widgets["Hint"].setWordWrap(True)
        widgets["Hint"].setAlignment(QtCore.Qt.AlignTop)

        widgets["PlayerButton"].setParent(panels["Footer"])
        widgets["PlayerButton"].move(px(10), px(10))
        widgets["PlayerButton"].setFixedSize(px(55), px(55))
        widgets["PlayerButton"].clicked.connect(self.on_play)
        widgets["PlayerButton"].hide()

        # widgets["TimelineButton"].setFixedSize(px(55), px(55))
        widgets["TimelineButton"].clicked.connect(self.on_back)

        widgets["Timeline"].pressed.connect(widgets["Player"].pause)
        widgets["Timeline"].moved.connect(widgets["Player"].jump_to)
        widgets["Timeline"].released.connect(widgets["Player"].play)
        widgets["Player"].frame_changed.connect(widgets["Timeline"].jump_to)

        def add_help(button, text):
            def on_entered():
                widgets["Hint"].setText(text)

            def on_exited():
                self.on_exited()

            button.entered.connect(on_entered)
            button.exited.connect(on_exited)

        add_help(widgets["PlayerButton"], "Click for demonstration video")
        add_help(widgets["Confirm"], "Apply and close")
        add_help(widgets["Apply"], "Apply and keep window open")
        add_help(widgets["Close"], "Do nothing and close")

        widgets["Parser"].changed.connect(self.on_changed)
        widgets["Parser"].entered.connect(self.on_entered)
        widgets["Parser"].exited.connect(self.on_exited)

        widgets["Help"].load(key)
        widgets["Help"].back.connect(self.on_back)

        menu = self.menuBar()
        edit = menu.addMenu("&Edit")
        hlp = menu.addMenu("&Help")

        save = edit.addAction("Save Settings")
        save.triggered.connect(self.on_save)
        reset = edit.addAction("Reset Settings")
        reset.triggered.connect(self.on_reset)
        hlp_on = hlp.addAction("Help on %s" % command_name)
        hlp_on.triggered.connect(self.on_help)

        widgets["ScrollArea"].setWidget(widgets["Options"])
        widgets["ScrollArea"].setWidgetResizable(True)
        widgets["ScrollArea"].setFrameShape(QtWidgets.QFrame.NoFrame)
        widgets["Options"].setMinimumHeight(px(300))
        widgets["Options"].setMinimumWidth(px(300))

        panels["Body"].addWidget(widgets["ScrollArea"])
        panels["Body"].addWidget(widgets["Player"])
        panels["Body"].addWidget(widgets["Help"])
        panels["Body"].setMaximumWidth(px(570))

        self.OptionsPage = 0
        self.PlayerPage = 1
        self.HelpPage = 2

        widgets["Parser"].help_wanted.connect(self.on_help)
        widgets["Parser"].help_entered.connect(self.on_help_entered)
        widgets["Parser"].help_exited.connect(self.on_exited)
        widgets["Parser"].setIcon(icon)
        widgets["Parser"].setDescription(description)

        spacer = QtWidgets.QWidget()
        spacer.setFixedWidth(px(45))
        layout = QtWidgets.QGridLayout(widgets["Options"])
        layout.addWidget(spacer, 0, 0)
        layout.addWidget(widgets["Parser"], 0, 1)
        layout.setContentsMargins(px(5), px(5), px(5), px(5))

        layout = QtWidgets.QHBoxLayout(panels["Buttons"])
        layout.setContentsMargins(px(5), px(5), px(5), px(7))
        layout.addWidget(widgets["Confirm"])
        layout.addWidget(widgets["Apply"])
        layout.addWidget(widgets["Close"])

        layout = QtWidgets.QVBoxLayout(panels["Central"])
        layout.addWidget(panels["Body"])
        layout.addWidget(panels["Buttons"])
        layout.addWidget(panels["Footer"])
        layout.addWidget(panels["Timeline"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout = QtWidgets.QHBoxLayout(panels["Timeline"])
        layout.addWidget(widgets["TimelineButton"])
        layout.addWidget(widgets["Timeline"])
        layout.addWidget(widgets["TimelineSpacing"])
        layout.setContentsMargins(0, 0, 0, 0)

        # Shown during playback
        panels["Timeline"].hide()

        widgets["Foreground"].setAttribute(QtCore.Qt.WA_StyledBackground)
        widgets["Foreground"].setGraphicsEffect(effects["Foreground"])
        widgets["Foreground"].setParent(self)
        widgets["Foreground"].hide()

        keys["Escape"].setKey(QtGui.QKeySequence("Esc"))
        keys["Escape"].activated.connect(self.on_back)
        keys["Escape"].setEnabled(False)

        self._keys = keys
        self._panels = panels
        self._widgets = widgets
        self._effects = effects
        self._command = command
        self._media = media

        # For uninstall
        Options.instance = self
        __.widgets[self.windowTitle()] = self

        self.setStyleSheet(_scaled_stylesheet(stylesheet))
        self.setCentralWidget(panels["Central"])

    def showEvent(self, event):
        super(Options, self).showEvent(event)

        self._widgets["Hint"].show()

        if self._media:
            self._widgets["PlayerButton"].show()

    def resizeEvent(self, event):
        height = event.size().height()
        width = event.size().width()
        self._widgets["Background"].move(0, height - px(75))
        self._widgets["Background"].resize(width, px(75))
        self._widgets["Foreground"].resize(event.size())
        return super(Options, self).resizeEvent(event)

    @property
    def parser(self):
        return self._widgets["Parser"]

    def transition(self, to):
        """Animate the transition from whatever state we're in, to `to`

        The transition is a solid color in front of all widgets that fade in,
        then a switch is made, followed by a fade out.

        """

        effect = self._effects["Foreground"]
        effect.setOpacity(0.0)

        def rehide():
            # Take case to physically hide the foreground widget,
            # as it would otherwise swallow all mouse and keyboard events
            self._widgets["Foreground"].hide()

        def fade_in():
            to()

            anim = QtCore.QPropertyAnimation(effect, b"opacity")
            anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            anim.setDuration(100)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.start()

            anim.finished.connect(rehide)

            # Keep from garbage collector
            self.__fadeout = anim

        def fade_out():
            self._widgets["Foreground"].show()
            self._widgets["Foreground"].raise_()

            anim = QtCore.QPropertyAnimation(effect, b"opacity")
            anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            anim.setDuration(100)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()

            anim.finished.connect(fade_in)

            # Keep from garbage collector
            self.__fadeout = anim

        fade_out()

    def on_help(self):
        self.transition(to=self.help_state)

    def on_back(self):
        self.transition(to=self.options_state)

    def on_play(self):
        self.transition(to=self.play_state)

    def options_state(self):
        self._panels["Body"].setCurrentIndex(self.OptionsPage)
        self._widgets["PlayerButton"].setChecked(False)
        self._widgets["Player"].stop()
        self._panels["Buttons"].show()
        self._panels["Footer"].show()
        self._panels["Timeline"].hide()
        self.menuBar().show()
        icon = _resource("icons", "play.png")
        self._widgets["PlayerButton"].setIcon(QtGui.QPixmap(icon))
        self._keys["Escape"].setEnabled(False)

    def play_state(self):
        self._widgets["TimelineButton"].setChecked(True)
        self._panels["Body"].setCurrentIndex(self.PlayerPage)
        self._widgets["Player"].start()
        self._panels["Buttons"].hide()
        self._panels["Footer"].hide()
        self._panels["Timeline"].show()
        self.menuBar().hide()

        icon = _resource("icons", "pause.png")
        self._widgets["PlayerButton"].setIcon(QtGui.QPixmap(icon))
        self._keys["Escape"].setEnabled(True)

    def help_state(self):
        self.menuBar().hide()
        self._panels["Buttons"].hide()
        self._panels["Footer"].hide()
        self._panels["Body"].setCurrentIndex(self.HelpPage)
        self._keys["Escape"].setEnabled(True)

    def on_confirm_clicked(self):
        if self._command():
            self.close()

    def on_apply_clicked(self):
        self._command()

    def on_close_clicked(self):
        self.close()

    def on_reset(self):
        for arg in self._widgets["Parser"]:
            arg.reset()

    def on_save(self):
        # They auto-save, so this is mostly for show
        # Like the button on pedestrian crossings
        log.info("Saved")

    def on_changed(self, arg):
        key = arg["name"]
        value = arg.read()

        options.write(key, value)

        log.debug("Edited %s=%s" % (key, value))

    def on_help_entered(self):
        self._widgets["Hint"].setText(
            "Click for an extended help page about %s"
            % self.windowTitle()
        )

    def on_entered(self, arg):
        text = markdown.markdown(arg["help"])
        self._widgets["Hint"].setText(text)

    def on_exited(self, arg=None):
        default = self._widgets["Hint"].property("defaultText")
        self._widgets["Hint"].setText(default)


YesButton = QtWidgets.QMessageBox.Yes
NoButton = QtWidgets.QMessageBox.No
CancelButton = QtWidgets.QMessageBox.Cancel
OkButton = QtWidgets.QMessageBox.Ok
InformationIcon = QtWidgets.QMessageBox.Information
QuestionIcon = QtWidgets.QMessageBox.Question
WarningIcon = QtWidgets.QMessageBox.Warning
CriticalIcon = QtWidgets.QMessageBox.Critical


def MessageBox(title, text, buttons=None, icon=QuestionIcon):
    parent = MayaWindow()
    message = QtWidgets.QMessageBox(parent)

    buttons = buttons or (
        QtWidgets.QMessageBox.Yes |
        QtWidgets.QMessageBox.No
    )

    message.setStandardButtons(buttons)
    message.setIcon(icon)

    message.setWindowTitle(title)
    message.setText(markdown.markdown(text))

    return message.exec_() == QtWidgets.QMessageBox.Yes


def product_to_marketingname(product):
    return {
        "enterprise": "Unlimited",
        "headless": "Batch",
        "personal": "Personal",
        "complete": "Complete",
        "trial": "Trial",
    }[product]


class SplashScreen(QtWidgets.QDialog):
    """Ragdoll Splash
     ____________________________________________
    |                                          x |
    |                                            |
    |                                            |
    |                                            |
    |                                            |
    |                    Logo                    |
    |                                            |
    |                                            |
    |                                            |
    |                                            |
    |____________________________________________|
    |                                            |
    | Licence text                   Expiry date |
    | __________________________________________ |
    ||                                          ||
    || Serial number 0000-0000-0000-0000        ||
    ||__________________________________________||
    | ___________  ______________  _____________ |
    ||           ||              ||             ||
    ||  Activate ||   Offline    ||    Trial    ||
    ||___________||______________||_____________||
    |____________________________________________|

    """

    instance = None

    def __init__(self, parent=None):
        super(SplashScreen, self).__init__(parent)
        self.setWindowTitle("Ragdoll Dynamics")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setFixedSize(px(500), px(410))  # 0.5x the size of splash.png

        panels = {
            "body": QtWidgets.QWidget(self),
            "status": QtWidgets.QWidget(),
            "serial": QtWidgets.QWidget(),
            "buttons": QtWidgets.QWidget(),
        }

        widgets = {
            "background": QtWidgets.QLabel(),
            "close": QtWidgets.QPushButton(self),
            "statusActivated": QtWidgets.QLabel(),
            "statusVerified": QtWidgets.QLabel(),
            "statusMessage": QtWidgets.QLabel("Trial"),
            "expiryDate": QtWidgets.QLabel(),
            "serial": QtWidgets.QLineEdit(),
            "activate": QtWidgets.QPushButton("Activate"),
            "deactivate": QtWidgets.QPushButton("Deactivate"),
            "activateOffline": QtWidgets.QPushButton("Activate Offline"),
            "deactivateOffline": QtWidgets.QPushButton("Deactivate Offline"),
            "continue": QtWidgets.QPushButton("Continue"),

            # Floating licence widgets
            "lease": QtWidgets.QPushButton("Request Lease"),
            "drop": QtWidgets.QPushButton("Drop Lease"),
            "ip": QtWidgets.QLineEdit(),
            "port": QtWidgets.QLineEdit(),
        }

        for name, obj in widgets.items():
            obj.setObjectName(name)

        for name, obj in panels.items():
            obj.setObjectName(name)

        pixmap = QtGui.QPixmap(_resource("ui", "splash3.png"))
        pixmap = pixmap.scaledToWidth(px(500), QtCore.Qt.SmoothTransformation)
        widgets["background"].setPixmap(pixmap)

        pixmap = QtGui.QPixmap(_resource("ui", "mode_red.png"))
        pixmap = pixmap.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)
        widgets["statusActivated"].setPixmap(pixmap)

        pixmap = QtGui.QPixmap(_resource("ui", "mode_orange.png"))
        pixmap = pixmap.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)
        widgets["statusVerified"].setPixmap(pixmap)

        icon = widgets["statusVerified"].setToolTip(
            "Could not verify with licence server")

        icon = QtGui.QIcon(QtGui.QPixmap(_resource("ui", "close_button.png")))
        widgets["close"].setIcon(icon)
        widgets["close"].setIconSize(QtCore.QSize(px(20), px(20)))

        panels["body"].setAttribute(QtCore.Qt.WA_StyledBackground)
        panels["body"].setFixedHeight(px(120))
        panels["body"].setObjectName("body")  # For CSS

        widgets["serial"].setPlaceholderText(
            "Enter your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        )

        layout = QtWidgets.QHBoxLayout(panels["status"])
        layout.addWidget(widgets["statusActivated"])
        layout.addWidget(widgets["statusMessage"])
        layout.addWidget(QtWidgets.QWidget(), 1)
        layout.addWidget(widgets["expiryDate"])
        layout.setSpacing(px(5))
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QHBoxLayout(panels["serial"])
        layout.addWidget(widgets["serial"])
        layout.addWidget(widgets["ip"], 2)
        layout.addWidget(widgets["port"], 1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QHBoxLayout(panels["buttons"])
        layout.addWidget(widgets["lease"])
        layout.addWidget(widgets["drop"])
        layout.addWidget(widgets["activate"])
        layout.addWidget(widgets["deactivate"])
        layout.addWidget(widgets["activateOffline"])
        layout.addWidget(widgets["deactivateOffline"])
        layout.addWidget(widgets["continue"])
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(panels["body"])
        layout.addWidget(panels["status"])
        layout.addWidget(panels["serial"], 1)
        layout.addWidget(panels["buttons"])
        layout.setSpacing(px(10))
        layout.setContentsMargins(px(10), px(10), px(10), px(10))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(widgets["background"])
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        widgets["serial"].textChanged.connect(self.on_serial_changed)
        widgets["activate"].clicked.connect(self.on_activate_clicked)
        widgets["lease"].clicked.connect(self.on_lease_clicked)
        widgets["drop"].clicked.connect(self.on_drop_clicked)
        widgets["deactivate"].clicked.connect(self.on_deactivate_clicked)
        widgets["continue"].clicked.connect(self.on_continue_clicked)

        widgets["ip"].hide()
        widgets["ip"].setEnabled(False)
        widgets["port"].hide()
        widgets["port"].setEnabled(False)
        widgets["lease"].hide()
        widgets["drop"].hide()
        widgets["deactivate"].hide()
        widgets["deactivateOffline"].hide()

        widgets["activateOffline"].clicked.connect(
            self.on_activate_offline)
        widgets["deactivateOffline"].clicked.connect(
            self.on_deactivate_offline)

        # Free-floating
        panels["body"].show()
        panels["body"].raise_()

        widgets["close"].clicked.connect(self.close)

        anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(150)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        self.setStyleSheet(_scaled_stylesheet(stylesheet))

        self._fade_anim = anim
        self._panels = panels
        self._widgets = widgets
        self._data = {}

        self.animate_fade_in()

        self.refresh()
        self.on_serial_changed()
        self.activateWindow()

        # For uninstall
        SplashScreen.instance = self
        __.widgets[self.windowTitle()] = self

    def refresh(self):
        data = licence.data()

        # Reset expiry
        self._widgets["expiryDate"].setText("")

        if data["key"]:
            self._widgets["serial"].setText("")
            self._widgets["serial"].setPlaceholderText(data["key"])

        if data["isFloating"]:
            self.on_floating(data)

        elif data["expires"]:
            if data["expiryDays"] < 1:
                self.on_expired(data["expiryDays"])
            else:
                self.on_trial(data["expiryDays"])

        elif data["isActivated"]:
            self.on_activated(data)

        elif data["isTrial"]:
            if data["trialDays"] > 0:
                self.on_trial(data["trialDays"])

            elif data["lastStatus"] == licence.STATUS_INET:
                self.on_trial_no_internet()

            elif data["trialDays"] < 1:
                self.on_expired(data["trialDays"])

            elif data["isVerified"]:
                self.on_verified()

        else:
            self.on_deactivated()

        self._data = data

    def on_activate_offline(self):
        key = self._widgets["serial"].text()
        modal = OfflineDialog(True, key, self)
        modal.exec_()
        self.refresh()

    def on_deactivate_offline(self):
        data = licence.data()
        key = data["key"]
        modal = OfflineDialog(False, key, self)
        modal.exec_()
        self.refresh()

    def on_serial_changed(self):
        key = self._widgets["serial"].text()

        if not key:
            key = self._data.get("key")

        self._widgets["activate"].setEnabled(bool(key))
        self._widgets["activateOffline"].setEnabled(bool(key))

    def on_continue_clicked(self):
        self.close()

    def on_activate_clicked(self):
        key = self._widgets["serial"].text()

        if not key:
            key = self._data.get("key")

        if not key:
            return log.warning("Provide a product key")

        if len(key) != 34 or key.count("-") != 6:
            return log.warning(
                "Bad product key, ensure it is in the following format: "
                "0000-0000-0000-0000-0000-0000-0000"
            )

        status = licence.activate(key)

        if status == licence.STATUS_OK:
            self.refresh()

    def on_lease_clicked(self):
        licence.request_lease()
        self.refresh()

    def on_drop_clicked(self):
        licence.drop_lease()
        self.refresh()

    def on_deactivate_clicked(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle("Deactivate Ragdoll")
        msgbox.setText(
            "Do you want me to deactivate Ragdoll on this machine?\n\n"
            "I'll try and revert to a trial licence."
        )
        msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes |
                                  QtWidgets.QMessageBox.No)

        if msgbox.exec_() != QtWidgets.QMessageBox.Yes:
            return log.info("Cancelled")

        status = licence.deactivate()

        if status == licence.STATUS_OK:
            pass

        elif status == licence.STATUS_ALREADY_ACTIVATED:
            pass

        else:
            pass

        self.refresh()

    def _expiry_string(self, trial_days):
        datestring = datetime.datetime.now()
        datestring += datetime.timedelta(days=trial_days)
        datestring = datestring.strftime("%d %B %Y")
        return datestring

    def _hide_all(self):
        self._widgets["activate"].hide()
        self._widgets["activateOffline"].hide()
        self._widgets["deactivate"].hide()
        self._widgets["deactivateOffline"].hide()
        self._widgets["serial"].hide()
        self._widgets["ip"].hide()
        self._widgets["port"].hide()
        self._widgets["lease"].hide()
        self._widgets["drop"].hide()
        self._widgets["activate"].hide()
        self._widgets["deactivate"].hide()

    def on_trial(self, trial_days):
        log.info("Ragdoll is in trial mode")

        status = _resource("ui", "mode_orange.png")
        status = QtGui.QPixmap(status)
        status = status.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)

        icon = self._widgets["statusActivated"]
        icon.setPixmap(status)
        icon.setToolTip("Licence is in trial mode")

        message = self._widgets["statusMessage"]
        message.setText(
            "Ragdoll - %s - Trial Version (node-locked)"
            % __.version_str
        )

        datestring = self._expiry_string(trial_days)
        expiry = self._widgets["expiryDate"]
        expiry.setText("Expires %s" % datestring)

    def on_expired(self, trial_days):
        log.info("Ragdoll is expired")

        self._widgets["activate"].show()
        self._widgets["activate"].setEnabled(False)
        self._widgets["activateOffline"].show()
        self._widgets["activateOffline"].setEnabled(False)
        self._widgets["deactivate"].hide()
        self._widgets["deactivateOffline"].hide()
        self._widgets["serial"].setText("")
        self._widgets["serial"].setPlaceholderText(
            "Enter your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        )

        status = _resource("ui", "mode_red.png")
        status = QtGui.QPixmap(status)
        status = status.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)

        icon = self._widgets["statusActivated"]
        icon.setPixmap(status)
        icon.setToolTip("Trial has expired.")

        message = self._widgets["statusMessage"]
        message.setText("Trial has <b>expired</b>")

        datestring = self._expiry_string(trial_days)
        expiry = self._widgets["expiryDate"]
        expiry.setText("Expired %s" % datestring)

    def on_trial_no_internet(self):
        self.on_expired(0)

        msg = "An internet connection required to activate Ragdoll."
        icon = self._widgets["statusActivated"]
        icon.setToolTip(msg)

        message = self._widgets["statusMessage"]
        message.setText("Trial is <b>inactive</b>")

        expiry = self._widgets["expiryDate"]
        expiry.setText(msg)

    def on_activated(self, data):
        log.info("Ragdoll is activated")

        self._widgets["activate"].hide()
        self._widgets["activateOffline"].hide()
        self._widgets["deactivate"].show()
        self._widgets["deactivateOffline"].show()

        status = _resource("ui", "mode_green.png")
        status = QtGui.QPixmap(status)
        status = status.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)

        icon = self._widgets["statusActivated"]
        icon.setPixmap(status)
        icon.setToolTip("%s licence is active" % licence)

        message = self._widgets["statusMessage"]
        message.setText(
            "Ragdoll - {version} - <b>{product}</b> ({licence})".format(
                version=__.version_str,
                product=product_to_marketingname(data["product"]),
                licence="floating" if data["isFloating"] else "node-locked",
            )
        )

        offline = self._widgets["activateOffline"]
        offline.setText("Deactivate Offline")

        if data["product"] == "personal":
            pixmap = QtGui.QPixmap(_resource("ui", "splash_personal.png"))
            pixmap = pixmap.scaledToWidth(
                px(500), QtCore.Qt.SmoothTransformation)
            self._widgets["background"].setPixmap(pixmap)

    def on_floating(self, data):
        log.info("Ragdoll is floating")

        self._hide_all()

        try:
            ip, port = licence._parse_environment()
        except (ValueError, RuntimeError):
            ip, port = "unknown", 0

        self._widgets["ip"].setText(ip)
        self._widgets["port"].setText(str(port))
        self._widgets["ip"].show()
        self._widgets["port"].show()

        if data["hasLease"]:
            icon = "mode_green.png"
            name = product_to_marketingname(data["product"])
            tooltip = "{} is active".format(name)
            self._widgets["drop"].show()
        else:
            icon = "mode_red.png"
            name = product_to_marketingname(data["product"])
            tooltip = "{} is inactive".format(name)
            self._widgets["lease"].show()

        status = _resource("ui", icon)
        status = QtGui.QPixmap(status)
        status = status.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)

        icon = self._widgets["statusActivated"]
        icon.setPixmap(status)
        icon.setToolTip(tooltip)

        if data["product"] == "personal":
            pixmap = QtGui.QPixmap(_resource("ui", "splash_personal.png"))
            pixmap = pixmap.scaledToWidth(
                px(500), QtCore.Qt.SmoothTransformation)
            self._widgets["background"].setPixmap(pixmap)

        message = self._widgets["statusMessage"]
        message.setText(
            "Ragdoll - {version} - <b>{product}</b> ({licence})".format(
                version=__.version_str,
                product=product_to_marketingname(data["product"]),
                licence="floating" if data["isFloating"] else "node-locked",
            )
        )

    def on_deactivated(self):
        log.info("Ragdoll is deactivated")

        self._widgets["activate"].show()
        self._widgets["activateOffline"].show()
        self._widgets["deactivate"].hide()
        self._widgets["deactivateOffline"].hide()
        self._widgets["serial"].setPlaceholderText(
            "Enter your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        )

        offline = self._widgets["activateOffline"]
        offline.setText("Activate Offline")

    def on_verified(self):
        status = _resource("ui", "mode_green.png")
        status = QtGui.QPixmap(status)
        status = status.scaledToWidth(px(15), QtCore.Qt.SmoothTransformation)

        icon = self._widgets["statusVerified"]
        icon.setPixmap(status)
        icon.setToolTip("Successfully verified with licence server")

    def resizeEvent(self, event):
        # Keep body at bottom, over backdrop
        size = event.size()
        body = self._panels["body"]
        height = body.height()
        body.setFixedWidth(size.width())
        body.move(0, size.height() - height)

        # Move close button to top-right corner
        close = self._widgets["close"]
        close.move(event.size().width() - px(20), 0)

        return super(SplashScreen, self).resizeEvent(event)

    def animate_fade_in(self):
        self._fade_anim.start()


class OfflineDialog(QtWidgets.QDialog):
    def __init__(self, activate, key, parent=None):
        super(OfflineDialog, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setWindowTitle("Ragdoll Offline Activation Wizard")

        widgets = {
            "HelpText": QtWidgets.QLabel(),
            "Serial": QtWidgets.QLineEdit(),
            "Request": QtWidgets.QPlainTextEdit(),
            "RequestPlaceholder": QtWidgets.QLabel(),
            "Response": QtWidgets.QPlainTextEdit(),
            "ResponsePlaceholder": QtWidgets.QLabel(),

            "Generate": QtWidgets.QPushButton("Generate"),
            "Activate": QtWidgets.QPushButton("Activate"),
            "Deactivate": QtWidgets.QPushButton("Deactivate"),
        }

        url = "https://ragdolldynamics.com/offline"
        url = (
            "<a href='{0}' style='color: white'>{0}</a>".format(url)
        )

        if activate:
            text = (
                "Welcome to the <b>Offline Activation Guide</b>"
                "<br>"
                "<br>"
                "1. Generate a request<br>"
                "2. Get response from {}<br>"
                "3. Enter response<br>"
                "4. Click Activate<br>"
            ).format(url)
        else:
            text = (
                "Welcome to the <b>Offline Deactivation Guide</b>"
                "<br>"
                "<br>"
                "1. Copy the text below<br>"
                "2. Go to {}<br>"
            ).format(url)

        widgets["HelpText"].setText(text)
        widgets["HelpText"].setOpenExternalLinks(True)

        widgets["Serial"].setReadOnly(True)
        widgets["Serial"].setText(key)
        widgets["Request"].setReadOnly(True)
        widgets["Request"].setLineWrapMode(
            QtWidgets.QPlainTextEdit.WidgetWidth)

        widgets["RequestPlaceholder"].setParent(widgets["Request"])

        if activate:
            widgets["RequestPlaceholder"].setText(
                "Click 'Generate' to generate a new request"
            )
        else:
            widgets["RequestPlaceholder"].setText(
                "Click 'Deactivate' to deactivate and generate a new request"
                "\n\n"
                "CAUTION: If you deactivate Maya without deactivating\n"
                "online, your licence will still be considered active\n"
                "and cannot be reactivated.\n"
                "\n"
                "If this happens, contact support@ragdolldynamics.com"
            )

        widgets["ResponsePlaceholder"].setText("Paste the response here")
        widgets["ResponsePlaceholder"].setParent(widgets["Response"])

        for name in ("ResponsePlaceholder", "RequestPlaceholder"):
            placeholder = widgets[name]
            placeholder.setObjectName(name)
            placeholder.move(px(5), px(5))
            placeholder.show()

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(widgets["HelpText"], 0, 0)
        layout.addWidget(widgets["Serial"], 1, 0)

        if activate:
            layout.addWidget(widgets["Generate"], 5, 0, 1, 2)
            layout.addWidget(widgets["Request"], 6, 0, 1, 2)
            layout.addWidget(widgets["Response"], 7, 0, 1, 2)
            layout.addWidget(widgets["Activate"], 8, 0, 1, 2)
        else:
            layout.addWidget(widgets["Request"], 5, 0, 1, 2)
            layout.addWidget(widgets["Deactivate"], 6, 0, 1, 2)

        self.setStyleSheet("""
            QLabel {
                color: #eee;
            }

            #ResponsePlaceholder, #RequestPlaceholder {
                color: #777;
                opacity: 0.5;
            }

            QDialog {
                background: #333;
            }

            QPlainTextEdit {
                font-family: Courier;
                background: #222;
            }
        """)

        self.setMinimumSize(px(400), px(400))

        widgets["Generate"].clicked.connect(self.on_generate_clicked)
        widgets["Activate"].clicked.connect(self.on_activate_clicked)
        widgets["Deactivate"].clicked.connect(self.on_deactivate_clicked)
        widgets["Response"].textChanged.connect(self.on_response)

        self._activate = activate
        self._key = key
        self._widgets = widgets
        self._reqfname = os.path.join(
            tempfile.gettempdir(), "ragdollTempRequest.xml"
        )
        self._resfname = os.path.join(
            tempfile.gettempdir(), "ragdollTempResponse.xml"
        )

        if activate:
            self.on_generate_clicked()

        self.on_response()

    def on_deactivate_clicked(self):
        print("deactivation_request_to_file: %s" % self._reqfname)
        if licence.deactivation_request_to_file(self._reqfname) != 0:
            return log.warning("Failed, see Script Editor")

        self.refresh()

    def on_generate_clicked(self):
        if licence.activation_request_to_file(self._key, self._reqfname) != 0:
            return log.warning("Failed, see Script Editor")

        self.refresh()

    def on_activate_clicked(self):
        text = self._widgets["Response"].toPlainText()
        assert text, "No response found"

        with open(self._resfname, "w") as f:
            f.write(text)

        if licence.activate_from_file(self._resfname) != 0:
            return log.warning("Failed, see Script Editor")

        self.close()

    def on_response(self):
        text = self._widgets["Response"].toPlainText()
        self._widgets["ResponsePlaceholder"].setVisible(text == "")
        self._widgets["Activate"].setEnabled(text != "")

    def refresh(self):
        text = ""

        try:
            with open(self._reqfname) as f:
                text = f.read()
        except Exception:
            pass

        self.set_request(text)

    def set_request(self, text):
        self._widgets["Request"].setPlainText(text)
        self._widgets["RequestPlaceholder"].setVisible(text == "")


def center_window(window):
    # Center in the Maya window
    maya_window = MayaWindow()

    center = maya_window.size() / 2
    center -= window.size() / 2.0

    if center.width() > 0 and center.height() > 0:
        pos = maya_window.pos()
        pos += QtCore.QPoint(center.width(), center.height())
        window.move(pos)

    else:
        log.debug(
            "Failed. Couldn't figure out the Maya window size"
        )


def warn(title, message, call_to_action, actions, option=None):
    msgbox = QtWidgets.QMessageBox()
    msgbox.setWindowTitle(title)
    msgbox.setInformativeText(call_to_action)
    layout = msgbox.layout()

    buttons = []
    for index, (label, func) in enumerate(actions):
        button = msgbox.addButton(label, msgbox.ActionRole)
        buttons += [button]

    if option:
        def on_remind_me(value):
            options.write(option, bool(value))
            log.info("Toggled %s" % option)

        remind_me = QtWidgets.QCheckBox("Keep telling me")
        remind_me.setChecked(True)
        remind_me.stateChanged.connect(on_remind_me)

        layout.addWidget(remind_me, 3, 1, QtCore.Qt.AlignHCenter)

    if message.endswith(".png"):
        poster = _resource("ui", message)
        pixmap = QtGui.QPixmap(poster)
        label = QtWidgets.QLabel()
        label.setPixmap(pixmap)
        layout.addWidget(label, 0, 0, 1, 2)

    else:
        msgbox.setText(message)

    msgbox.exec_()

    clicked = msgbox.clickedButton()
    for index, button in enumerate(buttons):
        if button == clicked:
            _, func = actions[index]
            return func()

    return False


class MessageBoard(QtWidgets.QDialog):
    def __init__(self, records, parent=None):
        super(MessageBoard, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Ragdoll Message Board")
        self.setMinimumWidth(px(600))
        self.setMinimumHeight(px(300))

        panels = {
            "body": QtWidgets.QWidget(),
            "footer": QtWidgets.QWidget(),
        }

        widgets = {
            "board": QtWidgets.QListWidget(),
            "close": QtWidgets.QPushButton("Close"),
        }

        count = 1
        for index, record in enumerate(records):
            if index < len(records) - 1:
                next_record = records[index + 1]

                if next_record.msg == record.msg:
                    count += 1
                    continue

            msg = "%s" % record.msg

            if count > 1:
                msg += " (%d)" % count

            widgets["board"].addItem(msg)
            count = 1

        layout = QtWidgets.QVBoxLayout(panels["body"])
        layout.addWidget(widgets["board"])

        layout = QtWidgets.QHBoxLayout(panels["footer"])
        layout.addWidget(widgets["close"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(panels["body"])
        layout.addWidget(panels["footer"])
        layout.setContentsMargins(0, 0, 0, 0)

        widgets["close"].clicked.connect(self.close)

        self._panels = panels
        self._widgets = widgets


class Explorer(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    instance = None

    def __init__(self, parent=None):
        super(Explorer, self).__init__(parent)
        self.setWindowTitle("Ragdoll Explorer")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMinimumWidth(px(200))
        self.setMinimumHeight(px(100))

        model = qjsonmodel.QJsonModel(editable=False)

        view = QtWidgets.QTreeView()
        view.setModel(model)
        view.header().resizeSection(0, px(200))

        raw = QtWidgets.QCheckBox("Show Raw")
        raw.stateChanged.connect(self.on_raw_changed)

        debug = QtWidgets.QCheckBox("Show Debug")
        debug.stateChanged.connect(self.on_debug_changed)

        refresh = QtWidgets.QPushButton("Refresh")
        refresh.clicked.connect(self.reload)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(view, 0, 0, 1, 3)
        layout.addWidget(QtWidgets.QWidget(), 1, 0)
        layout.addWidget(raw, 1, 1)
        layout.addWidget(debug, 1, 2)
        layout.addWidget(refresh, 2, 0, 1, 3)
        layout.setColumnStretch(0, 1)

        timer = QtCore.QTimer(parent=self)  # Delete on close
        timer.setInterval(1000.0)  # ms
        timer.timeout.connect(self.reload)

        self._view = view
        self._model = model
        self._timer = timer
        self._dump = None
        self._raw = False
        self._debug = False

        Explorer.instance = self

        # For uninstall
        __.widgets[self.windowTitle()] = self

    def on_raw_changed(self, state):
        self._raw = bool(state)
        self.reload()

    def on_debug_changed(self, state):
        self._debug = bool(state)
        self.reload()

    def parse(self, dump, raw=False):
        if self._raw:
            dump["entities"] = {
                int(entity): value
                for entity, value in dump["entities"].items()
            }
        else:
            for key in dump["entities"].copy():
                value = dump["entities"].pop(key)

                if "NameComponent" not in value["components"]:
                    continue

                name = value["components"]["NameComponent"]

                # E.g. _:|root_grp|upperArm_ctl|rRigid1
                name = "|".join([name["members"]["shortestPath"],
                                 name["members"]["value"]])

                # E.g. upperArm_ctl|rRigid1
                name = name.rsplit(":", 1)[-1]

                # This should never really happen, it means
                # there are two entities for a Ragdoll node.
                index = 1
                orig = name
                while name in dump["entities"]:
                    name = "%s (%d!)" % (orig, index)
                    index += 1

                # Move members directly under the component
                dump["entities"][name] = {
                    k: v["members"]
                    for k, v in value["components"].items()
                }

                dump["entities"][name]["id"] = key

        return dump

    def load(self, dump):
        self._dump = dump
        self.reload()

        # Need to implement updating of individual fields,
        # in order to not loose selection and navigation
        # self._timer.start()

    def reload(self):
        assert self._dump is not None, "Call load() first"
        dump = self._dump

        if callable(dump):
            dump = dump(debug=self._debug)

        if isinstance(dump, i__.string_types):
            dump = json.loads(dump)

        assert isinstance(dump, dict)

        parsed = self.parse(dump)
        self._model.load(parsed)
        self._view.expandToDepth(0)


EntityRole = QtCore.Qt.UserRole + 0
TransformRole = QtCore.Qt.UserRole + 1
OptionsRole = QtCore.Qt.UserRole + 2
OccupiedRole = QtCore.Qt.UserRole + 3
HintRole = QtCore.Qt.UserRole + 4
PathRole = QtCore.Qt.UserRole + 5
SearchTermRole = QtCore.Qt.UserRole + 5


Load = "Load"
Reinterpret = "Reinterpret"


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
    selection_changed = QtCore.Signal(dump.Entity, object)  # entity, transform

    def __init__(self, parent=None):
        super(DumpWidget, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

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
            wid.setAttribute(QtCore.Qt.WA_StyledBackground)
            wid.setObjectName(name)

        for name, wid in widgets.items():
            wid.setAttribute(QtCore.Qt.WA_StyledBackground)
            wid.setObjectName(name)

        # Setup

        pixmap = _resource("icons", "right.png")
        pixmap = QtGui.QPixmap(pixmap)
        pixmap = pixmap.scaledToWidth(px(16), QtCore.Qt.SmoothTransformation)
        widgets["TargetView"].mouseMoved.connect(self.on_mouse_moved)
        widgets["TargetView"].setModel(models["TargetModel"])
        widgets["TargetView"].setUniformRowHeights(True)
        widgets["TargetView"].setFrameShape(QtWidgets.QFrame.NoFrame)
        widgets["TargetView"].header().hide()
        widgets["TargetView"].setSelectionBehavior(
            QtWidgets.QTreeView.SelectRows)

        # Layout

        layout = QtWidgets.QGridLayout(panels["Body"])
        layout.addWidget(widgets["TargetView"], 1, 0, 1, 3)
        layout.setRowStretch(1, 1)
        layout.setSpacing(px(5))

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(panels["Body"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(px(5))

        selection_model = widgets["TargetView"].selectionModel()
        selection_model.currentRowChanged.connect(self.on_target_changed)

        timer = QtCore.QTimer(parent=self)
        timer.setInterval(50.0)  # ms
        timer.setSingleShot(True)
        timer.timeout.connect(self._reset)

        font_info = QtGui.QFontInfo(self.font())

        self._reset_timer = timer
        self._widgets = widgets
        self._panels = panels
        self._models = models
        self._loader = None

        # For refreshing without losing selection
        self._last_selected_path = ""

        # For automatically determining tree view height
        self._item_height = font_info.pixelSize() * 1.5

        style = _scaled_stylesheet("""
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
        """)

        style += """
            QTreeView::item {
                height: %dpx;
            }
        """ % self._item_height

        self.setStyleSheet(style)

    def leaveEvent(self, event):
        self.hinted.emit("")  # Clear
        return super(DumpWidget, self).leaveEvent(event)

    def on_mouse_moved(self, pos):
        index = self._widgets["TargetView"].indexAt(pos)
        tooltip = index.data(HintRole)
        self.hinted.emit(tooltip or "")

    def on_target_changed(self, current, previous):
        parent = current.parent()
        item = self._models["TargetModel"].index(current.row(), 0, parent)

        entity = item.data(EntityRole)
        term = item.data(SearchTermRole)
        self.selection_changed.emit(entity, term)

        self._store_current_selection()

    def reset(self, loader):
        # Reset after a given time period.
        # This allows reset to get called frequently, without
        # actually incuring the cost of resetting the model each
        # time. It keeps the user interactivity swift and clean.
        self._loader = loader
        self._reset_timer.start()

    def _reset(self):
        analysis = self._loader.analyse()

        def _transform(data, entity):
            shape_icon = None

            if self._loader.registry.has(entity, "MarkerUIComponent"):
                marker_ui = self._loader.registry.get(entity,
                                                      "MarkerUIComponent")

                # TODO: Replace .get with []
                shape_icon = marker_ui.get("shapeIcon")
                shape_icon = {
                    "joint": "maya_joint.png",
                    "mesh": "maya_mesh.png",
                    "nurbsCurve": "maya_curve.png",
                    "nurbsSurface": "maya_surface.png",
                }.get(shape_icon, "maya_transform.png")

                shape_icon = _resource("icons", shape_icon)
                shape_icon = QtGui.QIcon(shape_icon)

            occupied = entity in analysis["occupied"]
            no_transform = entity not in analysis["entityToTransform"]
            term = analysis["searchTerms"][entity]

            color = self.palette().color(self.foregroundRole())
            color.setAlpha(100)

            if occupied:
                # Dim any transform that isn't getting imported
                icon = _resource("icons", "check.png")
                icon = QtGui.QIcon(icon)

                occupied = analysis["entityToTransform"][entity]
                path = occupied.shortestPath()

                data[QtCore.Qt.DisplayRole] += [path]
                data[QtCore.Qt.DecorationRole] += [icon]
                data[QtCore.Qt.ForegroundRole] = (color, color)

                data[TransformRole] = occupied
                data[HintRole] += [
                    "%s already has a marker" % path
                ]

            elif no_transform:
                # There isn't any transform for this entity
                if options.read("importCreateMissingTransforms"):
                    data[QtCore.Qt.DisplayRole] += ["New"]
                    icon = _resource("icons", "add.png")
                    icon = QtGui.QIcon(icon)
                    tooltip = "A new transform will be created for this marker"

                else:
                    data[QtCore.Qt.ForegroundRole] = (color, color)
                    data[QtCore.Qt.DisplayRole] += [term]
                    icon = _resource("icons", "questionmark.png")
                    icon = QtGui.QIcon(icon)
                    tooltip = (
                        "<b>%s</b> - could not be found in the scene" % term
                    )

                data[QtCore.Qt.DecorationRole] += [icon]
                data[HintRole] += [tooltip]

            else:
                icon = _resource("icons", "right.png")
                icon = QtGui.QIcon(icon)
                transform = analysis["entityToTransform"][entity]

                # These paths can get *quite* long, so help the user
                # by keeping things as short as possible.
                path = transform.shortestPath()

                data[QtCore.Qt.DecorationRole] += [icon]
                data[QtCore.Qt.DisplayRole] += [path]
                data[TransformRole] = transform
                data[HintRole] += [path]

        def _marker_icon(data, entity):
            Desc = self._loader.registry.get(
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
                "marker.png"
            )

            icon = _resource("icons", icon)
            icon = QtGui.QIcon(icon)

            data[QtCore.Qt.DecorationRole] += [icon]

        def _default_data(entity):
            search_term = analysis["searchTerms"].get(entity, "")

            return {
                QtCore.Qt.DisplayRole: [],
                QtCore.Qt.DecorationRole: [],
                QtCore.Qt.TextAlignmentRole: (
                    QtCore.Qt.AlignLeft,
                    QtCore.Qt.AlignLeft,
                    QtCore.Qt.AlignLeft,
                ),

                HintRole: [],
                TransformRole: None,
                EntityRole: entity,
                OptionsRole: None,
                SearchTermRole: search_term,
            }

        solver_to_item = {}
        group_to_item = {}
        marker_to_item = {}
        constraint_to_item = {}
        all_items = {}

        def _add_solvers(root_item):
            for entity in analysis["solvers"]:
                Name = self._loader.registry.get(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "solver.png")
                icon = QtGui.QIcon(icon)

                data = _default_data(entity)
                data[QtCore.Qt.DecorationRole] += [icon]
                data[QtCore.Qt.DisplayRole] += [label, ""]
                data[HintRole] += [
                    Name["shortestPath"],
                    "A new solver will be created"
                ]

                item = qargparse.GenericTreeModelItem(data)
                root_item.addChild(item)

                solver_to_item[entity] = item
                all_items[entity] = item

        def _add_groups(root_item):
            for entity in analysis["groups"]:
                Name = self._loader.registry.get(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]
                icon = _resource("icons", "suit.png")
                icon = QtGui.QIcon(icon)

                data = _default_data(entity)
                data[QtCore.Qt.DecorationRole] += [icon]
                data[QtCore.Qt.DisplayRole] += [label]
                data[HintRole] += [
                    label,
                    "A new group will be created with the contained markers."
                ]

                Scene = self._loader.registry.get(entity, "SceneComponent")
                parent_item = solver_to_item.get(Scene["entity"])

                # It would be odd for a group not to be part of a solver
                if not parent_item:
                    parent_item = root_item

                item = qargparse.GenericTreeModelItem(data)
                parent_item.addChild(item)

                group_to_item[entity] = item
                all_items[entity] = item

        def _add_markers(root_item):
            registry = self._loader.registry

            for entity in reversed(analysis["markers"]):
                Name = registry.get(entity, "NameComponent")
                MarkerUi = registry.get(entity, "MarkerUIComponent")
                name = MarkerUi["sourceTransform"].rsplit("|", 1)[-1]
                name = name.rsplit(":", 1)[-1]

                data = _default_data(entity)
                data[QtCore.Qt.DisplayRole] += [name]
                data[HintRole] += [
                    Name["value"]
                ]

                _marker_icon(data, entity)
                _transform(data, entity)

                Group = registry.get(entity, "GroupComponent")
                parent_item = group_to_item.get(Group["entity"])

                # A marker may or may not be part of a group,
                # but is always part of a solver.
                if not parent_item:
                    Scene = registry.get(entity, "SceneComponent")
                    parent_item = solver_to_item.get(Scene["entity"])

                if not parent_item:
                    parent_item = root_item

                item = qargparse.GenericTreeModelItem(data)
                parent_item.addChild(item)

                marker_to_item[entity] = item
                all_items[entity] = item

        def _add_constraints(root_item):
            registry = self._loader.registry

            for entity in analysis["constraints"]:
                Name = registry.get(entity, "NameComponent")
                label = Name["path"].rsplit("|", 1)[-1]

                if registry.has(entity, "FixedJointComponent"):
                    icon = _resource("icons", "fixed_constraint.png")
                    target = "New Weld Constraint"

                elif registry.has(entity, "DistanceJointComponent"):
                    icon = _resource("icons", "distance.png")
                    target = "New Distance Constraint"

                elif registry.has(entity, "PinJointComponent"):
                    icon = _resource("icons", "softpin.png")
                    target = "New Pin Constraint"

                else:
                    icon = _resource("icons", "constraint.png")
                    target = "New Constraint"

                icon = QtGui.QIcon(icon)

                right_icon = _resource("icons", "right.png")
                right_icon = QtGui.QIcon(right_icon)

                data = _default_data(entity)
                data[QtCore.Qt.DecorationRole] += [icon, right_icon]
                data[QtCore.Qt.DisplayRole] += [label, target]
                data[HintRole] += [
                    Name["shortestPath"],
                    Name["shortestPath"]
                ]

                Scene = registry.get(entity, "SceneComponent")
                parent_item = solver_to_item.get(Scene["entity"])

                # A marker may or may not be part of a group
                if not parent_item:
                    parent_item = root_item

                item = qargparse.GenericTreeModelItem(data)
                parent_item.addChild(item)

                constraint_to_item[entity] = item
                all_items[entity] = item

        view = self._widgets["TargetView"]
        model = self._models["TargetModel"]

        root_item = qargparse.GenericTreeModelItem({
            QtCore.Qt.DisplayRole: ("Source Node", "Target Node")
        })

        if not self._loader.is_valid():
            icon = _resource("icons", "error.png")
            icon = QtGui.QIcon(icon)
            invalid_item = qargparse.GenericTreeModelItem({
                QtCore.Qt.DisplayRole: "Empty or incompatible .rag file",
                QtCore.Qt.DecorationRole: icon,
                QtCore.Qt.ForegroundRole: QtGui.QColor("#F66"),
            })

            root_item.addChild(invalid_item)

            for reason in self._loader.invalid_reasons():
                log.debug("Failure reason: %s" % reason)

            self._widgets["TargetView"].setIndentation(0)

        else:
            _add_solvers(root_item)
            _add_groups(root_item)
            _add_markers(root_item)
            _add_constraints(root_item)

            self._widgets["TargetView"].setIndentation(px(11))

        if all_items == {}:
            icon = _resource("icons", "error.png")
            icon = QtGui.QIcon(icon)
            invalid_item = qargparse.GenericTreeModelItem({
                QtCore.Qt.DisplayRole: "No Markers found in .rag file",
                QtCore.Qt.DecorationRole: icon,
                QtCore.Qt.ForegroundRole: QtGui.QColor("#F66"),
            })

            root_item.addChild(invalid_item)

            for reason in self._loader.invalid_reasons():
                log.debug("Failure reason: %s" % reason)

            view.setIndentation(0)

        model.reset(root_item)

        # Make sure everything is nice and tight
        view.expandAll()
        view.resizeColumnToContents(0)
        view.resizeColumnToContents(1)

        count = len(all_items) + 3  # + header & padding & space
        height = self._item_height * count
        view.setMinimumHeight(height)

        self._restore_current_selection()

    def _store_current_selection(self):
        """Serialise selection to string"""

        self._last_selected_path = ""

        view = self._widgets["TargetView"]
        selection = view.selectionModel()

        try:
            index = selection.currentIndex()
        except IndexError:
            return

        # Select first column
        parent = index.parent()
        index = self._models["TargetModel"].index(index.row(), 0, parent)

        path = index.data(QtCore.Qt.DisplayRole)
        parent = index.parent()

        while parent.isValid():
            path = "%s/%s" % (parent.data(QtCore.Qt.DisplayRole), path)
            parent = parent.parent()

        self._last_selected_path = path

    def _restore_current_selection(self):
        """Deserialise selection from string"""

        model = self._models["TargetModel"]
        index = model.index(0, 0)

        for comp in self._last_selected_path.split("/"):
            for ii in range(model.rowCount(index)):
                child = index.child(ii, 0)

                if child.data(QtCore.Qt.DisplayRole) == comp:
                    index = child
                    break

        view = self._widgets["TargetView"]
        view.setCurrentIndex(index)


class ImportOptions(Options):
    before_reset = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(ImportOptions, self).__init__(*args, **kwargs)
        self.setWindowTitle("Import Options")

        widgets = {
            "DumpWidget": DumpWidget(),
            "Thumbnail": QtWidgets.QLabel(),
        }

        for nam, obj in widgets.items():
            obj.setObjectName(nam)

        # Integrate with other options
        layout = self._widgets["Options"].layout()
        layout.addWidget(widgets["DumpWidget"], 1, 0, 1, 2)
        layout.setRowStretch(1, 1)

        self.parser._row += 1  # For the next subclass

        # Map known options to this widget
        parser = self._widgets["Parser"]
        import_path = parser.find("importPath")
        import_paths = parser.find("importPaths")
        search_replace = parser.find("importSearchAndReplace")
        match_by = parser.find("importMatchBy")
        use_selection = parser.find("importUseSelection")
        namespace = self.parser.find("importNamespace")
        namespace_custom = self.parser.find("importNamespaceCustom")
        create_missing = self.parser.find("importCreateMissingTransforms")

        custom_visible = namespace.read() == namespace["items"][-1]
        namespace_custom.setVisible(custom_visible)

        import_path.changed.connect(self.on_path_changed)
        import_path.browsed.connect(self.on_browsed)
        import_paths.changed.connect(self.on_filename_changed)
        use_selection.changed.connect(self.reset)
        namespace.changed.connect(self.reset)
        namespace_custom.changed.connect(self.reset)
        search_replace.changed.connect(self.reset)
        match_by.changed.connect(self.reset)
        create_missing.changed.connect(self.reset)

        default_thumbnail = _resource("icons", "no_thumbnail.png")
        default_thumbnail = QtGui.QPixmap(default_thumbnail)
        default_thumbnail = default_thumbnail.scaled(
            px(200), px(128),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        # Add a thumbnail next to the import paths
        #  ________________________________
        # |o --- -- ---   |                |
        # |o ----- ---    |                |
        # |o --- -- ---   |                |
        # |o ----- ---    |   thumbnail    |
        # |o ----- ---    |                |
        # |o ----- ---    |                |
        # |_______________|________________|
        #
        qimport_paths = import_paths.widget()
        qimport_paths.setFixedHeight(px(128))
        layout = qimport_paths.layout()
        layout.setSpacing(px(2))
        layout.addWidget(widgets["Thumbnail"], 1, QtCore.Qt.AlignCenter)
        widgets["Thumbnail"].setAlignment(QtCore.Qt.AlignCenter)
        widgets["Thumbnail"].setFixedWidth(px(200))
        widgets["Thumbnail"].setFixedHeight(px(128))
        widgets["Thumbnail"].setPixmap(default_thumbnail)

        widgets["DumpWidget"].hinted.connect(self.on_hinted)
        widgets["DumpWidget"].selection_changed.connect(
            self.on_content_selection_changed)

        self._loader = None
        self._selection_callback = None
        self._previous_dirname = None
        self._read_timer = QtCore.QTimer()
        self._read_timer.setInterval(200)
        self._read_timer.setSingleShot(True)
        self._read_timer.timeout.connect(self.read)
        self._default_thumbnail = default_thumbnail

        # Keep superclass informed
        self._widgets.update(widgets)

        # Kick things off, a few ms after opening
        QtCore.QTimer.singleShot(200, self.on_path_changed)

        ImportOptions.instance = self

    def init(self, loader):
        self._loader = loader

    def on_hinted(self, hint):
        if hint:
            text = hint
        else:
            text = self._widgets["Hint"].property("defaultText")

        # Trim very long instances
        if len(text) > 150:
            text = "..." + text[-147:]

        self._widgets["Hint"].setText(text)

    def on_content_selection_changed(self, entity, term):
        current_selection = self.parser.find("importCurrentSelection")
        current_selection.write(("", ""))

        if not entity:
            return

        if self._loader.registry.has(entity, "MarkerUIComponent"):
            MarkerUi = self._loader.registry.get(entity, "MarkerUIComponent")
            source_text = MarkerUi["sourceTransform"]
        else:
            Name = self._loader.registry.get(entity, "NameComponent")
            source_text = Name["path"] or Name["value"]

        current_selection.write((source_text, term))

        # Focus on the start of the path, for search-and-replace
        current_selection = current_selection.widget().layout()
        source_widget = current_selection.itemAt(0).widget()
        dest_widget = current_selection.itemAt(1).widget()
        source_widget.setCursorPosition(0)
        dest_widget.setCursorPosition(0)

    @i__.with_timing
    def reset(self):
        namespace = self.parser.find("importNamespace")
        namespace_custom = self.parser.find("importNamespaceCustom")

        items = namespace["items"]
        item = items[namespace.read()]

        Off = 0
        FromFile = 1
        Custom = -1  # Last

        if item == items[Custom]:
            namespace_custom.setVisible(True)

        else:
            namespace_custom.setVisible(False)

            if item == items[Off]:
                options.write("importNamespaceCustom", " ")
                namespace_custom.write(" ", notify=False)

            elif item == items[FromFile]:
                options.write("importNamespaceCustom", "")
                namespace_custom.write("", notify=False)

            else:
                options.write("importNamespaceCustom", item)
                namespace_custom.write(item, notify=False)

        self.before_reset.emit()
        self._widgets["DumpWidget"].reset(self._loader)

    def load(self, data):
        assert isinstance(data, dict), "data must be a dictionary"

        current_path = self.parser.find("importPath")
        current_path.write("<raw>", notify=False)

        self._loader.read(data)
        self.reset()

    def read(self, fname=None):
        fname = fname or self.parser.find("importPath").read()
        assert isinstance(fname, i__.string_types), "fname must be string"

        current_path = self.parser.find("importPath")
        current_path.write(fname, notify=False)

        self._loader.read(fname)
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
            fnames = i__.sort_filenames(fnames)
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

        self._read_timer.start()

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
                qthumbnail = base64_to_pixmap(thumbnail)

                # Fit it to our widget
                qthumbnail = qthumbnail.scaled(
                    px(200), px(128),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )

        self._widgets["Thumbnail"].setPixmap(qthumbnail)

    def on_browsed(self):
        path, suffix = QtWidgets.QFileDialog.getOpenFileName(
            MayaWindow(),
            "Open Ragdoll Data",
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


class ExportOptions(Options):
    exported = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(ExportOptions, self).__init__(*args, **kwargs)
        self.setWindowTitle("Export Options")

        widgets = {
            "DumpWidget": DumpWidget(),
        }

        for nam, obj in widgets.items():
            obj.setObjectName(nam)

        # Integrate with other options
        layout = self._widgets["Options"].layout()
        layout.addWidget(widgets["DumpWidget"], 1, 0, 1, 2)
        layout.setRowStretch(1, 1)

        # Map known options to this widget
        parser = self._widgets["Parser"]
        export_path = parser.find("exportPath")
        export_path.browsed.connect(self.on_browsed)
        thumbnail = parser.find("exportThumbnail")
        thumbnail.write(_resource("icons", "no_thumbnail.png"))
        thumbnail.clicked.connect(self.on_thumbnail_clicked)

        self._loader = None
        self._loader_factory = None

        self._refresh_timer = QtCore.QTimer()
        self._refresh_timer.setInterval(200)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self.refresh)

        # Keep superclass informed
        self._widgets.update(widgets)

        ExportOptions.instance = self

    def init(self, loader_factory=None):
        self._loader_factory = loader_factory
        self._refresh_timer.start()

    def refresh(self, loader_factory=None):
        pixmap = view_to_pixmap()

        parser = self._widgets["Parser"]
        thumbnail = parser.find("exportThumbnail")
        thumbnail.write(pixmap)

        self._loader = self._loader_factory()
        self._widgets["DumpWidget"].reset(self._loader)

    def on_browsed(self):
        path, suffix = QtWidgets.QFileDialog.getSaveFileName(
            MayaWindow(),
            "Save Ragdoll Data",
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

        export_path = self.parser.find("exportPath")
        export_path.write(path)

    def on_thumbnail_clicked(self):
        self.refresh()


class DragButton(QtWidgets.QPushButton):
    dragged = QtCore.Signal(QtCore.QPoint, QtCore.QPoint)  # delta, total

    # The native pressed/release cancel when the cursor
    # exits the button area, but these won't.
    really_pressed = QtCore.Signal()
    really_released = QtCore.Signal()

    def mousePressEvent(self, event):
        self._press_position = None
        self._move_position = None

        if event.button() == QtCore.Qt.LeftButton:
            self._press_position = event.globalPos()
            self._move_position = event.globalPos()

        self.really_pressed.emit()
        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            new_pos = event.globalPos()

            try:
                delta = new_pos - self._move_position
                total = new_pos - self._press_position
            except TypeError:
                # Work around PySide2 bug in Maya 2020
                # Where subtraction won't work if the user
                # drags outside of the main Maya window
                delta = QtCore.QPoint(0, 0)
                total = QtCore.QPoint(0, 0)

            self.dragged.emit(delta, total)
            self._move_position = new_pos

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.really_released.emit()

        if self._press_position is not None:
            moved = event.globalPos() - self._press_position
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragButton, self).mouseReleaseEvent(event)


class Notification(QtWidgets.QDialog):
    instance = None

    def __init__(self, parent=None):
        super(Notification, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle("Notification Singleton")  # Not visible

        widgets = {
            "icon": QtWidgets.QLabel(),
            "title": QtWidgets.QLabel(),
            "message": QtWidgets.QLabel(),
        }

        for name, obj in widgets.items():
            obj.setObjectName(name)

        icon = _resource("icons", "attributes.png")
        icon = QtGui.QPixmap(icon)
        icon = icon.scaledToWidth(px(16), QtCore.Qt.SmoothTransformation)

        widgets["icon"].setPixmap(icon)

        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(5)
        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(spacer, 0, 0)
        layout.addWidget(widgets["icon"], 1, 0)
        layout.addWidget(widgets["title"], 1, 1)
        layout.addWidget(widgets["message"], 2, 1)

        # Align title with icon on the left-hand side
        layout.setColumnStretch(1, 1)

        # Account for icon and arrow offset in paintEvent
        layout.setContentsMargins(px(5), px(5), px(15), px(12))

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.animate_fade_out)
        timer.setInterval(2000)  # 2 seconds

        effect = QtWidgets.QGraphicsOpacityEffect(self)

        fade_in = QtCore.QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        fade_out = QtCore.QPropertyAnimation(effect, b"opacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade_out.finished.connect(self.close)

        self._fade_in = fade_in
        self._fade_out = fade_out
        self._fade_out_timer = timer
        self._arrow_pos = px(20)

        self.setGraphicsEffect(effect)
        self.setStyleSheet("""
        Notification {
            border: transparent;
            background: transparent;
        }

        #title {
            font-weight: bold;
            color: #eee;
            color: rgb(241, 126, 46);
        }

        #message {
            color: #ddd;
        }
        """)

        self._widgets = widgets
        Notification.instance = self
        __.widgets[self.windowTitle()] = self

    def shake_it(self, origin):
        # Shake the notification, to bring attention to it

        def move(start, end):
            start = QtCore.QPoint(origin.x() + px(start), origin.y())
            end = QtCore.QPoint(origin.x() + px(end), origin.y())

            anim = QtCore.QPropertyAnimation(self, b"pos")
            anim.setDuration(70)
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)

            return anim

        group = QtCore.QSequentialAnimationGroup(self)
        group.insertPause(0, 200)
        group.addAnimation(move(0, 20))
        group.addAnimation(move(20, -20))
        group.addAnimation(move(-20, 20))
        group.addAnimation(move(20, 0))
        group.start()

        # Prevent garbage collection, no other reason for keeping this
        self.__shkgrp = group

    def animate_fade_in(self):
        self._fade_out.stop()
        self._fade_in.start()

    def animate_fade_out(self):
        self._fade_out.start()

    def init(self, pos, title, message, persistent=False, shake=False):
        self._widgets["title"].setText(title)
        self._widgets["message"].setText(message)

        self.show()

        window = self.parent()
        relative_pos = window.mapFromGlobal(pos)
        on_left_side = relative_pos.x() < (window.width() / 2)

        self._arrow_pos = px(100)

        # Take into account global position relative the Maya Window
        if on_left_side:
            self._arrow_pos = px(20)

        pos -= QtCore.QPoint(self._arrow_pos, 0)

        self.move(pos)

        self.animate_fade_in()

        if shake:
            self.shake_it(pos)

        if not persistent:
            self._fade_out_timer.start()

    def paintEvent(self, event):
        rect = event.rect()
        painter = QtGui.QPainter(self)
        path = QtGui.QPainterPath()

        # Draw a shadow
        offset = px(5)
        path.moveTo(offset, offset + 10)
        path.lineTo(offset, offset + 10)
        path.lineTo(rect.width() - offset + 2, 10)
        path.lineTo(rect.width(), rect.height())
        path.lineTo(offset, rect.height())
        path.lineTo(0, 10)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
        painter.setBrush(QtGui.QColor(0, 0, 0, 127))
        painter.setRenderHint(painter.Antialiasing)
        painter.drawPath(path)

        # Draw a rectangle with an arrow pointing to the menu
        #
        #  __/\___________
        # |               |
        # | icon title    |
        # |      message  |
        # |               |
        # |_______________|
        #
        path = QtGui.QPainterPath()
        path.moveTo(0, 10)
        path.lineTo(0, 10)
        path.lineTo(self._arrow_pos + px(0), 10)
        path.lineTo(self._arrow_pos + px(5), 0)
        path.lineTo(self._arrow_pos + px(10), 10)
        path.lineTo(rect.width() - offset, 10)
        path.lineTo(rect.width() - offset, rect.height() - offset)
        path.lineTo(0, rect.height() - offset)
        path.lineTo(0, 10)

        pen = QtGui.QPen(
            QtGui.QColor("#222"),
            1,
            QtCore.Qt.SolidLine,
            QtCore.Qt.FlatCap,
            QtCore.Qt.MiterJoin
        )
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor("#444"))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        self.close()
        return super(Notification, self).mousePressEvent(event)


def notify(title, message, location="cursor", persistent=False, shake=False):
    """Produce a transient balloon popup with `title` and `message`

    Arguments:
        title (str): Header of the popup, a summary of the event
        message (str): Body of the popup, more details about the event
        location (str): Where on screen to display the notification

    """

    pointer = MQtUtil.mainWindow()
    maya_win = shiboken2.wrapInstance(i__.long(pointer), QtWidgets.QMainWindow)

    instance = Notification.instance
    if instance is not None and shiboken2.isValid(instance):
        note = instance
    else:
        note = Notification(parent=maya_win)

    pos = QtGui.QCursor.pos()

    if location == "menu" and __.menu:
        menu = maya_win.menuBar()

        def find_action(text):
            for action in menu.actions():
                if action.text().startswith(text):
                    return action

        action = find_action("Ragdoll")

        if action:
            geo = menu.actionGeometry(action)
            pos = geo.topLeft()
            pos += QtCore.QPoint(geo.width() / 2, geo.height())
            pos = menu.mapToGlobal(pos)

    note.init(pos, title, message, persistent, shake=shake)

    return note


def view_to_pixmap(size=None):
    """Render currently active 3D viewport as a QPixmap"""
    from maya import cmds

    # # Ensure we're picking whichever model panel is active,
    panel = cmds.playblast(activeEditor=True)

    image = om.MImage()
    view = omui.M3dView.getM3dViewFromModelEditor(panel)
    view.readColorBuffer(image, True)

    # Translate from Maya -> Qt jargon
    image.verticalFlip()

    # Abracadabra!
    osize = size or QtCore.QSize(512, 256)
    isize = image.getSize()
    buf = ctypes.c_ubyte * isize[0] * isize[1]
    buf = buf.from_address(i__.long(image.pixels()))

    # Vimsalabim!
    qimage = QtGui.QImage(
        buf, isize[0], isize[1], QtGui.QImage.Format_RGB32
    ).rgbSwapped()

    return QtGui.QPixmap.fromImage(qimage).scaled(
        osize.width(), osize.height(),
        QtCore.Qt.KeepAspectRatioByExpanding,
        QtCore.Qt.SmoothTransformation
    )


def pixmap_to_base64(pixmap):
    array = QtCore.QByteArray()
    buffer = QtCore.QBuffer(array)

    buffer.open(QtCore.QIODevice.WriteOnly)
    pixmap.save(buffer, "png")

    return bytes(array.toBase64())


def base64_to_pixmap(base64):
    data = QtCore.QByteArray.fromBase64(base64)
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(data)
    return pixmap
