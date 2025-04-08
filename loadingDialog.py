# ui/loading.gif 必須存在
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("請稍候")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        self.setFixedSize(200, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel(self)
        self.movie = QMovie("ui/loading.gif")
        self.label.setMovie(self.movie)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def start(self):
        self.movie.start()
        self.show()

    def stop(self):
        self.movie.stop()
        self.accept()
