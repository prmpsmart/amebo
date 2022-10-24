from prmp_qt import *


class Label(QLabel):
    def __init__(self, pixmap: QPixmap):
        super().__init__()
        self.setPixmap(pixmap)


class App(QApplication):
    def __init__(self):
        super().__init__()

        self.w = HFrame()
        self.w.setStyleSheet("background: black")
        l = self.w.layout()

        pixmap = QPixmap("peachyLogo.jpg")

        r = 10
        rounded_pixmap = ROUNDED_PIXMAP(r, r, pixmap=pixmap)

        l.addWidget(Label(pixmap))
        l.addWidget(Label(rounded_pixmap))

        self.w.show()


app = App()
app.exec()
