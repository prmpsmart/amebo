from .chat_ui.home import *
from .sign_ui import *


qApp: QApplication


class _AmeboUi:
    def __init__(self: QMainWindow) -> None:
        user = AmeboClientData.user()
        # user = None
        if user:
            cw = Home()
        else:
            cw = Sign()

        self.setCentralWidget(cw)

    def signin_successful(self: QMainWindow):
        self.centralWidget().deleteLater()
        h = Home()
        self.setCentralWidget(h)
        QTimer.singleShot(100, lambda: h.set_default_width())

    def showEvent(self: QMainWindow, _: QShowEvent):
        sw = qApp.primaryScreen().availableSize().width()
        w = self.width()

        # self.setGeometry(sw - 380, 200, 0, 0)

        AmeboUserClient.get_client().start_client()

        # return
        self.setGeometry((sw - w) // 2, 50, 0, 0)

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        AmeboUserClient.get_client().close(reason="Ending Application")
        AmeboClientData.save()


class AmeboUI_R(_AmeboUi, PrmpWindow):
    def __init__(self, **kwargs):
        PrmpWindow.__init__(self, **kwargs)
        _AmeboUi.__init__(self)

        self.windowLayout().setContentsMargins(0, 0, 0, 10)
        addShadow(self.titleBar)

        # statusbar_lay = self.statusBar.layout()
        # statusbar_lay.setContentsMargins(5, 5, 5, 0)

    def setCentralWidget(self, widget: QWidget):
        self.setContentWidget(widget)


class AmeboUI(_AmeboUi, QMainWindow, BaseWindow_):
    def __init__(self, **kwargs):
        QMainWindow.__init__(self, **kwargs)
        _AmeboUi.__init__(self)
