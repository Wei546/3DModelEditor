import vtk
# 顯示模型
def render_model(renderer, vtk_widget, poly_data):
    # 清除所有的view props
    renderer.RemoveAllViewProps()
    # 建立映射器
    mapper = vtk.vtkPolyDataMapper()
    # 設定輸入資料
    mapper.SetInputData(poly_data)
    # 建立渲染器
    actor = vtk.vtkActor()
    # 渲染器放入映射器
    actor.SetMapper(mapper)
    # 渲染器放入render
    renderer.AddActor(actor)
    # 重置相機
    renderer.ResetCamera()
    # 更新視窗
    vtk_widget.GetRenderWindow().Render()
    # 回傳渲染物件
    return actor