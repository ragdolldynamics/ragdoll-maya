import os
import re
import math
import types
import logging
import tempfile
import shiboken2
from datetime import datetime
from PySide2 import QtCore, QtWidgets, QtGui

try:
    from PySide2 import QtWebEngineWidgets
except ImportError as e:
    # In our tests (on mottosso/maya:2020 image), this module could fail
    # on import because of missing libXss.so.1 object. And if that happens,
    # video playback feature will be disabled (for playing .webm file in
    # asset view).
    def _raise_err(*_, **__): raise e
    QtWebEngineWidgets = types.ModuleType("QtWebEngineWidgets")
    setattr(QtWebEngineWidgets, "QWebEngineView", type(
        "QWebEngineView", (), dict(__init__=_raise_err)
    ))
    HAS_QT_WEB_ENGINE = False
else:
    HAS_QT_WEB_ENGINE = True

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # py2

from . import base
from .. import ui, internal


__throwaway = datetime.strptime("2012-01-01", "%Y-%m-%d")
# This is a workaround for a Py2 bug:
#   The first use of strptime is not thread safe.
#   See: https://bugs.python.org/issue7980#msg221094
#        https://bugs.launchpad.net/openobject-server/+bug/947231/comments/8

log = logging.getLogger("ragdoll")
px = base.px

with open(ui._resource("ui", "style_welcome.css")) as f:
    stylesheet = f.read()


ENABLE_SIDEBAR = False

# padding levels
PD1 = px(20)
PD2 = px(14)
PD3 = px(10)
PD4 = px(6)
SCROLL_WIDTH = px(18)

VIDEO_WIDTH, VIDEO_HEIGHT = px(217), px(122)
CARD_PADDING = px(3)
CARD_ROUNDING = px(8)
CARD_WIDTH = VIDEO_WIDTH + (CARD_PADDING * 2)
CARD_HEIGHT = VIDEO_HEIGHT + (CARD_PADDING * 2)

ANCHOR_SIZE = px(42)
SIDEBAR_WIDTH = ANCHOR_SIZE + (PD3 * 2)
SPLASH_WIDTH = px(650)
SPLASH_HEIGHT = px(110)
WINDOW_WIDTH = SPLASH_WIDTH + (PD3 * 2) + SCROLL_WIDTH
WINDOW_HEIGHT = px(534)  # just enough to see the first 2 rows of assets
if ENABLE_SIDEBAR:
    WINDOW_WIDTH += SIDEBAR_WIDTH


def _tint_color(pixmap, color):
    painter = QtGui.QPainter(pixmap)
    painter.setCompositionMode(painter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()


class _ProductStatus(base.ProductStatus):

    def get_gradient(self):
        if self.is_trial_errored():
            return "#b53bed", "#652626"
        elif self.is_expired():
            return "#ed3b4b", "#652626"
        elif self.is_floating() and not self.has_lease():
            return "#ff934c", "#fc686f"
        elif self.is_perpetual():
            return "#01e9bd", "#007cde"
        elif self.is_trial():
            return "#38f8d4", "#13dc5c"
        else:
            return "#216383", "#71bfbc"


product_status = _ProductStatus()
internet_request = base.InternetRequestHandler()
asset_library = base.AssetLibrary()


class GreetingSplash(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(GreetingSplash, self).__init__(parent)
        gradient = QtGui.QColor("#3f7e81"), QtGui.QColor("#468f79")
        pixmap = QtGui.QPixmap(ui._resource("ui", "welcome-banner.png"))
        pixmap = pixmap.scaled(
            SPLASH_WIDTH,
            SPLASH_HEIGHT,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        self.setMinimumWidth(SPLASH_WIDTH)
        self.setFixedHeight(SPLASH_HEIGHT)
        self._image = pixmap
        self._gradient = gradient

    # This color picker is for testing gradient and picking good
    # color to blend with splash image.
    #
    #     c_picker = QtWidgets.QColorDialog(self)
    #     c_picker.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    #     c_picker.currentColorChanged.connect(self.on_color_changed)
    #     c_picker.show()
    #
    # def on_color_changed(self, color):
    #     self._gradient = (color, self._gradient[1])
    #     self.repaint()

    def paintEvent(self, event):
        """
          Splash image                 Status
         .---------------------.--------------.
        |   RAGDOLL            |               |
        |      DYNAMICS        |               |
        |______________________|_______________|

        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        r = px(8)
        w = self.width()
        h = self.height()

        clip_path = QtGui.QPainterPath()
        clip_path.setFillRule(QtCore.Qt.WindingFill)
        clip_path.addRoundedRect(QtCore.QRect(0, 0, w, h), r, r)
        clip_path.addRect(0, h - r, w, r)
        painter.setClipPath(clip_path.simplified())

        spacing = px(400)
        gradient = QtGui.QLinearGradient()
        gradient.setStart(spacing, h)
        gradient.setFinalStop(w, 0)
        gradient.setColorAt(0, self._gradient[0])
        gradient.setColorAt(1, self._gradient[1])

        painter.fillRect(spacing, 0, w - spacing, h, gradient)
        painter.drawPixmap(0, 0, self._image)


class GreetingTopRight(QtWidgets.QWidget):
    connection_checked = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(GreetingTopRight, self).__init__(parent)

        widgets = {
            "NoInternet": QtWidgets.QWidget(),
            "NoInternetIcon": QtWidgets.QLabel(),
            "NoInternetText": QtWidgets.QLabel(),
            "Expiry": QtWidgets.QWidget(),
            "ExpiryIcon": QtWidgets.QLabel(),
            "ExpiryDate": QtWidgets.QLabel(),
        }

        widgets["NoInternetIcon"].setFixedSize(px(12), px(12))
        _icon = ui._resource("ui", "cloud-slash.svg").replace("\\", "/")
        widgets["NoInternetIcon"].setStyleSheet("image: url(%s);" % _icon)
        widgets["NoInternetText"].setText("No internet for checking update")
        widgets["NoInternetText"].setStyleSheet("color: #b0b0b0;")
        widgets["NoInternet"].setStyleSheet("background: transparent;")
        widgets["NoInternet"].setVisible(False)

        widgets["Expiry"].setFixedHeight(base.ProductReleasedView.ButtonHeight)
        widgets["ExpiryDate"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["ExpiryIcon"].setFixedSize(px(12), px(12))
        widgets["ExpiryDate"].setStyleSheet("color: #d3d3d3;")

        layout = QtWidgets.QHBoxLayout(widgets["NoInternet"])
        layout.setContentsMargins(0, 0, px(2), 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addWidget(widgets["NoInternetIcon"])
        layout.addSpacing(px(4))
        layout.addWidget(widgets["NoInternetText"])

        layout = QtWidgets.QHBoxLayout(widgets["Expiry"])
        layout.setContentsMargins(px(4), 0, px(8), 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addWidget(widgets["ExpiryIcon"])
        layout.addSpacing(px(6))
        layout.addWidget(widgets["ExpiryDate"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, px(4), PD4, PD4 + px(3))
        layout.setSpacing(0)
        layout.addWidget(widgets["NoInternet"])
        layout.addStretch(1)
        layout.addWidget(widgets["Expiry"], alignment=QtCore.Qt.AlignRight)

        self.setFixedHeight(SPLASH_HEIGHT)

        self._widgets = widgets

        self.connection_checked.connect(self.set_offline_hint)

    def set_expiry(self):
        p_ = product_status
        perpetual = p_.is_perpetual()
        expiry_date = p_.expiry_date()
        expiry = expiry_date.strftime("%Y.%m.%d") if expiry_date else None
        aup_date = p_.aup_date()
        aup = aup_date.strftime("%Y.%m.%d") if aup_date else None
        expired = p_.is_expired()

        status = "%s  %s" % (
            "AUP" if perpetual else "Expiry", aup if perpetual else expiry,
        )
        self._widgets["ExpiryDate"].setText(status)

        if expired:
            icon = ui._resource("ui", "exclamation-circle-fill.svg")
            self._widgets["Expiry"].setStyleSheet(
                "border-radius: %dpx; background: #FF000000;" % px(9))
        else:
            icon = ui._resource("ui", "check-circle-fill.svg")
            self._widgets["Expiry"].setStyleSheet(
                "border-radius: %dpx; background: #44000000;" % px(9))

        icon = icon.replace("\\", "/")
        self._widgets["ExpiryIcon"].setStyleSheet(
            "background: transparent; image: url(%s);" % icon)

    def set_offline_hint(self, can_connect):
        is_offline = not can_connect
        self._widgets["NoInternet"].setVisible(is_offline)


class GreetingInteract(QtWidgets.QWidget):
    history_fetched = QtCore.Signal(list)

    def __init__(self, parent=None):
        super(GreetingInteract, self).__init__(parent)

        widgets = {
            "TopRight": GreetingTopRight(),
            "Timeline": base.ProductTimelineWidget(),
        }

        widgets["Timeline"].setMinimumWidth(SPLASH_WIDTH)

        overlay = base.OverlayWidget(self)
        layout = QtWidgets.QVBoxLayout(overlay)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["TopRight"])
        layout.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(widgets["Timeline"])

        self.setFixedHeight(
            SPLASH_HEIGHT +
            widgets["Timeline"].minimumHeight()
        )
        self._widgets = widgets

        self.history_fetched.connect(self.set_timeline)

    def status_widget(self):
        return self._widgets["TopRight"]

    def timeline_widget(self):
        return self

    def set_timeline(self, release_history):
        versions = set(release_history)
        current = product_status.current_version()
        versions.add(current)
        expiry_date = (product_status.aup_date()
                       if product_status.is_perpetual()
                       else product_status.expiry_date())

        self._widgets["Timeline"].set_data(
            released_versions=versions,
            current_ver=current,
            expiry_date=expiry_date,
        )
        self._widgets["Timeline"].draw()


class GreetingPage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GreetingPage, self).__init__(parent)

        widgets = {
            "Splash": GreetingSplash(),
            "Interact": GreetingInteract(),
        }

        overlay = base.OverlayWidget(parent=self)  # for overlay
        overlay.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        layout = QtWidgets.QVBoxLayout(overlay)
        layout.setContentsMargins(PD4, 0, PD4, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Interact"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(PD4, 0, PD4, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Splash"])
        layout.addStretch(1)

        self.setFixedHeight(widgets["Interact"].height())

        self._widgets = widgets

    def status_widget(self):
        return self._widgets["Interact"].status_widget()

    def timeline_widget(self):
        return self._widgets["Interact"].timeline_widget()

    def splash_widget(self):
        return self._widgets["Splash"]


class AssetVideoPlayer(QtWebEngineWidgets.QWebEngineView):

    def __init__(self, parent=None):
        super(AssetVideoPlayer, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.page().setBackgroundColor(QtGui.QColor("#353535"))
        self.page().loadFinished.connect(self.on_page_loaded)
        self._is_loaded = False
        self._first_play = True

    def on_page_loaded(self, ok):
        self._is_loaded = ok
        if self._first_play:
            self.play()

    def play(self):
        if self._is_loaded:
            self._first_play = False
            self.page().runJavaScript("""
            document.getElementById("video").play();
            """)
        else:
            self._first_play = True
            # We cannot play the video until the page is loaded.

    def pause(self):
        self._first_play = False
        self.page().runJavaScript("""
        document.getElementById("video").pause();
        """)

    def set_video(self, video):
        html_code = """
        <html><body style="background:transparent; margin:0px;">
        <div  class="video-mask"
              style="width:100%; height:100%; position:absolute;
                    overflow:hidden; border-radius: {r}px;
                    font-family:Open Sans; color:white;">

            <video id="video" loop preload="none" muted="muted"
                   style="width:100%; position:absolute;"
                <source src="{video}" type="video/webm">
                <p>HTML5 Video element not supported.</p></video>

            <div style="line-height:{h}px; text-align:center;">Loading...</div>

        </div></body></html>
        """.format(video=video, r=CARD_ROUNDING, h=VIDEO_HEIGHT)
        self.setHtml(html_code, baseUrl=QtCore.QUrl("file://"))

        if QtCore.__version_info__ < (5, 13):
            # The web-engine (Chromium 73) that shipped with Qt 5.13 and
            #   before somehow cannot render border-radius properly.
            rounded_rect = QtCore.QRectF(0, 0, VIDEO_WIDTH, VIDEO_HEIGHT)
            path = QtGui.QPainterPath()
            path.addRoundedRect(rounded_rect, CARD_ROUNDING, CARD_ROUNDING)

            region = QtGui.QRegion(path.toFillPolygon().toPolygon())
            self.setMask(region)


class AssetVideoPoster(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(AssetVideoPoster, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._image = None

    def set_poster(self, poster):
        """
        Args:
            poster (QtGui.QPixmap):
        """
        self._image = poster

    def paintEvent(self, event):
        """
        :param QtGui.QPaintEvent event:
        """

        if self._image is None:
            return

        w = self.width()
        h = self.height()

        # try centering the poster
        c = self._image.rect().center()
        x = c.x() - int(w / 2)
        y = c.y() - int(h / 2)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        rounded_rect = QtCore.QRectF(
            CARD_PADDING,
            CARD_PADDING,
            w - (CARD_PADDING * 2),
            h - (CARD_PADDING * 2),
        )
        path = QtGui.QPainterPath()
        path.addRoundedRect(rounded_rect, CARD_ROUNDING, CARD_ROUNDING)
        painter.setClipPath(path)

        if self._image.isNull():
            # background
            painter.setBrush(QtGui.QColor("#404040"))
            painter.drawRect(event.rect())
            # big cross X
            painter.setPen(QtGui.QColor("#8a8a8a"))
            painter.drawLine(0, 0, w, h)
            painter.drawLine(0, h, w, 0)

            def draw_text(text, y_offset, bg, fg):
                fr = painter.fontMetrics().boundingRect(text)
                pos = event.rect().center()
                pos.setY(int(h / 2) + y_offset)
                fr.moveCenter(pos)
                # backdrop
                painter.setBrush(QtGui.QColor(bg))
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawRect(fr.adjusted(-px(8), -px(1), px(8), px(1)))
                # text
                painter.setPen(QtGui.QColor(fg))
                painter.drawText(fr, text)

            draw_text("No Image ", -px(8), "#181818", "#8a8a8a")
        else:
            painter.drawPixmap(0, 0, self._image, x, y, w, h)


class AssetVideoFooter(base.OverlayWidget):

    def __init__(self, parent=None):
        super(AssetVideoFooter, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._label = ""
        self._dots = []

    def set_data(self, label, dots):
        self._label = label
        self._dots = dots

    def paintEvent(self, event):
        """
        :param QtGui.QPaintEvent event:
        """
        w = self.width()
        h = self.height()
        footer_h = int(h / 3) - px(5)
        dot_radius = px(5)
        dot_padding = px(6)
        dot_gap = px(3)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        # draw footer
        #   make a half rounded rect (sharped top, rounded bottom)
        #   ___________________
        #  |                  |
        #  |                  |
        #  \_________________/
        #
        # note: this footer is one pixel wider than the poster, to ensure
        #   no glitchy rounding corner after overlay.
        #
        footer_rect = QtCore.QRectF(
            CARD_PADDING - 1,
            h - footer_h - CARD_PADDING + 1,
            w - (CARD_PADDING * 2) + 2,  # +2 because both left and right
            footer_h,
        )
        footer_top_left = QtCore.QRectF(
            CARD_PADDING - 1,
            h - footer_h - CARD_PADDING + 1,
            CARD_ROUNDING,
            CARD_ROUNDING,
        )
        footer_top_right = QtCore.QRectF(
            w - CARD_PADDING - CARD_ROUNDING + 1,
            h - footer_h - CARD_PADDING + 1,
            CARD_ROUNDING,
            CARD_ROUNDING,
        )
        path = QtGui.QPainterPath()
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(footer_rect, CARD_ROUNDING, CARD_ROUNDING)
        path.addRect(footer_top_left)
        path.addRect(footer_top_right)
        painter.setClipPath(path.simplified())
        painter.fillRect(event.rect(), QtGui.QColor("#BB202020"))

        # draw text
        text_rect = footer_rect.adjusted(px(10), px(3), 0, 0)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(text_rect, self._label)

        # draw tag dots
        painter.setPen(QtCore.Qt.NoPen)
        dot_rect = QtCore.QRectF(
            footer_rect.x() + footer_rect.width() - dot_padding - dot_radius,
            footer_rect.y() + footer_rect.height() - dot_padding - dot_radius,
            dot_radius,
            dot_radius,
        )
        offset = -(dot_gap + dot_radius)
        for color in self._dots:  # right to left
            painter.setBrush(QtGui.QColor(color))
            dot_rect = dot_rect.adjusted(offset, 0, offset, 0)
            painter.drawEllipse(dot_rect)


class AssetCardItem(QtWidgets.QWidget):
    asset_opened = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetCardItem, self).__init__(parent=parent)

        widgets = {
            "Footer": AssetVideoFooter(self),
            "Poster": AssetVideoPoster(),
        }
        effects = {
            "Poster": QtWidgets.QGraphicsOpacityEffect(widgets["Poster"]),
        }
        animations = {
            "Poster": QtCore.QPropertyAnimation(effects["Poster"], b"opacity")
        }

        widgets["Poster"].setAttribute(QtCore.Qt.WA_StyledBackground)
        widgets["Poster"].setGraphicsEffect(effects["Poster"])
        widgets["Poster"].setFixedWidth(CARD_WIDTH)
        widgets["Poster"].setFixedHeight(CARD_HEIGHT)

        effects["Poster"].setOpacity(1)
        animations["Poster"].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Poster"])

        animations["Poster"].finished.connect(self.on_transition_end)

        self.setAutoFillBackground(True)
        self._widgets = widgets
        self._effects = effects
        self._animations = animations
        self._file_path = None
        self._video_link = None
        self._video_player = None

    def _playable(self):
        return self._video_link and HAS_QT_WEB_ENGINE

    def init_item(self, index):
        self._widgets["Footer"].set_data(
            index.data(AssetCardModel.NameRole),
            [],
        )
        self._file_path = index.data(AssetCardModel.AssetRole)

    def update_item(self, index):
        """
        :param QtCore.QModelIndex index:
        """
        file_path = index.data(AssetCardModel.AssetRole)
        lib_path, fname = os.path.split(file_path)

        def resource(path):
            if os.path.isfile(path):
                return path

            try:
                result = urlparse(path)
            except AttributeError:
                pass
            else:
                if all([result.scheme, result.netloc]):
                    return path  # is net location

            video_path = os.path.join(lib_path, path)
            return video_path if os.path.isfile(video_path) else None

        poster = index.data(AssetCardModel.PosterRole)
        video = index.data(AssetCardModel.VideoRole)
        self._widgets["Poster"].set_poster(poster)
        self._widgets["Footer"].set_data(
            index.data(AssetCardModel.NameRole),
            list(index.data(AssetCardModel.TagsRole).values()),
        )
        self._file_path = index.data(AssetCardModel.AssetRole)
        self._video_link = resource(video)

    def on_clicked(self):
        if os.path.isfile(self._file_path):
            self.asset_opened.emit(self._file_path)
        else:
            log.error("Asset file missing: %s" % self._file_path)

    def on_transition_end(self):
        leave = self._animations["Poster"].endValue() == 1.0
        if leave:
            self._effects["Poster"].setEnabled(False)
            if self._video_player is not None:
                self._video_player.pause()

    def enterEvent(self, event):
        if not self._playable():
            return
        self._effects["Poster"].setEnabled(True)
        anim = self._animations["Poster"]
        current = self._effects["Poster"].opacity()
        anim.stop()
        anim.setDuration(int(500 * current))
        anim.setStartValue(current)
        anim.setEndValue(0.0)
        anim.start()

        if self._video_player is None:
            player = AssetVideoPlayer(self)
            player.set_video(self._video_link)
            player.setFixedWidth(VIDEO_WIDTH)
            player.setFixedHeight(VIDEO_HEIGHT)

            self._widgets["Poster"].raise_()
            self._widgets["Footer"].raise_()
            player.move(CARD_PADDING, CARD_PADDING)
            player.show()

            self._video_player = player
        self._video_player.play()

    def leaveEvent(self, event):
        if not self._playable():
            return
        anim = self._animations["Poster"]
        current = self._effects["Poster"].opacity()
        anim.stop()
        anim.setDuration(500 - int(500 * current))
        anim.setStartValue(current)
        anim.setEndValue(1.0)
        anim.start()

    def mousePressEvent(self, event):
        super(AssetCardItem, self).mousePressEvent(event)
        self.on_clicked()


class AssetCardModel(base.BaseItemModel):
    card_created = QtCore.Signal(QtCore.QModelIndex)
    card_updated = QtCore.Signal(QtCore.QModelIndex)
    load_finished = QtCore.Signal(int)

    SortRole = QtCore.Qt.UserRole + 20
    # (dict) path data to load asset
    #   "asset": path/url to the asset zip archive
    #   "entry": the name of file in archive to load the asset
    AssetRole = QtCore.Qt.UserRole + 10
    # (str) name of the asset
    NameRole = QtCore.Qt.UserRole + 11
    # (str) path/url to the video file
    VideoRole = QtCore.Qt.UserRole + 12
    # (str) path to the poster image
    PosterRole = QtCore.Qt.UserRole + 13
    # (dict) tags of the asset
    #   <tag name>: <tag color>
    TagsRole = QtCore.Qt.UserRole + 14

    def __init__(self, parent=None):
        super(AssetCardModel, self).__init__(parent=parent)
        self._worker = None
        self._row_map = dict()

    def clear(self):
        self._row_map.clear()
        super(AssetCardModel, self).reset()

    def terminate(self):
        if base.NO_WORKER_THREAD_QT or self._worker is None:
            return
        self._worker.wait()
        self._worker.deleteLater()

    def start(self):
        if base.NO_WORKER_THREAD_QT:
            for job in asset_library._cache:
                self._do(job)
        else:
            if self._worker is not None:
                self._worker.start()

    def attach_library(self, queue):
        if self._worker is not None:
            return
        if base.NO_WORKER_THREAD_QT:
            self._worker = False  # just not None
        else:
            self._worker = base.Thread(
                self._threaded_consume, args=[queue], parent=self
            )

    def create_item(self, data):
        if data["path"] in self._row_map:
            return

        item = QtGui.QStandardItem()
        item.setData(os.path.basename(data["path"]), AssetCardModel.NameRole)
        item.setData(data["path"], AssetCardModel.AssetRole)
        item.setData(data["path"], AssetCardModel.SortRole)

        self._row_map[data["path"]] = self.rowCount()
        self.appendRow(item)
        self.card_created.emit(item.index())

    def update_item(self, data):
        row = self._row_map[data["path"]]
        index = self.index(row, 0)

        self.setData(index, data["name"], AssetCardModel.NameRole)
        self.setData(index, data["thumbnail"], AssetCardModel.PosterRole)
        self.setData(index, data["video"], AssetCardModel.VideoRole)
        self.setData(index, data["tags"], AssetCardModel.TagsRole)

        self.card_updated.emit(index)

    def _do(self, job):
        if job["type"] == "start":
            self.clear()
        elif job["type"] == "create":
            self.create_item(job["payload"])
        elif job["type"] == "update":
            self.update_item(job["payload"])
        elif job["type"] == "finish":
            self.load_finished.emit(self.rowCount())

    def _threaded_consume(self, queue):
        while True:
            job = queue.get()  # this guy blocks!

            if job["type"] == "terminate":
                queue.task_done()
                break
            else:
                self._do(job)

            queue.task_done()

    def update_tags(self, index, tags):
        self.setData(index, tags, AssetCardModel.TagsRole)

    def reload(self):
        if self._worker is None:
            return
        asset_library.stop()
        asset_library.reload()
        self.start()


class AssetCardProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(AssetCardProxyModel, self).__init__(parent=parent)
        self.setSortRole(AssetCardModel.SortRole)
        self._tags = set()

    def sort_name(self):
        order = QtCore.Qt.AscendingOrder
        self.sort(0, order=order)

    def set_tags(self, tags):
        self._tags = set(tags)
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        tags = model.data(index, AssetCardModel.TagsRole)
        if tags is None:  # loading not completed
            return True
        item_tags = tags.keys()
        return any(t in self._tags for t in item_tags) if self._tags else True


class AssetCardView(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(AssetCardView, self).__init__(parent=parent)
        self._horizontal_offset = 0
        self.setViewMode(self.ListMode)
        self.setResizeMode(self.Adjust)
        self.setLayoutMode(self.Batched)
        self.setBatchSize(50)
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setGridSize(QtCore.QSize(CARD_WIDTH, CARD_HEIGHT))
        self.setUniformItemSizes(True)
        self.setSelectionRectVisible(False)
        self.setMinimumWidth(CARD_WIDTH)
        self.viewport().setMinimumWidth(CARD_WIDTH)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def horizontalOffset(self):
        return self._horizontal_offset

    def adjust_viewport(self):
        viewport = self.viewport()
        width = viewport.width()
        item_count = self.model().rowCount()
        # expand view to show all items
        column_count = math.floor(width / CARD_WIDTH)
        row_count = math.ceil(item_count / column_count)
        viewport_height = row_count * CARD_HEIGHT
        viewport.setFixedHeight(viewport_height)
        self.setFixedHeight(viewport_height)


class AssetTag(QtWidgets.QPushButton):

    def __init__(self, name, color, parent=None):
        super(AssetTag, self).__init__(parent=parent)
        hover = QtGui.QColor(color).darker().toRgb()
        self.setText(name)
        self.setCheckable(True)
        self.setStyleSheet("""
        AssetTag {{
            background: transparent;
            height: {h}px;
            border: 1px solid {color};
            border-radius: {r}px;
            padding: 1px {p1}px 1px {p2}px;
            text-align: top center;
        }}
        AssetTag:checked {{
            background: {color};
        }}
        AssetTag:hover:!checked {{
            background: {hover};
        }}
        """.format(color=color, hover=hover.name(),
                   h=px(16), r=px(6), p1=px(6), p2=px(4)))


class AssetTagList(QtWidgets.QWidget):
    tagged = QtCore.Signal(set)

    def __init__(self, parent=None):
        super(AssetTagList, self).__init__(parent)
        base.FlowLayout(self)
        self._tags = dict()

    def add_tag(self, tag_name, tag_color):
        """Return consistence tag color across assets

        Return and maintaining tag color consistency for color dots in
        asset item footer.

        Different asset may have the same tag but different color, so we
        will only take color from the first same named tag. And the first
        one should be from the asset file that is most recently edited.

        """
        if tag_name in self._tags:
            return self._tags[tag_name]
        self._tags[tag_name] = tag_color

        button = AssetTag(tag_name, tag_color)
        button.setIcon(QtGui.QIcon(ui._resource("ui", "tag-fill.svg")))
        button.setCheckable(True)
        button.toggled.connect(self.on_tag_toggled)
        self.layout().addWidget(button)

        return tag_color

    def clear(self):
        self._tags.clear()
        layout = self.layout()
        item = layout.takeAt(0)
        while item:
            item.widget().deleteLater()
            item = layout.takeAt(0)

    def on_tag_toggled(self, _):
        activated = set()
        for btn in self.children():
            if isinstance(btn, QtWidgets.QPushButton) and btn.isChecked():
                activated.add(btn.text())
        self.tagged.emit(activated)


class AssetListPage(QtWidgets.QWidget):
    asset_opened = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetListPage, self).__init__(parent=parent)

        widgets = {
            "Tags": AssetTagList(),
            "List": AssetCardView(),
            "Status": QtWidgets.QLabel(),
            "Path": QtWidgets.QLineEdit(),
            "Browse": QtWidgets.QPushButton(),
            "Reload": QtWidgets.QPushButton(),
        }

        models = {
            "Source": AssetCardModel(),
            "Proxy": AssetCardProxyModel(),
        }

        widgets["Status"].setFixedHeight(px(40))
        widgets["Status"].setAlignment(QtCore.Qt.AlignHCenter)
        widgets["Status"].setVisible(False)
        widgets["Browse"].setIcon(QtGui.QIcon(
            ui._resource("ui", "folder.svg")))
        widgets["Reload"].setIcon(QtGui.QIcon(
            ui._resource("ui", "arrow-counterclockwise.svg")))
        widgets["Path"].setReadOnly(False)
        widgets["Path"].setText(asset_library.get_user_path())

        models["Proxy"].setSourceModel(models["Source"])
        widgets["List"].setModel(models["Proxy"])
        widgets["Browse"].setEnabled(False)
        widgets["Reload"].setEnabled(False)

        _path_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_path_row)
        layout.setContentsMargins(CARD_PADDING, 0, CARD_PADDING, 0)
        layout.addWidget(QtWidgets.QLabel("Extra Assets"))
        layout.addSpacing(PD4)
        layout.addWidget(widgets["Path"])
        layout.addWidget(widgets["Browse"])
        layout.addWidget(widgets["Reload"])

        _tags = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_tags)
        layout.setContentsMargins(CARD_PADDING, 0, CARD_PADDING, 0)
        layout.addWidget(widgets["Tags"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(PD4 - CARD_PADDING, 0, PD4 - CARD_PADDING, 0)
        layout.setSpacing(PD3)
        layout.addWidget(_tags)
        layout.addWidget(widgets["List"])
        layout.addWidget(widgets["Status"])
        layout.addWidget(_path_row)

        models["Source"].card_created.connect(self.on_card_created)
        models["Source"].card_updated.connect(self.on_card_updated)
        models["Source"].load_finished.connect(self.on_load_finished)
        widgets["Tags"].tagged.connect(self.on_tag_changed)
        widgets["Browse"].clicked.connect(self.on_asset_browse_clicked)
        widgets["Reload"].clicked.connect(self.on_asset_reload_clicked)
        widgets["Path"].editingFinished.connect(self.on_asset_extra_changed)

        self._models = models
        self._widgets = widgets

        asset_library.attach_consumer(models["Source"])

    def resizeEvent(self, event):
        super(AssetListPage, self).resizeEvent(event)
        self._widgets["List"].adjust_viewport()

    def on_card_created(self, index):
        widget = AssetCardItem()
        item = self._models["Source"].itemFromIndex(index)
        item.setSizeHint(widget.sizeHint())
        self._widgets["List"].setIndexWidget(
            self._models["Proxy"].mapFromSource(index),
            widget,
        )
        widget.init_item(index)

        # connect signal
        widget.asset_opened.connect(self.asset_opened)
        # update sorting
        self._widgets["List"].adjust_viewport()
        self._models["Proxy"].sort_name()

    def on_card_updated(self, index):
        raw_tags = self._models["Source"].data(index, AssetCardModel.TagsRole)
        colored_tags = dict()
        for name, color in raw_tags.items():
            color = self._widgets["Tags"].add_tag(name, color)
            colored_tags[name] = color

        self._models["Source"].update_tags(index, colored_tags)
        proxy_index = self._models["Proxy"].mapFromSource(index)
        widget = self._widgets["List"].indexWidget(proxy_index)
        widget.update_item(index)

    def on_load_finished(self, count):
        asset_loaded = bool(count)

        status = "No assets found, try adding a path in Extra Assets below"
        self._widgets["Status"].setText(status)
        self._widgets["Status"].setVisible(not asset_loaded)
        self._widgets["Path"].setEnabled(True)
        self._widgets["Browse"].setEnabled(True)
        self._widgets["Reload"].setEnabled(True)
        self._widgets["List"].setVisible(asset_loaded)
        self._widgets["List"].adjust_viewport()

    @internal.with_timing
    def on_tag_changed(self, tags):
        _view = self._widgets["List"]
        _proxy = self._models["Proxy"]
        _proxy.set_tags(tags)

        for row in range(_proxy.rowCount()):
            index = _proxy.index(row, 0)
            if _view.indexWidget(index) is None:
                src_index = _proxy.mapToSource(index)
                self.on_card_created(src_index)
                self.on_card_updated(src_index)
        _view.adjust_viewport()

    @internal.with_timing
    def on_asset_browse_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(dialog.Directory)
        dialog.setViewMode(dialog.Detail)
        dialog.setOptions(dialog.ReadOnly)
        dialog.setAcceptMode(dialog.AcceptOpen)

        if dialog.exec_():
            self._widgets["Path"].setText(dialog.selectedFiles()[0])
            self.on_asset_extra_changed()

    @internal.with_timing
    def on_asset_reload_clicked(self):
        self._reload()

    @internal.with_timing
    def on_asset_extra_changed(self):
        path = self._widgets["Path"].text()
        asset_library.set_user_path(path)
        self._reload()

    def _reload(self):
        self._widgets["Path"].setEnabled(False)
        self._widgets["Browse"].setEnabled(False)
        self._widgets["Reload"].setEnabled(False)
        self._widgets["Tags"].clear()
        self._models["Source"].reload()

    def start_worker(self):
        self._models["Source"].start()
        if not base.NO_WORKER_THREAD_QT:
            asset_library.rewind()

    def terminate_worker(self):
        self._models["Source"].terminate()


class LicenceStatusPlate(QtWidgets.QWidget):
    """A little colorful badge that indicates current licencing status
    """

    def __init__(self, parent=None):
        super(LicenceStatusPlate, self).__init__(parent=parent)
        self.setObjectName("LicencePlate")

        widgets = {
            "Product": QtWidgets.QLabel(),
        }

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Product"])

        self._widgets = widgets

    def set_product(self):
        p_ = product_status
        suffix = "Expired" if p_.is_expired() else ""
        suffix = "Error" if p_.is_trial_errored() else suffix
        stop_0, stop_1 = p_.get_gradient()
        name = "%s %s" % (p_.name(), suffix)
        self._widgets["Product"].setText(name)
        self._widgets["Product"].setStyleSheet("""
            max-height: %dpx;
            color: black;
            font-family: Sora;
            padding: 0px %dpx;
            border-radius: %dpx;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1, stop:0 %s, stop:1 %s
            );
        """ % (px(22), px(6), px(10), stop_0, stop_1))

    def paintEvent(self, event):
        # required for applying background styling
        opt = QtWidgets.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(
            QtWidgets.QStyle.PE_Widget, opt, painter, self
        )
        super(LicenceStatusPlate, self).paintEvent(event)


class SecretToggle(QtWidgets.QWidget):
    """A button that covers product key as password '******'
    """

    def __init__(self, parent=None):
        super(SecretToggle, self).__init__(parent=parent)

        widgets = {
            "Peek": base.ToggleButton(),
        }
        icon_show = ui._resource("ui", "eye-fill.svg")
        icon_hide = ui._resource("ui", "eye-slash.svg")
        widgets["Peek"].set_unchecked_icon(QtGui.QIcon(icon_hide))
        widgets["Peek"].set_checked_icon(QtGui.QIcon(icon_show))
        widgets["Peek"].setFixedWidth(px(26))
        widgets["Peek"].setChecked(True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD4)
        layout.addWidget(widgets["Peek"])

        widgets["Peek"].toggled.connect(self.on_secret_toggled)

        self._widgets = widgets

    def set_secret_shown(self, value):
        self._widgets["Peek"].setChecked(value)

    def on_secret_toggled(self, value):
        for line in self.findChildren(QtWidgets.QLineEdit):
            line.setEchoMode(line.Normal if value else line.Password)


def labeling(widget, label_text, vertical=False, **kwargs):
    c = QtWidgets.QWidget()
    label = QtWidgets.QLabel(label_text)
    _Layout = QtWidgets.QVBoxLayout if vertical else QtWidgets.QHBoxLayout
    _layout = _Layout(c)
    _layout.setContentsMargins(0, 0, 0, 0)
    _layout.setSpacing(PD3)
    _layout.addWidget(label)
    _layout.addWidget(widget, **kwargs)
    return c


class LicenceKeyEdit(QtWidgets.QLineEdit):
    switched = QtCore.Signal()

    Offline = 0
    Online = 1

    def __init__(self, switch_to, parent=None):
        super(LicenceKeyEdit, self).__init__(parent=parent)
        self.setObjectName("LicenceKeyEdit")
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_menu_requested)
        self._switch = switch_to

    def on_menu_requested(self):
        menu = self.createStandardContextMenu()

        if not product_status.is_activated():
            # For now, only for user who has trouble to activate
            #
            switch = QtWidgets.QAction(
                "Online Mode" if self._switch else "Offline Mode", menu
            )
            switch.triggered.connect(self.switched.emit)

            menu.addSeparator()
            menu.addAction(switch)

        menu.move(QtGui.QCursor.pos())
        menu.show()


class LicenceNodeLock(QtWidgets.QWidget):
    """Node-Lock (Online) licencing page of `LicenceSetupPanel` class
    """
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    switch_offline = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceNodeLock, self).__init__(parent=parent)

        widgets = {
            "ProductName": LicenceStatusPlate(),
            "ProductKey": LicenceKeyEdit(LicenceKeyEdit.Offline),
            "ProcessBtn": QtWidgets.QPushButton(),
            "Secret": SecretToggle(),
        }

        _ = "Your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        widgets["ProductKey"].setPlaceholderText(_)
        widgets["Secret"].layout().addWidget(widgets["ProductKey"])

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD4)
        layout.addWidget(widgets["ProductName"])
        layout.addWidget(widgets["Secret"], stretch=1)
        layout.addWidget(widgets["ProcessBtn"])

        widgets["ProductKey"].switched.connect(self.switch_offline.emit)
        widgets["ProductKey"].textEdited.connect(self.on_product_key_edited)
        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)

        self._widgets = widgets

    def on_product_key_edited(self, text):
        codes = text.split("-")
        is_key = (
            len(codes) == 7 and
            all(len(c) == 4 and c.isalnum() for c in codes)
        )
        self._widgets["ProcessBtn"].setEnabled(is_key)

    def on_process_clicked(self):
        action = self._widgets["ProcessBtn"].text()
        if action == "Activate":
            self.node_activated.emit(self._widgets["ProductKey"].text())
        else:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Deactivate Ragdoll")
            msgbox.setTextFormat(QtCore.Qt.RichText)
            msgbox.setText(
                "Do you want me to deactivate Ragdoll on this machine? "
                "I'll try and revert to a trial licence."
                "<br><br>"
                "<b>WARNING</b>: This will close your currently opened file"
            )
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes |
                                      QtWidgets.QMessageBox.No)

            if msgbox.exec_() != QtWidgets.QMessageBox.Yes:
                log.info("Cancelled")
                return
            self.node_deactivated.emit()

    def status_update(self):
        self._widgets["ProductName"].set_product()
        if product_status.is_activated():
            self._widgets["Secret"].set_secret_shown(False)
            self._widgets["ProductKey"].setText(product_status.key())
            self._widgets["ProductKey"].setReadOnly(True)
            self._widgets["ProcessBtn"].setText("Deactivate")
            self._widgets["ProcessBtn"].setEnabled(True)
        else:
            self._widgets["Secret"].set_secret_shown(True)
            self._widgets["ProductKey"].setText("")
            self._widgets["ProductKey"].setReadOnly(False)
            self._widgets["ProcessBtn"].setText("Activate")
            self._widgets["ProcessBtn"].setEnabled(False)


class LicenceNodeLockOffline(QtWidgets.QWidget):
    """Node-Lock (Offline) licencing page of `LicenceSetupPanel` class
    """
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)
    switch_online = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceNodeLockOffline, self).__init__(parent=parent)

        widgets = {
            "ProductName": LicenceStatusPlate(),
            "OfflineHint": QtWidgets.QLabel(),
            "ProductKey": LicenceKeyEdit(LicenceKeyEdit.Online),
            "RequestRow": QtWidgets.QWidget(),
            "CopyRequest": QtWidgets.QPushButton(),
            "WebsiteURL": QtWidgets.QLabel(),
            "Response": QtWidgets.QLineEdit(),
            "DeactivateText": QtWidgets.QLabel(),
            "ConfirmText": QtWidgets.QLabel(" Confirm Deactivated"),
            "ProcessBtn": QtWidgets.QPushButton(),
            "Secret": SecretToggle(),
        }
        widgets.update({
            "RequestWidget": labeling(widgets["RequestRow"], "1."),
            "ResponseWidget": labeling(widgets["Response"], "2."),
            "ConfirmWidget": labeling(widgets["ConfirmText"], "2.", stretch=1),
            "DeactivateHint": labeling(widgets["DeactivateText"], "CAUTION",
                                       vertical=True)
        })
        effects = {
            "Hint": QtWidgets.QGraphicsOpacityEffect(),
        }
        animations = {
            "Hint": QtCore.QPropertyAnimation(effects["Hint"], b"opacity")
        }

        _ = "Your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        widgets["ProductKey"].setPlaceholderText(_)
        widgets["Secret"].layout().addWidget(widgets["ProductKey"])

        widgets["OfflineHint"].setObjectName("HintMessage")
        widgets["OfflineHint"].setText(
            "Cannot reach Ragdoll licencing server.\n"
            "Require another internet accessible device to complete "
            "following process."
        )
        widgets["DeactivateText"].setObjectName("HintMessage")
        widgets["DeactivateText"].setText(
            'Only after you have completed the process, press "Dismiss" '
            'button down right below\nto remove this message.'
            "\n\n"
            "If you deactivate Maya without deactivating"
            "online,\nyour licence will still be considered active "
            "and cannot be reactivated.\n"
            "If this happens, contact support@ragdolldynamics.com"
        )

        widgets["CopyRequest"].setObjectName("IconTextPushButton")
        widgets["CopyRequest"].setText(" Copy Request Code")
        widgets["CopyRequest"].setIcon(
            QtGui.QIcon(ui._resource("ui", "clipboard.svg"))
        )

        effects["Hint"].setOpacity(0)
        animations["Hint"].setEasingCurve(QtCore.QEasingCurve.OutCubic)
        animations["Hint"].setDuration(500)
        animations["Hint"].setStartValue(0)
        animations["Hint"].setEndValue(1)
        widgets["WebsiteURL"].setGraphicsEffect(effects["Hint"])
        widgets["WebsiteURL"].setOpenExternalLinks(True)
        widgets["WebsiteURL"].setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        widgets["WebsiteURL"].setText(
            """
            <style> p {color: #acacac;} a:link {color: #80e5cc;}</style>
            <p>Copied! Now paste it to
            <a href=\"https://ragdolldynamics.com/offline\">
            ragdolldynamics.com/offline</a> (internet required)
            </p>
            """
        )
        widgets["Response"].setPlaceholderText(
            "Paste response code from https://ragdolldynamics.com/offline"
        )

        layout = QtWidgets.QHBoxLayout(widgets["RequestRow"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD3)
        layout.addWidget(widgets["CopyRequest"])
        layout.addWidget(widgets["WebsiteURL"])

        head = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(head)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["ProductName"])
        layout.addWidget(widgets["Secret"])
        layout.addSpacing(PD2)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(PD1, 0, PD2, 0)
        layout.setSpacing(PD3)
        layout.addWidget(widgets["OfflineHint"])
        layout.addWidget(widgets["DeactivateHint"])
        layout.addWidget(widgets["RequestWidget"], 0, QtCore.Qt.AlignLeft)
        layout.addWidget(widgets["ResponseWidget"])
        layout.addWidget(widgets["ConfirmWidget"])

        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD2)
        layout.addWidget(head)
        layout.addWidget(body, stretch=1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(panel)
        layout.addWidget(widgets["ProcessBtn"], 0, QtCore.Qt.AlignBottom)

        widgets["ProductKey"].switched.connect(self.switch_online.emit)
        widgets["ProductKey"].textEdited.connect(self.on_product_key_edited)
        widgets["CopyRequest"].clicked.connect(self.on_copy_request_clicked)
        widgets["Response"].textEdited.connect(self.on_response_edited)
        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)
        animations["Hint"].finished.connect(
            lambda: effects["Hint"].setEnabled(False))

        _temp = tempfile.gettempdir()
        self._reqfname = os.path.join(_temp, "ragdollTempRequest.xml")
        self._resfname = os.path.join(_temp, "ragdollTempResponse.xml")
        self._dreqfname = os.path.join(_temp, "ragdollTempDeRequest.xml")
        self._keyfname = os.path.join(_temp, "ragdollTempProductKey.txt")
        self._widgets = widgets
        self._effects = effects
        self._animations = animations

    def on_product_key_edited(self, text):
        codes = text.split("-")
        is_key = (
            len(codes) == 7 and
            all(len(c) == 4 and c.isalnum() for c in codes)
        )
        # Temporarily save user input key for offline activation
        if is_key:
            # key format validated, save it for now until activated offline
            self.write_temp_key()
        elif not text:
            self.remove_temp_key()

        self._widgets["RequestWidget"].setEnabled(is_key)
        self._widgets["ResponseWidget"].setEnabled(is_key)

    def on_copy_request_clicked(self):
        key = self._widgets["ProductKey"].text()
        self.offline_activate_requested.emit(key, self._reqfname)
        # show hint
        self._effects["Hint"].setEnabled(True)
        self._animations["Hint"].start()

    def on_response_edited(self, text):
        is_response = text.strip().endswith("</Response>")
        self._widgets["ProcessBtn"].setEnabled(is_response)

    def on_process_clicked(self):
        action = self._widgets["ProcessBtn"].text()
        if action == "Activate":
            with open(self._resfname, "w") as _f:
                _f.write(self._widgets["Response"].text())
            self.node_activated.emit(self._resfname)
        else:
            self.node_deactivated.emit()

    def request_offline_deactivate(self):
        self.offline_deactivate_requested.emit(self._dreqfname)

    def set_product_key(self, key):
        self._widgets["ProductKey"].setText(key)
        self.on_product_key_edited(key)

    def set_activation_request(self):
        try:
            with open(self._reqfname) as _f:
                request_code = _f.read()
        except Exception:
            self._widgets["ResponseWidget"].setEnabled(False)
        else:
            base.write_clipboard(request_code)
            self._widgets["ResponseWidget"].setEnabled(True)

    def is_deactivation_requested(self):
        return os.path.isfile(self._dreqfname)

    def read_deactivation_request_file(self):
        try:
            with open(self._dreqfname, "r") as _f:
                return _f.read().strip()
        except IOError:
            return ""

    def remove_deactivation_request_file(self):
        try:
            os.remove(self._dreqfname)
        except OSError:
            pass

    def read_temp_key(self):
        try:
            with open(self._keyfname, "r") as _f:
                return _f.read().strip()
        except IOError:
            return ""

    def write_temp_key(self):
        product_key = self._widgets["ProductKey"].text()
        with open(self._keyfname, "w") as _f:
            _f.write(product_key)

    def remove_temp_key(self):
        try:
            os.remove(self._keyfname)
        except OSError:
            pass

    def status_update(self):
        self._widgets["ProductName"].set_product()
        _temp_key = self.read_temp_key()

        if self.is_deactivation_requested():
            self._widgets["Secret"].set_secret_shown(False)
            self._widgets["ProductKey"].setText(_temp_key)
            self._widgets["ProductKey"].setReadOnly(True)
            self._widgets["ProcessBtn"].setText("Dismiss")
            self._widgets["ProcessBtn"].setEnabled(True)
            self._widgets["RequestWidget"].setEnabled(True)
            self._widgets["ResponseWidget"].hide()
            self._widgets["ConfirmWidget"].show()

        else:
            # restore product key for continuing offline activation
            self._widgets["Secret"].set_secret_shown(True)
            self._widgets["ProductKey"].setText(_temp_key)
            self._widgets["ProductKey"].setReadOnly(False)
            self._widgets["Response"].setText("")
            self._widgets["ProcessBtn"].setText("Activate")
            self._widgets["ProcessBtn"].setEnabled(False)
            self._widgets["ResponseWidget"].show()
            self._widgets["ConfirmWidget"].hide()
            self._widgets["RequestWidget"].setEnabled(bool(_temp_key))
            self._widgets["ResponseWidget"].setEnabled(bool(_temp_key))


class LicenceFloating(QtWidgets.QWidget):
    """Float licencing page of `LicenceSetupPanel` class
    """
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceFloating, self).__init__(parent=parent)

        widgets = {
            "ProductName": LicenceStatusPlate(),
            "ServerIP": QtWidgets.QLineEdit(),
            "ServerPort": QtWidgets.QLineEdit(),
            "ProcessBtn": QtWidgets.QPushButton(),
            "Secret": SecretToggle(),
        }

        widgets["ServerIP"].setReadOnly(True)  # set from env var
        widgets["ServerPort"].setReadOnly(True)  # set from env var
        widgets["Secret"].layout().addWidget(widgets["ServerIP"], stretch=7)
        widgets["Secret"].layout().addWidget(widgets["ServerPort"], stretch=3)
        widgets["Secret"].set_secret_shown(False)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD4)
        layout.addWidget(widgets["ProductName"])
        layout.addWidget(widgets["Secret"], stretch=1)
        layout.addWidget(widgets["ProcessBtn"])

        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)

        self._widgets = widgets

    def status_update(self):
        self._widgets["ProductName"].set_product()

        p_ = product_status
        action = "Drop Lease" if p_.has_lease() else "Request Lease"
        ip, port = p_.licence_server()
        self._widgets["ServerIP"].setText(ip)
        self._widgets["ServerPort"].setText(port)
        self._widgets["ProcessBtn"].setText(action)
        self._widgets["ProcessBtn"].setEnabled(True)

    def on_process_clicked(self):
        action = self._widgets["ProcessBtn"].text()
        if action == "Request Lease":
            self.float_requested.emit()
        else:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Drop Lease")
            msgbox.setTextFormat(QtCore.Qt.RichText)
            msgbox.setText(
                "Are you sure? "
                "<br><br>"
                "<b>WARNING</b>: This will close your currently opened file"
            )
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Yes |
                                      QtWidgets.QMessageBox.No)

            if msgbox.exec_() != QtWidgets.QMessageBox.Yes:
                log.info("Cancelled")
                return
            self.float_dropped.emit()


class LicenceSetupPanel(QtWidgets.QWidget):
    """The main widget that runs licencing

    A widget that enables users to activate/deactivate licence, node-lock
    or floating, and shows licencing status.

    This widget is DCC App agnostic, you must connect corresponding signals
    respectively so to collect licencing data from DCC App.

    """
    licence_updated = QtCore.Signal()
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(LicenceSetupPanel, self).__init__(parent=parent)

        widgets = {
            "Pages": base.SizeAdjustedStackedWidget(),
            "NodeLock": LicenceNodeLock(),
            "NodeLockOffline": LicenceNodeLockOffline(),
            "Floating": LicenceFloating(),
        }

        widgets["Pages"].addWidget(widgets["NodeLock"])
        widgets["Pages"].addWidget(widgets["NodeLockOffline"])
        widgets["Pages"].addWidget(widgets["Floating"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Pages"])

        widgets["Floating"].float_requested.connect(self.float_requested)
        widgets["Floating"].float_dropped.connect(self.float_dropped)
        widgets["NodeLock"].node_activated.connect(self.node_activated)
        widgets["NodeLock"].node_deactivated.connect(self.node_deactivated)
        widgets["NodeLock"].switch_offline.connect(
            self.on_online_switch_to_offline)
        widgets["NodeLockOffline"].node_activated.connect(self.node_activated)
        widgets["NodeLockOffline"].node_deactivated.connect(
            self.on_offline_deactivated)
        widgets["NodeLockOffline"].offline_activate_requested.connect(
            self.offline_activate_requested)
        widgets["NodeLockOffline"].offline_deactivate_requested.connect(
            self.offline_deactivate_requested)
        widgets["NodeLockOffline"].switch_online.connect(
            self.on_offline_switch_to_online)

        self._widgets = widgets

    def on_offline_activate_requested(self):
        self._widgets["NodeLockOffline"].set_activation_request()

    def on_offline_deactivate_requested(self):
        self._widgets["NodeLockOffline"].write_temp_key()

    def on_offline_deactivated(self):
        self._widgets["NodeLockOffline"].remove_deactivation_request_file()
        self._widgets["NodeLockOffline"].remove_temp_key()
        self.licence_updated.emit()

    def on_online_switch_to_offline(self):
        """For activation only
        """
        self._widgets["Pages"].setCurrentIndex(1)
        w = self._widgets["NodeLockOffline"]
        w.status_update()

    def on_offline_switch_to_online(self):
        """For activation only
        """
        self._widgets["Pages"].setCurrentIndex(0)
        w = self._widgets["NodeLock"]
        w.status_update()

    def switch_to_offline_activate(self, key):
        """When online activation failed
        """
        self._widgets["Pages"].setCurrentIndex(1)
        w = self._widgets["NodeLockOffline"]
        w.set_product_key(key)
        w.status_update()

    def switch_to_offline_deactivate(self):
        """When online deactivation failed
        """
        self._widgets["Pages"].setCurrentIndex(1)
        w = self._widgets["NodeLockOffline"]
        w.set_product_key(product_status.key())
        w.request_offline_deactivate()

    def status_update(self):
        p_ = product_status
        pages = self._widgets["Pages"]

        if self._widgets["NodeLockOffline"].is_deactivation_requested():
            log.info("Ragdoll is offline deactivated")
            # ensure user completed the process before dumping request code
            pages.setCurrentIndex(1)

        elif p_.is_floating():
            log.info("Ragdoll is floating")

            pages.setCurrentIndex(2)

        else:
            if p_.is_trial():
                if p_.is_trial_errored():
                    log.error(p_.trial_error_msg())
                elif p_.is_expired():
                    log.info("Ragdoll is expired")
                else:
                    log.info("Ragdoll is in trial mode")
            else:
                # node-lock
                if p_.is_activated():
                    log.info("Ragdoll is activated")
                else:
                    log.info("Ragdoll is deactivated")

            pages.setCurrentIndex(0)

        current_page = pages.currentWidget()
        current_page.status_update()


class LicencePage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LicencePage, self).__init__(parent=parent)

        widgets = {
            "Body": LicenceSetupPanel(),
        }

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(PD4, 0, PD4, 0)
        layout.addWidget(widgets["Body"])

        self._widgets = widgets

    def input_widget(self):
        """Exposed for connecting signals
        Returns:
            LicenceSetupPanel
        """
        return self._widgets["Body"]


class SideBarAnchorLayout(QtWidgets.QVBoxLayout):
    def invalidate(self):
        pass  # so we could arrange anchor position freely


class SideBar(QtWidgets.QFrame):
    """Anchor bar on the left side

    To show this, variable `ENABLE_SIDEBAR` (at the top of this file)
    has to be `True`.

    """
    anchor_clicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(SideBar, self).__init__(parent=parent)

        widgets = {
            "Body": QtWidgets.QWidget(),
        }

        self.setFixedWidth(SIDEBAR_WIDTH)

        layout = SideBarAnchorLayout(widgets["Body"])
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(PD3)
        layout.addSpacing(PD1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Body"])

        self.setStyleSheet("background: #2b2b2b;")
        self._widgets = widgets
        self._anchors = []

    def add_anchor(self, name, image, color):
        icon_size = int(ANCHOR_SIZE * 0.6)
        icon_size = QtCore.QSize(icon_size, icon_size)

        unchecked_icon = QtGui.QIcon(ui._resource("ui", image))
        pixmap = unchecked_icon.pixmap(icon_size)
        _tint_color(pixmap, QtGui.QColor("#333333"))
        checked_icon = QtGui.QIcon(pixmap)

        anchor = base.ToggleButton()
        anchor.setChecked(False)
        anchor.setIconSize(icon_size)

        anchor.set_checked_icon(checked_icon)
        anchor.set_unchecked_icon(unchecked_icon)

        anchor.setStyleSheet("""
            QPushButton {{
                height: {size}px;
                width: {size}px;
                border-radius: {radius}px;
                background: transparent;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: #454545;
            }}
            QPushButton:checked {{
                background: {color};
            }}
        """.format(color=color, size=ANCHOR_SIZE, radius=int(ANCHOR_SIZE / 2)))

        self._widgets["Body"].layout().addWidget(anchor)
        self._anchors.append(anchor)

        def on_clicked():
            for w in [w for w in self._anchors if w is not anchor]:
                w.setChecked(False)
            anchor.setChecked(True)
            self.anchor_clicked.emit(name)
        anchor.clicked.connect(on_clicked)

        return name

    def set_current_anchor(self, index):
        for i, anchor in enumerate(self._anchors):
            anchor.setChecked(i == index)

    def slide_anchors(self, widget_pos, slider_pos):
        count = len(self._anchors)
        view = self.height()  # should be the same as page height
        for index, pos in enumerate(widget_pos):
            anchor = self._anchors[index]
            offset = pos - slider_pos
            min_pos = PD1 + index * (ANCHOR_SIZE + PD3)
            max_pos = view - (PD1 + (count - index) * (ANCHOR_SIZE + PD3))

            if offset <= min_pos:
                anchor.move(anchor.x(), min_pos)
                self.set_current_anchor(index)
            elif offset > max_pos:
                anchor.move(anchor.x(), max_pos)
            else:
                anchor.move(anchor.x(), offset)


def _scaled_stylesheet(style):
    """Replace any mention of <num>px with scaled version

    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.

    """

    output = []
    for line in style.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            line = "".join([
                ("%dpx" % px(int(p))) if p.isdigit() else p
                for p in re.split(r"(\d*)px", line)
            ])
        output += [line]
    result = "\n".join(output)
    result = result % dict(
        res=ui._resource().replace("\\", "/"),
    )
    return result


class WelcomeWindow(base.SingletonMainWindow):
    """A GUI for welcoming user and as a Ragdoll asset library
    """
    asset_opened = QtCore.Signal(str)
    licence_updated = QtCore.Signal()
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    node_activate_inet_returned = QtCore.Signal(str)
    node_deactivate_inet_returned = QtCore.Signal()
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)

    @staticmethod
    def preload():
        """Launch heave load functions before GUI is up

        These run in separate threads (if not `RAGDOLL_SINGLE_THREADED_*`),
        on plugin load time.

        """

        def callback_website(*args):
            if WelcomeWindow.instance_weak is not None:
                self = WelcomeWindow.instance_weak()
                if self is not None and shiboken2.isValid(self):
                    _ = self._widgets["Greet"]
                    _.status_widget().connection_checked.emit(*args)

        req_website = base.RequestRagdollWebsite(callback_website)
        internet_request.submit(req_website)

        def callback_history(*args):
            if WelcomeWindow.instance_weak is not None:
                self = WelcomeWindow.instance_weak()
                if self is not None and shiboken2.isValid(self):
                    _ = self._widgets["Greet"]
                    _.timeline_widget().history_fetched.emit(*args)

        req_history = base.RequestVersionHistory(callback_history)
        internet_request.submit(req_history)

        internet_request.process()
        asset_library.reload()

    def __init__(self, parent=None):
        super(WelcomeWindow, self).__init__(parent=parent)
        self.protected = True

        _window_logo = "favicon-32x32.png"
        _sidebar_logo = "ragdoll_silhouette_white_128.png"
        self.setWindowTitle("Ragdoll Dynamics")
        self.setWindowIcon(QtGui.QIcon(ui._resource("ui", _window_logo)))

        panels = {
            "Central": QtWidgets.QWidget(),
            "SideBar": SideBar(),
            "Scroll": QtWidgets.QScrollArea(),
        }

        widgets = {
            "Body": QtWidgets.QWidget(),
            "Greet": GreetingPage(),
            "Licence": LicencePage(),
            "Assets": AssetListPage(),
            "VirtualSpace": QtWidgets.QSpacerItem(PD1, PD1),
        }

        panels["Scroll"].setWidgetResizable(True)
        panels["Scroll"].setWidget(widgets["Body"])

        anchor_list = [
            panels["SideBar"].add_anchor("Greet", _sidebar_logo, "#e5d680"),
            panels["SideBar"].add_anchor("Assets", "boxes.svg", "#e59680"),
        ]

        layout = QtWidgets.QVBoxLayout(widgets["Body"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addSpacing(PD4)
        layout.addWidget(widgets["Greet"])
        layout.addSpacing(PD4)
        layout.addWidget(widgets["Licence"])
        layout.addSpacing(PD3)
        layout.addWidget(widgets["Assets"])
        layout.addSpacerItem(widgets["VirtualSpace"])
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["Central"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(panels["SideBar"])
        layout.addWidget(panels["Scroll"])
        self.setCentralWidget(panels["Central"])

        panels["Scroll"].verticalScrollBar().valueChanged.connect(
            self.on_vertical_scrolled)
        panels["SideBar"].anchor_clicked.connect(self.on_anchor_clicked)
        widgets["Assets"].asset_opened.connect(self.asset_opened)
        lic = widgets["Licence"].input_widget()
        lic.licence_updated.connect(self.licence_updated)
        lic.float_requested.connect(self.float_requested)
        lic.float_dropped.connect(self.float_dropped)
        lic.node_activated.connect(self.node_activated)
        lic.node_deactivated.connect(self.node_deactivated)
        lic.offline_activate_requested.connect(self.offline_activate_requested)
        lic.offline_deactivate_requested.connect(
            self.offline_deactivate_requested)
        self.node_activate_inet_returned.connect(
            self.on_node_activate_inet_returned)
        self.node_deactivate_inet_returned.connect(
            self.on_node_deactivate_inet_returned)

        self._panels = panels
        self._widgets = widgets
        self._anchor_list = anchor_list
        self.__hidden = False

        if not ENABLE_SIDEBAR:
            panels["SideBar"].setVisible(False)

        with internal.Timer("stylesheet", verbose=True):
            self.setStyleSheet(_scaled_stylesheet(stylesheet))

        self.setMinimumWidth(WINDOW_WIDTH)
        self.setMinimumHeight(widgets["Greet"].height() + PD4 * 2)

    def hide(self):
        self.__hidden = True
        super(WelcomeWindow, self).hide()

    def show(self):
        super(WelcomeWindow, self).show()

        # Scroll to top, to make sure users always know where they are at
        self._panels["Scroll"].verticalScrollBar().setValue(0)

        if not self.__hidden:
            self._widgets["Assets"].start_worker()
            self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            self.__hidden = False

        self.licence_updated.emit()

    def closeEvent(self, event):
        asset_library.terminate()
        self._widgets["Assets"].terminate_worker()
        return super(WelcomeWindow, self).closeEvent(event)

    def resizeEvent(self, event):
        width, height = event.size().toTuple()

        virtual_space = int(height / 2)
        self._widgets["VirtualSpace"].changeSize(PD1, virtual_space)

        self._widgets["Body"].layout().invalidate()
        super(WelcomeWindow, self).resizeEvent(event)
        self._align_anchors()

    def on_licence_updated(self, data):
        product_status.data = data

        self._widgets["Licence"].input_widget().status_update()
        self._widgets["Greet"].status_widget().set_expiry()

        internet_request.fetch()

        # resize window a little bit just to trigger:
        #   1. anchor aligning and
        #   2. licence page resize
        #   after licence status updated.
        self.resize(self.size() + QtCore.QSize(0, 1))

        if product_status.is_trial_errored():
            QtWidgets.QApplication.instance().processEvents()
            ui.notify("Error",
                      product_status.trial_error_msg(),
                      location="LicencePlate",
                      persistent=True,
                      parent=self)

    def on_node_activate_inet_returned(self, key):
        self._widgets["Licence"].input_widget().switch_to_offline_activate(key)
        # don't forget our sidebar anchors after licence widget size changed!
        QtWidgets.QApplication.instance().processEvents()
        self._align_anchors()

    def on_node_deactivate_inet_returned(self):
        self._widgets["Licence"].input_widget().switch_to_offline_deactivate()
        # don't forget our sidebar anchors after licence widget size changed!
        QtWidgets.QApplication.instance().processEvents()
        self._align_anchors()

    def on_offline_activate_requested(self):
        w = self._widgets["Licence"].input_widget()
        w.on_offline_activate_requested()

    def on_offline_deactivate_requested(self):
        w = self._widgets["Licence"].input_widget()
        w.on_offline_deactivate_requested()
        self.licence_updated.emit()

    def on_anchor_clicked(self, name):
        widget = self._widgets.get(name)
        self._panels["Scroll"].verticalScrollBar().setValue(widget.y() - PD3)

    def on_vertical_scrolled(self, value):
        self._align_anchors(value)

    def _align_anchors(self, slider_pos=None):
        if not ENABLE_SIDEBAR:
            return
        slider_pos = (
            self._panels["Scroll"].verticalScrollBar().value()
            if slider_pos is None
            else slider_pos
        )
        pos = [
            self._widgets[name].y() for name in self._anchor_list
        ]
        self._panels["SideBar"].slide_anchors(pos, slider_pos)
