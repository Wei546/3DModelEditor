import vtk
from vtk import vtkInteractorStyleTrackballCamera
from models.interaction_styles.point_interactor import PointInteractor
from models.interaction_styles.point_interactor import TrimVisualize
from models.interaction_styles.lasso_interactor import LassoInteractor
from models.interaction_styles.box_interactor import BoxInteractor
from models.visible_select_func import VisibleSlt
import os

class HighlightInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, model_manager, renderer,interactor):
        super().__init__()
        # 互動器參數
        self.interactor = interactor
        # 渲染視窗
        self.renderer = renderer
        # 矩形鍵盤快捷鍵、按鈕選取開關
        self.boxSltMode = False 
        # 點鍵盤快捷鍵、按鈕選取開關
        self.pointSltMode = False
        # 套索鍵盤快捷鍵、按鈕選取開關
        self.lassoSltMode = False
         # 穿透按鈕開關
        self.throughBtnMode = False
        # 拼接按鈕開關
        self.stitchingBtnMode = False
        # 模型管理器
        self.model_manager = model_manager
        # 當前選取的模型
        self.active_model = None
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        # 移除父類別左、右鍵監聽器
        self.RemoveObservers("LeftButtonPressEvent")
        self.RemoveObservers("LeftButtonReleaseEvent")
        self.RemoveObservers("RightButtonPressEvent")
        self.RemoveObservers("RightButtonReleaseEvent")
        self.RemoveObservers("MouseMoveEvent")
        # 鍵盤按下監聽器
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonUp)
        self.AddObserver("RightButtonPressEvent", self.onRightButtonDown)
        self.AddObserver("RightButtonReleaseEvent", self.onRightButtonUp)
        self.AddObserver("KeyPressEvent", self.modeSltKeyPress)

       
    def set_active_model(self, name):
        self.active_model = self.model_manager.get_model(name)

    def enable_box_mode(self):
        self.boxSltMode = True
        self.pointSltMode = False
        self.lassoSltMode = False
        self.box_func = BoxInteractor(self.active_model.poly_data,self.interactor,self.renderer)
    def unable_box_mode(self):
        self.boxSltMode = False
        self.box_func.SetInteractor(None)
        # self.box_func = None
    def enable_point_mode(self):
        self.pointSltMode = True
        self.boxSltMode = False
        self.lassoSltMode = False
        self.point_func = PointInteractor(self.active_model.poly_data,self.interactor,self.renderer)
        print(f"[DEBUG] 建立 PointInteractor for {self.active_model.name}")
        print(f"[DEBUG] poly_data memory id: {id(self.active_model.poly_data)}")

    def unable_point_mode(self):
        self.pointSltMode = False
        self.point_func.SetInteractor(None)
        # self.point_func = None
    def enable_lasso_mode(self):
        self.lassoSltMode = True
        self.boxSltMode = False
        self.pointSltMode = False
        self.lasso_func = LassoInteractor(self.active_model.poly_data,self.interactor,self.renderer)
    def unable_lasso_mode(self):
        self.lassoSltMode = False
        self.lasso_func = None

    # 選取在視窗上可見的範圍功能狀態
    def enable_through_mode(self):
        self.throughBtnMode = True
        self.box_func = BoxInteractor(self.active_model.poly_data,self.interactor,self.renderer)
    def unable_through_mode(self):
        self.throughBtnMode = False
        print("Through button is off")
        self.box_func = None
    # 拼接功能狀態
    def enable_stitching_mode(self):
        self.through_func = VisibleSlt(self.renderer,self.interactor)
        self.through_func.process_stitching()

    # 鍵盤按下監聽器
    def modeSltKeyPress(self, obj, event):
        self.key = self.GetInteractor().GetKeySym()
        if self.key in ["c", "C"]:
            if self.boxSltMode:
                self.unable_box_mode()
            else:
                self.enable_box_mode()
        # 點選取模式
        elif self.key in ["p", "P"]:
            if self.pointSltMode:
                self.unable_point_mode()
            else:
                self.enable_point_mode()
        # 套索選取模式
        elif self.key in ["l", "L"]:
            if self.lassoSltMode:
                self.unable_lasso_mode()
            else:
                self.enable_lasso_mode()
        # 矩形刪除範圍，滿足按下delete鍵且矩形選取模式為True
        elif self.key == "Delete" and self.boxSltMode:
            # 移除選取範圍
            self.removeCells(self.active_model.poly_data,self.box_func.selection_frustum)
            # 清除所有矩形的視覺化資料
            self.box_func.unRenderAllSelectors()
        # 點刪除範圍，滿足按下delete鍵且點選取模式為True
        elif self.key == "Delete" and self.pointSltMode:
            # 移除選取範圍
            # self.removeCells(self.poly_data_1,self.point_func.loop)
            # 非穿透模式
            
            self.cut_select_area(self.point_func.total_path_point)
            # 清除所有點的視覺化資料、最短路徑資料等
            
        # 套索刪除範圍，滿足按下delete鍵且套索選取模式為True
        elif self.key == "Delete" and self.lassoSltMode:
            # 移除選取範圍
            self.removeCells(self.active_model.poly_data,self.lasso_func.loop)
            # 清除所有套索的視覺化資料、最短路徑資料等
            self.lasso_func.unRenderAllSelectors()
        # 封閉點選取範圍，滿足按下enter鍵
        elif self.key == "Return":
            # enter後閉合點選範圍
            self.point_func.closeArea()
        # 點選取undo，滿足按下z鍵且點選取模式為True
        elif (self.key == "z" or self.key == "Z") and self.pointSltMode:
            # 點選取undo
            self.point_func.undo(self.renderer,self.GetInteractor())
        # 點選取redo，滿足按下y鍵且點選取模式為True
        elif (self.key == "y" or self.key == "Y") and self.pointSltMode:
            # 點選取redo
            self.point_func.redo(self.renderer,self.GetInteractor())
        # 套索選取undo，滿足按下z鍵且套索選取模式為True
        elif (self.key == "z" or self.key=="Z") and self.lassoSltMode:
            # 套索選取undo
            self.lasso_func.undo(self.renderer,self.GetInteractor())
        # 套索選取redo，滿足按下y鍵且套索選取模式為True
        elif (self.key == "y" or self.key == "Y") and self.lassoSltMode:
            # 套索選取redo
            self.lasso_func.redo(self.renderer,self.GetInteractor())
    # 移除選取範圍，第一個參數接收輸入模型，第二個參數接收
    def removeCells(self,poly_data,selection_frustum):
        # 檢查輸入的剪裁資料，型別有無符合vtk.vtkImplicitFunction；如果沒有會報錯，如缺少參數等
        if not isinstance(selection_frustum, vtk.vtkImplicitFunction):
            return
        # 初始化剪裁器
        clipper = vtk.vtkClipPolyData()
        # 要剪裁的目標放入輸入的3D模型
        clipper.SetInputData(poly_data)
        # 剪裁的函數是選取範圍 
        clipper.SetClipFunction(selection_frustum)
        # 剪裁的方向是選取範圍的內部
        clipper.GenerateClippedOutputOff()
        # 更新剪裁器
        clipper.Update()
        # 取得剪裁後的資料
        new_poly_data = clipper.GetOutput()
        # 如果剪裁後的資料沒有任何cell，代表沒有選取到任何東西，不做事
        if new_poly_data.GetNumberOfCells() == 0:
            return
        '''待修改為model_mabager的acotr、,mapper、poly_data'''
        self.GetInteractor().GetRenderWindow().Render()
    '''刪除選取範圍'''
    def cut_select_area(self,loop_points):
        # 使用 SelectPolyData 建立封閉區域選取
        select = vtk.vtkSelectPolyData()
        select.SetInputData(self.active_model.poly_data)
        select.SetLoop(loop_points)
        select.GenerateSelectionScalarsOn()
        select.SetSelectionModeToClosestPointRegion()
        select.SetEdgeSearchModeToDijkstra()
        select.SetSelectionModeToSmallestRegion()  # 選取最小區域
        select.Update()


        # 用 ClipPolyData 根據 scalars 做裁切（小於 0 的區域被保留）
        clip = vtk.vtkClipPolyData()
        clip.SetInputConnection(select.GetOutputPort())
        clip.InsideOutOff()
        clip.Update()
        
        # 已經trim的poly_data，並且轉成 PolyData型別
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputConnection(clip.GetOutputPort())
        geometry.Update()
        
        new_poly_data = geometry.GetOutput()

        # 清除未連接部份
        connect_new_poly_data = vtk.vtkConnectivityFilter()
        connect_new_poly_data.SetInputData(new_poly_data)
        connect_new_poly_data.SetExtractionModeToLargestRegion()
        connect_new_poly_data.Update()
        new_poly_data = connect_new_poly_data.GetOutput()

        if self.active_model.actor:
            self.renderer.RemoveActor(self.active_model.actor)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(new_poly_data)
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.active_model.poly_data = new_poly_data
        self.active_model.actor = actor
        self.renderer.AddActor(actor)
        self.GetInteractor().GetRenderWindow().Render()
        self.point_func.unRenderAllSelectors(self.active_model.poly_data)

    '''保留inlay surface功能'''
    def keep_select_area(self,loop_points):
        # 使用 SelectPolyData 建立封閉區域選取
        select = vtk.vtkSelectPolyData()
        select.SetInputData(self.active_model.poly_data)
        select.SetLoop(loop_points)
        select.GenerateSelectionScalarsOn()
        select.SetSelectionModeToClosestPointRegion()
        select.SetEdgeSearchModeToDijkstra()
        select.SetSelectionModeToSmallestRegion()  # 選取最小區域
        select.Update()


        # 用 ClipPolyData 根據 scalars 做裁切（小於 0 的區域被保留）
        clip = vtk.vtkClipPolyData()
        clip.SetInputConnection(select.GetOutputPort())
        clip.InsideOutOn()
        clip.Update()
        
        # 已經trim的poly_data，並且轉成 PolyData型別
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputConnection(clip.GetOutputPort())
        geometry.Update()
        
        
        
        new_poly_data = geometry.GetOutput()

        # 清除未連接部份
        connect_new_poly_data = vtk.vtkConnectivityFilter()
        connect_new_poly_data.SetInputData(new_poly_data)
        connect_new_poly_data.SetExtractionModeToLargestRegion()
        connect_new_poly_data.Update()
        new_poly_data = connect_new_poly_data.GetOutput()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(new_poly_data)
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        #建立儲存路徑
        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        parent_dir = os.path.dirname(current_dir) #取得當前檔案的父資料夾路徑
        stitch_dir = os.path.join(parent_dir, "stitchResult")  
        if not os.path.exists(stitch_dir):
            os.makedirs(stitch_dir)
            # 建立輸出的完整路徑
        output_path = os.path.join(stitch_dir, "./inlay_surface.stl")  # 將檔案儲存到指定資料夾
        # 儲存檔案
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(output_path)
        writer.SetInputData(new_poly_data)
        writer.SetFileTypeToBinary()
        writer.Write()
        self.active_model.poly_data = new_poly_data
        self.active_model.actor = actor
        self.renderer.AddActor(actor)
        self.GetInteractor().GetRenderWindow().Render()


        '''
        # 待修改為model_mabager的acotr、,mapper、poly_data
        # Step 1：選出 loop 所在的 connected surface（排除下層）
        connectivity = vtk.vtkConnectivityFilter()
        connectivity.SetInputData(self.active_model.poly_data)
        connectivity.SetExtractionModeToClosestPointRegion()
        connectivity.SetClosestPoint(loop_points.GetPoint(0))  # 用 loop 的第一點當基準
        connectivity.Update()
        cleaned_surface = connectivity.GetOutput()

        # Step 2：建立封閉選取區域
        select = vtk.vtkSelectPolyData()
        select.SetInputData(cleaned_surface) 
        select.SetLoop(loop_points)
        select.GenerateSelectionScalarsOn()
        select.SetEdgeSearchModeToDijkstra()
        select.SetSelectionModeToSmallestRegion()
        select.Update()

        # Step 3：裁切 loop 包住的內部 patch
        clip = vtk.vtkClipPolyData()
        clip.SetInputConnection(select.GetOutputPort())
        clip.InsideOutOn()
        clip.Update()

        # Step 4：轉為 PolyData
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputConnection(clip.GetOutputPort())
        geometry.Update()
        

        # Step 5：更新畫面，只顯示選取結果
        self.renderer.RemoveAllViewProps()

        self.renderer.AddActor(self.actor)
        self.GetInteractor().GetRenderWindow().Render()
        '''
        # 使用 SelectPolyData 建立封閉區域選取
        
        
    def onRightButtonDown(self, obj, event):
        super().OnLeftButtonDown()
    def onRightButtonUp(self, obj, event):
        super().OnLeftButtonUp()
    def onLeftButtonDown(self, obj, event):   
        if self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and not self.throughBtnMode:
            print(f"enter to interaction style box mode left button down")
            self.box_func.onLeftButtonPress(obj,event)
        elif self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and self.throughBtnMode:
            print(f"box  in visible  mode.")
            print(f"{self.throughBtnMode}")
            self.box_func.onLeftButtonPress(obj,event)
            
        elif self.pointSltMode and not self.boxSltMode and not self.lassoSltMode:
            self.point_func.onLeftButtonDown(obj,event)
        elif self.lassoSltMode and not self.boxSltMode and not self.pointSltMode:
            self.lasso_func.onLeftButtonDown(obj,event)
        else:
            super().OnRightButtonDown()
    def onLeftButtonUp(self, obj, event):
        if self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and not self.throughBtnMode:
            self.box_func.onLeftButtonUp(obj,event)
            select_area = self.box_func.boxSelectArea()
            self.box_func.show_all_area(select_area)
        elif self.boxSltMode and not self.pointSltMode and not self.lassoSltMode and self.throughBtnMode:
            print(f"This is in-visible view")
            self.box_func.onLeftButtonUp(obj,event)
            self.box_func.show_on_visible()
        else:
            super().OnRightButtonUp()
        


    