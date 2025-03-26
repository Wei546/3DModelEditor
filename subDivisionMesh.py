import vtk

# 檔案路徑
file_path = "resources/test_input/teeth_ply_close.ply"
extension = file_path.split(".")[-1].lower()
if extension == "ply":
    # 實體化讀取ply的類別
    reader = vtk.vtkPLYReader()
elif extension == "obj":
    # 實體化讀取obj的類別
    reader = vtk.vtkOBJReader()
elif extension == "stl":
    # 實體化讀取stl的類別
    reader = vtk.vtkSTLReader()
elif extension == "vtp":
    # 實體化讀取vtp的類別
    reader = vtk.vtkXMLPolyDataReader()
else:
    raise ValueError("不支援的檔案格式.")
# reader設定檔案路徑
reader.SetFileName(file_path)
# 更新reader狀態
reader.Update()
# 取得reader的輸出
poly_data = reader.GetOutput()
# 細分模型
subdivision = vtk.vtkLoopSubdivisionFilter()
# 設定細分模型的輸入
subdivision.SetInputData(poly_data)
# cell的數量
print(f"poly_data cell數量: {poly_data.GetNumberOfCells()}")
# 設定細分模型的迭代次數
subdivision.SetNumberOfSubdivisions(5)
# 更新細分模型
subdivision.Update()
# 取得細分模型的輸出
poly_data = subdivision.GetOutput()
# 顯示輸入的模型
mapper = vtk.vtkPolyDataMapper()
# 將輸入的模型放入可視化的mapper
mapper.SetInputData(poly_data)
# 顯示輸入的模型
actor = vtk.vtkActor()
# 將mapper放入actor
actor.SetMapper(mapper)
# 實體化renderer
renderer = vtk.vtkRenderer()
# 將actor放入renderer
renderer.AddActor(actor)
# 實體化render window
render_window = vtk.vtkRenderWindow()
# 將renderer放入render window
render_window.AddRenderer(renderer)
# 實體化render window interactor

render_window_interactor = vtk.vtkRenderWindowInteractor()
# 將render window放入render window interactor
render_window_interactor.SetRenderWindow(render_window)
# 顯示視窗
render_window.Render()
# 持續顯示視窗
render_window_interactor.Start()
