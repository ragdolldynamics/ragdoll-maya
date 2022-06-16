
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


video_width, video_height = 320, 180
card_padding = 6
card_rounding = 12
card_width = video_width + (card_padding * 2)
card_height = video_height + (card_padding * 2)


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


class GreetingStatus(base.OverlayWidget):
    FixedHeight = 48

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
        widgets["Line"].setFixedWidth(GreetingPage.FixedWidth)
        widgets["Line"].setFixedHeight(self.FixedHeight)
        widgets["Line"].setStyleSheet("""
        #GreetingStatusLine {
            background-color: #8c000000;
            border-bottom-left-radius: 16px;
            border-bottom-right-radius: 16px;
        }
        """)

        widgets["UpdateIcon"].setFixedSize(QtCore.QSize(32, 32))
        widgets["UpdateLink"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Version"].setText("Version %s" % __.version_str)

        widgets["StartupChk"].setChecked(True)  # todo: optionVar
        widgets["StartupChk"].setStyleSheet(
            "background: transparent; padding-right: 20px; padding-top: 10px;"
        )

        layout = QtWidgets.QHBoxLayout(widgets["Line"])
        layout.setContentsMargins(16, 8, 0, 8)
        layout.setSpacing(10)
        layout.addWidget(widgets["Version"])
        layout.addSpacing(26)
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
    FixedWidth = 1060
    FixedHeight = 533

    def __init__(self, parent=None):
        super(GreetingPage, self).__init__(parent)

        widgets = {
            "Splash": QtWidgets.QLabel(),
            "Status": GreetingStatus(self)  # overlay
        }

        widgets["Splash"].setFixedWidth(self.FixedWidth)
        widgets["Splash"].setFixedHeight(self.FixedHeight)
        widgets["Splash"].setStyleSheet("""
        background-image: url({banner});
        background-repeat: no-repeat;
        border-radius: 16px;
        """.format(banner=_resource("ui", "welcome-banner.png")))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widgets["Splash"], alignment=QtCore.Qt.AlignHCenter)

        self._widgets = widgets

    def status_widget(self):
        return self._widgets["Status"]


class AssetVideoPlayer(QtWebEngineWidgets.QWebEngineView):
    released = QtCore.Signal()
    pressed = QtCore.Signal()
    clicked = QtCore.Signal()
    entered = QtCore.Signal()
    leave = QtCore.Signal()

    def __init__(self, parent=None):
        super(AssetVideoPlayer, self).__init__(parent=parent)
        self.page().setBackgroundColor(QtGui.QColor("#353535"))
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def eventFilter(self, source, event):
        # note: for focus proxy
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() is QtCore.Qt.LeftButton:
                self.pressed.emit()

        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() is QtCore.Qt.LeftButton:
                self.released.emit()
                if self.geometry().contains(event.pos()):
                    self.clicked.emit()

        return super(AssetVideoPlayer, self).eventFilter(source, event)

    def enterEvent(self, event):
        self.entered.emit()
        self.play()

    def leaveEvent(self, event):
        self.leave.emit()
        self.pause()

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
        self.focusProxy().installEventFilter(self)
        # note: focus proxy exists after web content set.

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
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(rounded_rect, card_rounding, card_rounding)
        painter.setClipPath(path.simplified())
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
        footer_h = int(h / 3) - 10
        dot_radius = 9
        dot_padding = 12
        dot_gap = 3

        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing)

        # draw footer
        #   make a half rounded rect (sharped top, rounded bottom)
        #   ___________________
        #  |                  |
        #  |                  |
        #  \_________________/
        #
        footer_rect = QtCore.QRectF(
            card_padding,
            h - footer_h - card_padding,
            w - (card_padding * 2),
            footer_h,
        )
        footer_top_left = QtCore.QRectF(
            card_padding,
            h - footer_h - card_padding,
            card_rounding,
            card_rounding,
        )
        footer_top_right = QtCore.QRectF(
            w - card_padding - card_rounding,
            h - footer_h - card_padding,
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
        text_rect = footer_rect.adjusted(20, 6, 0, 0)
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
            "Poster": AssetVideoPoster(self),
            "Player": AssetVideoPlayer(self),
        }

        effects = {
            "Poster": QtWidgets.QGraphicsOpacityEffect(widgets["Poster"]),
        }

        animations = {
            "Poster": QtCore.QPropertyAnimation(effects["Poster"], b"opacity")
        }

        widgets["Poster"].setAttribute(QtCore.Qt.WA_StyledBackground)
        widgets["Poster"].setGraphicsEffect(effects["Poster"])
        widgets["Player"].setFixedWidth(video_width)
        widgets["Player"].setFixedHeight(video_height)

        effects["Poster"].setOpacity(1)
        animations["Poster"].setEasingCurve(QtCore.QEasingCurve.OutCubic)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(*(card_padding, ) * 4)
        layout.addWidget(widgets["Player"])

        widgets["Player"].clicked.connect(self.on_clicked)

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
        self._widgets["Poster"].set_poster(poster)
        self._widgets["Footer"].set_data(
            index.data(AssetCardModel.NameRole),
            [tag["color"] for tag in index.data(AssetCardModel.TagsRole)]
        )

    def on_clicked(self):
        print("clicked!")  # todo: open scene

    def enterEvent(self, event):
        anim = self._animations["Poster"]
        current = self._effects["Poster"].opacity()
        anim.stop()
        anim.setDuration(int(500 * current))
        anim.setStartValue(current)
        anim.setEndValue(0.0)
        anim.start()

    def leaveEvent(self, event):
        anim = self._animations["Poster"]
        current = self._effects["Poster"].opacity()
        anim.stop()
        anim.setDuration(500 - int(500 * current))
        anim.setStartValue(current)
        anim.setEndValue(1.0)
        anim.start()


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
            data = json.load(f)

        all_tags = data.get("tags") or []

        for asset in data.get("assets") or []:
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
        self.setText(name)
        self.setCheckable(True)
        self.setStyleSheet("""
        AssetTag {{
            background: transparent;
            height: 26px;
            border: 1px solid {color};
            border-radius: 10px;
            padding: 1px 10px 1px 8px;
            text-align: top center;
        }}
        AssetTag:checked {{
            background: {color};
        }}
        AssetTag:hover {{
            background: {color};
        }}
        """.format(color=color))


class AssetTagList(QtWidgets.QWidget):
    tagged = QtCore.Signal(set)

    def __init__(self, parent=None):
        super(AssetTagList, self).__init__(parent)
        base.FlowLayout(self)
        self._tags = set()

    def add_tag(self, tag, tag_color):
        if tag in self._tags:
            return
        button = AssetTag(tag, tag_color)
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
        layout.addSpacing(10)
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
        widgets["Empty"].setFixedHeight(200)
        widgets["Empty"].setAlignment(QtCore.Qt.AlignCenter)
        widgets["Empty"].setVisible(False)

        models["Proxy"].setSourceModel(models["Source"])
        widgets["List"].setModel(models["Proxy"])

        layout = QtWidgets.QVBoxLayout(self)
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

        widgets["Deco"].setFixedWidth(10)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Plan"])
        layout.addWidget(widgets["Deco"])
        layout.addWidget(widgets["Stat"])

        self._widgets = widgets
        self._c_head = ""
        self._c_tail = ""
        self._c_text = ""

    def set_status(self, data):
        is_trial = data["isTrial"]
        trial_days = data["trialDays"]
        product = data["product"]
        expiry = data["expiry"]
        perpetual = not expiry
        aup = data["annualUpgradeProgram"]

        if is_trial:
            expiry_date = datetime.now() + timedelta(days=trial_days)
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = trial_days < 1
            perpetual = False

        elif perpetual:
            # Assuming perpetual licence always have AUP expiry date
            _aup_date = datetime.strptime(aup, '%Y-%m-%d %H:%M:%S')
            aup = _aup_date.strftime("%b.%d.%Y")
            expired = False
        else:
            expiry_date = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
            expiry = expiry_date.strftime("%b.%d.%Y")
            expired = expiry_date < datetime.now()

        self._c_head = (
            "#5ba3bd" if perpetual
            else "#ac4a4a" if expired
            else "#5ddb7a"
        )
        self._c_tail = (
            "#8ebecf" if perpetual
            else "#e27d7d" if expired
            else "#92dba3"
        )
        self._c_text = (
            "#2d5564" if perpetual
            else "#732a2a" if expired
            else "#206931"
        )

        w = self._widgets
        w["Plan"].setText(product.capitalize())
        w["Stat"].setText("%s %s" % (
            "perpetual" if perpetual else "expired" if expired else "expiry",
            ("/ AUP " + aup) if perpetual else expiry,
        ))

        w["Plan"].setStyleSheet("""
            background: {c_head};
            color: #ffffff;
            padding-left: 10px;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        """.format(c_head=self._c_head))
        w["Plan"].style().unpolish(w["Plan"])
        w["Plan"].style().polish(w["Plan"])

        w["Stat"].setStyleSheet("""
            background: {c_tail};
            color: {c_text};
            padding-left: 4px;
            padding-right: 10px;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        """.format(c_tail=self._c_tail, c_text=self._c_text))
        w["Stat"].style().unpolish(w["Stat"])
        w["Stat"].style().polish(w["Stat"])


class LicenceStatusPlate(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(LicenceStatusPlate, self).__init__(parent=parent)
        self.setObjectName("LicencePlate")
        self.setFixedHeight(172)

        panels = {
            "Product": QtWidgets.QWidget(),
        }

        widgets = {
            "Product": QtWidgets.QLabel(),
            "Commercial": QtWidgets.QLabel(),
            "Features": QtWidgets.QLabel(),
        }

        panels["Product"].setAttribute(QtCore.Qt.WA_NoSystemBackground)
        widgets["Product"].setObjectName("PlateProduct")
        widgets["Commercial"].setObjectName("PlateCommercial")
        widgets["Features"].setObjectName("PlateFeatures")

        layout = QtWidgets.QVBoxLayout(panels["Product"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widgets["Product"])
        layout.addWidget(widgets["Commercial"], alignment=QtCore.Qt.AlignRight)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 12, 12)
        layout.addWidget(panels["Product"])
        layout.addWidget(widgets["Features"])
        layout.addStretch(1)

        self._widgets = widgets

    def set_product(self, data):
        # todo: product feature list
        # todo: gradient color for each product and expired/invalid
        product = data["product"]
        non_commercial = data["isNonCommercial"]

        product_pretty = {
            "trial": "Trial Mode",
        }.get(product, product)

        self._widgets["Product"].setText(product_pretty.capitalize())
        self._widgets["Commercial"].setText(
            "Non-Commercial" if non_commercial else "Commercial use"
        )
        self.setStyleSheet("""
        #LicencePlate {
            font-family: Sora;
            border-radius: 20px;
            background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #c1fdc9,
                        stop:1 #57f5a1
                        );
        }
        #PlateProduct {
            font-family: Sora;
            font-size: 24pt;
            background: transparent;
            color: #353535;
        }
        #PlateCommercial {
            font-family: Sora;
            background: transparent;
            color: #353535;
        }
        #PlateFeatures {
            background: transparent;
            color: #FFFFFF;
        }
        """)

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

        panels["Floating"].setMaximumWidth(800)
        panels["NodeLock"].setMaximumWidth(800)

        widgets["ServerIP"].setFixedWidth(240)
        widgets["ServerPort"].setFixedWidth(120)
        widgets["ServerIP"].setReadOnly(True)  # set from env var
        widgets["ServerPort"].setReadOnly(True)  # set from env var

        widgets["RequestCode"].setReadOnly(True)
        widgets["RequestCodeBtn"].setObjectName("IconPushButton")
        widgets["RequestCodeBtn"].setIcon(
            QtGui.QIcon(_resource("ui", "arrow-repeat.svg"))
        )

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
            label.setFixedSize(QtCore.QSize(90, 90))
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
            _layout.setSpacing(19)
            _layout.addWidget(label)
            _layout.addWidget(widget)
            widget.setParent(c)
            return c

        _set_icon(widgets["FloatingIcon"], "building.svg")
        _set_title(widgets["FloatingTitle"], "Floating")

        _server_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_server_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addWidget(_wrap(widgets["ServerIP"], "Server IP"))
        layout.addWidget(_wrap(widgets["ServerPort"], "Server Port"))

        _btn_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_btn_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addStretch(1)
        layout.addWidget(widgets["LeaseBtn"])

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addWidget(widgets["FloatingTitle"])
        layout.addWidget(_server_row)
        layout.addWidget(_btn_row)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["Floating"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addWidget(widgets["FloatingIcon"], alignment=QtCore.Qt.AlignTop)
        layout.addWidget(_body)
        layout.addStretch(1)

        _set_icon(widgets["NodeLockIcon"], "pc-display.svg")
        _set_title(widgets["NodeLockTitle"], "Node Lock")

        _req_line = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_req_line)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(widgets["RequestCode"])
        layout.addWidget(widgets["RequestCodeBtn"])

        _req_code = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_req_code)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(_wrap(_req_line, "Request Code"))
        layout.addWidget(widgets["CopyPasteURL"], 0, QtCore.Qt.AlignRight)

        layout = QtWidgets.QVBoxLayout(widgets["OfflineOpts"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addWidget(widgets["OfflineHint"])
        layout.addWidget(_req_code)
        layout.addWidget(_wrap(widgets["ResponseCode"], "Response Code"))

        _btn_row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(_btn_row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addStretch(1)
        layout.addWidget(widgets["KeyBtn"])

        _body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(_body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
        layout.addWidget(widgets["NodeLockTitle"])
        layout.addWidget(_wrap(widgets["ProductKey"], "Product Key"))
        layout.addWidget(widgets["OfflineOpts"])
        layout.addWidget(_btn_row)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["NodeLock"])
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(28)
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

                with open(self._resfname, "w") as f:
                    f.write(text)
                self.node_activated.emit(self._resfname)
            else:
                key = self._widgets["ProductKey"].text() or self._data.get("key")
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
        layout.setSpacing(28)
        layout.addWidget(widgets["Title"])
        layout.addWidget(widgets["Plate"])
        layout.addWidget(widgets["Body"])

        self._widgets = widgets

    def input_widget(self):
        """
        Returns:
            LicenceSetupPanel
        """
        return self._widgets["Body"]

    def status_widget(self):
        """
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
        layout.setSpacing(19)
        layout.addSpacing(38)
        self.setFixedWidth(100)
        self.setStyleSheet("background: #2b2b2b;")
        self._anchors = []

    def add_anchor(self, name, image, color):
        unchecked_icon = QtGui.QIcon(_resource("ui", image))
        pixmap = unchecked_icon.pixmap(QtCore.QSize(44, 44))
        _tint_color(pixmap, QtGui.QColor("#333333"))
        checked_icon = QtGui.QIcon(pixmap)

        anchor = base.ToggleButton()
        anchor.setChecked(False)
        anchor.setIconSize(QtCore.QSize(44, 44))

        anchor.set_checked_icon(checked_icon)
        anchor.set_unchecked_icon(unchecked_icon)

        anchor.setStyleSheet("""
        QPushButton {{
            height: 72px;
            width: 72px;
            border-radius: 36px;
            background: transparent;
            padding: 0px;
        }}
        QPushButton:hover {{
            background: #454545;
        }}
        QPushButton:checked {{
            background: {color};
        }}
        """.format(color=color))

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


class WelcomeWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(WelcomeWindow, self).__init__(parent=parent)
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
        layout.addWidget(widgets["Greet"])
        layout.addWidget(widgets["Assets"])
        layout.addWidget(widgets["Licence"])
        layout.addSpacing(200)
        layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout(panels["Central"])
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(0)
        layout.addWidget(panels["SideBar"])
        layout.addWidget(panels["Scroll"])
        self.setCentralWidget(panels["Central"])

        panels["SideBar"].anchor_clicked.connect(self.on_anchor_clicked)

        self._panels = panels
        self._widgets = widgets
        self.setStyleSheet(_main_stylesheet)
        self.setMinimumWidth(1200)
        self.resize(1200, 850)

    def licence_input_widget(self):
        """
        Returns:
            LicenceSetupPanel
        """
        return self._widgets["Licence"].input_widget()

    def licence_status_widget(self):
        """
        Returns:
            LicenceStatusPlate
        """
        return self._widgets["Licence"].status_widget()

    def greeting_status_widget(self):
        """
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


_main_stylesheet = """
* {
    color: #d2d2d2;
    background: #353535;
    font-size: 9pt;
}
#Heading1 {
    font-family: Sora;
    font-size: 18pt;
}
#Heading2 {
    font-size: 15pt;
}
QLineEdit {
    height: 40px;
    border: 1px solid #4d4d4d;
    border-radius: 20px;
    padding-left: 20px;
    padding-right: 20px;
}
QCheckBox::indicator:unchecked {
    image: url("%(res)s/ui/square.svg");
}
QCheckBox::indicator:checked {
    image: url("%(res)s/ui/square-check.svg");
}
QPushButton {
    background: #4d4d4d;
    height: 40px;
    min-width: 40px;
    border-radius: 20px;
    padding-left: 20px;
    padding-right: 20px;
}
QPushButton:hover {
    background: #5f5f5f;
}
QPushButton:pressed {
    background: #424242;
}
#IconPushButton {
    padding: 0px;
}

AssetCardView {
    border: none;
    outline: none; /* Disable dotted border on focus */
}
AssetCardView::item:hovered {
    background-color: transparent; /* no highlight on hovered */
}

QAbstractScrollArea {
    border: none;
}

QScrollBar:horizontal {
    height: 12px;
    border: none;
    margin: 0px 12px 0px 12px;
}

QScrollBar::handle:horizontal {
    background-color: #AADDDDDD;
    min-width: 14px;
    margin: 1px 1px 0px 1px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    margin: 1px 0px 0px 0px;
    height: 12px;
    width: 12px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

QScrollBar::sub-line:horizontal {
    image: none;
    subcontrol-position: left;
    subcontrol-origin: margin;
}

QScrollBar::add-line:horizontal {
    image: none;
    subcontrol-position: right;
    subcontrol-origin: margin;
}


QScrollBar:vertical {
    width: 12px;
    border: none;
    margin: 12px 0px 12px 0px;
}

QScrollBar::handle:vertical {
    background-color: #40CDCDCD;
    border-radius: 5px;
    min-height: 14px;
    margin: 1px 0px 1px 1px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    margin: 0px 0px 0px 1px;
    height: 12px;
    width: 12px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar::sub-line:vertical {
    image: none;
    subcontrol-position: top;
    subcontrol-origin: margin;
}

QScrollBar::add-line:vertical {
    image: none;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}

""" % dict(
    res=_resource().replace("\\", "/"),
)
