import vtk
from vtk import vtkInteractorStyleTrackballCamera
from models.interaction_styles.point_interactor import PointInteractor
from models.interaction_styles.point_interactor import TrimVisualize
from models.interaction_styles.lasso_interactor import LassoInteractor
from models.interaction_styles.box_interactor import BoxInteractor
from models.visible_select_func import VisibleSlt
import os
import open3d as o3d
import numpy as np

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
        self.AddObserver("MiddleButtonPressEvent", self.onMiddleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent", self.onMiddleButtonReleaseEvent)
        self.AddObserver("MouseWheelForwardEvent", self.onMouseWheelForwardEvent)
        self.AddObserver("MouseWheelBackwardEvent", self.onMouseWheelBackwardEvent)

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

    def enable_point_mode(self):
        self.pointSltMode = True
        self.boxSltMode = False
        self.lassoSltMode = False
        self.point_func = PointInteractor(self.active_model.poly_data,self.interactor,self.renderer)
    def unable_point_mode(self):
        self.pointSltMode = False
        self.point_func.SetInteractor(None)

    def enable_lasso_mode(self):
        self.lassoSltMode = True
        self.boxSltMode = False
        self.pointSltMode = False
        self.lasso_func = LassoInteractor(self.active_model.poly_data,self.interactor,self.renderer)
    def unable_lasso_mode(self):
        self.lassoSltMode = False
        self.lasso_func.interactorSetter(None)

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
            self.removeCells(self.active_model.poly_data,self.active_model.actor,self.box_func.selection_frustum)
            # 清除所有矩形的視覺化資料
            self.box_func.unRenderAllSelectors()
        # 點刪除範圍，滿足按下delete鍵且點選取模式為True
        elif self.key == "Delete" and self.pointSltMode:
            self.keep_select_area(self.active_model.poly_data,self.active_model.actor,self.point_func.total_path_point)
            # 清除所有點的視覺化資料、最短路徑資料等
            self.point_func.unRenderAllSelectors()
            
        # 套索刪除範圍，滿足按下delete鍵且套索選取模式為True
        elif self.key == "Delete" and self.lassoSltMode:
            # 移除選取範圍
            self.lassoClip(self.active_model.poly_data,self.active_model.actor,self.lasso_func.getClip())
            print(f"lasso select area:{self.lasso_func.getClip()}")
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
            return
        # 套索選取redo，滿足按下y鍵且套索選取模式為True
        elif (self.key == "y" or self.key == "Y") and self.lassoSltMode:
            # 套索選取redo
            return
    def lassoClip(self,poly_data,actor, selected_ids):
        poly_data.BuildLinks()#反查頂點連接的面
        print(f"lasso select area: {selected_ids}")
        points = vtk.vtkPoints() # 創建一個 vtkPoints 對象來儲存選取的點
        cell_ids = vtk.vtkIdList() # 儲存連接的cell id
        cells_to_delete = set() # 儲存要刪除的cell id
        for i in range(selected_ids.GetNumberOfTuples()): # 迭代所有選取的點
            try: # 確認是否有點
                point_id = selected_ids.GetValue(i) # 取得點的id
                x, y, z = poly_data.GetPoint(point_id) # 取得點的座標
                points.InsertNextPoint(x, y, z) # 將點加入vtkPoints

                poly_data.GetPointCells(point_id, cell_ids) # 取得連接的cell id
                for j in range(cell_ids.GetNumberOfIds()): # 迭代所有cell id
                    cells_to_delete.add(cell_ids.GetId(j)) # 將cell id加入刪除列表
            except Exception as e: # 如果沒有點，擲回錯誤訊息
                print(f"[ERROR] point_id={point_id}: {e}")
        new_cells = vtk.vtkCellArray() # 創建一個新的cell array來儲存新的cell

        id_list = vtk.vtkIdList() # 創建一個vtkIdList來儲存cell的id
        for cid in range(poly_data.GetNumberOfCells()): # 迭代所有cell id
            if cid in cells_to_delete: # 如果cell id在刪除列表中，則跳過
                continue #  跳過這個cell id
            poly_data.GetCellPoints(cid, id_list) # 取得cell的點
            new_cells.InsertNextCell(id_list) # 將cell的點加入新的cell array
        poly_data.SetPolys(new_cells) # 設定新的cell array為poly_data的cell array
        poly_data.Modified() # 更新poly_data


        mapper = vtk.vtkPolyDataMapper() # 創建一個 PolyDataMapper 對象
        mapper.SetInputData(poly_data) # 設定映射器的輸入資料
        mapper.ScalarVisibilityOff()
        actor.SetMapper(mapper) # 設定Actor的映射器
        self.renderer.AddActor(actor) # 將Actor加入渲染器   
        self.GetInteractor().GetRenderWindow().Render() # 渲染視窗

        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        parent_dir = os.path.dirname(current_dir) #取得當前檔案的父資料夾路徑
        stitch_dir = os.path.join(parent_dir, "stitchResult") # 拼接結果資料夾
        if not os.path.exists(stitch_dir): # 如果資料夾不存在，則創建它
            os.makedirs(stitch_dir) # 創建資料夾
        # 建立輸出的完整路徑
        output_path = os.path.join(stitch_dir, "lasso_select_area.stl")
        # 儲存檔案
        writer = vtk.vtkSTLWriter() # 儲存檔案
        writer.SetFileName(output_path) # 設定儲存檔案的路徑
        writer.SetInputData(poly_data) # 設定輸入資料
        writer.SetFileTypeToBinary() # 設定檔案類型為二進位制
        writer.Write() # 儲存檔案

        self.active_model.poly_data = poly_data # 更新active_model的poly_data
        self.active_model.actor = actor # 更新active_model的actor
        '''
        #選取視覺化
        polydata = vtk.vtkPolyData() # 創建一個 vtkPolyData 對象來儲存選取的點
        polydata.SetPoints(points) # 設定 vtkPoints 為 vtkPolyData 的點資料
        glyph_filter = vtk.vtkVertexGlyphFilter() # 使用 vtkVertexGlyphFilter 將點轉換為可渲染的圖元
        glyph_filter.SetInputData(polydata) # 將點資料設置為輸入
        glyph_filter.Update() # 更新過濾器以生成圖元

        mapper = vtk.vtkPolyDataMapper() # 創建一個 PolyDataMapper 對象
        mapper.SetInputConnection(glyph_filter.GetOutputPort()) # 將過濾器的輸出連接到映射器

        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        parent_dir = os.path.dirname(current_dir) # 取得當前檔案的父資料夾路徑
        stitch_dir = os.path.join(parent_dir, "stitchResult") # 拼接結果資料夾
        if not os.path.exists(stitch_dir): # 如果資料夾不存在，則創建它
            os.makedirs(stitch_dir) # 創建資料夾
        output_path = os.path.join(stitch_dir, "lasso_select_area.stl")  # 將檔案儲存到指定資料夾
        
        writer = vtk.vtkSTLWriter() # 儲存檔案
        writer.SetFileName(output_path) # 設定儲存檔案的路徑
        writer.SetInputData(glyph_filter.GetOutput()) # 設定輸入資料
        writer.SetFileTypeToBinary() # 設定檔案類型為二進位制
        writer.Write() # 儲存檔案

        new_poly_data = vtk.vtkSTLReader() # 輸入剛剛儲存的檔案
        new_poly_data.SetFileName(output_path) # 設定檔案路徑
        new_poly_data.Update() # 更新讀取器以獲取資料
        new_poly_data = new_poly_data.GetOutput()# 獲取輸出資料
        actor = vtk.vtkActor() # 創建一個 Actor 對象
        actor.SetMapper(mapper) # 設定映射器
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 設定顏色為紅色
        actor.GetProperty().SetPointSize(5)  # 可選：設定點的大小
        mapper = vtk.vtkPolyDataMapper() # 創建一個 PolyDataMapper 對象
        mapper.SetInputData(new_poly_data) # 設定映射器的輸入資料
        self.renderer.AddActor(actor) # 將Actor加入渲染器
        self.GetInteractor().GetRenderWindow().Render() # 渲染視窗
        '''
    # 移除選取範圍，第一個參數接收輸入模型，第二個參數接收剪取資料
    def removeCells(self,poly_data,actor,selection_frustum):
        '''創建一個 vtkClipPolyData進行剪裁'''
        if not isinstance(selection_frustum, vtk.vtkImplicitFunction):  # 檢查輸入的剪裁資料，型別有無符合vtk.vtkImplicitFunction；如果沒有會報錯，如缺少參數等
            return
        clipper = vtk.vtkClipPolyData() # 初始化剪裁器
        clipper.SetInputData(poly_data)# 要剪裁的目標放入輸入的3D模型
        clipper.SetClipFunction(selection_frustum)# 剪裁的函數是選取範圍 
        clipper.GenerateClippedOutputOff()# 剪裁的方向是選取範圍的內部
        clipper.Update()# 更新剪裁器
        clip_poly_data = clipper.GetOutput()# 取得剪裁後的資料

        poly_data.DeepCopy(clip_poly_data) # 將剪裁後的資料複製到原本的poly_data上

        if poly_data.GetNumberOfCells() == 0: #  如果剪裁後的資料沒有任何cell，代表沒有選取到任何東西，不做事
            return
        print(f"Get selected poly data cells:{poly_data.GetNumberOfCells()}")
        '''將poly_data儲存到指定資料夾'''
        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        parent_dir = os.path.dirname(current_dir) #取得當前檔案的父資料夾路徑
        stitch_dir = os.path.join(parent_dir, "stitchResult") # 輸出到stitchResult資料夾
        if not os.path.exists(stitch_dir): # 如果資料夾不存在，則創建它
            os.makedirs(stitch_dir) # 創建資料夾
            # 建立輸出的完整路徑
        output_path = os.path.join(stitch_dir, "remove_cells_box.stl")  # 將檔案儲存到指定資料夾
        # 儲存檔案
        writer = vtk.vtkSTLWriter() # 儲存檔案
        writer.SetFileName(output_path) # 設定儲存檔案的路徑
        writer.SetInputData(poly_data)  # 設定輸入資料
        writer.SetFileTypeToBinary() #  設定檔案類型為二進位制
        writer.Write() # 儲存檔案
        '''待修改為model_mabager的acotr、,mapper、poly_data'''
        mapper = vtk.vtkPolyDataMapper() # 創建一個 PolyDataMapper 對象
        mapper.SetInputData(poly_data) # 設定映射器的輸入資料
        mapper.ScalarVisibilityOff()
        actor.SetMapper(mapper) # 設定Actor的映射器
        self.renderer.AddActor(actor) # 將Actor加入渲染器
        self.GetInteractor().GetRenderWindow().Render() # 渲染視窗
        self.active_model.poly_data = poly_data # 更新active_model的poly_data
        self.active_model.actor = actor # 更新active_model的actor

    '''保留inlay surface功能'''
    def keep_select_area(self,poly_data,actor,loop_points):
        # 使用 SelectPolyData 建立封閉區域選取
        select = vtk.vtkSelectPolyData()
        select.SetInputData(poly_data)
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

        poly_data.DeepCopy(clip.GetOutput()) # 將裁切後的資料複製到原本的poly_data上

        # 清除未連接部份
        connect_new_poly_data = vtk.vtkConnectivityFilter()
        connect_new_poly_data.SetInputData(poly_data)
        connect_new_poly_data.SetExtractionModeToLargestRegion()
        connect_new_poly_data.Update()
        poly_data.DeepCopy(connect_new_poly_data.GetOutput()) # 將裁切後的資料複製到原本的poly_data上

        mapper = vtk.vtkPolyDataMapper()
        mapper.ScalarVisibilityOff()
        mapper.SetInputData(poly_data)
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)
        self.GetInteractor().GetRenderWindow().Render()

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
        writer.SetInputData(poly_data)
        writer.SetFileTypeToBinary()
        writer.Write()
        self.active_model.poly_data = poly_data
        self.active_model.actor = actor
        # 使用 SelectPolyData 建立封閉區域選取
    def onMiddleButtonPressEvent(self, obj, event):
        super().OnMiddleButtonDown()
    def onMiddleButtonReleaseEvent(self, obj, event):
        super().OnMiddleButtonUp()
    def onMouseWheelForwardEvent(self, obj, event):
        super().OnMouseWheelForward()
    def onMouseWheelBackwardEvent(self, obj, event):
        super().OnMouseWheelBackward()
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
            self.lasso_func.interactorSetter(self.interactor)
            self.lasso_func.onLeftButtonDown(obj,event)
            self.lasso_func.onMouseMove(obj,event)
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
        elif self.lassoSltMode and not self.boxSltMode and not self.pointSltMode:
            self.lasso_func.interactorSetter(self.interactor)
            self.lasso_func.onLeftButtonRelease(obj,event)
        else:
            super().OnRightButtonUp()
        


    