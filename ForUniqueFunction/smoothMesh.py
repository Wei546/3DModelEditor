import vtk

# 檔案路徑
file_path = "resources/test_input/teeth_ply_open.ply"
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
# 平滑模型
smooth_fillter = vtk.vtkSmoothPolyDataFilter()
smooth_fillter.SetInputConnection(reader.GetOutputPort())
smooth_fillter.SetNumberOfIterations(0)
smooth_fillter.Update()
poly_data = smooth_fillter.GetOutput()
# 設定平滑模型的輸入

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
