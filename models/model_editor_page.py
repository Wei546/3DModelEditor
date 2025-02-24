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
        # 載入檔案按鈕觸發load_file函數
        self.load.clicked.connect(self.load_file)
        # layout放入的是vtk視窗
        layout = QVBoxLayout(self.vtkWidgetContainer)
        # 使用QVTKRenderWindowInteractor類別，變成互動器，可以旋轉、拖曳等功能
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        # layout放入vtk視窗
        layout.addWidget(self.vtk_widget)
        # 實體化vtkRenderer類別
        self.renderer = vtk.vtkRenderer()
        # 渲染畫面
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        # self.boxBtn是取型選取按鈕，觸發矩形按鍵
        self.boxBtn.clicked.connect(self.boxBtnPress)
        # self.pointBtn是點選取按鈕，觸發點選取按鍵
        self.pointBtn.clicked.connect(self.pointBtnPress)
        # self.lassoBtn是套索選取按鈕，觸發套索選取按鍵
        self.lassoBtn.clicked.connect(self.lassoBtnPress)
        # self.saveBtn是儲存檔案按鈕，觸發save_file函數
        self.saveBtn.clicked.connect(self.save_file)

        
        # 瀏覽3D物件
        self.model_actor = None
        # 3D物件
        self.poly_data = None
        # HighlightInteractorStyle類別
        self.style = None
        # 實體化點選取類別
        self.point_func = PointInteractor(self.poly_data)
        # 實體化套索類別
        self.lasso_func = LassoInteractor(self.poly_data)
        # 觸發穿透按鍵
        self.throughFuncBtn.clicked.connect(self.throughBtnPress)
        # 穿透功能
        self.throughFunc = VisibleSlt(self.renderer,self.vtk_widget.GetRenderWindow().GetInteractor())
        

    # 穿透按鍵
    def throughBtnPress(self):
        # 穿透按鍵模式為True
        if self.style.throughBtnMode:
            # 穿透功能開啟，改變顏色
            self.throughFuncBtn.setStyleSheet("background-color: #F5DEB3;")

            self.throughFunc.projectToPerspective(self.renderer)
            
            self.throughFunc.checkWindowMode(self.renderer)
            # interaction_style類別需要確定是否開啟穿透功能。
            self.style.mode(False)

        else:
            # 關閉穿透功能，還原原本的樣式
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
        # 開啟點選取模式
        if self.style.pointSltMode:
            # 點選取模式為False
            self.style.pointSltMode = False
            # 點選取開啟，矩形選取可以點擊
            self.boxBtn.setEnabled(True)
            # 點選取開啟，套索選取可以點擊
            self.lassoBtn.setEnabled(True)
        # 關閉點選取模式
        else:
            # 點選取模式為True
            self.style.pointSltMode = not self.style.pointSltMode
            # 點選取關閉，矩形選取不能點擊
            self.boxBtn.setEnabled(False)
            # 點選取關閉，套索選取不能點擊
            self.lassoBtn.setEnabled(False)
            
    # 套索選取模式
    def lassoBtnPress(self):
        # 開啟套索選取模式
        if self.style.lassoSltMode:
            # 套索選取模式為False
            self.style.lassoSltMode = False
            # 套索選取開啟，矩形選取不能點擊
            self.boxBtn.setEnabled(True)
            # 套索選取開啟，點選取不能點擊
            self.pointBtn.setEnabled(True)
        # 關閉套索選取模式
        else:
            # 套索選取模式為True
            self.style.lassoSltMode = not self.style.lassoSltMode
            # 套索選取關閉，矩形選取不能點擊
            self.boxBtn.setEnabled(False)
            # 套索選取關閉，點選取不能點擊
            self.pointBtn.setEnabled(False)
            
    # 載入檔案
    def load_file(self):
        # 選擇檔案
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        # 檢查檔案的型別
        if file_path:
            try:
                # 讀取模型
                self.poly_data = self.read_model(file_path)
                # 渲染模型
                self.model_actor = render_model(self.renderer, self.vtk_widget, self.poly_data)
                # 顯示功能
                interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
                # 點擊視窗的效果
                self.vtk_widget.setFocus()
                # 顯示模型
                self.style = HighlightInteractorStyle(self.poly_data, self.renderer)
                # 更新畫面
                interactor.SetInteractorStyle(self.style)
            except ValueError as e:
                QMessageBox.critical(self, "錯誤", str(e))
    # 儲存檔案
    def save_file(self):
        # 選擇儲存檔案
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存檔案", "", "模型文件 (*.vtp *.obj *.ply *.stl)")
        # 檢查檔案的型別
        if file_path:
            try:
                # 寫入檔案
                writer = None
                # 將副檔名前面的字轉換小寫
                extension = file_path.split('.')[-1].lower()
                # 確認檔案型別為vtp
                if extension == 'vtp':
                    # 實體化vtkXMLPolyDataWriter類別
                    writer = vtk.vtkXMLPolyDataWriter()
                # 確認檔案型別為obj
                elif extension == 'obj':
                    # 實體化vtkOBJWriter類別
                    writer = vtk.vtkOBJWriter()
                # 確認檔案型別為ply
                elif extension == 'ply':
                    # 實體化vtkPLYWriter類別
                    writer = vtk.vtkPLYWriter()
                # 確認檔案型別為stl
                elif extension == 'stl':
                    # 實體化vtkSTLWriter類別
                    writer = vtk.vtkSTLWriter()
                else:
                    raise ValueError("不支援的檔案格式.")
                # 寫入檔案
                writer.SetFileName(file_path)
                # 寫入資料
                writer.SetInputData(self.poly_data)
                # 更新檔案
                writer.Write()
            except ValueError as e:
                QMessageBox.critical(self, "錯誤", str(e))
    # 讀檔；參數放入檔案路徑
    def read_model(self, file_path):
        # 將副檔名前面的字轉換小寫
        extension = file_path.split('.')[-1].lower()
        # 讀取檔案變數
        reader = None
        # 確認檔案型別為vtp
        if extension == 'vtp':
            # 實體化vtkXMLPolyDataReader類別
            reader = vtk.vtkXMLPolyDataReader()
        # 確認檔案型別為obj
        elif extension == 'obj':
            # 實體化vtkOBJReader類別
            reader = vtk.vtkOBJReader()
        # 確認檔案型別為ply
        elif extension == 'ply':
            # 實體化vtkPLYReader類別
            reader = vtk.vtkPLYReader()
        # 確認檔案型別為stl
        elif extension == 'stl':
            # 實體化vtkSTLReader類別
            reader = vtk.vtkSTLReader()
        else:
            raise ValueError("不支援的檔案格式.")
        reader.SetFileName(file_path)
        reader.Update()
        return reader.GetOutput()