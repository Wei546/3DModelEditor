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
# 點選取類別
class PointInteractor(vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data):
        super().__init__()
        self.poly_data = poly_data
        self.dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
        self.dijkstra_path_point = vtk.vtkPoints()
        self.dijkstra.SetInputData(self.poly_data)
        self.idList = vtk.vtkIdList()
        self.sphereActors = []
        self.lineActors = []
        self.pathList = []
        self.meshNumList = []
        self.redoLineActors = []
        self.redoSphereActors = []
        self.redoPathList = []
        self.redoMeshNumList = []
        self.dijkstra_path_arr = []
        self.selectionPoints = vtk.vtkPoints()
        self.loop = vtk.vtkImplicitSelectionLoop()

        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown)
    # 滑鼠左鍵按下
    def onLeftButtonDown(self,obj,event,interactor,renderer):
        
        clickPos = interactor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.Pick(clickPos[0],clickPos[1],0,renderer)
        print(f"point coord: {self.poly_data.GetPoint(picker.GetPointId())}")
        if(picker.GetCellId() != -1):
            # 視覺化選取點
            self.pathList.append(picker.GetPointId())
            point_position = self.poly_data.GetPoint(picker.GetPointId())
            sphereSource = vtk.vtkSphereSource()
            sphereSource.SetCenter(point_position)
            sphereSource.SetRadius(0.02)
            sphereMapper = vtk.vtkPolyDataMapper()
            sphereMapper.SetInputConnection(sphereSource.GetOutputPort())
            self.sphereActor = vtk.vtkActor()
            self.sphereActor.SetMapper(sphereMapper)
            self.sphereActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            renderer.AddActor(self.sphereActor)
            self.sphereActors.append(self.sphereActor)
            print(f"pathList: {self.pathList}")
            # 求最小路徑
            if len(self.pathList) > 1:
                self.dijkstra.SetStartVertex(self.pathList[-2])
                self.dijkstra.SetEndVertex(self.pathList[-1])
                self.dijkstra.Update()

                self.idList = self.dijkstra.GetIdList()
                for i in range(self.idList.GetNumberOfIds()-1,-1,-1):
                    print(f"index{-i} point id: {self.idList.GetId(i)}|point coord: {self.poly_data.GetPoint(self.idList.GetId(i))}")
                self.meshNumList.append(self.idList.GetNumberOfIds())
                print(f"meshNumList: {self.meshNumList}")
                for i in range(self.idList.GetNumberOfIds() -1):
                    lineSource = vtk.vtkLineSource()
                    lineSource.SetPoint1(self.poly_data.GetPoint(self.idList.GetId(i)))
                    lineSource.SetPoint2(self.poly_data.GetPoint(self.idList.GetId(i+1)))
                    lineMapper = vtk.vtkPolyDataMapper()
                    lineMapper.SetInputConnection(lineSource.GetOutputPort())
                    self.lineActor = vtk.vtkActor()
                    self.lineActor.SetMapper(lineMapper)
                    self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                    renderer.AddActor(self.lineActor)
                    self.lineActors.append(self.lineActor)
                    interactor.GetRenderWindow().Render()
                    self.dijkstra_path_arr.append(self.idList.GetId(i))
            self.dijkstra_path_arr=list(set(self.dijkstra_path_arr))
            print(f"Here is the dijkstra_path_arr: {self.dijkstra_path_arr}")
            interactor.GetRenderWindow().Render()

    # 封閉選取範圍
    def closeArea(self,interactor,renderer):
        self.selectionPoints.SetNumberOfPoints(len(self.dijkstra_path_arr))
        for i in range(len(self.dijkstra_path_arr)):
            self.selectionPoints.SetPoint(i,self.poly_data.GetPoint(self.dijkstra_path_arr[i]))
        self.loop.SetLoop(self.selectionPoints)
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