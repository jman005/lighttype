from PyQt5.QtWidgets import (QMainWindow, QAction)
from lightype.widgets.testWindow import TestWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Lightype")
        self.resize(800, 700)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        testWindow = TestWindow()
        self.setCentralWidget(testWindow)

        self.show()
