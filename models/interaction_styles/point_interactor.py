import vtk
from vtk import vtkInteractorStyleTrackballCamera

class PointInteractor(vtkInteractorStyleTrackballCamera):
    # poly_data是輸入的3D模型
    def __init__(self,poly_data,interactor,renderer):
        super().__init__()
        self.renderer = renderer
        self.SetInteractor(interactor)
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
        # 回傳給visible_select_func的3D座標
        self.pick3DCoord = vtk.vtkCellPicker()
        # 穿透模式
        self.throughBtnMode = False
        # 第一個參數是事件名稱，第二個參數是事件的回調函數
    # 滑鼠左鍵按下；interactor是HightlightInteractorStyle的互動器，renderer是HightlightInteractorStyle的渲染器
    def onLeftButtonDown(self,obj,event):
        # 初始化點選位置座標
        clickPos = self.GetInteractor().GetEventPosition()
        # 初始化靠近選取位置的網格
        picker = vtk.vtkCellPicker()
        # 選取位置轉成3D座標
        picker.Pick(clickPos[0],clickPos[1],0,self.renderer)
        # 給予pick3DCoord資料
        self.pick3DCoord.Pick(clickPos[0],clickPos[1],0,self.renderer)
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
            self.renderer.AddActor(self.sphereActor)
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
                '''
                combinedPoints = vtk.vtkPoints()
                self.combinedLine = vtk.vtkPolyLine()
                self.combinedLine.GetPointIds().SetNumberOfIds(self.idList.GetNumberOfIds())
                self.total_point_counter = 0
                for i in range(self.idList.GetNumberOfIds()):
                    point_id = self.idList.GetId(i)
                    point_coord = self.poly_data.GetPoint(point_id)
                    if len(self.meshNumList) > 1 and i == 0:
                        self.total_point_counter += self.meshNumList[-2]
                    combinedPoints.InsertNextPoint(point_coord)
                    self.combinedLine.GetPointIds().InsertNextId(i)
                    self.total_point_counter += 1
                cells = vtk.vtkCellArray()
                cells.InsertNextCell(self.combinedLine)
                self.combinedPolyData = vtk.vtkPolyData()
                self.combinedPolyData.SetPoints(combinedPoints)
                self.combinedPolyData.SetLines(cells)

                # 視覺化最短路徑
                splineFilter = vtk.vtkSplineFilter()
                splineFilter.SetInputData(self.combinedPolyData)
                splineFilter.SetNumberOfSubdivisions(10)
                splineFilter.Update()

                # 將線段資料轉換成平面圖形資料
                lineMapper = vtk.vtkPolyDataMapper()
                # SetInputConnection()動態傳遞點選的線段；GetOutputPort()取得線段
                lineMapper.SetInputConnection(splineFilter.GetOutputPort())
                # 將線段資料轉換成視覺化物件
                self.lineActor = vtk.vtkActor()
                # actor放入mapper，轉換成適合渲染的物件
                self.lineActor.SetMapper(lineMapper)
                # 設定線段顏色為紅色
                self.lineActor.GetProperty().SetColor(1.0, 0.0, 0.0)
                # 設定線段寬度
                self.lineActor.GetProperty().SetLineWidth(2)
                # 將actor放入渲染器
                self.renderer.AddActor(self.lineActor)
                '''
                

                
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
                    self.renderer.AddActor(self.lineActor)
                    # undo、消除的列表
                    self.lineActors.append(self.lineActor)
                    # 添加所有最短路徑的點到dijkstra_path_arr
                    self.dijkstra_path_arr.append(self.idList.GetId(i))
            # 去除重複的最短路徑點
            self.dijkstra_path_arr=list(set(self.dijkstra_path_arr))
            print(f" original dijkstra_path_arr: {self.dijkstra_path_arr}")
            # 渲染最短路徑
            self.GetInteractor().GetRenderWindow().Render()

    # 封閉選取範圍；interactor是HightlightInteractorStyle的互動器，renderer是HightlightInteractorStyle的渲染器
    def closeArea(self):
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
            self.renderer.AddActor(self.lineActor)
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
        self.GetInteractor().GetRenderWindow().Render()

    # 清除選取輔助樣式；interactor是HightlightInteractorStyle的互動器，renderer是HightlightInteractorStyle的渲染器
    def unRenderAllSelectors(self):
        # 清除所有視覺化點
        for actor in self.sphereActors:
            # 移除actor
            self.renderer.RemoveActor(actor)
        # 清除所有視覺化線段
        for actor in self.lineActors:
            # 移除actor
            self.renderer.RemoveActor(actor)
        # 移除封閉線段視覺化線條
        for actor in self.closeLineActors:
            # 移除actor
            self.renderer.RemoveActor(actor)
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
        # 渲染畫面
        self.GetInteractor().GetRenderWindow().Render()
    # 取消上一步選取；先回收視覺化點->最短路徑實際線段->最短路徑視覺化線段->再清除存放實際線段的列表
    def undo(self):
        # undo上一步點的視覺化
        last_sphere = self.sphereActors.pop()
        # 清除視覺化點
        self.renderer.RemoveActor(last_sphere)
        # 存放undo視覺化點
        self.redoSphereActors.append(last_sphere)
        # undo儲存實際點選列表
        last_path_point = self.pathList.pop()
        # 存放undo點選列表
        self.redoPathList.append(last_path_point)
        # 因為要更新點undo的畫面，這裡重新渲染畫面
        self.GetInteractor().GetRenderWindow().Render()
        # undo儲存實際線段數量，沒有實際線段，不做事情
        if len(self.meshNumList) == 0:
            return
        # 一段段回收最短路徑的線段，避免有落單的沒有放到redo
        for i in range(self.meshNumList[-1]):
            # 避免實際線段超出範圍
            if i == self.meshNumList[-1] - 1:
                break
            # undo視覺化線段
            last_line = self.lineActors.pop()
            # 清除視覺化線段
            self.renderer.RemoveActor(last_line)
            # 把undo線段放回redo
            self.redoLineActors.append(last_line)
        # 抽出最短路徑實際線段儲存的資料
        last_mesh_num = self.meshNumList.pop()
        # 存放undo實際線段數量
        self.redoMeshNumList.append(last_mesh_num)
        # 更新畫面
        self.GetInteractor().GetRenderWindow().Render()
    # 還原選取；先回收視覺化點->最短路徑實際線段->最短路徑視覺化線段->再清除存放實際線段的列表
    def redo(self):
        # redo視覺化點
        redo_sphere = self.redoSphereActors.pop()
        # 渲染器放入視覺化點
        self.renderer.AddActor(redo_sphere)
        # 把視覺化點放回原本的列表
        self.sphereActors.append(redo_sphere)
        # redo儲存實際點選列表
        redo_path_point = self.redoPathList.pop()
        # 把undo點選列表放回原本的列表
        self.pathList.append(redo_path_point)
        # 重新更新畫面，因為要還原視覺化點
        self.GetInteractor().GetRenderWindow().Render()
        # redo儲存實際線段數量
        if len(self.redoMeshNumList) == 0:
            return
        # 迭代每一筆最短路徑的資料
        for i in range(self.redoMeshNumList[-1]):
            if i == self.redoMeshNumList[-1] - 1:
                break
            # redo視覺化線段
            redo_line = self.redoLineActors.pop()
            # 重新渲染視覺化線段資料
            self.renderer.AddActor(redo_line)
            # 添加回原本的列表
            self.lineActors.append(redo_line)
        # redo實際線段數量
        redo_mesh_num = self.redoMeshNumList.pop()
        # 添加回原本的列表
        self.meshNumList.append(redo_mesh_num)
        # 重新更新畫面
        self.GetInteractor().GetRenderWindow().Render()
    # 穿透選取模式
    def mode(self,btnStatus):
        self.throughBtnMode = btnStatus