import vtk
class PolygonInteractor(vtk.vtkInteractorStyleDrawPolygon):
    def __init__(self,poly_data):
        self.poly_data = poly_data

    def color_model(self):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.poly_data)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 1)
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderWindow)
        interactor.SetInteractorStyle(self)
        interactor.Initialize()
        interactor.Start()


input_reader = vtk.vtkSTLReader()
input_reader.SetFileName("resources/0075/ai_data0075down_smooth.stl")  # 替換成你的 STL 路徑
input_reader.Update()

selectMode = PolygonInteractor(input_reader.GetOutput())
selectMode.color_model()


