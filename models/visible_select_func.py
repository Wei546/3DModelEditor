import vtk
import numpy as np
from models.stitches_slt_btn_func import Stitching
class VisibleSlt:
    def __init__(self,renderer,interactor):
        self.renderer = renderer
        self.interactor = interactor
        self.stitching = Stitching(self.renderer,self.interactor)
        return
    def boxOnlyForVisible(self,startCoord,endCoord,poly_data):
        # 取得起始與結束座標
        selectXStart, selectYStart = startCoord
        selectXEnd, selectYEnd = endCoord

        # 選取當前能看見的範圍，不會選到背面被遮住的地方
        hardware_selector = vtk.vtkHardwareSelector()
        # 將選取的物件設定為網格
        hardware_selector.SetFieldAssociation(vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS)
        # 把選取範圍加入渲染器，後續才能使用GetNode
        hardware_selector.SetRenderer(self.renderer)
        # 小的x座標是起始座標，放第一個參數；小的y座標是起始座標，放第二個參數；大的x座標是結束座標，放第三個參數；大的y座標是結束座標，放第四個參數
        if selectXStart < selectXEnd and selectYStart < selectYEnd:
            hardware_selector.SetArea(selectXStart, selectYStart, selectXEnd, selectYEnd)
        elif selectXStart < selectXEnd and selectYStart > selectYEnd:
            hardware_selector.SetArea(selectXStart, selectYEnd, selectXEnd, selectYStart)
        elif selectXStart > selectXEnd and selectYStart < selectYEnd:
            hardware_selector.SetArea(selectXEnd, selectYStart, selectXStart, selectYEnd)
        else:
            hardware_selector.SetArea(selectXEnd, selectYEnd, selectXStart, selectYStart)
        # 取得選取的物件
        selection = hardware_selector.Select()
        # 在vtkHardwareSelector類別取得可以拿到選擇網格數量的屬性
        selectionNode = selection.GetNode(0)
        # 取得選取的網格數量的列表
        selectionList = selectionNode.GetSelectionList()
        colors = poly_data.GetCellData().GetScalars()
        print(f"visible select func:{selectionList}")

        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)  # RGB
        colors.SetNumberOfTuples(poly_data.GetNumberOfCells())
        poly_data.GetCellData().SetScalars(colors)
        for i in range(poly_data.GetNumberOfCells()):
            colors.SetTuple(i, [255, 255, 255])
        poly_data.GetCellData().SetScalars(colors)
        for i in range(selectionList.GetNumberOfTuples()):
            cell_id = selectionList.GetValue(i)  # 這裡使用 GetValue(i) 獲取網格 ID
            colors.SetTuple(cell_id, [255, 0, 0])
        poly_data.GetCellData().SetScalars(colors)
        self.clipped_data = self.stitching.stitching_func(selectionList,poly_data)
    def pointOnlyForVisible(self,pickCoord):
        print(f"entering to visible select func pickCoord:{pickCoord}")
        return
    def process_stitching(self):
        self.stitching.boundary_stitching(self.clipped_data)
        




        

  
            
        