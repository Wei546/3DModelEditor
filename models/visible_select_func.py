import vtk
import numpy as np
class VisibleSlt:
    def __init__(self):
        return
    def checkWindowMode(self, renderer):
         # 檢查render是否為正交視角
        if renderer.GetActiveCamera().GetParallelProjection():
            print("Parallel Projection")
        else:
            print("Perspective Projection")
    # 設定render為正交視角
    def projectToParallel(self, renderer):
        # 取得當前視角
        camera = renderer.GetActiveCamera()
        # 設定render為正交視角
        camera.ParallelProjectionOn()
        # 3D物體固定大小
        camera.SetParallelScale(1)
        # 渲染為正交視角
        renderer.SetActiveCamera(camera)
    def projectToPerspective(self, renderer):
        # 取得當前視角
        camera = renderer.GetActiveCamera()
        # 設定render為透視視角
        camera.ParallelProjectionOff()
        # 渲染為透視視角
        renderer.SetActiveCamera(camera)
    def checkDepth(self,renderer):
        # 創建新的視窗
        render_window = renderer.GetRenderWindow()
        # 將舊的渲染器加入到新的視窗
        render_window.AddRenderer(renderer)
        # 渲染
        render_window.Render()
        # 創建深度測試
        depth_buffer = vtk.vtkFloatArray()
        # 取得深度測試
        render_window.GetZbufferData(0, 0, 100, 100, depth_buffer)
        # 轉換為numpy
        depth_buffer = np.array(depth_buffer)
        # 檢查深度
        print("Depth Buffer:\n", depth_buffer)
    def selectVisible(self,startCoord,endCoord,renderer):
        # debug輸入座標
        print("Start Coord:",startCoord)
        print("End Coord:",endCoord)
        # 實體化hardware selector
        hardware_selector = vtk.vtkHardwareSelector()
        # 設定渲染器
        hardware_selector.SetRenderer(renderer)
        # 選擇範圍
        hardware_selector.SetFieldAssociation(vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS)
        # 取得起始座標
        selectXStart = startCoord[0]
        selectYStart = startCoord[1]
        # 取得結束座標
        selectXEnd = endCoord[0]
        selectYEnd = endCoord[1] 
        print(f"selectXStart:{selectXStart}")
        print(f"selectYStart:{selectYStart}")
        print(f"selectXEnd:{selectXEnd}")
        print(f"selectYEnd:{selectYEnd}")
        
        # debug有無進入selectVisible
        print("Selecting...")
        # 選取hardware_selectorv選取範圍
        hardware_selector.SetArea(selectXStart,selectYStart,selectXEnd,selectYEnd)
        # hardware選取
        res =  hardware_selector.Select()
        # 取得hardware節點數
        num_nodes = res.GetNumberOfNodes()
        # 印出hardware_selector的node的列表
        print(f"hardware_list:{num_nodes.GetSelectionList().tolist}")

        

  
            
        