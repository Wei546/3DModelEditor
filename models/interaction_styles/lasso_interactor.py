import vtk
from vtk import vtkInteractorStyleTrackballCamera
# 套索選取類別
class LassoInteractor(vtkInteractorStyleTrackballCamera):
    def __init__(self,poly_data,interactor,renderer):
        super().__init__()
        self.renderer = renderer
        self.SetInteractor(interactor)
        # 初始化輸入資料，用於後續計算在物體表面選取的點
        self.poly_data = poly_data
        # 初始化選取範圍資料
        self.picker = vtk.vtkCellPicker()
        # 選取範圍資料
        self.select_append = vtk.vtkAppendPolyData()
        # 用於處理undo、redo、刪除網格後清除資料功能；儲存點選的所有點
        self.selection_point = vtk.vtkPoints()
        # 儲存想要刪除的部份
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
    # 滑鼠左鍵按下
    def onLeftButtonDown(self, obj, event):
        # 點選位置
        clickPos = self.GetInteractor().GetEventPosition()
        # 選取位置轉成3D座標
        self.picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
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
        # 更新視覺化套索線段
        self.select_append.Update()
        # boundary列表儲存視覺化套索線段資料
        self.boundary = self.select_append.GetOutput()     
        # 實體化選取範圍要放入的映射器變數
        boundaryMapper = vtk.vtkPolyDataMapper()
        # 映射器放入boundary列表
        boundaryMapper.SetInputData(self.boundary)
        # 選取範圍要放入的渲染物件變數
        self.boundaryActor = vtk.vtkActor()
        # 渲染物件放入映射器
        self.boundaryActor.SetMapper(boundaryMapper)
        # 設定選取範圍的線寬
        self.boundaryActor.GetProperty().SetLineWidth(2)
        # 設定選取範圍線段的顏色為紅色
        self.boundaryActor.GetProperty().SetColor(1, 0, 0)
        # 視覺化線段套索要清除效果放入的列表
        self.boundaryActors.append(self.boundaryActor)
        # 渲染器放入視覺化線段套索
        self.renderer.AddActor(self.boundaryActor)
        # 小於3個點不做事
        if len(self.pickpointId) < 3:
            return
        # 選取範圍資料
        self.loop.SetLoop(self.boundary.GetPoints())
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()
        
    # 清除選取樣式、資料；render是HightLightInteractorStyle的渲染器，interactor是HightLightInteractorStyle的互動器
    def unRenderAllSelectors(self):
        # 視覺化線段套索要清除效果
        for actor in self.boundaryActors:
            # 移除渲染物件
            self.renderer.RemoveActor(actor)
        # 清除視覺化線段套索
        self.boundaryActors.clear()
        # 清除點選位置資料
        self.selection_point.Reset()
        # 清除存放最短路徑的列表的資料
        self.dijkstra_path.clear()
        # 清除點選位置的id的資料
        self.pickpointId.clear()
        # 清除選取範圍的資料
        self.select_append.RemoveAllInputs()
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()
    # 取消上一步選取；render是HightLightInteractorStyle的渲染器，interactor是HightLightInteractorStyle的互動器
    def undo(self):
        # 沒有選到點不做事
        if not self.pickpointId:
            return
        # undo點選位置
        last_pickpointId = self.pickpointId.pop()
        # 存放undo點選位置，用於redo
        self.redoPickpointId.append(last_pickpointId)
        # undo最短路徑
        if self.dijkstra_path:
            # 避免最短路徑的資料重複使用，使用copy方法把資料放入redo的列表
            self.redoDijkstraPath.append(self.dijkstra_path.copy())
            # 清除上一步最短路徑的資料
            self.dijkstra_path.clear()
        # undo視覺化線段
        if self.boundaryActors:
            # undo視覺化線段，存放到redo的列表
            last_actor = self.boundaryActors.pop()
            # 存放undo視覺化線段，用於redo
            self.redoBoundaryActors.append(last_actor)
            # 移除undo視覺化線段
            self.renderer.RemoveActor(last_actor)
        # 清除點選泛維資料
        self.selection_point.Reset()
        # 清除選取範圍資料
        self.select_append.RemoveAllInputs()
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()
    # 還原選取
    def redo(self):
        # redo點選位置
        if self.redoPickpointId:
            # 拿出undo的點選位置資料
            redo_pickpointId = self.redoPickpointId.pop()
            # 將undo資料添加回點選位置列表
            self.pickpointId.append(redo_pickpointId)
        # redo最短路徑
        if self.redoDijkstraPath:
            # 拿出undo的最短路徑資料
            redo_dijkstra_path = self.redoDijkstraPath.pop()
            # 將undo資料添加回最短路徑列表
            self.dijkstra_path = redo_dijkstra_path
        # redo視覺化線段
        if self.redoBoundaryActors:
            # 拿出undo的視覺化線段資料
            redo_boundary_actor = self.redoBoundaryActors.pop()
            # 將undo資料添加回視覺化線段列表
            self.boundaryActors.append(redo_boundary_actor)
            # 渲染器放入視覺化線段
            self.renderer.AddActor(redo_boundary_actor)
        # 更新視窗
        self.GetInteractor().GetRenderWindow().Render()