import vtk
'''
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
    threshold.SetLowerThreshold(0.4)
    threshold.SetUpperThreshold(0.5)
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
'''
def get_inlay_surface(hole_teeth, repair_teeth):
    distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SetInputData(0, repair_teeth)
    distance_filter.SetInputData(1, hole_teeth)
    distance_filter.SignedDistanceOff()  # 只取絕對值
    distance_filter.Update()

    distance_data = distance_filter.GetOutput()
    distance_data.GetPointData().SetActiveScalars("Distance")  # ✅ 確保 mapper 使用 distance scalar

    # ===== 建立 LookupTable（藍 → 綠 → 黃 → 紅）=====
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.Build()


    # ========== 可視化距離 Scalar 整體（非 threshold 後） ==========
    full_mapper = vtk.vtkPolyDataMapper()
    full_mapper.SetInputData(distance_data)
    full_mapper.SetScalarRange(0.0, 1.0)  # ✅ 調整最大值依你的 mesh
    full_mapper.SetLookupTable(lut)
    full_mapper.SetScalarModeToUsePointData()

    full_actor = vtk.vtkActor()
    full_actor.SetMapper(full_mapper)
    full_actor.GetProperty().SetOpacity(1.0)  # 有色區顯示距離

    # ========== 抽取 patch ==========
    threshold = vtk.vtkThreshold()
    threshold.SetInputData(distance_data)
    threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
    threshold.SetLowerThreshold(0.4)
    threshold.SetUpperThreshold(0.5)
    threshold.Update()

    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(threshold.GetOutputPort())
    geometry_filter.Update()
    contact_patch = geometry_filter.GetOutput()

    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(contact_patch)
    connectivity_filter.SetExtractionModeToLargestRegion()
    connectivity_filter.Update()
    main_patch = connectivity_filter.GetOutput()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(main_patch)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(0.0, 1.0)
    mapper.SetScalarModeToUsePointData()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(1.0)

    # 渲染
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.AddActor(full_actor)  # 整體距離視覺化
    renderer.AddActor(actor)       # threshold patch
    renderer.SetBackground(1.0, 1.0, 1.0)
    render_window.SetSize(800, 600)
    render_window.Render()
    interactor.Start()
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
reader_repair.SetFileName("resources/repair_teeth_align/repair_teeth_align_0109_down.stl")
reader_repair.Update()
# 取得polydata
hole_polydata = reader_hole.GetOutput()
repair_polydata = reader_repair.GetOutput()
get_inlay_surface(hole_polydata,repair_polydata)
