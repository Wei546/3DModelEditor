from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox, QMainWindow
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models.interaction_styles.interaction_styles import HighlightInteractorStyle
from models.visible_select_func import VisibleSlt
from models.hold_slt_btn_func import HoldSltbtnFunc
import vtk
from utils.renderer import render_model
from utils.files_io import get_writer_by_extension, read_model
from models.meshlibStitching import run_stitching_process


class ModelEditorPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_vtk()
        self.init_buttons()
        self.init_variables()
        self.stackedWidget.hide()

    def init_ui(self):
        uic.loadUi('ui/20250309.ui', self)
        layout = QVBoxLayout(self.vtkWidgetContainer)
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)

    def init_vtk(self):
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

    def init_buttons(self):
        self.importBtn.clicked.connect(self.load_file)
        self.exportBtn.clicked.connect(self.save_file)
        self.boxBtn.clicked.connect(self.boxBtnPress)
        self.pointBtn.clicked.connect(self.pointBtnPress)
        self.lassoBtn.clicked.connect(self.lassoBtnPress)
        self.paintBrushBtn.clicked.connect(self.holdBtnPress)
        self.throughFuncBtn.clicked.connect(self.throughBtnPress)
        self.stitchesFuncBtn.clicked.connect(self.call_stitching)
        self.selectBtn.clicked.connect(self.show_select_page)
        self.editBtn.clicked.connect(self.show_edit_page)
        self.sculptBtn.clicked.connect(self.show_sculpt_page)
        
    def show_select_page(self):
        # 顯示堆疊窗口
        self.stackedWidget.show()
        # 顯示select的頁面
        self.stackedWidget.setCurrentWidget(self.selectPage)
    def show_edit_page(self):
        # 顯示堆疊窗口
        self.stackedWidget.show()
        # 顯示edit的頁面
        self.stackedWidget.setCurrentWidget(self.editPage)
    def show_sculpt_page(self):
        # 顯示堆疊窗口
        self.stackedWidget.show()
        # 顯示sculpt的頁面
        self.stackedWidget.setCurrentWidget(self.sculptPage)

    def init_variables(self):
        self.poly_data = None
        self.style = None
        self.holdSltBtnMode = False
        self.throughFunc = VisibleSlt(self.renderer, self.vtk_widget.GetRenderWindow().GetInteractor())

    def holdBtnPress(self):
        self.holdSltBtnMode = not self.holdSltBtnMode
        self.holdSltBtn.setStyleSheet("background-color: #F5DEB3;" if self.holdSltBtnMode else "background-color: none;")
        self.pointBtn.setEnabled(not self.holdSltBtnMode)
        self.lassoBtn.setEnabled(not self.holdSltBtnMode)
        self.boxBtn.setEnabled(not self.holdSltBtnMode)

    def throughBtnPress(self):
        if self.style.throughBtnMode:
            self.style.unable_through_mode()
            print(f"status in model editor page:{self.style.throughBtnMode}")
            self.style.throughBtnMode = False
        else:
            self.style.enable_through_mode()
            print(f"status in model editor page:{self.style.throughBtnMode}")
            self.style.throughBtnMode = True

    # 拼接按鈕功能
    def stitchingBtnPress(self):
        print(f"stitchingBtnPress")
        self.style.enable_stitching_mode()

    def boxBtnPress(self):
        if self.style.boxSltMode:
            self.style.unable_box_mode()
            self.lassoBtn.setEnabled(True)
            self.pointBtn.setEnabled(True)
            self.style.boxSltMode = False
            print(f"status in model editor page:{self.style.boxSltMode}")
        else:
            self.style.enable_box_mode()
            self.lassoBtn.setEnabled(False)
            self.pointBtn.setEnabled(False)
            self.style.boxSltMode = True
            print(f"status in model editor page:{self.style.boxSltMode}")

    def pointBtnPress(self):
       if self.style.pointSltMode:
            self.style.unable_point_mode()
            self.lassoBtn.setEnabled(True)
            self.boxBtn.setEnabled(True)
            self.style.pointSltMode = False
            print(f"status in model editor page:{self.style.pointSltMode}")
       else:
            self.style.enable_point_mode()
            self.lassoBtn.setEnabled(False)
            self.boxBtn.setEnabled(False)
            self.style.pointSltMode = True
            print(f"status in model editor page:{self.style.pointSltMode}")

    def lassoBtnPress(self):
        if self.style.lassoSltMode:
            self.style.unable_lasso_mode()
            self.pointBtn.setEnabled(True)
            self.boxBtn.setEnabled(True)
            self.style.lassoSltMode = False
            print(f"status in model editor page:{self.style.lassoSltMode}")
        else:
            self.style.enable_lasso_mode()
            self.pointBtn.setEnabled(False)
            self.boxBtn.setEnabled(False)
            self.style.lassoSltMode = True
            print(f"status in model editor page:{self.style.lassoSltMode}")
    
    def load_file(self):
        # 選擇檔案
        file_paths, _ = QFileDialog.getOpenFileNames(self, "選擇(上顎/下顎)", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        # 將檔名放入meshlib的縫合功能
        self.file_paths_for_stitching = file_paths
        # 沒有檔案提示
        if not file_paths:
            QMessageBox.warning(self, "警告", "請至少選擇 **一個** 牙齒模型。")
            return
        if len(file_paths) > 2:
            QMessageBox.warning(self, "警告", "最多只能載入 **上下顎** 牙齒模型。")
            return
        try:
            # 給定上下顎模型
            self.teeth_models = {"upper":None,"lower":None}
            for file_path in file_paths:
                # model_type代表上顎、下顎
                model_type = self.checkTeethType(file_path)
                # 讀取模型
                poly_data = read_model(file_path)
                # 實際poly_data對應上下鄂的索引
                self.teeth_models[model_type] = poly_data
                # 顯示模型
                render_model(self.renderer,self.vtk_widget,self.teeth_models[model_type])
            # 互動模式
            self.style = HighlightInteractorStyle(self.teeth_models["upper"],self.teeth_models["lower"],self.renderer,self.vtk_widget.GetRenderWindow().GetInteractor())
            self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(self.style)
        except ValueError as e:
            QMessageBox.critical(self, "錯誤", str(e))
    def call_stitching(self):
        # 顯示拼接功能
        print("call stitching")
        run_stitching_process(self.file_paths_for_stitching[0])
        # 清除畫布
        self.renderer.RemoveAllViewProps()
        # 渲染檔案路徑stitched_merge_0075.stl的檔案
        poly_data = read_model("stitched_merge_0075.stl")
        render_model(self.renderer, self.vtk_widget, poly_data)
        # 互動模式
        self.style = HighlightInteractorStyle(poly_data, None, self.renderer, self.vtk_widget.GetRenderWindow().GetInteractor())
        self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(self.style)
        

    # 給予使用者選擇上顎或下顎
    def checkTeethType(self, file_path):
        # 儲存下拉選項類型
        options = {"上顎(upper)": "upper", "下顎(lower)": "lower"}

        # 顯示選擇視窗
        choice, ok = QtWidgets.QInputDialog.getItem(
            self, "選擇牙齒模型類別", f"請選擇 {file_path} 是上顎或下顎", list(options.keys()), 0, False
        )

        # 回傳使用者選擇上顎或下顎
        if ok:
            return options[choice]
        else:
            return None  # 用戶取消選擇
    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        if file_path:
            try:
                writer = get_writer_by_extension(file_path)
                writer.SetFileName(file_path)
                writer.SetInputData(self.poly_data)
                writer.Write()
            except ValueError as e:
                QMessageBox.critical(self, "錯誤", str(e))

    
