import vtk
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D, vtkInteractorStyleTrackballCamera
import numpy as np
import utils.pointLinkList as pl
class HighlightInteractorStyle(vtkInteractorStyleRubberBand3D):
    def __init__(self, poly_data, renderer):
        super().__init__()
        # 初始化輸入資料
        self.poly_data = poly_data
        self.renderer = renderer
        # 選取模式開關
        self.boxSltMode = False 
        self.pointSltMode = False
        self.lassoSltMode = False
        # 選取範圍資料
        self.start_position = None
        self.end_position = None
        self.geometry_filter = None
        self.selected_poly_data = None
        self.extract_geometry = None
        # 實體化點、套索選取類別
        self.point_func = PointInteractor(poly_data)
        self.lasso_func = LassoInteractor(poly_data)
        # 選取範圍
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.boxArea = vtk.vtkAreaPicker()
        # 選取模式監聽器
        self.AddObserver("KeyPressEvent", self.modeSltKeyPress)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonUp)
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
        # 回傳互動器

    # 選取模式
    def modeSltKeyPress(self, obj, event):
        self.key = self.GetInteractor().GetKeySym()
        # 矩形選取模式
        if self.key == "c" or self.key == "C":
            if not self.boxSltMode:
                self.boxSltMode = True
            else:
                self.boxSltMode = False
        # 點選取模式
        elif self.key == "p" or self.key == "P":
            if not self.pointSltMode:
                self.point_func.pathList = []
                self.pointSltMode = True
            else:
                self.pointSltMode = False
                self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
                self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
                print("type of point_func self.GetInteractor: ",type(self.point_func))
        # 套索選取模式
        elif self.key == "l" or self.key == "L":
            if not self.lassoSltMode:
                self.lasso_func.pickpointId = []
                self.lassoSltMode = True
            else:
                self.lassoSltMode = False
                self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
                self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 矩形刪除範圍
        elif self.key == "Delete"  and self.boxSltMode:
            self.removeCells(self.poly_data,self.selection_frustum)
        # 點刪除範圍
        elif self.key == "Delete" and self.pointSltMode:
            self.removeCells(self.poly_data,self.point_func.loop)
            self.point_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 套索刪除範圍
        elif self.key == "Delete" and self.lassoSltMode:
            self.removeCells(self.poly_data,self.lasso_func.loop)
            self.lasso_func.unRenderAllSelectors(self.renderer,self.GetInteractor())
        # 封閉點選取範圍
        elif self.key == "Return":
            self.point_func.closeArea(self.GetInteractor(),self.renderer)
        # 點選取undo
        elif (self.key == "z" or self.key == "Z") and self.pointSltMode:
            self.point_func.undo(self.renderer,self.GetInteractor())
        # 點選取redo
        elif (self.key == "y" or self.key == "Y") and self.pointSltMode:
            self.point_func.redo(self.renderer,self.GetInteractor())
        # 套索選取undo
        elif (self.key == "z" or self.key=="Z") and self.lassoSltMode:
            self.lasso_func.undo(self.renderer,self.GetInteractor())
        # 套索選取redo
        elif (self.key == "y" or self.key == "Y") and self.lassoSltMode:
            self.lasso_func.redo(self.renderer,self.GetInteractor())
    # 移除選取範圍
    def removeCells(self,poly_data,selection_frustum):
        if not isinstance(selection_frustum, vtk.vtkImplicitFunction):
            return

        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(poly_data) 
        clipper.SetClipFunction(selection_frustum)
        clipper.GenerateClippedOutputOff()
        clipper.Update()

        new_poly_data = clipper.GetOutput()

        if new_poly_data.GetNumberOfCells() == 0:
            return

        self.poly_data.DeepCopy(new_poly_data)
        self.renderer.RemoveActor(self.actor)

        self.mapper.SetInputData(poly_data)
    
        self.GetInteractor().GetRenderWindow().Render()
    # 滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event):
        if self.boxSltMode:
            self.start_position = self.GetInteractor().GetEventPosition()
            self.OnLeftButtonDown()
        elif self.pointSltMode:
            self.point_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
        elif self.lassoSltMode:
            self.lasso_func.onLeftButtonDown(obj,event,self.GetInteractor(),self.renderer)
    # 滑鼠左鍵放開
    def onLeftButtonUp(self,obj,event):
        if self.boxSltMode:
            self.end_position = self.GetInteractor().GetEventPosition()
            self.boxArea.AreaPick(self.start_position[0],self.start_position[1],self.end_position[0],self.end_position[1],self.renderer)
            self.selection_frustum = self.boxArea.GetFrustum()
            self.extract_geometry = vtk.vtkExtractGeometry()
            self.extract_geometry.SetInputData(self.poly_data)
            self.extract_geometry.SetImplicitFunction(self.selection_frustum)
            self.extract_geometry.Update()
            self.selected_poly_data = self.extract_geometry.GetOutput()   
            self.geometry_filter = vtk.vtkGeometryFilter()
            self.geometry_filter.SetInputData(self.selected_poly_data)
            self.geometry_filter.Update()
            self.mapper.SetInputData(self.geometry_filter.GetOutput())
            self.actor.SetMapper(self.mapper)
            self.actor.GetProperty().SetColor(1.0, 0.0, 0.0) 
            self.renderer.AddActor(self.actor)
            self.OnLeftButtonUp()
            self.GetInteractor().GetRenderWindow().Render()
# 套索選取類別
class LassoInteractor(vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data):
        super().__init__()
        # 初始化輸入資料
        self.poly_data = poly_data
        self.picker = vtk.vtkCellPicker()
        # 選取範圍資料
        self.select_append = vtk.vtkAppendPolyData()
        self.selection_point = vtk.vtkPoints()
        self.loop = vtk.vtkImplicitSelectionLoop()
        # 儲存最短路徑
        self.dijkstra_path = []
        self.pickpointId = []
        # 視覺化套索線段
        self.boundaryActors = []
        # redo、undo功能
        self.redoPickpointId = []
        self.redoDijkstraPath = []
        self.redoBoundaryActors = []
        # 新的計算多邊形列表
        self.store_select_arr = []
        # 選取模式監聽器
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下
    def onLeftButtonDown(self, obj, event, interactor, renderer):
        # 渲染、互動器
        self.renderer = renderer
        self.interactor = interactor
        # 點選位置
        clickPos = interactor.GetEventPosition()
        self.picker.Pick(clickPos[0], clickPos[1], 0, renderer)
        self.pickpointId.append(self.picker.GetPointId())
        # 計算最短路徑
        for i in range(len(self.pickpointId)):
            dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
            dijkstra.SetInputData(self.poly_data)
            dijkstra.SetStartVertex(self.pickpointId[i])
            dijkstra.SetEndVertex(self.pickpointId[i-1])
            dijkstra.Update()
            self.dijkstra_path.append(dijkstra)
        # 複製最短路徑資料給self.boundary
        for path in self.dijkstra_path:
            self.select_append.AddInputData(path.GetOutput())
        self.select_append.Update()
        self.boundary = self.select_append.GetOutput()     
        # 視覺化套索線段
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
        # mesh作為選取範圍的資料
        self.selectionCells = vtk.vtkCellArray()
        # 選取範圍
        self.loop = vtk.vtkImplicitSelectionLoop()
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
        # 不是選取輸入物件不做事
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
                    # 視覺化最短路徑
                    interactor.GetRenderWindow().Render()
                    # 添加所有最短路徑的點到dijkstra_path_arr
                    self.dijkstra_path_arr.append(self.idList.GetId(i))
            # 去除重複的最短路徑點
            self.dijkstra_path_arr=list(set(self.dijkstra_path_arr))
            self.dijkstra_path_arr = list(reversed(self.dijkstra_path_arr))
            print(f" original dijkstra_path_arr: {self.dijkstra_path_arr}")
            
            # 渲染最短路徑
            interactor.GetRenderWindow().Render()

    # 封閉選取範圍
    def closeArea(self,interactor,renderer):
        # 將最後一個點與第一個點連接

        # 如果點選的點數小於2，不做事
        if len(self.pathList) < 2:
            return
        # 實體化線段
        lineSource = vtk.vtkLineSource()
        # 從self.dijkstra_path_arr取得最後一個點作為封閉線段起始點
        lineSource.SetPoint1(self.poly_data.GetPoint(self.dijkstra_path_arr[-1]))
        print(f"self.dijkstra_path_arr[-1]: {self.dijkstra_path_arr[-1]}")
        # 將self.pathList取德第一個點作為封閉線段結束點
        lineSource.SetPoint2(self.poly_data.GetPoint(self.pathList[0]))
        print(f"self.dijkstra_path_arr[0]: {self.pathList[0]}")
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
        interactor.GetRenderWindow().Render()

    # 清除選取輔助樣式
    def unRenderAllSelectors(self,renderer,interactor):
        for actor in self.sphereActors:
            renderer.RemoveActor(actor)
        self.sphereActors.clear()
        for actor in self.lineActors:
            renderer.RemoveActor(actor)
        self.pathList = []
        self.meshNumList = []
        self.dijkstra_path_arr = []
        self.lineActors.clear()
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