from PyQt5 import QtWidgets
import sys
from models.model_editor_page import ModelEditorPage

# 主程式
def main():
    app = QtWidgets.QApplication(sys.argv)
    dialog = ModelEditorPage()
    dialog.show()
    sys.exit(app.exec_())
# 執行
if __name__ == "__main__":
    main()