import vtk
# 顯示模型
def render_model(renderer, vtk_widget, poly_data):
    renderer.RemoveAllViewProps()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer.AddActor(actor)
    renderer.ResetCamera()

    vtk_widget.GetRenderWindow().Render()

    return actor