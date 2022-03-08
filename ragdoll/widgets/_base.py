
from PySide2 import QtCore, QtWidgets, QtGui


class HTMLSkinnedButton(QtWidgets.QPushButton):

    def __init__(self, html, css=None, parent=None):
        super(HTMLSkinnedButton, self).__init__(parent=parent)
        self.draw_skin(html, css)

    def draw_skin(self, html, css=None):
        rich_text = QtGui.QTextDocument()
        if css:
            rich_text.setDefaultStyleSheet(css)
        rich_text.setHtml(html)

        size = rich_text.size()
        pixmap = QtGui.QPixmap(int(size.width()), int(size.height()))
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        rich_text.drawContents(painter, pixmap.rect())

        icon = QtGui.QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(pixmap.rect().size())

        painter.end()  # important


class FramelessDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(FramelessDialog, self).__init__(parent=parent)
        self.setWindowFlags(
            self.windowFlags()
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowSystemMenuHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self._dragging = False
        self._last_pos = None

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

    def paintEvent(self, event):
        # type: (QtGui.QPaintEvent) -> None
        p = QtGui.QPainter(self)
        p.setRenderHint(p.Antialiasing)

        if self.testAttribute(QtCore.Qt.WA_StyleSheetTarget):
            opt = QtWidgets.QStyleOption()
            opt.initFrom(self)
            self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, p, self)
            p.end()
            return

        rect = QtCore.QRectF(QtCore.QPointF(0, 0), self.size())
        p.setPen(QtCore.Qt.NoPen)
        p.setBrush(self.palette().brush(self.backgroundRole()))
        p.drawRoundedRect(rect, 8, 8, QtCore.Qt.AbsoluteSize)
        p.end()

        # todo: drop-shadow
