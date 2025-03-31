from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QMessageBox, QMainWindow,QDialog
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models.interaction_styles.interaction_styles import HighlightInteractorStyle
from models.visible_select_func import VisibleSlt
from models.hold_slt_btn_func import HoldSltbtnFunc
import vtk
from utils.renderer import render_model
from utils.files_io import get_writer_by_extension, read_model
from models.meshlibStitching import run_stitching_process
from models.model_manager import ModelManager
from models.align_dialog import AlignDialog
from models.vtkAlignModel import align_models_icp


class ModelEditorPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model_manager = ModelManager()
        self.init_ui()
        self.init_vtk()
        self.init_buttons()
        self.init_variables()
        self.stackedWidget.hide()

    def init_ui(self):
        uic.loadUi('ui/20250309_backup.ui', self)
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
        self.modelListWidget.currentRowChanged.connect(self.on_model_selected)
        self.alignFuncBtn.clicked.connect(self.call_align)
        
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
    # 這是由QListWidget觸發的，當QListWidget的檔案被點選他負責通知
    def on_model_selected(self, index):
        # 當某個檔名，例如"model_1.stl"被點選時，會觸發這個函式
        item = self.modelListWidget.item(index)
        # 如果真的有item
        if item:
            # 只擷取檔名的文字部分
            model_name = item.text()
            self.model_manager.set_active_model(model_name)
            self.style.set_active_model(model_name)
    
    def load_file(self):
        # 選擇檔案
        file_paths, _ = QFileDialog.getOpenFileNames(self, "選擇檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        self.file_paths_for_stitching = file_paths
        # 將檔名放入meshlib的縫合功能
        self.file_paths_for_stitching = file_paths
        for file_path in file_paths:
            # 擷取檔名
            model_name = file_paths[0].split("/")[-1]
            # 讀取檔案
            poly_data = read_model(file_path)
            # 註冊新模型
            model_name_for_list = self.model_manager.add_model(model_name, poly_data)
            # 更新ui
            self.modelListWidget.addItem(model_name_for_list)
            # 使用model_manager的get_model函式取得模型
            model_slot = self.model_manager.get_model(model_name_for_list)
            self.renderer.AddActor(model_slot.actor)
            # 初始化HighlightInteractorStyle
            self.style = HighlightInteractorStyle(self.model_manager, self.renderer, self.vtk_widget.GetRenderWindow().GetInteractor())
            self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(self.style)
            # 渲染模型
            self.vtk_widget.GetRenderWindow().Render()
    # 這是slef.stitchesFuncBtn的功能
    def call_stitching(self):
        # 顯示拼接功能
        print("call stitching")
        stitch_file_name = run_stitching_process(self.file_paths_for_stitching[0])
        # 清除畫布
        self.renderer.RemoveAllViewProps()
        # 渲染檔案路徑stitched_merge_0075.stl的檔案
        poly_data = read_model(stitch_file_name)
        render_model(self.renderer, self.vtk_widget, poly_data)
        self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(self.style)
    def call_align(self):
        model_names = self.model_manager.get_all_model_names()
        dialog = AlignDialog(model_names, self)
        if dialog.exec_() == QDialog.Accepted:
            source_name, target_name = dialog.get_selected_models()
            print("使用者選擇的對齊模型:", source_name, "→", target_name)
            print(f"source type:{type(source_name)}, target type:{type(target_name)}")
            # 取得 poly_data
            source_slot = self.model_manager.get_model(source_name)
            target_slot = self.model_manager.get_model(target_name)

            # 這裡呼叫你的對齊函式
            aligned_poly_data = align_models_icp(source_slot.poly_data, target_slot.poly_data)
            # 更新模型資料與視覺化
            self.renderer.RemoveActor(source_slot.actor)  # 移除原本的 actor
            source_slot.update_poly_data(aligned_poly_data)  # 更新 polydata 與 actor
            self.renderer.AddActor(source_slot.actor)  # 加入新 actor
            self.vtk_widget.GetRenderWindow().Render()
            
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

    
