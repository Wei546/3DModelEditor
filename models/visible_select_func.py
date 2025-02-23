import vtk
import numpy as np
class VisibleSlt:
    def __init__(self,renderer,interactor):
        self.renderer = renderer
        self.interactor = interactor
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
        return
    def selectVisible(self,startCoord,endCoord):
        # Debug輸入座標
        print("Start Coord:", startCoord)
        print("End Coord:", endCoord)

        # 取得起始與結束座標
        selectXStart, selectYStart = startCoord
        selectXEnd, selectYEnd = endCoord

        print(f"selectXStart: {selectXStart}")
        print(f"selectYStart: {selectYStart}")
        print(f"selectXEnd: {selectXEnd}")
        print(f"selectYEnd: {selectYEnd}")

        # 設定 hardware selector
        hardware_selector = vtk.vtkHardwareSelector()
        hardware_selector.SetFieldAssociation(vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS)  # 選取可視區域
        hardware_selector.SetRenderer(self.renderer)
        print("Hardware Selector:", hardware_selector)
        print(f"hardware input:{hardware_selector.SetArea(selectXStart, selectYStart, selectXEnd, selectYEnd)}")
        print(f"{hardware_selector.GetArea()}")
        self.renderer
        # 開始選取
        hardware_selector.Select()
        hardware_selector.SetArea(selectXStart, selectYStart, selectXEnd, selectYEnd)
        self.interactor
        

        

  
            
        