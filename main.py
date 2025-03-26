from PyQt5 import QtWidgets
import sys
from models.model_editor_page import ModelEditorPage

# 主程式
def main():
    # 初始化顯示應用程式
    app = QtWidgets.QApplication(sys.argv)
    # 初始化顯示視窗類別  
    dialog = ModelEditorPage()
    # 顯示視窗
    dialog.show()
    # 等待視窗關閉
    sys.exit(app.exec_())
# 執行
if __name__ == "__main__":
    main()