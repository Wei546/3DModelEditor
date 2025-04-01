import vtk
def get_inlay_surface(hole_teeth, repair_teeth):
    distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SetInputData(0, repair_teeth)
    distance_filter.SetInputData(1, hole_teeth)
    distance_filter.SignedDistanceOff()  # 只取絕對值
    distance_filter.Update()

    # 取得距離資料
    distance_data = distance_filter.GetOutput()
    distance_array = distance_data.GetPointData().GetScalars()
    max_distance = distance_array.GetRange()[1]
    min_distance = distance_array.GetRange()[0]
    print("最大距離:", max_distance)
    print("最小距離:", min_distance)

    # 選取距離小於一定閾值的 patch（可手動調整）
    threshold = vtk.vtkThreshold()
    threshold.SetInputData(distance_data)

    threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
    threshold.SetLowerThreshold(0.4)
    threshold.SetUpperThreshold(2)

    
    '''
    threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_LOWER)
    threshold.SetLowerThreshold(0.4)
    threshold.Update()
    '''
    

    # 將 patch 轉成 PolyData
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(threshold.GetOutputPort())
    geometry_filter.Update()
    contact_patch = geometry_filter.GetOutput()

    # 計算面積
    mass = vtk.vtkMassProperties()
    mass.SetInputData(contact_patch)
    mass.Update()

    # === 🔵 自動 scalar mapping 用顏色表示距離 ===
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(contact_patch)
    mapper.SetScalarRange(min_distance, max_distance)  # 顯示 scalar 顏色
    mapper.ScalarVisibilityOn()

    # 建立 actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(0.9)

    # === 🟦 顏色圖例（scalar bar） ===
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    scalar_bar.SetTitle("Distance")
    scalar_bar.SetNumberOfLabels(5)
    scalar_bar.UnconstrainedFontSizeOn()

    # === 渲染視窗 ===
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    renderer.AddActor(actor)
    renderer.AddActor2D(scalar_bar)
    renderer.SetBackground(1.0, 1.0, 1.0)  # 白底
    render_window.SetSize(800, 600)

    render_window.Render()
    render_window_interactor.Start()

    print("凹陷表面面積:", mass.GetSurfaceArea())

# 讀取STL檔案
reader_hole = vtk.vtkSTLReader()
reader_hole.SetFileName("resources/0075/data0075down.stl")
reader_hole.Update()
reader_repair = vtk.vtkSTLReader()
reader_repair.SetFileName("aligned_model_only_align.stl")
reader_repair.Update()
# 取得polydata
hole_polydata = reader_hole.GetOutput()
repair_polydata = reader_repair.GetOutput()
get_inlay_surface(hole_polydata,repair_polydata)
