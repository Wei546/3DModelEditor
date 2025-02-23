import vtk
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D, vtkInteractorStyleTrackballCamera
from models.visible_select_func import VisibleSlt

class HighlightInteractorStyle(vtkInteractorStyleRubberBand3D):
    def __init__(self, poly_data, renderer):
        super().__init__()
        # 初始化輸入資料
        self.poly_data = poly_data
        # 渲染視窗
        self.renderer = renderer
        # 矩形鍵盤快捷鍵、按鈕選取開關
        self.boxSltMode = False 
        # 點鍵盤快捷鍵、按鈕選取開關
        self.pointSltMode = False
        # 套索鍵盤快捷鍵、按鈕選取開關
        self.lassoSltMode = False
        # 矩形範圍按下起始點
        self.start_position = None
        # 矩形範圍放開起始點
        self.end_position = None
        # 
        self.geometry_filter = None
        self.selected_poly_data = None
        self.extract_geometry = None
        # 實體化點選取類別
        self.point_func = PointInteractor(poly_data)
        # 實體化套索選取類別
        self.lasso_func = LassoInteractor(poly_data)
        # 選取範圍
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.boxArea = vtk.vtkAreaPicker()
        # 鍵盤按下監聽器
        self.AddObserver("KeyPressEvent", self.modeSltKeyPress)
        # 滑鼠左鍵放開監聽器
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonUp)
        # 滑鼠左鍵按下監聽器
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
        
        # 穿透按鈕開關
        self.throughBtnMode = False


    # 選取模式
    def modeSltKeyPress(self, obj, event):
        # 取得按下的按鍵
        self.key = self.GetInteractor().GetKeySym()
        # 矩形選取模式
        if self.key == "c" or self.key == "C":
            # 如果矩形選取模式為False
            if not self.boxSltMode:
                # 打開矩形選取模式
                self.boxSltMode = True
                # 矩形選取開啟，點選取不能點擊
                self.pointBtn.setEnabled(True)
                # 矩形選開啟，套索選取不能點擊
                self.lassoBtn.setEnabled(True)
            # 如果矩形選取模式為True
            else:
                # 關閉矩形選取模式
                self.boxSltMode = False
                # 矩形選取關閉，點選取可以點擊
                self.pointBtn.setEnabled(False)
                # 矩形選取關閉，套索選取可以點擊
                self.lassoBtn.setEnabled(False)
        # 點選取模式
        elif self.key == "p" or self.key == "P":
            # 如果點選取模式為False
            if not self.pointSltMode:
                # 取消按鍵點選，清空點選的列表
                self.point_func.pathList = []
                # 打開點選取模式
                self.pointSltMode = True
            # 如果點選取模式為True
            else:
                # 關閉點選取模式
                self.pointSltMode = False
                # 清除所有點的視覺化資料、最短路徑資料等
                self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
                # 清除所有套索的視覺化資料、最短路徑資料等
                self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索選取模式
        elif self.key == "l" or self.key == "L":
            # 如果套索選取模式為False
            if not self.lassoSltMode:
                # 清空套索選取的儲存id
                self.lasso_func.pickpointId = []
                # 打開套索選取模式
                self.lassoSltMode = True
            # 如果套索選取模式為True
            else:
                # 關閉套索選取模式
                self.lassoSltMode = False
                # 清除所有套索的視覺化資料、最短路徑資料等
                self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
                # 清除所有套索的視覺化資料、最短路徑資料等
                self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 矩形刪除範圍，滿足按下delete鍵且矩形選取模式為True
        elif self.key == "Delete"  and self.boxSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data,self.selection_frustum)
        # 點刪除範圍，滿足按下delete鍵且點選取模式為True
        elif self.key == "Delete" and self.pointSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data,self.point_func.loop)
            # 清除所有點的視覺化資料、最短路徑資料等
            self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索刪除範圍，滿足按下delete鍵且套索選取模式為True
        elif self.key == "Delete" and self.lassoSltMode:
            # 移除選取範圍
            self.removeCells(self.poly_data,self.lasso_func.loop)
            # 清除所有套索的視覺化資料、最短路徑資料等
            self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 封閉點選取範圍，滿足按下enter鍵
        elif self.key == "Return":
            # enter後閉合點選範圍
            self.point_func.closeArea(self.GetInteractor(),self.renderer)
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
        # 要剪裁的目標就是輸入的3D模型
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
        # 複製剪裁後的資料給輸入的3D模型
        self.poly_data.DeepCopy(new_poly_data)
        # 移除所有視覺化資料
        self.renderer.RemoveActor(self.actor)
        # 更新視覺化資料
        self.mapper.SetInputData(poly_data)
        # 更新渲染器、互動器
        self.GetInteractor().GetRenderWindow().Render()
    # 進入到class HightlightInteractorStyle，監聽器的狀態都是屬於矩形選取模式；滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event):
        # 取得左鍵按下時的位置，起點座標2D
        self.start_position = self.GetInteractor().GetEventPosition()
        # 矩形選取模式，在class HighlightInteractorStyle
        if self.boxSltMode: 
            # override class vtkInteractorStyleRubberBand3D預設左鍵按下的功能
            self.OnLeftButtonDown()
        # 點選模式，在class PointInteractor
        elif self.pointSltMode:
            # 使用實體變數point_func，呼叫onLeftButtonDown函數，放入監聽器的參數，互動器、渲染器
            self.point_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
        # 套索選取模式，在class LassoInteractor
        elif self.lassoSltMode:
            # 使用實體變數lasso_func，呼叫onLeftButtonDown函數，放入監聽器的參數，互動器、渲染器
            self.lasso_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
    # 進入到class HightlightInteractorStyle，監聽器的狀態都是屬於矩形選取模式；滑鼠左鍵放開
    def onLeftButtonUp(self,obj,event):
        # 取得左鍵放開時的位置，終點座標2D
        self.end_position = self.GetInteractor().GetEventPosition()
        # 先檢查使用穿透與否
        if self.throughBtnMode:
            self.OnLeftButtonUp()
            self.checkThroughModel()
            
        else:
            # 矩形選取模式
            if self.boxSltMode:
                # start_position[0]代表x座標，start_position[1]代表y座標；end_position[0]代表x座標，end_position[1]代表y座標
                self.boxArea.AreaPick(self.start_position[0],self.start_position[1],self.end_position[0],self.end_position[1],self.renderer)
                # 取得選取範圍
                self.selection_frustum = self.boxArea.GetFrustum()
                # 剪裁選取範圍
                self.extract_geometry = vtk.vtkExtractGeometry()
                # 輸入剪裁的3D模型
                self.extract_geometry.SetInputData(self.poly_data)
                # 設定剪裁的選取範圍
                self.extract_geometry.SetImplicitFunction(self.selection_frustum)
                # 更新剪裁器
                self.extract_geometry.Update()
                # 取得剪裁後的資料
                self.selected_poly_data = self.extract_geometry.GetOutput()   
                # 移除所有視覺化資料
                self.geometry_filter = vtk.vtkGeometryFilter()
                # 設定輸入資料
                self.geometry_filter.SetInputData(self.selected_poly_data)
                # 更新幾何過濾器
                self.geometry_filter.Update()
                # 移除所有視覺化資料
                self.mapper.SetInputData(self.geometry_filter.GetOutput())
                # 更新視覺化資料
                self.actor.SetMapper(self.mapper)
                # 設定填滿示意顏色為紅色
                self.actor.GetProperty().SetColor(1.0, 0.0, 0.0) 
                # 設定渲染器
                self.renderer.AddActor(self.actor)
                # override舊監聽器
                self.OnLeftButtonUp()
                # 更新視窗
                self.GetInteractor().GetRenderWindow().Render()
    # 穿透功能狀態
    def checkThroughModel(self):
        if self.throughBtnMode:
            print("Through button is on")
            self.visibleSlt = VisibleSlt(self.renderer,self.GetInteractor().GetRenderWindow().Render())
            self.visibleSlt.selectVisible(self.start_position,self.end_position)
        else:
            
            print("Through button is off")

    def mode(self,throughBtn):
        self.throughBtnMode = throughBtn
        print(f"throughBtnMode: {self.throughBtnMode}")


# 套索選取類別
class LassoInteractor(vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data):
        super().__init__()
        # 初始化輸入資料
        self.poly_data = poly_data
        # 初始化選取範圍資料
        self.picker = vtk.vtkCellPicker()
        # 選取範圍資料
        self.select_append = vtk.vtkAppendPolyData()
        self.selection_point = vtk.vtkPoints()
        self.loop = vtk.vtkImplicitSelectionLoop()
        # 儲存最短路徑
        self.dijkstra_path = []
        # 點選位置
        self.pickpointId = []
        # 視覺化套索線段
        self.boundaryActors = []
        # 存放redo點選位置之列表
        self.redoPickpointId = []
        # 存放最短路徑之列表
        self.redoDijkstraPath = []
        # 存放redo視覺化線段之列表
        self.redoBoundaryActors = []
        # 新的計算多邊形列表
        self.store_select_arr = []
        # 選取模式監聽器
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下
    def onLeftButtonDown(self, obj, event, interactor, renderer):
        # 渲染器
        self.renderer = renderer
        # 互動器
        self.interactor = interactor
        # 點選位置
        clickPos = interactor.GetEventPosition()
        # 選取位置轉成3D座標
        self.picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        # 選取輸入物件
        self.pickpointId.append(self.picker.GetPointId())
        # 計算最短路徑
        for i in range(len(self.pickpointId)):
            # 實體化最短路徑
            dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
            # 設定最短路徑的輸入資料
            dijkstra.SetInputData(self.poly_data)
            # 最短路徑最後一點為選取的點
            dijkstra.SetStartVertex(self.pickpointId[i])
            # 最短路徑第一點為選取的點
            dijkstra.SetEndVertex(self.pickpointId[i-1])
            # 更新最短路徑
            dijkstra.Update()
            # 存放最短路徑
            self.dijkstra_path.append(dijkstra)
        # 複製最短路徑資料給self.boundary
        for path in self.dijkstra_path:
            # 視覺化套索線段
            self.select_append.AddInputData(path.GetOutput())
        self.select_append.Update()
        self.boundary = self.select_append.GetOutput()     
        boundaryMapper = vtk.vtkPolyDataMapper()
        boundaryMapper.SetInputData(self.boundary)
        self.boundaryActor = vtk.vtkActor()
        self.boundaryActor.SetMapper(boundaryMapper)
        self.boundaryActor.GetProperty().SetLineWidth(2)
        self.boundaryActor.GetProperty().SetColor(1, 0, 0)
        self.boundaryActors.append(self.boundaryActor)
        renderer.AddActor(self.boundaryActor)
        interactor.GetRenderWindow().Render()
        # 小於3個點不做事
        if len(self.pickpointId) < 3:
            return
        # 選取範圍資料
        self.loop.SetLoop(self.boundary.GetPoints())
        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(self.poly_data)
        clipper.SetClipFunction(self.loop)
        clipper.InsideOutOn()
        clipper.Update()
        clipperMapper = vtk.vtkPolyDataMapper()
        clipperMapper.SetInputConnection(clipper.GetOutputPort())
        clipperActor = vtk.vtkActor()
        clipperActor.SetMapper(clipperMapper)
        renderer.AddActor(clipperActor)
        interactor.GetRenderWindow().Render()
        
    # 清除選取輔助樣式
    def unRenderAllSelectors(self,renderer,interactor):
        for actor in self.boundaryActors:
            renderer.RemoveActor(actor)
        self.boundaryActors.clear()
        self.selection_point.Reset()
        self.dijkstra_path.clear()
        self.pickpointId.clear()
        self.select_append.RemoveAllInputs()
        interactor.GetRenderWindow().Render()
    # 取消上一步選取
    def undo(self,renderer,interactor):
        # 沒有選到點不做事
        if not self.pickpointId:
            return
        # undo點選位置
        last_pickpointId = self.pickpointId.pop()
        self.redoPickpointId.append(last_pickpointId)
        # undo最短路徑
        if self.dijkstra_path:
            self.redoDijkstraPath.append(self.dijkstra_path.copy())
            self.dijkstra_path.clear()

        if self.boundaryActors:
            last_actor = self.boundaryActors.pop()
            self.redoBoundaryActors.append(last_actor)
            renderer.RemoveActor(last_actor)

        self.selection_point.Reset()
        self.select_append.RemoveAllInputs()

        if len(self.pickpointId) >= 1:
            for point_id in self.pickpointId:
                self.selection_point.InsertNextPoint(self.poly_data.GetPoint(point_id))
            

            if len(self.pickpointId) >= 2:
                for i in range(1, len(self.pickpointId)):
                    dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
                    dijkstra.SetInputData(self.poly_data)
                    dijkstra.SetStartVertex(self.pickpointId[i])
                    dijkstra.SetEndVertex(self.pickpointId[i - 1])
                    dijkstra.Update()
                    self.select_append.AddInputData(dijkstra.GetOutput())

                self.select_append.Update()

        interactor.GetRenderWindow().Render()
        print(f"------------undo detail start------------")
        print(f"pick point num: {len(self.pickpointId)}")
        print(f"boundaryActors length: {len(self.boundaryActors)}")
        print(f"selection point length: {self.selection_point.GetNumberOfPoints()}")
        print(f"after undo dijkstra path length: {len(self.dijkstra_path)}")
        print(f"------------undo detail end------------")
    # 還原選取
    def redo(self,renderer,interactor):
        # redo點選位置
        if self.redoPickpointId:
            redo_pickpointId = self.redoPickpointId.pop()
            self.pickpointId.append(redo_pickpointId)
        # redo最短路徑
        if self.redoDijkstraPath:
            redo_dijkstra_path = self.redoDijkstraPath.pop()
            self.dijkstra_path = redo_dijkstra_path
        # redo視覺化線段
        if self.redoBoundaryActors:
            redo_boundary_actor = self.redoBoundaryActors.pop()
            self.boundaryActors.append(redo_boundary_actor)
            renderer.AddActor(redo_boundary_actor)
        # redo選取點
        if len(self.pickpointId) >= 1:
            for point_id in self.pickpointId:
                self.selection_point.InsertNextPoint(self.poly_data.GetPoint(point_id))
            
            if len(self.pickpointId) >= 2:
                for i in range(1, len(self.pickpointId)):
                    dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
                    dijkstra.SetInputData(self.poly_data)
                    dijkstra.SetStartVertex(self.pickpointId[i])
                    dijkstra.SetEndVertex(self.pickpointId[i - 1])
                    dijkstra.Update()
                    self.select_append.AddInputData(dijkstra.GetOutput())

                self.select_append.Update()

        interactor.GetRenderWindow().Render()
        print(f"------------redo detail start------------")
        print(f"pick point num: {len(self.pickpointId)}")
        print(f"boundaryActors length: {len(self.boundaryActors)}")
        print(f"selection point length: {self.selection_point.GetNumberOfPoints()}")
        print(f"after redo dijkstra path length: {len(self.dijkstra_path)}")
        print(f"------------redo detail end------------")
# 點選取類別，繼承vtkInteractorStyleTrackballCamera
class PointInteractor(vtkInteractorStyleTrackballCamera):
    # poly_data是輸入的3D模型
    def __init__(self,poly_data):
        super().__init__()
        # 初始化輸入資料，用於後續計算在物體表面選取的點
        self.poly_data = poly_data
        # 初始化最短路徑，用於計算點選的最短路徑
        self.dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
        # dijkstra最短路徑使用的資料是poly_data
        self.dijkstra.SetInputData(self.poly_data)
        # 最短路徑存放所有點的類
        self.idList = vtk.vtkIdList()
        # 存放所有視覺化球體的列表
        self.sphereActors = []
        # 存放所有視覺化線段的列表
        self.lineActors = []
        # 存放封閉視覺化線段
        self.closeLineActors = []
        # 點選點的列表
        self.pathList = []
        # 最短路徑的點的列表，也就是實際的線段
        self.meshNumList = []
        # redo線段視覺化的列表
        self.redoLineActors = []
        # redo球體視覺化的列表
        self.redoSphereActors = []
        # redo點選的列表
        self.redoPathList = []
        # redo實際線段的列表
        self.redoMeshNumList = []
        # 最短路徑每一點的列表
        self.dijkstra_path_arr = []
        # 選取範圍
        self.loop = vtk.vtkImplicitSelectionLoop()
        # 實體化封閉路線最短路徑
        self.close_dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
        # 封閉線段的最短路徑列表
        self.close_dijkstra_path_arr = []
        # 輸入封閉最短路徑的資料
        self.close_dijkstra.SetInputData(self.poly_data)
        # 放入loop的點
        self.selection_point = vtk.vtkPoints()
        # 整合所有最短路徑列表
        self.all_dijkstra_path_arr = []
        # 第一個參數是事件名稱，第二個參數是事件的回調函數
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event,interactor,renderer):
        # 初始化點選位置座標
        clickPos = interactor.GetEventPosition()
        # 初始化靠近選取位置的網格
        picker = vtk.vtkCellPicker()
        # 選取位置轉成3D座標
        picker.Pick(clickPos[0],clickPos[1],0,renderer)
        print(f"point coord: {self.poly_data.GetPoint(picker.GetPointId())}")
        # 選取輸入物件
        if(picker.GetCellId() != -1):
            # 視覺化選取點
            self.pathList.append(picker.GetPointId())
            # 點選位置座標
            point_position = self.poly_data.GetPoint(picker.GetPointId())
            # 實體化球體
            sphereSource = vtk.vtkSphereSource()
            # 球體中心位置設定點選座標
            sphereSource.SetCenter(point_position)
            # 半徑設定0.02
            sphereSource.SetRadius(0.02)
            # 將圓形立體資料轉換成平面圖形資料
            sphereMapper = vtk.vtkPolyDataMapper()
            # SetInputConnection()動態傳遞點選的球體；GetOutputPort()取得球體
            sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
            # 將球體資料轉換成視覺化物件
            self.sphereActor = vtk.vtkActor()
            # actor放入mapper，轉換成適合渲染的物件
            self.sphereActor.SetMapper(sphereMapper)
            # 設定球體顏色為紅色
            self.sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            # 將actor放入渲染器
            renderer.AddActor(self.sphereActor)
            # undo、消除的列表
            self.sphereActors.append(self.sphereActor)
            print(f"pathList: {self.pathList}")
            
            # 求最小路徑，至少一個點以上才能求最短路徑
            if len(self.pathList) > 1:
                # 最短路徑起始點是點選的倒數第二個點
                self.dijkstra.SetStartVertex(self.pathList[-2])
                # 最短路徑結束點是點選的最後一個點
                self.dijkstra.SetEndVertex(self.pathList[-1])
                # 更新最短路徑
                self.dijkstra.Update()
                # 取得最短路徑的點
                self.idList = self.dijkstra.GetIdList() 

                for i in range(self.idList.GetNumberOfIds()-1):
                    print(f"index{i} point id: {self.idList.GetId(i)}|point coord: {self.poly_data.GetPoint(self.idList.GetId(i))}")
                # 最短路徑實際數量
                self.meshNumList.append(self.idList.GetNumberOfIds())
                print(f"meshNumList: {self.meshNumList}")
                # 視覺化最短路徑
                for i in range(self.idList.GetNumberOfIds()-1):
                    # 實體化線段
                    lineSource = vtk.vtkLineSource()
                    # 從點選的最短路徑的列表取得索引值為i的點作為線段的起始點
                    lineSource.SetPoint1(self.poly_data.GetPoint(self.idList.GetId(i)))
                    # 從點選的最短路徑的列表取得索引值為i+1的點作為線段的結束點
                    lineSource.SetPoint2(self.poly_data.GetPoint(self.idList.GetId(i+1)))
                    # 將線段資料轉換成平面圖形資料
                    lineMapper = vtk.vtkPolyDataMapper()
                    # SetInputConnection()動態傳遞點選的線段；GetOutputPort()取得線段
                    lineMapper.SetInputConnection(lineSource.GetOutputPort())
                    # 將線段資料轉換成視覺化物件
                    self.lineActor = vtk.vtkActor()
                    # actor放入mapper，轉換成適合渲染的物件
                    self.lineActor.SetMapper(lineMapper)
                    # 設定線段顏色為紅色
                    self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                    # 將actor放入渲染器
                    renderer.AddActor(self.lineActor)
                    # undo、消除的列表
                    self.lineActors.append(self.lineActor)
                    # 添加所有最短路徑的點到dijkstra_path_arr
                    self.dijkstra_path_arr.append(self.idList.GetId(i))
            # 去除重複的最短路徑點
            self.dijkstra_path_arr=list(set(self.dijkstra_path_arr))
            print(f" original dijkstra_path_arr: {self.dijkstra_path_arr}")
            # 渲染最短路徑
            interactor.GetRenderWindow().Render()

    # 封閉選取範圍
    def closeArea(self,interactor,renderer):
        # 封閉最短路徑的起點是點選的最後一個點
        self.close_dijkstra.SetStartVertex(self.pathList[-1])
        # 封閉最短路徑的終點是點選的第一個點
        self.close_dijkstra.SetEndVertex(self.pathList[0])
        # 更新封閉最短路徑
        self.close_dijkstra.Update()
        # 取得封閉最短路徑的點
        self.closeIdList = self.close_dijkstra.GetIdList()
        for i in range(self.closeIdList.GetNumberOfIds()-1):
            print(f"index{i} point id: {self.closeIdList.GetId(i)}|point coord: {self.poly_data.GetPoint(self.closeIdList.GetId(i))}")
        # 計算封閉起點與終點之間的實際線段
        for i in range(self.closeIdList.GetNumberOfIds()-1):
            # 實體化線段
            lineSource = vtk.vtkLineSource()
            # 從self.dijkstra_path_arr取得最後一個點作為封閉線段起始點
            lineSource.SetPoint1(self.poly_data.GetPoint(self.closeIdList.GetId(i)))
            # 將self.pathList取德第一個點作為封閉線段結束點
            lineSource.SetPoint2(self.poly_data.GetPoint(self.closeIdList.GetId(i+1)))
            # 將線段資料轉換成平面圖形資料
            lineMapper = vtk.vtkPolyDataMapper()
            # SetInputConnection()動態傳遞點選的線段；GetOutputPort()取得線段
            lineMapper.SetInputConnection(lineSource.GetOutputPort())
            # 將線段資料轉換成視覺化物件
            self.lineActor = vtk.vtkActor()
            # actor放入mapper，轉換成適合渲染的物件
            self.lineActor.SetMapper(lineMapper)
            # 設定線段顏色為紅色
            self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            # 將actor放入渲染器
            renderer.AddActor(self.lineActor)
            # 添加所有封閉最短路徑的點到dijkstra_path_arr
            self.close_dijkstra_path_arr.append(self.closeIdList.GetId(i))
            # 線段視覺化列表
            self.closeLineActors.append(self.lineActor)
        # 去除重複的最短路徑點
        self.close_dijkstra_path_arr=list(set(self.close_dijkstra_path_arr))
        # 將封閉最短路徑整合到dijkstra_path_arr
        print(f"all point id:{self.dijkstra_path_arr+self.close_dijkstra_path_arr}")
        # 整合所有最短路徑
        self.all_dijkstra_path_arr = self.dijkstra_path_arr+self.close_dijkstra_path_arr
        # 將所有點最短路徑的點儲存到selection_point
        for point in (self.all_dijkstra_path_arr):
            # 轉換成座標
            coord = self.poly_data.GetPoint(point)
            # 將座標放入selection_point
            self.selection_point.InsertNextPoint(coord)
        # 將selection_point放入loop
        self.loop.SetLoop(self.selection_point)
        # 查看loop有無資料
        print(f"loop: {self.loop.GetLoop()}")
        # 渲染畫面
        interactor.GetRenderWindow().Render()

    # 清除選取輔助樣式
    def unRenderAllSelectors(self,renderer,interactor):
        # 清除所有視覺化點
        for actor in self.sphereActors:
            # 移除actor
            renderer.RemoveActor(actor)
        # 清除所有視覺化線段
        for actor in self.lineActors:
            # 移除actor
            renderer.RemoveActor(actor)
        # 移除封閉線段視覺化線條
        for actor in self.closeLineActors:
            # 移除actor
            renderer.RemoveActor(actor)
        # 清除點選資料
        self.pathList = []
        # 清除實際線段數量
        self.meshNumList = []
        # 清除所有最短路徑
        self.dijkstra_path_arr = []
        # 清除封閉最短路徑
        self.close_dijkstra_path_arr = []
        # 清除所有最短路徑
        self.all_dijkstra_path_arr = []
        # 清除loop內的點
        self.selection_point.Reset()
        # 清除原點列表
        self.sphereActors.clear()
        # 清除原線段列表
        self.lineActors.clear()
        # 清除封閉線段列表
        self.closeLineActors.clear()
        # 檢查資料有無完全清除
        print(f"------------unRenderAllSelectors detail start------------")
        print(f"len(sphereActors): {len(self.sphereActors)}")
        print(f"len(lineActors): {len(self.lineActors)}")
        print(f"pathList: {self.pathList}")
        print(f"meshNumList: {self.meshNumList}")
        print(f"dijkstra_path_arr: {self.dijkstra_path_arr}")
        print(f"close_dijkstra_path_arr: {self.close_dijkstra_path_arr}")
        print(f"all_dijkstra_path_arr: {self.all_dijkstra_path_arr}")
        print(f"------------unRenderAllSelectors detail end------------")
        # 渲染畫面
        interactor.GetRenderWindow().Render()
    # 取消上一步選取
    def undo(self,renderer,interactor):
        # undo視覺化點
        last_sphere = self.sphereActors.pop()
        renderer.RemoveActor(last_sphere)
        self.redoSphereActors.append(last_sphere)
        # undo儲存實際點選列表
        last_path_point = self.pathList.pop()
        self.redoPathList.append(last_path_point)
        interactor.GetRenderWindow().Render()
        # undo儲存實際線段數量
        if len(self.meshNumList) == 0:
            return
        for i in range(self.meshNumList[-1]):
            if i == self.meshNumList[-1] - 1:
                break
            # undo視覺化線段
            last_line = self.lineActors.pop()
            renderer.RemoveActor(last_line)
            self.redoLineActors.append(last_line)
        last_mesh_num = self.meshNumList.pop()
        self.redoMeshNumList.append(last_mesh_num)
        interactor.GetRenderWindow().Render()
    # 還原選取
    def redo(self,renderer,interactor):
        # redo視覺化點
        redo_sphere = self.redoSphereActors.pop()
        renderer.AddActor(redo_sphere)
        self.sphereActors.append(redo_sphere)
        # redo儲存實際點選列表
        redo_path_point = self.redoPathList.pop()
        self.pathList.append(redo_path_point)
        interactor.GetRenderWindow().Render()
        # redo儲存實際線段數量
        if len(self.redoMeshNumList) == 0:
            return
        for i in range(self.redoMeshNumList[-1]):
            if i == self.redoMeshNumList[-1] - 1:
                break
            # redo視覺化線段
            redo_line = self.redoLineActors.pop()
            renderer.AddActor(redo_line)
            self.lineActors.append(redo_line)
        redo_mesh_num = self.redoMeshNumList.pop()
        self.meshNumList.append(redo_mesh_num)
        interactor.GetRenderWindow().Render()