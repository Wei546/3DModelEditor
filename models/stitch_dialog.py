from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class StitchDialog(QDialog):
    def __init__(self, model_names, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/20250411_stitch_dialog.ui", self)  # 替換成實際路徑

        # 填入模型名稱
        self.defectCmbx.addItems(model_names)
        self.repairCmbx.addItems(model_names)

        # 連接確定或取消按鈕
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def get_selected_models(self):
        return self.defectCmbx.currentText(), self.repairCmbx.currentText()
