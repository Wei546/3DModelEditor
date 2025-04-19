import numpy as np
import vtkmodules.all as vtk
from vtkmodules.util import numpy_support as nps
from vtkmodules.vtkCommonCore import vtkCommand
import  cv2

class LassoInteractor(vtk.vtkInteractorStyle): # 繼承vtkInteractorStyle類別
    class vtkInternal(object): # 內部類別，模擬C++的private變數；用來繪製多邊形
        def __init__(self,parent = None): # 初始化函式
            super().__init__() # 初始化父類別
            self._points = [] # 儲存點的列表
        @property # 裝飾器，讓points變數可以像屬性一樣使用
        def points(self): # 取得點的列表
            return np.array(self._points) # 將點的列表轉換為numpy陣列
        def AddPoint(self,x,y): # 新增點到列表中
            self._points.append([x,y])
        def GetPoint(self,index): # 取得指定索引的點
            if index < 0 or index > len(self._points)-1: # 檢查索引是否在範圍內
                return
            return np.array(self._points[index]) # 將點轉換為numpy陣列
        def GetNumberOfPoints(self): # 取得點的數量
            return len(self._points) # 返回點的數量
        def Clear(self): # 清除點的列表
            self._points = []
        def DrawPixels(self,StartPos,EndPos,pixels,size): # 繪製像素
            length = int(round(np.linalg.norm(StartPos-EndPos))) # 計算起始點和結束點之間的距離
            if length == 0: # 如果距離為0，則不繪製像素
                return # 不繪製
            x1,y1 = StartPos # 取得起始點的x和y座標
            x2,y2 = EndPos # 取得結束點的x和y座標
            x = [int(round(v)) for v in np.linspace(x1,x2,length)] # 計算x座標的範圍
            y = [int(round(v)) for v in np.linspace(y1,y2,length)] # 計算y座標的範圍
            indices = np.array([row*size[0]+col for col,row in zip(x,y)]) # 計算像素的索引
            pixels[indices] = 255 ^ pixels[indices] # 繪製像素，將像素值取反
            
    def __init__(self,poly_data,interactor,renderer): # 初始化函式，傳入poly_data和renderer
        super().__init__()
        self.interactor = interactor # 互動器
        self.renderer = renderer # 渲染器
        self.poly_data = poly_data  # 輸入資料
        self.setup() # 設定初始值
        self.AddObserver("MouseMoveEvent", self.onMouseMove) # 滑鼠移動事件
        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonDown) # 滑鼠左鍵按下事件
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonRelease) # 滑鼠左鍵放開事件
    def setup(self): #setup内變數為了保持與C++的風格一致，使用PascalCase命名
        self.Internal = self.vtkInternal() # 內部變數
        self.Moving = False # 設定移動狀態
        self.StartPosition = np.zeros(2,dtype=np.int32) #一維陣列，長度為2，型態為int32，模擬C++的std::vector<vtkVector2i>
        self.EndPosition = np.zeros(2,dtype=np.int32) #一維陣列，長度為2，型態為int32，模擬C++的std::vector<vtkVector2i>
        self.PixelArray = vtk.vtkUnsignedCharArray() # 儲存像素資料的陣列，模擬C++的vtkUnsignedCharArray
        self.DrawPolygonPixels = True # 設定是否繪製多邊形像素
    def interactorSetter(self,interactor): # 避免放在建構子直接初始化
        self.SetInteractor(interactor) # 設定互動器
    def DrawPolygon(self): # 繪製多邊形，透過滑鼠移動
        tmpPixelArray = vtk.vtkUnsignedCharArray() # 儲存像素資料的陣列，模擬C++的vtkUnsignedCharArray
        tmpPixelArray.DeepCopy(self.PixelArray) # 深度複製像素資料陣列
        pixels = nps.vtk_to_numpy(tmpPixelArray) # 將像素資料陣列轉換為numpy陣列
        renWin = self.GetInteractor().GetRenderWindow() # 取得渲染視窗
        size = renWin.GetSize() # 取得渲染視窗的大小

        for i in range(self.Internal.GetNumberOfPoints()-1): # 繪製多邊形的每一條邊
            StartPos = self.Internal.GetPoint(i) # 取得起始點
            EndPos = self.Internal.GetPoint(i+1) # 取得結束點
            self.Internal.DrawPixels(StartPos,EndPos,pixels,size) # 繪製像素

        if (self.Internal.GetNumberOfPoints() >= 3): # 如果點的數量大於等於3，則繪製多邊形
            StartPos = self.Internal.GetPoint(0) # 取得起始點
            EndPos = self.Internal.GetPoint(self.Internal.GetNumberOfPoints()-1) # 取得結束點
            self.Internal.DrawPixels(StartPos,EndPos,pixels,size) # 繪製像素

        renWin.SetPixelData(0,0,size[0]-1,size[1]-1,pixels.flatten(),0,0) # 設定渲染視窗的像素資料
        renWin.Frame() # 更新渲染視窗
    def DrawPolygonPixelsOn(self): # 繪製多邊形像素
        self.DrawPolygonPixels = True # 設定繪製多邊形像素的狀態
    def DrawPolygonPixelsOff(self): # 停止繪製多邊形像素
        self.DrawPolygonPixels = False # 設定停止繪製多邊形像素的狀態
    def GetPolygonPoints(self): # 取得多邊形的點
        return self.Internal.points # 返回點的列表
    def onLeftButtonDown(self, obj, event):
        print("enter lasso onLeftButtonDown")
        if self.GetInteractor() is None:
            return
        self.Moving = True # 設定移動狀態為True
        renWin = self.GetInteractor().GetRenderWindow() # 取得渲染視窗
        eventPos = self.GetInteractor().GetEventPosition() # 取得滑鼠點擊位置

        self.StartPosition[0] , self.StartPosition[1] = eventPos[0], eventPos[1] # 設定起始位置
        self.EndPosition =self.StartPosition # 設定結束位置

        self.PixelArray.Initialize() # 初始化像素資料陣列
        self.PixelArray.SetNumberOfComponents(3) # 設定像素資料陣列的維度為3
        size = renWin.GetSize() # 取得渲染視窗的大小
        self.PixelArray.SetNumberOfTuples(size[0]*size[1]) # 設定像素資料陣列的大小為渲染視窗的大小
        self.pixels = None # 儲存像素資料的變數

        renWin.GetPixelData(0,0,size[0]-1,size[1]-1,1,self.PixelArray,0) # 取得畫面的像素資料
        self.Internal.Clear() # 清除點的列表
        self.Internal.AddPoint(self.StartPosition[0], self.StartPosition[1]) # 新增起始點到列表中
        self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent) # 觸發開始互動事件
        
        super().OnLeftButtonDown() # 呼叫父類別的OnLeftButtonDown方法
        return
    def onLeftButtonRelease(self,obj, event):
        if self.GetInteractor() is None or not self.Moving:
            return
        if self.DrawPolygonPixels: #檢查是否繪製多邊形像素
            renWin = self.GetInteractor().GetRenderWindow() # 取得渲染視窗
            size = renWin.GetSize() # 取得渲染視窗的大小
            pixels = nps.vtk_to_numpy(self.PixelArray) # 將像素資料陣列轉換為numpy陣列
            renWin.SetPixelData(0,0,size[0]-1,size[1]-1,pixels.flatten(),0,0) # 設定渲染視窗的像素資料
            renWin.Frame() # 更新渲染視窗
        self.Moving = False # 設定移動狀態為False
        self.InvokeEvent(vtkCommand.SelectionChangedEvent) # 觸發選取變更事件
        self.InvokeEvent(vtkCommand.EndPickEvent) # 觸發開始互動事件
        self.InvokeEvent(vtkCommand.EndInteractionEvent) # 觸發結束互動事件
        self.getSelectArea(self.GetPolygonPoints()) # 取得選取範圍
        super().OnLeftButtonUp() # 呼叫父類別的OnLeftButtonUp方法
        return
    def onMouseMove(self,obj,event):
        if self.GetInteractor() is None or not self.Moving: 
            return
        eventPos = self.GetInteractor().GetEventPosition() # 取得滑鼠移動位置
        self.EndPosition[0], self.EndPosition[1] = eventPos[0], eventPos[1] # 設定結束位置
        size = self.GetInteractor().GetRenderWindow().GetSize() # 取得渲染視窗的大小
        if self.EndPosition[0] > size[0] -1: # 滑鼠x座標超過視窗範圍
            self.EndPosition[0] = size[0] -1  # 設定為視窗的最大x座標
        if self.EndPosition[0] < 0: # 滑鼠x座標小於0
            self.EndPosition[0] = 0 # 設定為0
        if self.EndPosition[1] > size[1] -1: # 滑鼠y座標超過視窗範圍
            self.EndPosition[1] = size[1] -1 # 設定為視窗的最大y座標
        if self.EndPosition[1] < 0: # 滑鼠y座標小於0
            self.EndPosition[1] = 0 # 設定為0
        lastPoint = self.Internal.GetPoint(self.Internal.GetNumberOfPoints()-1) # 取得最後一個點
        newPoint = self.EndPosition # 設定新的點
        if np.linalg.norm(lastPoint-newPoint) > 10: # 如果新的點和最後一個點的距離大於10，則新增點
            self.Internal.AddPoint(*newPoint) # 新增點到列表中，使用物件參考
            if self.DrawPolygonPixels:
                self.DrawPolygon() # 繪製多邊形
        
        super().OnMouseMove() # 呼叫父類別的OnMouseMove方法
        return
    def SetDrawPolygonPixels(self,drawPolygonPixels): # 設定是否繪製多邊形像素
        self.DrawPolygonPixels = drawPolygonPixels # 設定繪製多邊形像素的狀態
    def getSelectArea(self,select_point): #視覺化取得的點
       # 建立 mask
        w, h = self.renderer.GetRenderWindow().GetSize() # 取得視窗大小
        mask = np.zeros((h, w), dtype=np.uint8) # 建立一個全黑的mask
        cv2.fillPoly(mask, [np.array(select_point, dtype=np.int32)], 255) # 在mask上繪製多邊形，255表示白色

        coord = vtk.vtkCoordinate() # 建立 vtkCoordinate 物件
        coord.SetCoordinateSystemToWorld() # 設定座標系統為世界座標系統

        selected_ids = vtk.vtkIdTypeArray() # 儲存選取的點的ID
        selected_ids.SetNumberOfComponents(1) # 設定ID的維度為1

        for ptId in range(self.poly_data.GetNumberOfPoints()): # 迴圈遍歷所有點
            world_point = self.poly_data.GetPoint(ptId) # 取得點的世界座標
            coord.SetValue(world_point) # 設定座標系統為世界座標系統
            display_point = coord.GetComputedDisplayValue(self.renderer) # 取得顯示座標

            x, y = int(display_point[0]), int(display_point[1]) # 轉換為整數座標
            if 0 <= x < w and 0 <= y < h and mask[y, x] == 255: # 如果在mask範圍內
                selected_ids.InsertNextValue(ptId) # 新增ID到選取的ID列表
        self.setClipRange(selected_ids) # 設定選取範圍
       

    def setClipRange(self,selected_ids): # 設定選取範圍
        self.selected_ids = selected_ids
    def getClip(self):
        return self.selected_ids # 返回選取的輸出資料

        



        
'''
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
'''

