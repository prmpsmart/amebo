from PySide6.QtWidgets import *


app = QApplication()
win = QColorDialog()
win.show()
win.destroyed.connect(app.quit)
app.exec()
