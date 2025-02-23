from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import QVBoxLayout,QFileDialog,QMessageBox
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from models.interaction_styles import HighlightInteractorStyle,PointInteractor,LassoInteractor
from models.visible_select_func import VisibleSlt
import vtk
from utils.renderer import render_model
# 檢視3D物件
class ModelEditorPage(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # 載入UI
        uic.loadUi('ui/20241012_v2.ui', self)
        self.load.clicked.connect(self.load_file)
        # vtk視窗
        layout = QVBoxLayout(self.vtkWidgetContainer)
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        # 渲染畫面
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        # 觸發按鍵
        self.boxBtn.clicked.connect(self.boxBtnPress)
        self.pointBtn.clicked.connect(self.pointBtnPress)
        self.lassoBtn.clicked.connect(self.lassoBtnPress)
        self.saveBtn.clicked.connect(self.save_file)

        
        # 瀏覽3D物件
        self.model_actor = None
        self.poly_data = None
        # HighlightInteractorStyle類別
        self.style = None
        # 實體化點選取類別
        self.point_func = PointInteractor(self.poly_data)
        # 實體化套索類別
        self.lasso_func = LassoInteractor(self.poly_data)
        # 觸發穿透按鍵
        self.throughFuncBtn.clicked.connect(self.throughBtnPress)
        self.throughFunc = VisibleSlt(self.renderer,self.vtk_widget.GetRenderWindow().GetInteractor())
        

    # 穿透按鍵
    def throughBtnPress(self):
        if self.style.throughBtnMode:
            self.throughFuncBtn.setStyleSheet("background-color: #F5DEB3;")
            self.style.mode(False)
            self.throughFunc.projectToPerspective(self.renderer)
            self.throughFunc.checkWindowMode(self.renderer)
            self.style.mode(False)

        else:
            self.throughFuncBtn.setStyleSheet("background-color: none;")
            self.throughFunc.projectToParallel(self.renderer)
            self.throughFunc.checkWindowMode(self.renderer)
            self.style.throughBtnMode = not self.style.throughBtnMode
            self.style.mode(True)
        
    # 矩形選取模式
    def boxBtnPress(self):
        # 矩形選取模式為True
        if self.style.boxSltMode:
            # 再按一下關閉矩形選取
            self.style.boxSltMode = False
            # 矩形選取開啟，點選取不能點擊
            self.pointBtn.setEnabled(True)
            # 矩形選開啟，套索選取不能點擊
            self.lassoBtn.setEnabled(True)
        # 矩形選取模式為False
        else:
            # 再按一下開啟矩形選取
            self.style.boxSltMode = not self.style.boxSltMode
            # 矩形選取關閉，點選取可以點擊
            self.pointBtn.setEnabled(False)
            # 矩形選取關閉，套索選取可以點擊
            self.lassoBtn.setEnabled(False)
            
    # 點選取模式
    def pointBtnPress(self):
        if self.style.pointSltMode:
            self.style.pointSltMode = False
            self.boxBtn.setEnabled(True)
            self.lassoBtn.setEnabled(True)
        else:
            self.style.pointSltMode = not self.style.pointSltMode
            self.boxBtn.setEnabled(False)
            self.lassoBtn.setEnabled(False)
            
    # 套索選取模式
    def lassoBtnPress(self):
        if self.style.lassoSltMode:
            self.style.lassoSltMode = False
            self.boxBtn.setEnabled(True)
            self.pointBtn.setEnabled(True)
        else:
            self.style.lassoSltMode = not self.style.lassoSltMode
            self.boxBtn.setEnabled(False)
            self.pointBtn.setEnabled(False)
            
    # 載入檔案
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        # 讀檔+顯示+渲染+顯示功能
        if file_path:
            try:
                self.poly_data = self.read_model(file_path)
                self.model_actor = render_model(self.renderer, self.vtk_widget, self.poly_data)
                # 顯示功能
                interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                self.vtk_widget.setFocus()
                self.style = HighlightInteractorStyle(self.poly_data, self.renderer)
                interactor.SetInteractorStyle(self.style)
            except ValueError as e:
                QMessageBox.critical(self, "錯誤", str(e))
    # 儲存檔案
    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        if file_path:
            try:
                writer = None
                extension = file_path.split('.')[-1].lower()
                if extension == 'vtp':
                    writer = vtk.vtkXMLPolyDataWriter()
                elif extension == 'obj':
                    writer = vtk.vtkOBJWriter()
                elif extension == 'ply':
                    writer = vtk.vtkPLYWriter()
                elif extension == 'stl':
                    writer = vtk.vtkSTLWriter()
                else:
                    raise ValueError("不支援的檔案格式.")
                writer.SetFileName(file_path)
                writer.SetInputData(self.poly_data)
                writer.Write()
            except ValueError as e:
                QMessageBox.critical(self, "錯誤", str(e))
    # 讀檔
    def read_model(self, file_path):
        extension = file_path.split('.')[-1].lower()
        reader = None
        if extension == 'vtp':
            reader = vtk.vtkXMLPolyDataReader()
        elif extension == 'obj':
            reader = vtk.vtkOBJReader()
        elif extension == 'ply':
            reader = vtk.vtkPLYReader()
        elif extension == 'stl':
            reader = vtk.vtkSTLReader()
        else:
            raise ValueError("不支援的檔案格式.")
        reader.SetFileName(file_path)
        reader.Update()
        return reader.GetOutput()