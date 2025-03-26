import vtk

# 讀取 .ply 檔案
reader = vtk.vtkPLYReader()
reader.SetFileName("resources/00109/data0109down.ply")
reader.Update()

# 將資料轉為 STL 格式
stlWriter = vtk.vtkSTLWriter()
stlWriter.SetInputConnection(reader.GetOutputPort())
stlWriter.SetFileName("resources/00109/data0109down.stl")
stlWriter.Write()
