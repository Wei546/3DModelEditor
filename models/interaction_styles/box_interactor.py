from vtkmodules.vtkInteractionStyle import vtkInteractorStyleRubberBand3D
from models.visible_select_func import VisibleSlt
import vtk
class BoxInteractor(vtkInteractorStyleRubberBand3D):
    def __init__(self,poly_data,interactor,renderer):
        super().__init__()
        self.renderer = renderer
        self.poly_data = poly_data
        self.SetInteractor(interactor)
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.selection_frustum = None
        self.extract_geometry = None
        self.selected_poly_data = None
        self.end_position = [0,0]
        self.start_position = [0,0]
        self.boxArea = vtk.vtkAreaPicker()
        self.colorActors = []
        self.RemoveObservers("LeftButtonPressEvent")
        self.RemoveObservers("LeftButtonUpEvent")
        self.AddObserver("RightButtonPressEvent", self.onRightButtonPress)
        self.AddObserver("RightButtonReleaseEvent", self.onRightButtonUp)
    
    def onRightButtonPress(self, obj, event):
        self.onLeftButtonPress(obj, event)
    def onRightButtonUp(self, obj, event):
        self.onLeftButtonUp(obj, event)

    def onLeftButtonPress(self, obj, event):
        start_coord = self.GetInteractor().GetEventPosition()
        self.start_position = [start_coord[0], start_coord[1]]
        print(f"start_position:{self.start_position}")
        print(f"enter to box interactor button down")
    def onLeftButtonUp(self, obj, event):
        end_coord = self.GetInteractor().GetEventPosition()
        self.end_position = [end_coord[0], end_coord[1]]
        print(f"end_position:{self.end_position}")
        super().OnLeftButtonUp()
    def boxSelectArea(self):
        self.boxArea.AreaPick(self.start_position[0], self.start_position[1], self.end_position[0], self.end_position[1], self.renderer)
        self.selection_frustum = self.boxArea.GetFrustum()


        self.extract_geometry = vtk.vtkExtractGeometry()
        self.extract_geometry.SetInputData(self.poly_data)
        self.extract_geometry.SetImplicitFunction(self.selection_frustum)
        self.extract_geometry.Update()

        self.selected_poly_data = self.extract_geometry.GetOutput()
        print(f"Get selected poly data cells:{self.selected_poly_data.GetNumberOfCells()}")

        self.geometry_filter = vtk.vtkGeometryFilter()
        self.geometry_filter.SetInputData(self.selected_poly_data)
        self.geometry_filter.Update()
        return self.geometry_filter.GetOutput()

        
    def show_all_area(self,input_model):
        self.mapper.SetInputData(input_model)
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 設定紅色

        self.colorActors.append(self.actor)
        self.renderer.AddActor(self.actor)
        self.GetInteractor().GetRenderWindow().Render()
    # 移除染色資料
    def unRenderAllSelectors(self):
        for colorActor in self.colorActors:
            self.renderer.RemoveActor(colorActor)
        self.GetInteractor().GetRenderWindow().Render()

    def show_on_visible(self):
        print(f"show on process and coordinate:{self.start_position},{self.end_position}")
        self.visibleSlt = VisibleSlt(self.renderer,self.GetInteractor())
        self.visible_poly_data = self.visibleSlt.boxOnlyForVisible(self.start_position,self.end_position,self.poly_data)



