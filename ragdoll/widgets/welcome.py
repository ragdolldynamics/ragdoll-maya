
import os
import re
import math
import json
import logging
import tempfile
from datetime import datetime, timedelta
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2 import QtWebEngineWidgets
try:
    from urllib import request
except ImportError:
    import urllib as request  # py2
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # py2

from . import base
from .. import __, ui


__throwaway = datetime.strptime("2012-01-01", "%Y-%m-%d")
# This is a workaround for a Py2 bug:
#   The first use of strptime is not thread safe.
#   See: https://bugs.python.org/issue7980#msg221094
#        https://bugs.launchpad.net/openobject-server/+bug/947231/comments/8

log = logging.getLogger("ragdoll")
px = base.px

# padding levels
pd1 = px(20)
pd2 = px(14)
pd3 = px(10)
pd4 = px(6)
scroll_width = px(6)

video_width, video_height = px(217), px(122)
card_padding = px(3)
card_rounding = px(8)
card_width = video_width + (card_padding * 2)
card_height = video_height + (card_padding * 2)

anchor_size = px(48)
sidebar_width = anchor_size + (pd3 * 2)
splash_width = px(700)
splash_height = px(160)
timeline_width = splash_width
timeline_height = px(14)
window_width = sidebar_width + splash_width + (pd4 * 2) + scroll_width
window_height = px(590)  # just enough to see the first row of videos


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname)).replace("\\", "/")


def _tint_color(pixmap, color):
    painter = QtGui.QPainter(pixmap)
    painter.setCompositionMode(painter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()


def _text_to_color(text):
    return QtGui.QColor.fromHsv(
        (hash(text) & 0xFF0000) >> 16,
        (hash(text) & 0x00FF00) >> 8,
        180,
    )


def _aup_to_datetime(aup_string):
    return datetime.strptime(aup_string, "%Y-%m-%d %H:%M:%S")


class GreetingSplash(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(GreetingSplash, self).__init__(parent)
        pixmap = QtGui.QPixmap(_resource("ui", "welcome-banner.png"))
        pixmap = pixmap.scaled(
            splash_width,
            splash_height,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation
        )
        self.setFixedWidth(splash_width)
        self.setFixedHeight(splash_height)
        self._image = pixmap

    def paintEvent(self, event):
        r = px(8)
        w = self.width()
        h = self.height()

        path = QtGui.QPainterPath()
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(QtCore.QRect(0, 0, w, h), r, r)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.setClipPath(path.simplified())
        painter.drawPixmap(0, 0, self._image)


class GreetingStatus(base.OverlayWidget):

    def __init__(self, parent=None):
        super(GreetingStatus, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

        widgets = {
            "Line": QtWidgets.QLabel(),
            "Version": QtWidgets.QLabel(),
            "UpdateIcon": QtWidgets.QLabel(),
            "UpdateLink": QtWidgets.QLabel("checking update..."),
            "Badge": LicenceStatusBadge(),
        }

        widgets["Line"].setObjectName("GreetingStatusLine")
        widgets["Line"].setFixedWidth(splash_width)
        widgets["Line"].setFixedHeight(px(32))
        widgets["Line"].setStyleSheet("""
        #GreetingStatusLine {{
            background-color: #6c000000;
            border-bottom-left-radius: {radius}px;
            border-bottom-right-radius: {radius}px;
        }}
        """.format(radius=px(8)))

        widgets["UpdateIcon"].setFixedSize(QtCore.QSize(px(20), px(20)))
        widgets["UpdateLink"].setStyleSheet("color: #acacac;")
        widgets["UpdateLink"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setText("Current Version: %s" % __.version_str)

        layout = QtWidgets.QHBoxLayout(widgets["Line"])
        layout.setContentsMargins(px(8), px(6), px(2), px(6))
        layout.setSpacing(px(6))
        layout.addWidget(widgets["Badge"])
        layout.addStretch(1)
        layout.addWidget(widgets["Version"])
        layout.addSpacing(px(8))

        _update_row = QtWidgets.QWidget()
        _update_row.setFixedWidth(splash_width)
        _update_row.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        layout = QtWidgets.QHBoxLayout(_update_row)
        layout.setContentsMargins(0, 0, px(12), px(6))
        layout.addStretch(1)
        layout.addWidget(widgets["UpdateIcon"])
        layout.addSpacing(px(2))
        layout.addWidget(widgets["UpdateLink"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(_update_row, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(widgets["Line"], alignment=QtCore.Qt.AlignHCenter)

        self._widgets = widgets

    def _on_update_checked(self, result):
        status, latest = result
        widgets = self._widgets

        icon = {
            "update": _resource("ui", "cloud-arrow-down-fill.svg"),
            "uptodate": _resource("ui", "cloud-check-fill.svg"),
            "offline": _resource("ui", "cloud-slash.svg"),
            "expired": _resource("ui", "cloud.svg"),
        }[status]
        color = {
            "update": "#e0db57",
            "uptodate": "#67bf8f",
            "offline": "#585858",
            "expired": "#e27d7d",
        }[status]
        text = {
            "update": "Update Version: %s" % latest,
            "uptodate": "Version up to date.",
            "offline": "No internet, can't check for update.",
            "expired": "Annual upgrade expired.",
        }[status]

        # icon
        widgets["UpdateIcon"].setStyleSheet(
            "background: transparent; image: url(%s);" % icon
        )
        widgets["UpdateIcon"].style().unpolish(widgets["UpdateIcon"])
        widgets["UpdateIcon"].style().polish(widgets["UpdateIcon"])

        # download link or text message
        widgets["UpdateLink"].setStyleSheet("""
            color: %s;
            font: %s;
            background: transparent;
            border: none;
            outline: none;
        """ % (color, "bold" if status == "update" else "normal"))

        if status == "update":
            widgets["UpdateLink"].setOpenExternalLinks(True)
            widgets["UpdateLink"].setTextInteractionFlags(
                QtCore.Qt.TextBrowserInteraction
            )
            widgets["UpdateLink"].setText("""
            <style> a:link {color: %s;}</style>
            <a href=\"https://learn.ragdolldynamics.com/download/\">%s</a>
            """ % (color, text))
        else:
            widgets["UpdateLink"].setOpenExternalLinks(False)
            widgets["UpdateLink"].setTextInteractionFlags(
                QtCore.Qt.NoTextInteraction
            )
            widgets["UpdateLink"].setText(text)

        widgets["UpdateIcon"].show()

    def _check_update(self, data):
        if data["isTrial"]:
            aup_expired = False  # doesn't have valid aup date in trial
        else:
            aup = data["annualUpgradeProgram"]
            aup_expired = (
                _aup_to_datetime(aup) < datetime.now() if aup
                else False
            )

        if aup_expired:
            return "expired", ""
        else:
            # check update
            url = "https://ragdolldynamics.com/version"
            try:
                response = request.urlopen(url)
            except Exception:
                response = None
                responded = False
            else:
                responded = response.code == 200

            if responded:
                latest = json.loads(response.read())["latestVersion"]
                latest = tuple(map(int, latest.split("_", 3)[:3]))
                current = tuple(map(int, __.version_str.split(".")[:3]))
                if latest <= current:
                    return "uptodate", ""
                else:
                    return "update", ".".join(map(str, latest))
            else:
                return "offline", ""

    def check_update(self, data):
        self._widgets["UpdateIcon"].hide()
        worker = base.Thread(self._check_update, parent=self)
        worker.result_ready.connect(self._on_update_checked)
        worker.finished.connect(worker.deleteLater)
        worker.start(args=[data])

    def set_licence(self, data):
        self._widgets["Badge"].set_status(data)


class GreetingBanner(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GreetingBanner, self).__init__(parent)

        widgets = {
            "Splash": GreetingSplash(),
            "Status": GreetingStatus(self)  # overlay
        }

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, pd4, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Splash"], alignment=QtCore.Qt.AlignHCenter)

        self._widgets = widgets

    def status_widget(self):
        return self._widgets["Status"]


class GreetingTimeline(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GreetingTimeline, self).__init__(parent)

        widgets = {
            "Timeline": base.TimelineWidget(),
        }

        widgets["Timeline"].min_size = QtCore.QSize(
            timeline_width, timeline_height
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Timeline"])

        self._widgets = widgets

    def _fetch_versions(self, data):
        # get AUP, or expire date
        expiry = data["expiry"] if data["expires"] else None
        trial = data["isTrial"] or data["product"] == "trial"
        aup = data["annualUpgradeProgram"]
        perpetual = not expiry and aup and not trial

        if perpetual:
            pass

        elif trial:
            pass

        else:
            pass

        aup_end = _aup_to_datetime(aup).replace(hour=0, minute=0, second=0)
        aup_start = aup_end.replace(year=aup_end.year - 1)

        # aup_expired = (
        #     _aup_to_datetime(aup) < datetime.now() if aup
        #     else False
        # )

        def count_days(date):
            return (date - aup_start).days

        def in_range(ver_str):
            ver_date = datetime(*map(int, ver_str.split(".")))
            if aup_start <= ver_date <= aup_end:
                return count_days(ver_date), ver_str

        def parse(ver_list):
            return {
                ver_days: ver_str
                for ver_days, ver_str in filter(None, map(in_range, ver_list))
            }

        url = "https://learn.ragdolldynamics.com/news"
        try:
            response = request.urlopen(url)
        except Exception:
            response = None
            responded = False
        else:
            responded = response.code == 200

        if responded:
            pattern = re.compile(
                rb'.*<a href="/releases/(\d{4}\.\d{2}\.\d{2}).*">'
            )
            versions = []
            for line in response.readlines():
                matched = pattern.match(line)
                if matched:
                    versions.append(matched.group(1).decode())

            current = ".".join(__.version_str.split(".")[:3])
            versions.append(current)
            versions.append("2022.06.12")  # test

            return {
                "versions": parse(versions),
                "current": in_range(current),
                "start": aup_start,
                "end": aup_end,
            }
        else:
            return {}

    def set_timeline(self, data):
        worker = base.Thread(self._fetch_versions, parent=self)
        worker.result_ready.connect(self._widgets["Timeline"].set_data)
        worker.finished.connect(worker.deleteLater)
        worker.start(args=[data])


class GreetingPage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GreetingPage, self).__init__(parent)

        widgets = {
            "Banner": GreetingBanner(),
            "Timeline": GreetingTimeline(),
        }

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(widgets["Banner"])
        layout.addWidget(widgets["Timeline"])

        self._widgets = widgets

    def status_widget(self):
        return self._widgets["Banner"].status_widget()

    def timeline_widget(self):
        return self._widgets["Timeline"]


class AssetVideoPlayer(QtWebEngineWidgets.QWebEngineView):

    def __init__(self, parent=None):
        super(AssetVideoPlayer, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.page().setBackgroundColor(QtGui.QColor("#353535"))
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def play(self):
        self.page().runJavaScript("""
        document.getElementById("video").play();
        """)
        # todo: add video loading page

    def pause(self):
        self.page().runJavaScript("""
        document.getElementById("video").pause();
        """)

    def set_video(self, video):
        html_code = """
        <html><body style="background:transparent; margin:0px;">
        <div  class="video-mask"
              style="width:100%; height:100%; position:absolute;
                    overflow:hidden; border-radius: {r}px;">

            <video id="video" loop preload="none" muted="muted"
                   style="width:100%; position:absolute;"
                <source src="{video}" type="video/webm">
                <p>HTML5 Video element not supported.</p></video>

        </div></body></html>
        """.format(video=video, r=card_rounding)
        self.setHtml(html_code, baseUrl=QtCore.QUrl("file://"))

        if QtCore.__version_info__ < (5, 13):
            # The web-engine (Chromium 73) that shipped with Qt 5.13 and
            #   before somehow cannot render border-radius properly.
            rounded_rect = QtCore.QRectF(0, 0, video_width, video_height)
            path = QtGui.QPainterPath()
            path.addRoundedRect(rounded_rect, card_rounding, card_rounding)

            region = QtGui.QRegion(path.toFillPolygon().toPolygon())
            self.setMask(region)


class AssetVideoPoster(base.OverlayWidget):

    def __init__(self, parent=None):
        super(AssetVideoPoster, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._image = None

    def set_poster(self, poster):
        """
        Args:
            poster (QtGui.QPixmap):
        """
        self._image = poster.scaled(
            video_width,
            video_height,
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation,
        )

    def paintEvent(self, event):
        """
        :param QtGui.QPaintEvent event:
        """
        w = self.width()
        h = self.height()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        rounded_rect = QtCore.QRectF(
            card_padding,
            card_padding,
            w - (card_padding * 2),
            h - (card_padding * 2),
        )
        path = QtGui.QPainterPath()
        path.addRoundedRect(rounded_rect, card_rounding, card_rounding)
        painter.setClipPath(path)
        painter.drawPixmap(card_padding, card_padding, self._image)


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
            card_padding - 1,
            h - footer_h - card_padding + 1,
            w - (card_padding * 2) + 2,  # +2 because both left and right
            footer_h,
        )
        footer_top_left = QtCore.QRectF(
            card_padding - 1,
            h - footer_h - card_padding + 1,
            card_rounding,
            card_rounding,
        )
        footer_top_right = QtCore.QRectF(
            w - card_padding - card_rounding + 1,
            h - footer_h - card_padding + 1,
            card_rounding,
            card_rounding,
        )
        path = QtGui.QPainterPath()
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(footer_rect, card_rounding, card_rounding)
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
        for i, color in enumerate(self._dots):  # right to left
            offset = -(dot_gap + dot_radius) * i
            painter.setBrush(QtGui.QColor(color))
            dot_rect = dot_rect.adjusted(offset, 0, offset, 0)
            painter.drawEllipse(dot_rect)


class AssetCardItem(QtWidgets.QWidget):
    asset_opened = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetCardItem, self).__init__(parent=parent)

        widgets = {
            "Footer": AssetVideoFooter(self),
            "PosterStill": AssetVideoPoster(self),
            "PosterAnim": AssetVideoPoster(self),
            "Player": AssetVideoPlayer(self),
        }

        effects = {
            "Poster": QtWidgets.QGraphicsOpacityEffect(widgets["PosterAnim"]),
        }

        animations = {
            "Poster": QtCore.QPropertyAnimation(effects["Poster"], b"opacity")
        }

        widgets["PosterAnim"].setAttribute(QtCore.Qt.WA_StyledBackground)
        widgets["PosterAnim"].setGraphicsEffect(effects["Poster"])
        widgets["Player"].setFixedWidth(video_width)
        widgets["Player"].setFixedHeight(video_height)

        effects["Poster"].setOpacity(1)
        animations["Poster"].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(*(card_padding, ) * 4)
        layout.addWidget(widgets["Player"])

        animations["Poster"].finished.connect(self.on_transition_end)

        self.setAutoFillBackground(True)
        self._widgets = widgets
        self._effects = effects
        self._animations = animations
        self._file_path = None

    def init(self, index):
        """
        :param QtCore.QModelIndex index:
        """
        poster = index.data(AssetCardModel.PosterRole)
        video = index.data(AssetCardModel.VideoRole)
        self._widgets["Player"].set_video(video)
        self._widgets["PosterStill"].set_poster(poster)
        self._widgets["PosterAnim"].set_poster(poster)
        self._widgets["Footer"].set_data(
            index.data(AssetCardModel.NameRole),
            list(index.data(AssetCardModel.TagsRole).values()),
        )
        self._file_path = index.data(AssetCardModel.AssetRole)

    def on_clicked(self):
        if os.path.isfile(self._file_path):
            self.asset_opened.emit(self._file_path)
        else:
            log.error("Asset file missing: %s" % self._file_path)

    def on_transition_end(self):
        leave = self._animations["Poster"].endValue() == 1.0
        if leave:
            # Animated poster not able to update/redraw correctly when
            #   the main page gets scrolled. Use another still poster
            #   to cover that.
            self._widgets["Player"].pause()
            self._widgets["PosterStill"].show()
            self._widgets["PosterAnim"].hide()

    def enterEvent(self, event):
        anim = self._animations["Poster"]
        current = self._effects["Poster"].opacity()
        anim.stop()
        anim.setDuration(int(500 * current))
        anim.setStartValue(current)
        anim.setEndValue(0.0)
        anim.start()
        self._widgets["PosterAnim"].show()
        self._widgets["PosterStill"].hide()
        self._widgets["Player"].play()

    def leaveEvent(self, event):
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


class AssetCardModel(QtGui.QStandardItemModel):
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

    def is_net_location(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            return False

    def resource(self, path, lib_path):
        if self.is_net_location(path):
            return path
        else:
            return os.path.join(lib_path, path)

    def refresh(self, extra_assets_path=""):
        self.clear()
        self.load_assets(extra_assets_path)
        self.load_assets(os.getenv("RAGDOLL_ASSETS", ""))

    @staticmethod
    def get_manifest(lib_path):
        manifest = {
            "assets": list(),
            "tags": set(),
        }

        rag_files = []
        for item in os.listdir(lib_path):
            path = os.path.join(lib_path, item)
            if item.endswith(".rag") and os.path.isfile(path):
                rag_files.append(path)

        for path in sorted(rag_files, key=lambda p: os.stat(p).st_mtime):
            with open(path) as _f:
                rag = json.load(_f)
            _d = rag.get("ui")
            _fname = os.path.basename(path)

            manifest["assets"].append({
                "path": path,
                "name": rag.get("name") or _fname.rsplit(".", 1)[0],
                "video": _d.get("video") or _fname.rsplit(".", 1)[0] + ".webm",
                "poster": _d["thumbnail"],
                "tags": _d.get("tags") or [],
            })

            manifest["tags"].update(
                _d.get("tags") or []
            )

        return manifest

    def load_assets(self, lib_path):
        if not lib_path:
            return

        log.info("Loading assets from %r" % lib_path)
        manifest = self.get_manifest(lib_path)

        all_dots = {
            tag: _text_to_color(tag) for tag in manifest["tags"]
        }
        for data in manifest.get("assets") or []:
            item = QtGui.QStandardItem()
            name = data["name"]
            asset = data["path"]
            poster = ui.base64_to_pixmap(data["poster"].encode("ascii"))
            video = self.resource(data["video"], lib_path)

            tags = {
                tag_name: all_dots.get(tag_name, "black")
                for tag_name in set(data["tags"])
            }

            item.setData(name, AssetCardModel.NameRole)
            item.setData(asset, AssetCardModel.AssetRole)
            item.setData(poster, AssetCardModel.PosterRole)
            item.setData(video, AssetCardModel.VideoRole)
            item.setData(tags, AssetCardModel.TagsRole)

            self.appendRow(item)


class AssetCardProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(AssetCardProxyModel, self).__init__(parent=parent)
        self._tags = set()

    def set_tags(self, tags):
        self._tags = set(tags)
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        item_tags = model.data(index, AssetCardModel.TagsRole).keys()
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
        self.setGridSize(QtCore.QSize(card_width, card_height))
        self.setUniformItemSizes(True)
        self.setSelectionRectVisible(False)
        self.setMinimumWidth(card_width)
        self.viewport().setMinimumWidth(card_width)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def horizontalOffset(self):
        return self._horizontal_offset

    def adjust_viewport(self):
        viewport = self.viewport()
        width = viewport.width()
        item_count = self.model().rowCount()
        # expand view to show all items
        column_count = math.floor(width / card_width)
        row_count = math.ceil(item_count / column_count)
        viewport_height = row_count * card_height
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
                   h=px(16), r=px(6), p1=px(5), p2=px(4)))


class AssetTagList(QtWidgets.QWidget):
    tagged = QtCore.Signal(set)

    def __init__(self, parent=None):
        super(AssetTagList, self).__init__(parent)
        base.FlowLayout(self)
        self._tags = set()

    def add_tag(self, tag_name, tag_color):
        if tag_name in self._tags:
            return
        self._tags.add(tag_name)
        button = AssetTag(tag_name, tag_color)
        button.setIcon(QtGui.QIcon(_resource("ui", "tag-fill.svg")))
        button.setCheckable(True)
        button.toggled.connect(self.on_tag_toggled)
        self.layout().addWidget(button)

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
    asset_browsed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AssetListPage, self).__init__(parent=parent)

        widgets = {
            "Head": QtWidgets.QLabel("Assets"),
            "Tags": AssetTagList(),
            "List": AssetCardView(),
            "Empty": QtWidgets.QLabel("No Asset Found."),
            "Path": QtWidgets.QLineEdit(),
            "Browse": QtWidgets.QPushButton(),
        }

        models = {
            "Source": AssetCardModel(),
            "Proxy": AssetCardProxyModel(),
        }

        widgets["Head"].setObjectName("Heading1")
        widgets["Empty"].setFixedHeight(px(40))
        widgets["Empty"].setAlignment(QtCore.Qt.AlignHCenter)
        widgets["Empty"].setVisible(False)
        widgets["Browse"].setIcon(QtGui.QIcon(_resource("ui", "folder.svg")))

        models["Proxy"].setSourceModel(models["Source"])
        widgets["List"].setModel(models["Proxy"])

        _path_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_path_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("Extra Assets"))
        layout.addSpacing(pd4)
        layout.addWidget(widgets["Path"])
        layout.addWidget(widgets["Browse"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(pd1, 0, pd1, 0)
        layout.setSpacing(pd3)
        layout.addWidget(widgets["Head"])
        layout.addWidget(widgets["Tags"])
        layout.addWidget(widgets["List"])
        layout.addWidget(widgets["Empty"])
        layout.addWidget(_path_row)

        widgets["Tags"].tagged.connect(self.on_tag_changed)
        widgets["Path"].textEdited.connect(lambda _: self.reset())
        widgets["Browse"].clicked.connect(self.on_asset_browse_clicked)

        self._models = models
        self._widgets = widgets

    def resizeEvent(self, event):
        super(AssetListPage, self).resizeEvent(event)
        self._widgets["List"].adjust_viewport()

    def on_tag_changed(self, tags):
        _view = self._widgets["List"]
        _proxy = self._models["Proxy"]
        _proxy.set_tags(tags)

        for row in range(_proxy.rowCount()):
            index = _proxy.index(row, 0)
            if _view.indexWidget(index) is None:
                self.init_widget(_proxy.mapToSource(index))
        _view.adjust_viewport()

    def on_asset_browse_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(dialog.DirectoryOnly)
        dialog.setOptions(dialog.DontUseNativeDialog | dialog.ReadOnly)
        dialog.setAcceptMode(dialog.AcceptOpen)
        if dialog.exec_():
            paths = dialog.selectedFiles()
            extra_assets_path = paths[0]
            self.asset_browsed.emit(extra_assets_path)
            self._widgets["Path"].setText(extra_assets_path)
            self.reset()

    def set_extra_assets(self, extra_assets_path):
        self._widgets["Path"].setText(extra_assets_path)

    def reset(self):
        self._widgets["Tags"].clear()
        model = self._models["Source"]
        model.refresh(self._widgets["Path"].text())

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            self.init_widget(index)
            for name, color in model.data(index, model.TagsRole).items():
                self._widgets["Tags"].add_tag(name, color)

        asset_loaded = bool(model.rowCount())
        self._widgets["Empty"].setVisible(not asset_loaded)
        self._widgets["List"].setVisible(asset_loaded)

    def init_widget(self, index):
        widget = AssetCardItem()
        widget.init(index)
        item = self._models["Source"].itemFromIndex(index)
        item.setSizeHint(widget.sizeHint())
        self._widgets["List"].setIndexWidget(
            self._models["Proxy"].mapFromSource(index),
            widget,
        )
        # connect signal
        widget.asset_opened.connect(self.asset_opened)


class LicenceStatusBadge(QtWidgets.QWidget):
    """One liner product badge

    A badge that sit at left bottom corner of top splash image.
    Which looks like this:

        * Complete | Expiry June.20.2022

    """

    def __init__(self, parent=None):
        super(LicenceStatusBadge, self).__init__(parent=parent)

        widgets = {
            "Icon": QtWidgets.QPushButton(),
            "Plan": QtWidgets.QLabel(),
        }

        widgets["Icon"].setStyleSheet("background: transparent; padding: 0px;")
        widgets["Icon"].setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Icon"])
        layout.addWidget(widgets["Plan"])
        layout.addStretch(1)

        self._widgets = widgets

    def set_status(self, data):
        expiry = data["expiry"] if data["expires"] else None
        trial = data["isTrial"] or data["product"] == "trial"
        aup = data["annualUpgradeProgram"]
        perpetual = not expiry and aup and not trial

        if perpetual:
            _aup_date = datetime.strptime(aup, '%Y-%m-%d %H:%M:%S')
            aup = _aup_date.strftime("%b.%d.%Y")
            expired = False
            color = "#63a1b8"

        elif trial:
            expiry_date = datetime.now() + timedelta(days=data["trialDays"])
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = data["trialDays"] < 1
            perpetual = False
            color = "#ec7171" if expired else "#67a776"

        else:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = expiry_date < datetime.now()
            color = "#ec7171" if expired else "#67a776"

        if not expired and data["isFloating"] and not data["hasLease"]:
            color = "#f3bc75"

        w = self._widgets
        status = "%s | %s %s" % (
            data["marketingName"],
            "Perpetual" if perpetual else "Expired" if expired else "Expiry",
            ("/ AUP " + aup) if perpetual else expiry,
        )
        w["Plan"].setText(status)
        w["Plan"].setStyleSheet("background: transparent; "
                                "color: {color};".format(color=color))

        _size = QtCore.QSize(px(16), px(16))
        _icon = QtGui.QIcon(_resource("ui", "award.svg"))
        pixmap = _icon.pixmap(_size)
        _tint_color(pixmap, QtGui.QColor(color))
        _icon = QtGui.QIcon(pixmap)
        w["Icon"].setIcon(_icon)
        w["Icon"].setIconSize(_size)


class LicenceStatusPlate(QtWidgets.QWidget):
    """Fancy product banner

    A big pretty banner that honors the product.
    Which looks like this:

    .---------------------------------------------.
    |  Complete     Unlimited recording frames    |
    |    ......     Export up to 10 Markers       |
    |               Makes you look decent         |
    `---------------------------------------------`

    """

    def __init__(self, parent=None):
        super(LicenceStatusPlate, self).__init__(parent=parent)
        self.setObjectName("LicencePlate")
        self.setMinimumHeight(px(86))

        panels = {
            "Product": QtWidgets.QWidget(),
            "Features": QtWidgets.QWidget(),
        }

        widgets = {
            "Product": QtWidgets.QLabel(),
            "Commercial": QtWidgets.QLabel(),
            "Features": QtWidgets.QLabel(),
        }

        panels["Product"].setFixedWidth(px(140))
        panels["Product"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        panels["Features"].setAttribute(QtCore.Qt.WA_NoSystemBackground)

        widgets["Product"].setObjectName("PlateProduct")
        widgets["Commercial"].setObjectName("PlateCommercial")
        widgets["Features"].setObjectName("PlateFeatures")

        layout = QtWidgets.QVBoxLayout(panels["Product"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addSpacing(pd4)
        layout.addWidget(widgets["Product"], alignment=QtCore.Qt.AlignRight)
        layout.addWidget(widgets["Commercial"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QVBoxLayout(panels["Features"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addSpacing(pd4)
        layout.addWidget(widgets["Features"], alignment=QtCore.Qt.AlignLeft)
        layout.addStretch(1)
        layout.addSpacing(pd4)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(px(12), px(6), px(6), px(6))
        layout.addWidget(panels["Product"])
        layout.addSpacing(px(30))
        layout.addWidget(panels["Features"])
        layout.addStretch(1)

        self._widgets = widgets

    def set_product(self, data):
        self._widgets["Product"].setText(data["marketingName"])
        self._widgets["Commercial"].setText(
            "Non-Commercial" if data["isNonCommercial"]
            else "Commercial" if not data["isFloating"]
            else "Lease Assigned" if data["hasLease"] else "Lease Dropped"
        )

        features = {
            "Trial": (
                "Record up to 100 frames\n"
                "Export up to 10 Markers"
            ),
            "Personal": (
                "Record up to 100 frames\n"
                "Export up to 10 Markers\n"
                "Free upgrades forever"
            ),
            "Complete": (
                "Unlimited recording frames\n"
                "Export up to 10 Markers\n"
                "High-performance solver"
            ),
            "Unlimited": (
                "The fully-featured, unrestricted version"
            ),
            "Batch": (
                ""
            ),
        }.get(data["marketingName"], "Unknown Product")

        self._widgets["Features"].setText(
            "<p style=\"line-height:%d%%\">%s</p>"
            % (140, features.replace("\n", "<br>"))
        )

        expiry = data["expiry"] if data["expires"] else None
        trial = data["isTrial"] or data["product"] == "trial"
        aup = data["annualUpgradeProgram"]
        perpetual = not expiry and aup and not trial

        if perpetual:
            expired = False
            gradient = "stop:0 #4facfe, stop:1 #00f2fe"

        elif trial:
            expired = data["trialDays"] < 1
            if expired:
                gradient = "stop:0 #f3465a, stop:1 #db2550"
            else:
                gradient = "stop:0 #43ea80, stop:1 #38f8d4"

        else:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
            expired = expiry_date < datetime.now()
            if expired:
                gradient = "stop:0 #f3465a, stop:1 #db2550"
            else:
                gradient = "stop:0 #43ea80, stop:1 #38f8d4"

        if not expired and data["isFloating"] and not data["hasLease"]:
            gradient = "stop:0 #ff934c, stop:1 #fc686f"

        self.setStyleSheet("""
        #LicencePlate {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, %s);
        }
        """ % gradient)

    def paintEvent(self, event):
        # required for applying background styling
        opt = QtWidgets.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(
            QtWidgets.QStyle.PE_Widget, opt, painter, self
        )
        super(LicenceStatusPlate, self).paintEvent(event)


class _LicencePanelHelper(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(_LicencePanelHelper, self).__init__(parent=parent)
        self.setMaximumWidth(px(540))

    def set_heading(self, title, icon_file):
        icon_label = self._widgets["Icon"]
        icon_label.setFixedSize(QtCore.QSize(px(64), px(64)))
        icon_label.setStyleSheet("""
        image: url({image});
        """.format(image=_resource("ui", icon_file)))

        title_label = self._widgets["Title"]
        title_label.setObjectName("Heading2")
        title_label.setText(title)

    def labeling(self, widget, label_text):
        c = QtWidgets.QWidget()
        label = QtWidgets.QLabel(label_text)
        _layout = QtWidgets.QVBoxLayout(c)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(pd3)
        _layout.addWidget(label)
        _layout.addWidget(widget)
        return c


class LicenceNodeLock(_LicencePanelHelper):
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceNodeLock, self).__init__(parent=parent)

        widgets = {
            "Icon": QtWidgets.QLabel(),
            "Title": QtWidgets.QLabel(),
            "ProductKey": QtWidgets.QLineEdit(),
            "ProcessBtn": QtWidgets.QPushButton(),
        }

        _ = "Your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        widgets["ProductKey"].setPlaceholderText(_)

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Title"])
        layout.addWidget(self.labeling(widgets["ProductKey"], "Product Key"))
        layout.addWidget(widgets["ProcessBtn"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Icon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)

        widgets["ProductKey"].textEdited.connect(self.on_product_key_edited)
        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)

        self._widgets = widgets
        self.set_heading("Node Lock", "pc-display.svg")

    def on_product_key_edited(self, text):
        codes = text.split("-")
        is_key = (
            len(codes) == 7
            and all(len(c) == 4 and c.isalnum() for c in codes)
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

    def status_update(self, data):
        if data["isActivated"]:
            self._widgets["ProductKey"].setText(data["key"])
            self._widgets["ProductKey"].setReadOnly(True)
            self._widgets["ProcessBtn"].setText("Deactivate")
            self._widgets["ProcessBtn"].setEnabled(True)
        else:
            self._widgets["ProductKey"].setText("")
            self._widgets["ProductKey"].setReadOnly(False)
            self._widgets["ProcessBtn"].setText("Activate")
            self._widgets["ProcessBtn"].setEnabled(False)


class LicenceNodeLockOffline(_LicencePanelHelper):
    node_activated = QtCore.Signal(str)
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(LicenceNodeLockOffline, self).__init__(parent=parent)

        widgets = {
            "Icon": QtWidgets.QLabel(),
            "Title": QtWidgets.QLabel(),
            "OfflineHint": QtWidgets.QLabel(),
            "ProductKey": QtWidgets.QLineEdit(),
            "RequestWidget": QtWidgets.QWidget(),
            "CopyHint": QtWidgets.QLabel(),
            "CopyRequest": QtWidgets.QPushButton(),
            "WebsiteURL": QtWidgets.QLabel(),
            "Response": QtWidgets.QLineEdit(),
            "ProcessBtn": QtWidgets.QPushButton(),
        }
        widgets["ResponseWidget"] = self.labeling(widgets["Response"],
                                                  "Response Code")

        effects = {
            "CopyHint": QtWidgets.QGraphicsOpacityEffect(widgets["CopyHint"]),
        }

        animations = {
            "CopyHint": QtCore.QPropertyAnimation(effects["CopyHint"],
                                                  b"opacity")
        }

        effects["CopyHint"].setOpacity(0)
        animations["CopyHint"].setDuration(3000)
        animations["CopyHint"].setStartValue(1.0)
        animations["CopyHint"].setKeyValueAt(0.8, 1.0)
        animations["CopyHint"].setEndValue(0.0)
        animations["CopyHint"].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        widgets["OfflineHint"].setText(
            "Cannot reach Ragdoll licencing server.\n"
            "Require another internet accessible device to complete "
            "following process."
        )

        _ = "Your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
        widgets["ProductKey"].setPlaceholderText(_)
        widgets["OfflineHint"].setObjectName("HintMessage")
        widgets["RequestWidget"].setEnabled(False)

        widgets["CopyHint"].setText("Copied to clipboard!")
        widgets["CopyHint"].setGraphicsEffect(effects["CopyHint"])
        widgets["CopyRequest"].setText("Copy Request Code")
        widgets["CopyRequest"].setIcon(
            QtGui.QIcon(_resource("ui", "clipboard.svg"))
        )
        widgets["WebsiteURL"].setOpenExternalLinks(True)
        widgets["WebsiteURL"].setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        widgets["WebsiteURL"].setText(
            """
            <style> p {color: #8c8c8c;} a:link {color: #80e5cc;}</style>
            <p>And paste the code to </p> 
            <a href=\"https://ragdolldynamics.com/offline\">
            https://ragdolldynamics.com/offline</a>
            """
        )
        widgets["Response"].setPlaceholderText(
            "Paste response code from https://ragdolldynamics.com/offline"
        )

        _request_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_request_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(widgets["CopyRequest"])
        layout.addWidget(widgets["WebsiteURL"])

        _request_label = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_request_label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(QtWidgets.QLabel("Request Code"))
        layout.addWidget(widgets["CopyHint"])
        layout.addStretch(1)

        layout = QtWidgets.QVBoxLayout(widgets["RequestWidget"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(_request_label)
        layout.addWidget(_request_row)

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Title"])
        layout.addWidget(widgets["OfflineHint"])
        layout.addWidget(self.labeling(widgets["ProductKey"], "Product Key"))
        layout.addWidget(widgets["RequestWidget"])
        layout.addWidget(widgets["ResponseWidget"])
        layout.addWidget(widgets["ProcessBtn"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Icon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)

        widgets["ProductKey"].textEdited.connect(self.on_product_key_edited)
        widgets["CopyRequest"].clicked.connect(self.on_copy_request_clicked)
        widgets["Response"].textEdited.connect(self.on_response_edited)
        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)

        _temp = tempfile.gettempdir()
        self._reqfname = os.path.join(_temp, "ragdollTempRequest.xml")
        self._resfname = os.path.join(_temp, "ragdollTempResponse.xml")
        self._dreqfname = os.path.join(_temp, "ragdollTempDeRequest.xml")
        self._keyfname = os.path.join(_temp, "ragdollTempProductKey.txt")
        self._widgets = widgets
        self._animations = animations

        self.set_heading("Node Lock (Offline)", "pc-display.svg")

    def on_product_key_edited(self, text):
        codes = text.split("-")
        is_key = (
            len(codes) == 7
            and all(len(c) == 4 and c.isalnum() for c in codes)
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
            self.offline_deactivate_requested.emit(self._dreqfname)
            # Also deactivates the node right away.

    def set_activation_request(self):
        try:
            with open(self._reqfname) as _f:
                request_code = _f.read()
        except Exception:
            self._widgets["ResponseWidget"].setEnabled(False)
        else:
            base.write_clipboard(request_code)
            self._animations["CopyHint"].stop()
            self._animations["CopyHint"].start()
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

    def status_update(self, data):
        if data["isActivated"]:
            self._widgets["ProductKey"].setText(data["key"])
            self._widgets["ProductKey"].setReadOnly(True)
            self._widgets["ProcessBtn"].setText("Deactivate")
            self._widgets["ProcessBtn"].setEnabled(True)
            self._widgets["RequestWidget"].hide()
            self._widgets["ResponseWidget"].hide()
            self.remove_temp_key()

        else:
            # restore product key for continuing offline activation
            _temp_key = self.read_temp_key()
            self._widgets["ProductKey"].setText(self.read_temp_key())
            self._widgets["ProductKey"].setReadOnly(False)
            self._widgets["ProcessBtn"].setText("Activate")
            self._widgets["ProcessBtn"].setEnabled(False)
            self._widgets["RequestWidget"].show()
            self._widgets["ResponseWidget"].show()
            self._widgets["RequestWidget"].setEnabled(bool(_temp_key))
            self._widgets["ResponseWidget"].setEnabled(bool(_temp_key))


class LicenceOfflineDeactivationBox(_LicencePanelHelper):
    dismissed = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceOfflineDeactivationBox, self).__init__(parent=parent)

        widgets = {
            "Icon": QtWidgets.QLabel(),
            "Title": QtWidgets.QLabel(),
            "OfflineHint": QtWidgets.QLabel(),
            "ProductKey": QtWidgets.QLineEdit(),
            "RequestWidget": QtWidgets.QWidget(),
            "CopyHint": QtWidgets.QLabel(),
            "CopyRequest": QtWidgets.QPushButton(),
            "WebsiteURL": QtWidgets.QLabel(),
            "DismissBtn": QtWidgets.QPushButton("Dismiss"),
        }

        effects = {
            "CopyHint": QtWidgets.QGraphicsOpacityEffect(widgets["CopyHint"]),
        }

        animations = {
            "CopyHint": QtCore.QPropertyAnimation(effects["CopyHint"],
                                                  b"opacity")
        }

        effects["CopyHint"].setOpacity(0)
        animations["CopyHint"].setDuration(3000)
        animations["CopyHint"].setStartValue(1.0)
        animations["CopyHint"].setKeyValueAt(0.8, 1.0)
        animations["CopyHint"].setEndValue(0.0)
        animations["CopyHint"].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        widgets["ProductKey"].setReadOnly(True)
        widgets["OfflineHint"].setObjectName("HintMessage")
        widgets["OfflineHint"].setText(
            "Please continue following steps to complete offline deactivation."
            "\n"
            'And ONLY after you have completed the process, press "Dismiss" '
            'button down below\nto remove this message.'
            "\n\n"
            "CAUTION: If you deactivate Maya without deactivating"
            "online,\nyour licence will still be considered active "
            "and cannot be reactivated.\n"
            "If this happens, contact support@ragdolldynamics.com"
        )

        widgets["CopyHint"].setText("Copied to clipboard!")
        widgets["CopyHint"].setGraphicsEffect(effects["CopyHint"])
        widgets["CopyRequest"].setText("Copy Request Code")
        widgets["CopyRequest"].setIcon(
            QtGui.QIcon(_resource("ui", "clipboard.svg"))
        )
        widgets["WebsiteURL"].setOpenExternalLinks(True)
        widgets["WebsiteURL"].setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        widgets["WebsiteURL"].setText(
            """
            <style> p {color: #8c8c8c;} a:link {color: #80e5cc;}</style>
            <p>And paste the code to </p> 
            <a href=\"https://ragdolldynamics.com/offline\">
            https://ragdolldynamics.com/offline</a>
            """
        )

        _request_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_request_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(widgets["CopyRequest"])
        layout.addWidget(widgets["WebsiteURL"])

        _request_label = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_request_label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(QtWidgets.QLabel("Request Code"))
        layout.addWidget(widgets["CopyHint"])
        layout.addStretch(1)

        layout = QtWidgets.QVBoxLayout(widgets["RequestWidget"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addWidget(_request_label)
        layout.addWidget(_request_row)

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Title"])
        layout.addWidget(self.labeling(widgets["OfflineHint"], "Important"))
        layout.addWidget(self.labeling(widgets["ProductKey"], "Product Key"))
        layout.addWidget(widgets["RequestWidget"])
        layout.addWidget(widgets["DismissBtn"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Icon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)
        layout.addStretch(1)

        widgets["CopyRequest"].clicked.connect(self.on_copy_request_clicked)
        widgets["DismissBtn"].clicked.connect(self.dismissed)

        self._widgets = widgets
        self._animations = animations
        self._req_code = None
        self.set_heading("Node Lock (Offline Deactivating)", "pc-display.svg")

    def on_copy_request_clicked(self):
        base.write_clipboard(self._req_code)
        self._animations["CopyHint"].stop()
        self._animations["CopyHint"].start()

    def set_product_key(self, key):
        self._widgets["ProductKey"].setText(key)

    def set_request_code(self, code):
        self._req_code = code

    def status_update(self, data):
        return


class LicenceFloating(_LicencePanelHelper):
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()

    def __init__(self, parent=None):
        super(LicenceFloating, self).__init__(parent=parent)

        widgets = {
            "Icon": QtWidgets.QLabel(),
            "Title": QtWidgets.QLabel(),
            "ServerIP": QtWidgets.QLineEdit(),
            "ServerPort": QtWidgets.QLineEdit(),
            "ProcessBtn": QtWidgets.QPushButton(),
        }

        widgets["ServerIP"].setFixedWidth(px(120))
        widgets["ServerPort"].setFixedWidth(px(60))
        widgets["ServerIP"].setReadOnly(True)  # set from env var
        widgets["ServerPort"].setReadOnly(True)  # set from env var

        _server_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_server_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(self.labeling(widgets["ServerIP"], "Server IP"))
        layout.addWidget(self.labeling(widgets["ServerPort"], "Server Port"))

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Title"])
        layout.addWidget(_server_row)
        layout.addWidget(widgets["ProcessBtn"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Icon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)
        layout.addStretch(1)

        widgets["ProcessBtn"].clicked.connect(self.on_process_clicked)

        self._widgets = widgets
        self.set_heading("Floating", "building.svg")

    def status_update(self, data):
        action = "Drop Lease" if data["hasLease"] else "Request Lease"
        self._widgets["ServerIP"].setText(data["ip"])
        self._widgets["ServerPort"].setText(data["port"])
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
    """Manage product licence

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
            "ConnCheckHint": QtWidgets.QLabel("Checking internet..."),
            "Pages": QtWidgets.QStackedWidget(),
            "NodeLock": LicenceNodeLock(),
            "NodeLockOffline": LicenceNodeLockOffline(),
            "Floating": LicenceFloating(),
            "DeactivationBox": LicenceOfflineDeactivationBox(),
        }
        widgets["ConnCheckHint"].setVisible(False)
        widgets["ConnCheckHint"].setObjectName("HintMessage")

        widgets["Pages"].addWidget(widgets["NodeLock"])
        widgets["Pages"].addWidget(widgets["NodeLockOffline"])
        widgets["Pages"].addWidget(widgets["Floating"])
        widgets["Pages"].addWidget(widgets["DeactivationBox"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["ConnCheckHint"])
        layout.addWidget(widgets["Pages"])

        widgets["DeactivationBox"].dismissed.connect(self.on_box_dismissed)
        widgets["Floating"].float_requested.connect(self.float_requested)
        widgets["Floating"].float_dropped.connect(self.float_dropped)
        widgets["NodeLock"].node_activated.connect(self.node_activated)
        widgets["NodeLock"].node_deactivated.connect(self.node_deactivated)
        widgets["NodeLockOffline"].node_activated.connect(self.node_activated)
        widgets["NodeLockOffline"].offline_activate_requested.connect(
            self.offline_activate_requested)
        widgets["NodeLockOffline"].offline_deactivate_requested.connect(
            self.offline_deactivate_requested)

        self._widgets = widgets
        self._is_offline = None

    def on_offline_activate_requested(self):
        self._widgets["NodeLockOffline"].set_activation_request()

    def on_offline_deactivate_requested(self):
        self._widgets["NodeLockOffline"].write_temp_key()
        self.licence_updated.emit()

    def on_box_dismissed(self):
        self._widgets["NodeLockOffline"].remove_deactivation_request_file()
        self._widgets["NodeLockOffline"].remove_temp_key()
        self.licence_updated.emit()

    def _update(self, data):
        if self._widgets["NodeLockOffline"].is_deactivation_requested():
            # ensure user completed the process before dumping request code
            self._widgets["Pages"].setCurrentIndex(3)
            _off = self._widgets["NodeLockOffline"]
            _box = self._widgets["DeactivationBox"]
            _box.set_product_key(_off.read_temp_key())
            _box.set_request_code(_off.read_deactivation_request_file())

        if data["isFloating"]:
            log.info("Ragdoll is floating")
            self._widgets["Pages"].setCurrentIndex(2)

        elif data["isTrial"]:
            if data["trialDays"] < 1:
                log.info("Ragdoll is expired")
            else:
                log.info("Ragdoll is in trial mode")
        else:
            # node-lock
            if data["isActivated"]:
                log.info("Ragdoll is activated")
            else:
                log.info("Ragdoll is deactivated")
            self._widgets["Pages"].setCurrentIndex(bool(self._is_offline))

        widget = self._widgets["Pages"].currentWidget()
        widget.status_update(data)

    def status_update(self, data):
        if not data["isFloating"] and self._is_offline is None:
            # check server connection for node-lock licencing on first run
            self._widgets["ConnCheckHint"].setVisible(True)
            self.setEnabled(False)

            def check_internet():
                try:
                    response = request.urlopen("https://wyday.com")
                except Exception:
                    return False
                return response.code == 200

            def on_internet_checked(_200):
                self._is_offline = not _200
                self._widgets["ConnCheckHint"].setVisible(False)
                self._update(data)
                self.setEnabled(True)

            worker = base.Thread(check_internet, parent=self)
            worker.result_ready.connect(on_internet_checked)
            worker.finished.connect(worker.deleteLater)
            worker.start()

        else:
            self._update(data)


class LicencePage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LicencePage, self).__init__(parent=parent)

        widgets = {
            "Title": QtWidgets.QLabel("Licence"),
            "Plate": LicenceStatusPlate(),
            "Body": LicenceSetupPanel(),
        }

        widgets["Title"].setObjectName("Heading1")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(pd1, 0, pd1, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["Title"])
        layout.addWidget(widgets["Plate"])
        layout.addWidget(widgets["Body"])

        self._widgets = widgets

    def input_widget(self):
        """Exposed for connecting signals
        Returns:
            LicenceSetupPanel
        """
        return self._widgets["Body"]

    def status_widget(self):
        """Exposed for connecting signals
        Returns:
            LicenceStatusPlate
        """
        return self._widgets["Plate"]


class SideBar(QtWidgets.QFrame):
    anchor_clicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(SideBar, self).__init__(parent=parent)

        widgets = {
            "Body": QtWidgets.QWidget(),
        }

        widgets["Body"].setMinimumWidth(sidebar_width)

        layout = QtWidgets.QVBoxLayout(widgets["Body"])
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addSpacing(pd1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addWidget(widgets["Body"], stretch=2)

        self.setStyleSheet("background: #2b2b2b;")
        self._widgets = widgets
        self._anchors = []

    def add_anchor(self, name, image, color):
        icon_size = int(anchor_size * 0.6)
        icon_size = QtCore.QSize(icon_size, icon_size)

        unchecked_icon = QtGui.QIcon(_resource("ui", image))
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
        """.format(color=color, size=anchor_size, radius=int(anchor_size / 2)))

        self._widgets["Body"].layout().addWidget(anchor)
        self._anchors.append(anchor)

        def on_clicked():
            for w in [w for w in self._anchors if w is not anchor]:
                w.setChecked(False)
            anchor.setChecked(True)
            self.anchor_clicked.emit(name)
        anchor.clicked.connect(on_clicked)

    def set_current_anchor(self, index):
        anchor = self._anchors[index]
        anchor.setChecked(True)


with open(_resource("ui", "style_welcome.css")) as f:
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
    result = result % dict(
        res=_resource().replace("\\", "/"),
    )
    return result


class WelcomeWindow(QtWidgets.QMainWindow):
    asset_opened = QtCore.Signal(str)
    asset_browsed = QtCore.Signal(str)
    licence_updated = QtCore.Signal()
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(WelcomeWindow, self).__init__(parent=parent)
        self.setWindowTitle("Ragdoll Dynamics")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        panels = {
            "Central": QtWidgets.QWidget(),
            "SideBar": SideBar(),
            "Scroll": QtWidgets.QScrollArea(),
        }

        widgets = {
            "Stretch": QtWidgets.QWidget(),
            "Body": QtWidgets.QWidget(),
            "Greet": GreetingPage(),
            "Assets": AssetListPage(),
            "Licence": LicencePage(),
            "VirtualSpace": QtWidgets.QSpacerItem(pd1, pd1),
        }

        spacers = []

        def add_body_spacer(_layout):
            spacers.append(QtWidgets.QSpacerItem(pd1, 0))
            _layout.addSpacerItem(spacers[-1])

        animations = {
            "FadeIn": QtCore.QPropertyAnimation(self, b"windowOpacity")
        }

        animations["FadeIn"].setDuration(150)
        animations["FadeIn"].setStartValue(0.0)
        animations["FadeIn"].setEndValue(1.0)

        panels["Scroll"].setWidgetResizable(True)
        panels["Scroll"].setWidget(widgets["Stretch"])

        panels["SideBar"].add_anchor(
            "Greet", "ragdoll_silhouette_white_128.png", "#e5d680")
        panels["SideBar"].add_anchor("Assets", "boxes.svg", "#e59680")
        panels["SideBar"].add_anchor("Licence", "award.svg", "#80e5cc")

        layout = QtWidgets.QVBoxLayout(widgets["Body"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Greet"])
        add_body_spacer(layout)
        layout.addWidget(widgets["Assets"])
        add_body_spacer(layout)
        layout.addWidget(widgets["Licence"])
        layout.addSpacerItem(widgets["VirtualSpace"])

        layout = QtWidgets.QHBoxLayout(widgets["Stretch"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QWidget(), stretch=1)
        layout.addWidget(widgets["Body"], stretch=20)
        layout.addWidget(QtWidgets.QWidget(), stretch=1)

        layout = QtWidgets.QHBoxLayout(panels["Central"])
        layout.setContentsMargins(0, 0, px(2), 0)
        layout.setSpacing(0)
        layout.addWidget(panels["SideBar"], stretch=1)
        layout.addWidget(panels["Scroll"], stretch=16)
        self.setCentralWidget(panels["Central"])

        panels["SideBar"].anchor_clicked.connect(self.on_anchor_clicked)
        widgets["Assets"].asset_opened.connect(self.asset_opened)
        widgets["Assets"].asset_browsed.connect(self.asset_browsed)
        lic = widgets["Licence"].input_widget()
        lic.licence_updated.connect(self.licence_updated)
        lic.node_activated.connect(self.node_activated)
        lic.node_deactivated.connect(self.node_deactivated)
        lic.float_requested.connect(self.float_requested)
        lic.float_dropped.connect(self.float_dropped)
        lic.offline_activate_requested.connect(self.offline_activate_requested)
        lic.offline_deactivate_requested.connect(
            self.offline_deactivate_requested)

        self._panels = panels
        self._widgets = widgets
        self._spacers = spacers
        self._animations = animations
        self.setStyleSheet(_scaled_stylesheet(stylesheet))
        self.setMinimumWidth(window_width)

    def resizeEvent(self, event):
        width, height = event.size().toTuple()

        spacing = pd1 * (width / window_width)
        for spacer in self._spacers:
            spacer.changeSize(pd1, spacing)

        virtual_space = height - self._widgets["Licence"].height()
        self._widgets["VirtualSpace"].changeSize(pd1, virtual_space)

        self._widgets["Body"].layout().invalidate()
        super(WelcomeWindow, self).resizeEvent(event)

    def on_licence_updated(self, data):
        self._widgets["Licence"].input_widget().status_update(data)
        self._widgets["Licence"].status_widget().set_product(data)
        self._widgets["Greet"].status_widget().set_licence(data)
        self._widgets["Greet"].status_widget().check_update(data)
        self._widgets["Greet"].timeline_widget().set_timeline(data)

    def on_offline_activate_requested(self):
        w = self._widgets["Licence"].input_widget()
        w.on_offline_activate_requested()

    def on_offline_deactivate_requested(self):
        w = self._widgets["Licence"].input_widget()
        w.on_offline_deactivate_requested()

    def show(self, extra_assets_path=""):
        self._widgets["Assets"].set_extra_assets(extra_assets_path)
        self._widgets["Assets"].reset()
        self._panels["SideBar"].set_current_anchor(0)
        self.setWindowOpacity(0)
        super(WelcomeWindow, self).show()
        self.resize(window_width, window_height)
        self._animations["FadeIn"].start()
        # init
        self.licence_updated.emit()

    def on_anchor_clicked(self, name):
        widget = self._widgets.get(name)
        self._panels["Scroll"].verticalScrollBar().setValue(widget.y() - pd1)
