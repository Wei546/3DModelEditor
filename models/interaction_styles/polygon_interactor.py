import vtk

class PolygonInteractor(vtk.vtkInteractorStyleDrawPolygon):
    def __init__(self, poly_data):
        self.poly_data = poly_data
        self.renderer = None  # 預留欄位
        self.RemoveObservers("LeftButtonPressEvent")
        self.RemoveObservers("LeftButtonReleaseEvent")
        self.RemoveObservers("RightButtonPressEvent")
        self.RemoveObservers("RightButtonReleaseEvent")
        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release)
        self.AddObserver("RightButtonPressEvent", self.on_right_button_press)
        self.AddObserver("RightButtonReleaseEvent", self.on_right_button_release)

    def set_renderer(self, renderer):
        self.renderer = renderer

    def on_left_button_press(self, obj, event):
        super().OnLeftButtonDown()

    def on_left_button_release(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition()
        print("Left button released at:", click_pos)
        picker = vtk.vtkPropPicker()
        picker.Pick(click_pos[0], click_pos[1], 0, self.GetDefaultRenderer())
        world_pos = picker.GetPickPosition()
        print("World coordinates:", world_pos)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.poly_data)
        mapper.Update()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 1)

        self.renderer.AddActor(actor)
        self.GetInteractor().GetRenderWindow().Render()

    def on_right_button_press(self, obj, event):
        super().OnRightButtonDown()

    def on_right_button_release(self, obj, event):
        super().OnRightButtonUp()


# === 主程式部分 ===
reader = vtk.vtkSTLReader()
reader.SetFileName("resources/0075/ai_data0075down_smooth.stl")
reader.Update()

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# 安裝自定義互動器樣式
style = PolygonInteractor(reader.GetOutput())
style.set_renderer(renderer)
style.SetDefaultRenderer(renderer)
interactor.SetInteractorStyle(style)

# 初始顯示原始模型
initial_mapper = vtk.vtkPolyDataMapper()
initial_mapper.SetInputData(reader.GetOutput())
initial_actor = vtk.vtkActor()
initial_actor.SetMapper(initial_mapper)
renderer.AddActor(initial_actor)

renderWindow.Render()
interactor.Start()
