import vtk
def align_models_icp(source_polydata, target_polydata):
    """
    使用 VTK 的 ICP 對齊 source 到 target
    :param source_polydata: 要移動的模型（修復牙）
    :param target_polydata: 目標模型（缺陷牙）
    :return: 對齊後的 polydata
    """
    # 建立 ICP 轉換器
    icp = vtk.vtkIterativeClosestPointTransform()
    icp.SetSource(source_polydata)
    icp.SetTarget(target_polydata)
    icp.GetLandmarkTransform().SetModeToRigidBody()
    icp.SetMaximumNumberOfIterations(100)
    icp.SetMaximumMeanDistance(0.00001)
    icp.StartByMatchingCentroidsOn()
    icp.Modified()
    icp.Update()

    # 套用 ICP 轉換結果到 source
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(source_polydata)
    transform_filter.SetTransform(icp)
    transform_filter.Update()

    # 回傳對齊後的模型
    aligned_polydata = vtk.vtkPolyData()
    aligned_polydata.DeepCopy(transform_filter.GetOutput())
    # 輸出對齊後的模型與目標模型合併
    aligned_polydata_append = vtk.vtkAppendPolyData()
    aligned_polydata_append.AddInputData(transform_filter.GetOutput())
    aligned_polydata_append.AddInputData(target_polydata)
    aligned_polydata_append.Update()
    writer = vtk.vtkSTLWriter()
    writer.SetFileName("aligned_model_append.stl")
    writer.SetInputData(aligned_polydata_append.GetOutput())
    writer.SetFileTypeToBinary()
    writer.Write()
    writer_only_align = vtk.vtkSTLWriter()
    writer_only_align.SetFileName("repair_teeth_align_0109.stl")
    writer_only_align.SetInputData(aligned_polydata)
    writer_only_align.SetFileTypeToBinary()
    writer_only_align.Write()
    print("aligned_model_append.stl")
source_reader = vtk.vtkSTLReader()
source_reader.SetFileName("resources/repair_teeth_align/repair_teeth_align_0078.stl")
source_reader.Update()
target_reader = vtk.vtkSTLReader()
target_reader.SetFileName("resources/0078/data0078down.stl")
target_reader.Update()
source_polydata = source_reader.GetOutput()
target_polydata = target_reader.GetOutput()
align_models_icp(source_polydata, target_polydata)
    