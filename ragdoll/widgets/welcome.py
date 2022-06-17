
import os
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

from . import base
from .. import __

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
splash_height = px(350)
window_width = sidebar_width + splash_width + (pd4 * 2) + scroll_width
window_height = px(574)  # just enough to see the first row of videos


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
        painter.setClipPath(path.simplified())
        painter.setRenderHint(painter.Antialiasing)
        painter.drawPixmap(0, 0, self._image)


class GreetingStatus(base.OverlayWidget):

    def __init__(self, parent=None):
        super(GreetingStatus, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

        widgets = {
            "StartupChk": QtWidgets.QCheckBox("Show on startup"),
            "Line": QtWidgets.QLabel(),
            "Version": QtWidgets.QLabel(),
            "UpdateIcon": QtWidgets.QLabel(),
            "UpdateLink": QtWidgets.QLabel(),
            "Badge": LicenceStatusBadge(),
        }

        widgets["Line"].setObjectName("GreetingStatusLine")
        widgets["Line"].setFixedWidth(splash_width)
        widgets["Line"].setFixedHeight(px(32))
        widgets["Line"].setStyleSheet("""
        #GreetingStatusLine {{
            background-color: #8c000000;
            border-bottom-left-radius: {radius}px;
            border-bottom-right-radius: {radius}px;
        }}
        """.format(radius=px(8)))

        widgets["UpdateIcon"].setFixedSize(QtCore.QSize(px(20), px(20)))
        widgets["UpdateLink"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setText("Version %s" % __.version_str)

        widgets["StartupChk"].setObjectName("GreetingStartupChk")
        widgets["StartupChk"].setChecked(True)  # todo: optionVar

        layout = QtWidgets.QHBoxLayout(widgets["Line"])
        layout.setContentsMargins(px(8), px(6), px(2), px(6))
        layout.setSpacing(px(5))
        layout.addWidget(widgets["Version"])
        layout.addSpacing(px(12))
        layout.addWidget(widgets["UpdateIcon"], alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(widgets["UpdateLink"], alignment=QtCore.Qt.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(widgets["Badge"], alignment=QtCore.Qt.AlignRight)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["StartupChk"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)
        layout.addWidget(widgets["Line"], alignment=QtCore.Qt.AlignHCenter)

        self._widgets = widgets

    def check_update(self, data):
        widgets = self._widgets

        def on_update_checked(status, latest):
            icon = {
                "update": _resource("ui", "cloud-arrow-down-fill.svg"),
                "uptodate": _resource("ui", "cloud-check-fill.svg"),
                "offline": _resource("ui", "cloud-slash.svg"),
                "expired": _resource("ui", "cloud.svg"),
            }[status]
            color = {
                "update": "#83d0f0",
                "uptodate": "",
                "offline": "",
                "expired": "",
            }[status]
            text = {
                "update": "update available (%s)" % latest,
                "uptodate": "you're up to date",
                "offline": "no internet, can't check for update",
                "expired": "annual upgrade expired",
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
                background: transparent;
                border: none;
                outline: none;
            """ % color)

            if status == "update":
                widgets["UpdateLink"].setOpenExternalLinks(True)
                widgets["UpdateLink"].setTextInteractionFlags(
                    QtCore.Qt.TextBrowserInteraction
                )
                widgets["UpdateLink"].setText("""
                <style> a:link {color: #83d0f0;}</style>
                <a href=\"https://learn.ragdolldynamics.com/download/\">%s</a>
                """ % text)
            else:
                widgets["UpdateLink"].setOpenExternalLinks(False)
                widgets["UpdateLink"].setTextInteractionFlags(
                    QtCore.Qt.NoTextInteraction
                )
                widgets["UpdateLink"].setText(text)

        def _check_update():
            if data["offlineMode"]:
                on_update_checked("offline", "")
            else:
                if data["isTrial"]:
                    aup_expired = False  # doesn't have valid aup date in trial
                else:
                    _df = '%Y-%m-%d %H:%M:%S'
                    aup = data["annualUpgradeProgram"]
                    aup_expired = (
                        datetime.strptime(aup, _df) < datetime.now() if aup
                        else False
                    )

                if aup_expired:
                    on_update_checked("expired", "")
                else:
                    # check update
                    url = "https://ragdolldynamics.com/version"
                    response = request.urlopen(url)
                    latest = json.loads(response.read())["latestVersion"]
                    if latest == __.version_str:
                        on_update_checked("uptodate", "")
                    else:
                        on_update_checked("update", latest)

        _check_update()

    def set_licence(self, data):
        self._widgets["Badge"].set_status(data)


class GreetingPage(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(GreetingPage, self).__init__(parent)

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
        self._image = QtGui.QPixmap(poster).scaled(
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
            [tag["color"] for tag in index.data(AssetCardModel.TagsRole)]
        )

    def on_clicked(self):
        # todo: unzip and open, unzip to where? right next to the zip file.
        print("clicked!")

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
    NameRole = QtCore.Qt.UserRole + 10
    TagsRole = QtCore.Qt.UserRole + 11
    VideoRole = QtCore.Qt.UserRole + 12
    PosterRole = QtCore.Qt.UserRole + 13
    SceneRole = QtCore.Qt.UserRole + 14

    AssetFileName = "ragdollAssets.json"

    def refresh(self, lib_path=None):
        self.clear()

        lib_path = lib_path or _resource()
        asset_file = os.path.join(lib_path, self.AssetFileName)
        if not os.path.isfile(asset_file):
            return

        with open(asset_file) as f:
            manifest = json.load(f)

        all_tags = manifest.get("tags") or []

        for asset in manifest.get("assets") or []:
            item = QtGui.QStandardItem()
            name = asset["name"]
            poster = os.path.join(lib_path, asset["poster"])
            video = os.path.join(lib_path, asset["video"])  # todo: http link
            scene = os.path.join(lib_path, asset["scene"])  # todo: http link
            tags = []
            for tag_name in set(asset["tags"]):
                for tag in all_tags:
                    if tag["name"] == tag_name:
                        tags.append(tag)
                        break
                else:
                    tags.append({
                        "name": tag_name,
                        "color": "black",
                    })

            item.setData(name, AssetCardModel.NameRole)
            item.setData(poster, AssetCardModel.PosterRole)
            item.setData(video, AssetCardModel.VideoRole)
            item.setData(scene, AssetCardModel.SceneRole)
            item.setData(tags, AssetCardModel.TagsRole)

            self.appendRow(item)


class AssetCardProxyModel(QtCore.QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(AssetCardProxyModel, self).__init__(parent=parent)
        self.setFilterRole(AssetCardModel.NameRole)
        # todo: support multiple tags


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
        AssetTag:hover {{
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
            item = layout.takeAt(0)

    def on_tag_toggled(self, _):
        activated = set()
        for btn in self.children():
            if isinstance(btn, QtWidgets.QPushButton) and btn.isChecked():
                activated.add(btn.text())
        self.tagged.emit(activated)


class AssetLibraryPath(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(AssetLibraryPath, self).__init__(parent=parent)

        widgets = {
            "LineEdit": QtWidgets.QLineEdit(),
            "Browse": QtWidgets.QPushButton(),
        }
        widgets["Browse"].setIcon(QtGui.QIcon(_resource("ui", "folder.svg")))

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Offline Library Path"))
        layout.addSpacing(pd4)
        layout.addWidget(widgets["LineEdit"])
        layout.addWidget(widgets["Browse"])

        widgets["Browse"].clicked.connect(self.on_browsed)

        self._widgets = widgets

    def on_browsed(self):
        pass  # todo: save selected folder into optionVar

    def current_path(self):
        return self._widgets["LineEdit"].text()


class AssetListPage(QtWidgets.QWidget):
    # todo: poster shifts when scrolling

    def __init__(self, parent=None):
        super(AssetListPage, self).__init__(parent=parent)

        widgets = {
            "Head": QtWidgets.QLabel("Assets"),
            "Tags": AssetTagList(),
            "List": AssetCardView(),
            "Path": AssetLibraryPath(),
            "Empty": QtWidgets.QLabel("No Asset Found.")
        }

        models = {
            "Source": AssetCardModel(),
            "Proxy": AssetCardProxyModel(),
        }

        widgets["Head"].setObjectName("Heading1")
        widgets["Empty"].setFixedHeight(px(100))
        widgets["Empty"].setAlignment(QtCore.Qt.AlignCenter)
        widgets["Empty"].setVisible(False)

        models["Proxy"].setSourceModel(models["Source"])
        widgets["List"].setModel(models["Proxy"])

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(pd1, 0, pd1, 0)
        layout.setSpacing(pd3)
        layout.addWidget(widgets["Head"])
        layout.addWidget(widgets["Tags"])
        layout.addWidget(widgets["List"])
        layout.addWidget(widgets["Empty"])
        layout.addWidget(widgets["Path"])

        widgets["Tags"].tagged.connect(self.on_tag_changed)

        self._models = models
        self._widgets = widgets

    def resizeEvent(self, event):
        super(AssetListPage, self).resizeEvent(event)
        self._widgets["List"].adjust_viewport()

    def on_tag_changed(self, tags):
        _proxy = self._models["Proxy"]
        _view = self._widgets["List"]

        _proxy.setFilterRegExp(" ".join(tags))
        for row in range(_proxy.rowCount()):
            index = _proxy.index(row, 0)
            if _view.indexWidget(index) is None:
                self.init_widget(_proxy.mapToSource(index))
        _view.adjust_viewport()

    def reset(self):
        lib_path = self._widgets["Path"].current_path()
        model = self._models["Source"]
        model.refresh(lib_path)

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            self.init_widget(index)
            for tag in model.data(index, model.TagsRole):
                self._widgets["Tags"].add_tag(tag["name"], tag["color"])

        self._widgets["Empty"].setVisible(not model.rowCount())

    def init_widget(self, index):
        widget = AssetCardItem()
        widget.init(index)
        item = self._models["Source"].itemFromIndex(index)
        item.setSizeHint(widget.sizeHint())
        self._widgets["List"].setIndexWidget(
            self._models["Proxy"].mapFromSource(index),
            widget,
        )


class LicenceStatusBadge(QtWidgets.QWidget):
    """One liner product badge

    A badge that sit at right bottom corner of top splash image.
    Which looks like this:

        ( Complete > Expiry June.20.2022 )

    """

    def __init__(self, parent=None):
        super(LicenceStatusBadge, self).__init__(parent=parent)

        class _Arrow(QtWidgets.QWidget):
            def paintEvent(self_, event):
                rect = event.rect()

                path = QtGui.QPainterPath()
                path.moveTo(rect.topLeft())
                path.lineTo(rect.bottomLeft())
                path.lineTo(QtCore.QPointF(rect.width(), rect.height() / 2))
                path.lineTo(rect.topLeft())

                p = QtGui.QPainter(self_)
                p.setRenderHint(p.Antialiasing)
                p.setPen(QtCore.Qt.NoPen)
                p.fillRect(rect, QtGui.QBrush(QtGui.QColor(self._c_tail)))
                p.fillPath(path, QtGui.QBrush(QtGui.QColor(self._c_head)))

        widgets = {
            "Plan": QtWidgets.QLabel(),
            "Deco": _Arrow(),
            "Stat": QtWidgets.QLabel(),
        }

        widgets["Deco"].setFixedWidth(px(8))  # Arrow size |>

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(px(5), 0, px(5), 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Plan"])
        layout.addWidget(widgets["Deco"])
        layout.addWidget(widgets["Stat"])

        self._widgets = widgets
        self._c_head = ""
        self._c_tail = ""

    def set_status(self, data):
        expiry = data["expiry"]
        aup = data["annualUpgradeProgram"]
        perpetual = not expiry and aup and data["product"] != "trial"

        if perpetual:
            _aup_date = datetime.strptime(aup, '%Y-%m-%d %H:%M:%S')
            aup = _aup_date.strftime("%b.%d.%Y")
            expired = False
        elif expiry:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = expiry_date < datetime.now()
        else:
            # as in trial
            expiry_date = datetime.now() + timedelta(days=data["trialDays"])
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = data["trialDays"] < 1
            perpetual = False

        self._c_head = (
            "#5ba3bd" if perpetual else "#ac4a4a" if expired else "#5ddb7a")
        self._c_tail = (
            "#8ebecf" if perpetual else "#e27d7d" if expired else "#92dba3")
        _text = (
            "#2d5564" if perpetual else "#732a2a" if expired else "#206931")

        p = px(8)
        r = px(6)  # border radius
        w = self._widgets
        w["Plan"].setText(data["marketingName"])
        w["Stat"].setText("%s %s" % (
            "perpetual" if perpetual else "expired" if expired else "expiry",
            ("/ AUP " + aup) if perpetual else expiry,
        ))

        w["Plan"].setStyleSheet("""
            background: {c_head};
            color: #ffffff;
            padding-left: {p}px;
            border-top-left-radius: {r}px;
            border-bottom-left-radius: {r}px;
        """.format(c_head=self._c_head, p=p, r=r))

        w["Stat"].setStyleSheet("""
            background: {c_tail};
            color: {c_text};
            padding-left: {_}px;
            padding-right: {p}px;
            border-top-right-radius: {r}px;
            border-bottom-right-radius: {r}px;
        """.format(c_tail=self._c_tail, c_text=_text, r=r, p=p, _=px(4)))


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
        self.setFixedHeight(px(86))

        panels = {
            "Product": QtWidgets.QWidget(),
        }

        widgets = {
            "Product": QtWidgets.QLabel(),
            "Commercial": QtWidgets.QLabel(),
            "Features": QtWidgets.QLabel(),
        }

        panels["Product"].setFixedWidth(px(125))
        panels["Product"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Product"].setObjectName("PlateProduct")
        widgets["Commercial"].setObjectName("PlateCommercial")
        widgets["Features"].setObjectName("PlateFeatures")

        layout = QtWidgets.QVBoxLayout(panels["Product"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Product"], alignment=QtCore.Qt.AlignRight)
        layout.addWidget(widgets["Commercial"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(px(12), px(6), px(6), px(6))
        layout.addWidget(panels["Product"])
        layout.addSpacing(px(30))
        layout.addWidget(widgets["Features"])
        layout.addStretch(1)

        self._widgets = widgets

    def set_product(self, data):
        self._widgets["Product"].setText(data["marketingName"])
        self._widgets["Commercial"].setText(
            "Non-Commercial" if data["isNonCommercial"] else "Commercial use"
        )
        self._widgets["Features"].setText(
            # Max four lines
            {
                "Trial": (
                    "Record up to 100 frames\n"
                    "Export up to 10 Markers\n"
                ),
                "Personal": (
                    "Record up to 100 frames\n"
                    "Export up to 10 Markers\n"
                    "Free upgrades forever\n"
                ),
                "Complete": (
                    "Unlimited recording frames\n"
                    "Export up to 10 Markers\n"
                    "High-performance solver\n"
                ),
                "Unlimited": (
                    "The fully-featured, unrestricted version\n"
                ),
                "Batch": (
                    ""
                ),
            }.get(data["marketingName"], "Unknown Product")
        )
        gradient = {
            "Trial": "stop:0 #ff7a95, stop:1 #ffb696",
            "Personal": "stop:0 #4facfe, stop:1 #00f2fe",
            "Complete": "stop:0 #c1fdc9, stop:1 #57f5a1",
            "Unlimited": "stop:0 #dbddd7, stop:0.5 #cf436b, stop:1 #1f1828",
            "Batch": "stop:0 #a7a6cb, stop:1 #8989ba",
        }.get(data["marketingName"], "stop:0 #959595, stop:1 #646464")

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


class LicenceSetupPanel(QtWidgets.QStackedWidget):
    """Manage product licence

    A widget that enables users to activate/deactivate licence, node-lock
    or floating, and shows licencing status.

    This widget is DCC App agnostic, you must connect corresponding signals
    respectively so to collect licencing data from DCC App.

    """
    updated = QtCore.Signal()
    node_activated = QtCore.Signal(str)
    node_deactivated = QtCore.Signal()
    float_requested = QtCore.Signal()
    float_dropped = QtCore.Signal()
    offline_activate_requested = QtCore.Signal(str, str)
    offline_deactivate_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(LicenceSetupPanel, self).__init__(parent=parent)

        panels = {
            "Floating": QtWidgets.QWidget(),
            "NodeLock": QtWidgets.QWidget(),
        }

        widgets = {
            # floating
            "FloatingIcon": QtWidgets.QLabel(),
            "FloatingTitle": QtWidgets.QLabel(),
            "ServerIP": QtWidgets.QLineEdit(),
            "ServerPort": QtWidgets.QLineEdit(),
            "LeaseBtn": QtWidgets.QPushButton(),
            # node-lock
            "NodeLockIcon": QtWidgets.QLabel(),
            "NodeLockTitle": QtWidgets.QLabel(),
            "ProductKey": QtWidgets.QLineEdit(),
            "KeyBtn": QtWidgets.QPushButton(),
            # node-lock (offline)
            "OfflineOpts": QtWidgets.QWidget(),
            "OfflineHint": QtWidgets.QLabel(),
            "RequestCode": QtWidgets.QLineEdit(),
            "RequestCodeBtn": QtWidgets.QPushButton(),
            "CopyPasteURL": QtWidgets.QLabel(),
            "ResponseCode": QtWidgets.QLineEdit(),
        }

        panels["Floating"].setMaximumWidth(px(540))
        panels["NodeLock"].setMaximumWidth(px(540))

        widgets["ServerIP"].setFixedWidth(px(120))
        widgets["ServerPort"].setFixedWidth(px(60))
        widgets["ServerIP"].setReadOnly(True)  # set from env var
        widgets["ServerPort"].setReadOnly(True)  # set from env var

        widgets["OfflineHint"].setObjectName("OfflineHint")
        widgets["RequestCodeBtn"].setObjectName("IconPushButton")
        widgets["RequestCodeBtn"].setIcon(
            QtGui.QIcon(_resource("ui", "arrow-repeat.svg"))
        )
        widgets["RequestCode"].setReadOnly(True)

        widgets["CopyPasteURL"].setObjectName("CopyPasteURL")
        widgets["CopyPasteURL"].setOpenExternalLinks(True)
        widgets["CopyPasteURL"].setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction
        )
        widgets["CopyPasteURL"].setText(
            """
            <style> p {color: #8c8c8c;} a:link {color: #80e5cc;}</style>
            <p>Copy paste to </p> 
            <a href=\"https://ragdolldynamics.com/offline\">
            https://ragdolldynamics.com/offline</a>
            """
        )

        widgets["ResponseCode"].setPlaceholderText(
            "Paste response code from https://ragdolldynamics.com/offline"
        )

        def _set_icon(label, image):
            label.setFixedSize(QtCore.QSize(px(64), px(64)))
            label.setStyleSheet("""
            image: url({image});
            """.format(image=_resource("ui", image)))

        def _set_title(label, text):
            label.setObjectName("Heading2")
            label.setText(text)

        def _wrap(widget, with_label):
            c = QtWidgets.QWidget()
            label = QtWidgets.QLabel(with_label)
            _layout = QtWidgets.QVBoxLayout(c)
            _layout.setContentsMargins(0, 0, 0, 0)
            _layout.setSpacing(pd3)
            _layout.addWidget(label)
            _layout.addWidget(widget)
            widget.setParent(c)
            return c

        _set_icon(widgets["FloatingIcon"], "building.svg")
        _set_title(widgets["FloatingTitle"], "Floating")

        _server_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_server_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(_wrap(widgets["ServerIP"], "Server IP"))
        layout.addWidget(_wrap(widgets["ServerPort"], "Server Port"))

        _btn_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_btn_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addStretch(1)
        layout.addWidget(widgets["LeaseBtn"])

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["FloatingTitle"])
        layout.addWidget(_server_row)
        layout.addWidget(_btn_row)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["Floating"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["FloatingIcon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)
        layout.addStretch(1)

        _set_icon(widgets["NodeLockIcon"], "pc-display.svg")
        _set_title(widgets["NodeLockTitle"], "Node Lock")

        _req_line = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_req_line)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd4)
        layout.addWidget(widgets["RequestCode"])
        layout.addWidget(widgets["RequestCodeBtn"])

        _req_code = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_req_code)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(px(1))
        layout.addWidget(_wrap(_req_line, "Request Code"))
        layout.addWidget(widgets["CopyPasteURL"], 0, QtCore.Qt.AlignRight)

        layout = QtWidgets.QVBoxLayout(widgets["OfflineOpts"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["OfflineHint"])
        layout.addWidget(_req_code)
        layout.addWidget(_wrap(widgets["ResponseCode"], "Response Code"))

        _btn_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_btn_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addStretch(1)
        layout.addWidget(widgets["KeyBtn"])

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["NodeLockTitle"])
        layout.addWidget(_wrap(widgets["ProductKey"], "Product Key"))
        layout.addWidget(widgets["OfflineOpts"])
        layout.addWidget(_btn_row)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["NodeLock"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd2)
        layout.addWidget(widgets["NodeLockIcon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)

        widgets["RequestCodeBtn"].clicked.connect(self.on_request_code_clicked)
        widgets["ResponseCode"].textChanged.connect(self.on_response_changed)
        widgets["KeyBtn"].clicked.connect(self.on_key_clicked)
        widgets["LeaseBtn"].clicked.connect(self.on_lease_clicked)

        self.addWidget(panels["NodeLock"])
        self.addWidget(panels["Floating"])

        self._panels = panels
        self._widgets = widgets
        self._data = None
        self._reqfname = os.path.join(
            tempfile.gettempdir(), "ragdollTempRequest.xml"
        )
        self._resfname = os.path.join(
            tempfile.gettempdir(), "ragdollTempResponse.xml"
        )

    def update_data(self, data):
        self._data = data

        # floating license
        if data["isFloating"]:
            self.on_floating()

        # node-lock
        elif data["isTrial"]:
            if data["trialDays"] < 1:
                self.on_expired()
            else:
                self.on_trail()

        elif data["isActivated"]:
            self.on_activated()

        else:
            self.on_deactivated()

    def set_offline_request_code(self):
        try:
            with open(self._reqfname) as f:
                self._widgets["RequestCode"].setText(f.read())
        except Exception:
            self._widgets["RequestCode"].setText("")

    def _offline_options(self):
        if self._data["offlineMode"]:
            self._widgets["OfflineOpts"].show()
            self._widgets["ResponseCode"].setText("")
            hint = (
                "No internet, cannot reach official Ragdoll server.\n"
                "Require another internet accessible device to complete "
                "following process."
            )
            if self._data["isActivated"]:
                hint += (
                    "\n\n"
                    "CAUTION: If you deactivate Maya without deactivating"
                    "online,\nyour licence will still be considered active "
                    "and cannot be reactivated.\n\n"
                    "If this happens, contact support@ragdolldynamics.com"
                )
                self._widgets["ResponseCode"].parent().hide()
                self._widgets["OfflineHint"].setText(hint)
                self._widgets["KeyBtn"].setEnabled(True)
            else:
                self._widgets["ResponseCode"].parent().show()
                self._widgets["OfflineHint"].setText(hint)
                self._widgets["KeyBtn"].setEnabled(False)

        else:
            self._widgets["OfflineOpts"].hide()

    def _update_product_key(self):
        self._widgets["ProductKey"].setText("")

        key = self._data["key"]
        if key:
            self._widgets["ProductKey"].setPlaceholderText(key)
        else:
            self._widgets["ProductKey"].setPlaceholderText(
                "Your key, e.g. 0000-0000-0000-0000-0000-0000-0000"
            )

    def on_floating(self):
        log.info("Ragdoll is floating")
        self.setCurrentIndex(1)
        data = self._data

        self._widgets["ServerIP"].setText(data["ip"] or "")
        self._widgets["ServerPort"].setText(str(data["port"]) or "")

        if data["hasLease"]:
            self._widgets["LeaseBtn"].setText("Drop Lease")
        else:
            self._widgets["LeaseBtn"].setText("Request Lease")

    def on_expired(self):
        log.info("Ragdoll is expired")
        self.setCurrentIndex(0)
        self._update_product_key()
        self._offline_options()
        self._widgets["ProductKey"].setReadOnly(False)
        self._widgets["KeyBtn"].setText("Activate")

    def on_trail(self):
        log.info("Ragdoll is in trial mode")
        self.setCurrentIndex(0)
        self._update_product_key()
        self._offline_options()
        self._widgets["ProductKey"].setReadOnly(False)
        self._widgets["KeyBtn"].setText("Activate")

    def on_activated(self):
        log.info("Ragdoll is activated")
        self.setCurrentIndex(0)
        self._update_product_key()
        self._offline_options()
        self._widgets["ProductKey"].setReadOnly(True)
        self._widgets["KeyBtn"].setText("Deactivate")

    def on_deactivated(self):
        log.info("Ragdoll is deactivated")
        self.setCurrentIndex(0)
        self._update_product_key()
        self._offline_options()
        self._widgets["ProductKey"].setReadOnly(False)
        self._widgets["KeyBtn"].setText("Activate")

    def on_request_code_clicked(self):
        key = self._widgets["ProductKey"].text()
        self.offline_activate_requested.emit(key, self._reqfname)

    def on_key_clicked(self):
        if self._data["isActivated"]:
            # deactivation
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

            if self._data["offlineMode"]:
                self.offline_deactivate_requested.emit(self._reqfname)
            else:
                self.node_deactivated.emit()

        else:
            # activation
            if self._data["offlineMode"]:
                text = self._widgets["ResponseCode"].toPlainText()
                assert text, "No response found"

                with open(self._resfname, "w") as _f:
                    _f.write(text)
                self.node_activated.emit(self._resfname)
            else:
                key = (
                    self._widgets["ProductKey"].text() or self._data.get("key")
                )
                if key:
                    self.node_activated.emit(key)
                else:
                    log.warning("Provide a product key")

    def on_lease_clicked(self):
        if self._data["hasLease"]:
            # drop
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
        else:
            # request
            self.float_requested.emit()

    def on_response_changed(self, text):
        self._widgets["KeyBtn"].setEnabled(bool(text))


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
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd3)
        layout.addSpacing(pd1)
        self.setFixedWidth(sidebar_width)
        self.setStyleSheet("background: #2b2b2b;")
        self._anchors = []

    def add_anchor(self, name, image, color):
        icon_size = QtCore.QSize(px(30), px(30))

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

        self.layout().addWidget(anchor)
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

    def __init__(self, parent=None):
        super(WelcomeWindow, self).__init__(parent=parent)
        self.setWindowTitle("Welcome")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        panels = {
            "Central": QtWidgets.QWidget(),
            "SideBar": SideBar(),
            "Scroll": QtWidgets.QScrollArea(),
        }

        widgets = {
            "Body": QtWidgets.QWidget(),
            "Greet": GreetingPage(),
            "Assets": AssetListPage(),
            "Licence": LicencePage(),
        }

        panels["Scroll"].setWidgetResizable(True)
        panels["Scroll"].setWidget(widgets["Body"])

        panels["SideBar"].add_anchor(
            "Greet", "ragdoll_silhouette_white_128.png", "#e5d680")
        panels["SideBar"].add_anchor("Assets", "boxes.svg", "#e59680")
        panels["SideBar"].add_anchor("Licence", "shield-lock.svg", "#80e5cc")

        layout = QtWidgets.QVBoxLayout(widgets["Body"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(pd1)
        layout.addWidget(widgets["Greet"])
        layout.addWidget(widgets["Assets"])
        layout.addWidget(widgets["Licence"])
        layout.addSpacing(px(100))
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["Central"])
        layout.setContentsMargins(0, 0, px(2), 0)
        layout.setSpacing(0)
        layout.addWidget(panels["SideBar"])
        layout.addWidget(panels["Scroll"])
        self.setCentralWidget(panels["Central"])

        panels["SideBar"].anchor_clicked.connect(self.on_anchor_clicked)

        self._panels = panels
        self._widgets = widgets
        self.setStyleSheet(_scaled_stylesheet(stylesheet))
        self.setMinimumWidth(window_width)
        self.resize(window_width, window_height)

    def licence_input_widget(self):
        """Exposed for connecting signals
        Returns:
            LicenceSetupPanel
        """
        return self._widgets["Licence"].input_widget()

    def licence_status_widget(self):
        """Exposed for connecting signals
        Returns:
            LicenceStatusPlate
        """
        return self._widgets["Licence"].status_widget()

    def greeting_status_widget(self):
        """Exposed for connecting signals
        Returns:
            GreetingStatus
        """
        return self._widgets["Greet"].status_widget()

    def show(self):
        super(WelcomeWindow, self).show()
        self._widgets["Assets"].reset()
        self.licence_input_widget().updated.emit()
        self._panels["SideBar"].set_current_anchor(0)

    def on_anchor_clicked(self, name):
        widget = self._widgets.get(name)
        self._panels["Scroll"].ensureWidgetVisible(widget)
