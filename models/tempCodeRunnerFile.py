import vtk

def get_inlay_surface(hole_teeth, repair_teeth):
    distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SetInputData(0, repair_teeth)
    distance_filter.SetInputData(1, hole_teeth)
    distance_filter.SignedDistanceOff()  # 只取絕對值
    distance_filter.Update()

    # 取得距離資料
    distance_data = distance_filter.GetOutput()

    # 選取距離小於一定閾值的 patch（可手動調整）
    threshold = vtk.vtkThreshold()
    threshold.SetInputData(distance_data)

    threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
    threshold.SetLowerThreshold(0.6)
    threshold.SetUpperThreshold(4)
    threshold.Update()


    # 將 patch 轉成 PolyData
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(threshold.GetOutputPort())
    geometry_filter.Update()
    contact_patch = geometry_filter.GetOutput()

    # 原色的面積
    full_mapper = vtk.vtkPolyDataMapper()
    full_mapper.SetInputData(repair_teeth)
    full_actor = vtk.vtkActor()
    full_actor.SetMapper(full_mapper)
    full_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    full_actor.GetProperty().SetOpacity(0.2)

    # 連通性過濾器，只保留最大區塊
    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(contact_patch)
    connectivity_filter.SetExtractionModeToLargestRegion()
    connectivity_filter.Update()
    main_patch = connectivity_filter.GetOutput()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(main_patch)

    # 建立 actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.1, 0.8, 0.1)
    actor.GetProperty().SetOpacity(0.9)

    # === 渲染視窗 ===
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    renderer.AddActor(full_actor)
    renderer.AddActor(actor)
    renderer.SetBackground(1.0, 1.0, 1.0)  # 白底
    render_window.SetSize(800, 600)

    render_window.Render()
    render_window_interactor.Start()
    # 儲存檔案
    save_file("contact_patch_surface.stl", main_patch)

def save_file(file_path, polydata):
    '''儲存檔案'''
    writer = vtk.vtkSTLWriter()
    writer.SetFileName(file_path)
    writer.SetInputData(polydata)
    writer.Write()
    print(f"Saved file as {file_path}")

# 讀取STL檔案
reader_hole = vtk.vtkSTLReader()
reader_hole.SetFileName("resources/00109/data0109down.stl")
reader_hole.Update()
reader_repair = vtk.vtkSTLReader()
reader_repair.SetFileName("resources/repair_teeth_align/repair_teeth_align_0109.stl")
reader_repair.Update()
# 取得polydata
hole_polydata = reader_hole.GetOutput()
repair_polydata = reader_repair.GetOutput()
get_inlay_surface(hole_polydata,repair_polydata)
