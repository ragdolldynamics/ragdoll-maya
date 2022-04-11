
import os
from PySide2 import QtCore, QtWidgets, QtGui
from ..vendor import cmdx
from .. import internal
from . import base, px

# Unused, for type hint in IDEs
__ = cmdx


def _resource(*fname):
    dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(dirname)
    resdir = os.path.join(dirname, "resources")
    return os.path.normpath(os.path.join(resdir, *fname))


def _get_all_solver_size(solvers):
    solver_size = dict()
    for solver in solvers:
        solver_id = int(solver["ragdollId"])
        solver_size[solver_id] = internal.compute_solver_size(solver)
    return solver_size


def _solver_ui_name_by_sizes(solver_sizes, solver):
    solver_id = int(solver["ragdollId"])
    solver_size = solver_sizes[solver_id]

    has_same_size = any(
        _id != solver_id and size == solver_size
        for _id, size in solver_sizes.items()
    )
    transform = solver.parent()
    return transform.shortest_path() if has_same_size else transform.name()


class TippedLabel(QtWidgets.QWidget):
    tip_shown = QtCore.Signal(str)

    def __init__(self, label, parent=None):
        super(TippedLabel, self).__init__(parent=parent)

        label = QtWidgets.QLabel(label)
        label.setStyleSheet("QLabel {color: rgba(240,240,240,125)}")

        value = QtWidgets.QLabel()
        value.setAlignment(QtCore.Qt.AlignRight)  # elide from start

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch(1)  # for pushing value label back to left

        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_timer_timeout)

        self._value = value
        self._timer = timer
        self._tool_tip = None
        self.__entered = False

    def _on_timer_timeout(self):
        text = self._tool_tip if self.__entered else None
        text = text or ""
        self.tip_shown.emit(text)

    def setText(self, text):
        self._value.setText(text)

    def setToolTip(self, text):
        self._tool_tip = text

    def enterEvent(self, event):
        self.__entered = True
        self._timer.start(1000)

    def leaveEvent(self, event):
        self.__entered = False
        self._timer.start(0)


class SolverButton(QtWidgets.QPushButton):
    tip_shown = QtCore.Signal(str)

    def __init__(self, solver_sizes, solver=None, parent=None):
        """
        Arguments:
            solver_sizes (dict):
            solver (cmdx.DagNode or None):
            parent (QtWidgets.QWidget or None):
        """
        super(SolverButton, self).__init__(parent=parent)

        body = QtWidgets.QWidget()
        info = QtWidgets.QWidget()

        _icon_img = _resource("icons", "solver.png")
        _pixmap = QtGui.QIcon(_icon_img).pixmap(px(24))
        _pixmap = _pixmap.scaledToWidth(px(24), QtCore.Qt.SmoothTransformation)
        icon = QtWidgets.QLabel()
        icon.setPixmap(_pixmap)

        val_name = TippedLabel("Name:")
        val_size = TippedLabel("Size:")

        layout = QtWidgets.QVBoxLayout(info)
        layout.setSpacing(4)
        layout.addWidget(val_name)
        layout.addWidget(val_size)

        layout = QtWidgets.QHBoxLayout(body)
        layout.setSpacing(0)
        layout.addWidget(icon, stretch=0)
        layout.addWidget(info, stretch=1, alignment=QtCore.Qt.AlignLeft)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(
            body, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )

        val_name.tip_shown.connect(self.tip_shown)
        val_size.tip_shown.connect(self.tip_shown)

        self._solver_sizes = solver_sizes
        self._name = val_name
        self._size = val_size
        self._dag_path = None

        if solver is not None:
            self.set_solver(solver)

    def sizeHint(self):
        """
        Returns:
            QtCore.QSize
        """
        size = QtCore.QSize()
        for child in self.children():
            if isinstance(child, QtWidgets.QLayout):
                size += child.sizeHint()
        # expand a bit
        size += QtCore.QSize(4, 4)
        return size

    @property
    def dag_path(self):
        return self._dag_path

    def set_solver(self, solver):
        solver_name = _solver_ui_name_by_sizes(self._solver_sizes, solver)
        solver_size = self._solver_sizes[int(solver["ragdollId"])]

        self._name.setText(solver_name)
        self._size.setText(str(solver_size))

        self._name.setToolTip("Shortest name of this solver:\n %s"
                              % solver.dag_path())
        self._size.setToolTip("Size of the solver. The sum of all component "
                              "related to this solver, e.g. count of markers, "
                              "constraints, and other ragdoll nodes.")

        self._dag_path = solver.shortest_path()


class SolverComboBox(QtWidgets.QComboBox):

    def __init__(self, solver_sizes, solvers=None, parent=None):
        """
        Arguments:
            solver_sizes (dict):
            solvers (list[cmdx.DagNode]):
            parent (QtWidgets.QWidget or None):
        """
        super(SolverComboBox, self).__init__(parent=parent)

        _icon = QtGui.QIcon(_resource("icons", "solver.png"))
        for i, solver in enumerate(solvers):
            solver_name = _solver_ui_name_by_sizes(solver_sizes, solver)
            solver_size = solver_sizes[int(solver["ragdollId"])]

            item_name = "[%d] %s" % (solver_size, solver_name)
            self.addItem(_icon, item_name)

        self._solvers = solvers

    def get_solver(self, index):
        return self._solvers[index]


class SolverSelectorDialog(base.FramelessDialog):
    solver_picked = QtCore.Signal(str)

    def __init__(self, solvers, help, best_guess=None, parent=None):
        """
        Arguments:
            solvers (list[cmdx.DagNode]):
            best_guess (cmdx.DagNode or None):
            parent (QtWidgets.QWidget or None):
        """
        super(SolverSelectorDialog, self).__init__(parent=parent)

        solver_sizes = _get_all_solver_size(solvers)

        body = QtWidgets.QWidget()
        title = QtWidgets.QLabel("Pick Solver")

        if len(solvers) > 2:
            view = self._init_full(solver_sizes, solvers, best_guess)
        else:
            view = self._init_slim(solver_sizes, solvers)

        pixmap = QtGui.QPixmap(_resource("ui", "background1.png"))
        footer = RoundedImageFooter(pixmap)

        info = InfoToggle()
        info.setObjectName("Info")
        info.setParent(footer)

        hint = QtWidgets.QTextEdit()
        hint.setParent(footer)
        hint.setObjectName("Hint")
        hint.setVisible(False)
        hint.setReadOnly(True)
        hint.setLineWrapMode(hint.WidgetWidth)
        hint.setAlignment(QtCore.Qt.AlignTop)

        tips = QtWidgets.QTextEdit()
        tips.setVisible(False)
        tips.setReadOnly(True)
        tips.setHtml(help)

        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(18, 24, 18, 14)
        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addWidget(view)
        layout.addWidget(tips)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(body)
        layout.addWidget(footer)

        info.toggled.connect(self.on_info_toggled)

        # sizing
        self.setFixedWidth(px(380))
        footer.setFixedHeight(px(70))
        info.move(px(10), px(6))
        hint.move(px(10), px(6))
        hint.setFixedWidth(px(320))
        hint.setFixedHeight(px(70))

        self.setStyleSheet("""
        #Info {
            color: #AFAFAF;
            text-align: left;
            background: transparent;
            padding: %dpx;
            border: none;
            border-radius: %dpx;
        }
        #Info:hover {
            background: rgba(255,255,255,60);
        }
        QTextEdit, #Hint {
            color: white;
            background: transparent;
            border: none;
        }
        """ % (px(5), px(4)))

        self._info = info
        self._hint = hint
        self._stack = [view, tips]

    def on_info_toggled(self, show_tips):
        self._stack[0].setVisible(False)
        self._stack[1].setVisible(False)
        self._stack[int(show_tips)].setVisible(True)

    def on_tip_shown(self, text):
        self._info.setVisible(not text)
        self._hint.setVisible(bool(text))
        self._hint.setText(text or "")

    def _init_slim(self, solver_sizes, solvers):
        """
        Arguments:
            solver_sizes (dict):
            solvers (list[cmdx.DagNode]):
        Returns:
            QtWidgets.QWidget
        """
        view = QtWidgets.QWidget()
        solver_bar = QtWidgets.QWidget()
        solver_btn_row = [SolverButton(solver_sizes, s) for s in solvers]

        layout = QtWidgets.QHBoxLayout(solver_bar)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        for btn in solver_btn_row:
            btn.setMinimumHeight(px(75))
            btn.setMinimumWidth(px(150))
            layout.addWidget(btn)

        layout = QtWidgets.QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_bar)

        for btn in solver_btn_row:
            btn.clicked.connect(self.on_solver_clicked)
            btn.tip_shown.connect(self.on_tip_shown)

        return view

    def _init_full(self, solver_sizes, solvers, best_guess=None):
        """
        Arguments:
            solver_sizes (dict):
            solvers (list[cmdx.DagNode]):
            best_guess (cmdx.DagNode or None):
        Returns:
            QtWidgets.QWidget
        """
        view = QtWidgets.QWidget()
        solver_btn = SolverButton(solver_sizes)
        solver_combo = SolverComboBox(solver_sizes, solvers)

        layout = QtWidgets.QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(solver_combo)
        layout.addWidget(solver_btn)

        def on_solver_changed(index):
            solver = solver_combo.get_solver(index)
            solver_btn.set_solver(solver)

        solver_combo.currentIndexChanged.connect(on_solver_changed)
        solver_btn.clicked.connect(self.on_solver_clicked)
        solver_btn.tip_shown.connect(self.on_tip_shown)

        # init
        if best_guess is None:
            on_solver_changed(0)
        else:
            assert best_guess in solvers
            solver_combo.setCurrentIndex(solvers.index(best_guess))
            if solver_combo.currentIndex() == 0:
                on_solver_changed(0)

        return view

    def on_solver_clicked(self):
        clicked = self.sender()  # type: SolverButton
        self.solver_picked.emit(clicked.dag_path)
        self.close()


class InfoToggle(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(InfoToggle, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setCheckable(True)
        self._reset()
        self.toggled.connect(self._on_toggled)

        self.setStyleSheet("""
            QPushButton {
                color: white;
            }

            QPushButton:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        """)

    def _on_toggled(self, state):
        if state:
            self._toggled()
        else:
            self._reset()

    def _toggled(self):
        self.setText("Got it")
        self.setIcon(QtGui.QIcon(_resource("icons", "back.png")))

    def _reset(self):
        self.setText("Why this popup?")
        self.setIcon(QtGui.QIcon(_resource("icons", "info.png")))


class RoundedImageFooter(QtWidgets.QLabel):

    def __init__(self, pixmap, *args, **kwargs):
        super(RoundedImageFooter, self).__init__(*args, **kwargs)
        self.setObjectName("Background")
        self._image = pixmap

    def paintEvent(self, event):
        r = px(10)
        w = self.width()
        h = self.height()

        # make a half rounded rect (sharped top, rounded bottom)
        #   ___________________
        #  |                  |
        #  |                  |
        #  \_________________/
        #
        path = QtGui.QPainterPath()
        path.setFillRule(QtCore.Qt.WindingFill)
        path.addRoundedRect(QtCore.QRect(0, 0, w, h), r, r)
        path.addRect(QtCore.QRect(0, 0, r, r))
        path.addRect(QtCore.QRect(w - r, 0, r, r))

        painter = QtGui.QPainter(self)
        painter.setClipPath(path.simplified())
        painter.setRenderHint(painter.Antialiasing)
        painter.drawPixmap(0, 0, self._image)
