import vtk
import numpy as np

def is_white_surface_facing_down(polydata):
    # 計算法向量的filter
    normals_filter = vtk.vtkPolyDataNormals()
    normals_filter.SetInputData(polydata)
    normals_filter.Update()
    # 取出所有頂點的法向量
    poly_with_normals = normals_filter.GetOutput()
    normals = poly_with_normals.GetPointData().GetNormals()

    # 把所有點的法向量相加，取平均法向量
    avg_normal = np.zeros(3)
    for i in range(normals.GetNumberOfTuples()):
        # 取得所有頂點法向量
        n = np.array(normals.GetTuple(i))
        # 加總
        avg_normal += n
    # 取平均
    avg_normal /= normals.GetNumberOfTuples()

    # 把平均法向量轉成長度為 1 的方向向量，這樣後面可以直接看數值判斷方向
    direction = avg_normal / np.linalg.norm(avg_normal)
    print("平均法向量方向:", direction)
    # 如果這個平均法向量在 Z 軸方向是負的，就代表白色面朝下
    return direction[2] < 0  
def is_white_surface_facing_inner(polydata, threshold=0.6):
    # 計算法向量的filter
    normals_filter = vtk.vtkPolyDataNormals()
    normals_filter.SetInputData(polydata)
    normals_filter.Update()
    # 取得計算好的法向量模型資料，polydata可使用GetCenter()、GetPoints()、GetPointData().GetNormals()取得資料
    polydata = normals_filter.GetOutput()
    # 取得模型中心、頂點、法向量
    center = np.array(polydata.GetCenter())
    points = polydata.GetPoints()
    normals = polydata.GetPointData().GetNormals()
    # 計數器，統計多少個法向量朝內
    inward_count = 0
    # 取得每個點的法向量，計算法向量與到中心的向量的內積
    for i in range(points.GetNumberOfPoints()):
        # 取得網格的點
        pt = np.array(points.GetPoint(i))
        # 取得該點的法向量
        n = np.array(normals.GetTuple(i))
        # 計算該點指向模型的法向量
        to_center = center - pt
        # 用內積判斷「法向量」跟「指向中心的方向」是否一致
        dot = np.dot(n, to_center)
        # 是正值，表示這個點是朝內的，也就是白色面朝內
        if dot > 0: 
            inward_count += 1
    # 計算朝內法向比例
    ratio = inward_count / points.GetNumberOfPoints()
    print(f"朝內法向比例：{ratio}")
    print(f"threshold: {threshold}")
    print(ratio > threshold)
    return ratio > threshold
# 讀取檔案
inlay_surface_file_path = "resources/inlay_slice/data0078/inlay_surface_0078.stl"
hole_file_path = "resources/inlay_slice/data0078/hole_0078.stl"
# 輸出檔案名稱
file_name = inlay_surface_file_path.split("/")[-1].split(".")[0]
# 讀取inlay的表面
inlay_surface_reader = vtk.vtkSTLReader()
inlay_surface_reader.SetFileName(inlay_surface_file_path)
inlay_surface_reader.Update()
# 讀取缺陷牙凹洞
hole_reader = vtk.vtkSTLReader()
hole_reader.SetFileName(hole_file_path)
hole_reader.Update()

# 計算inlay表面的法向量
inlay_surface_normal = vtk.vtkPolyDataNormals()
inlay_surface_normal.SetInputData(inlay_surface_reader.GetOutput())
# 確定白色表面是否朝下，有朝下就不用翻轉法向量
if is_white_surface_facing_down(inlay_surface_reader.GetOutput()):
    inlay_surface_normal.SetAutoOrientNormals(False)
    inlay_surface_normal.SetConsistency(True)
    inlay_surface_normal.SplittingOff()
    print("inlay不翻轉法向量")
else:
    inlay_surface_normal.SetAutoOrientNormals(True)
    inlay_surface_normal.SetConsistency(True)
    inlay_surface_normal.SplittingOff()
    print("inlay翻轉法向量")
inlay_surface_normal.Update()

# 計算缺陷牙表面的法向量
hole_normal = vtk.vtkPolyDataNormals()
hole_normal.SetInputData(hole_reader.GetOutput())
# 確定白色那面是否朝內，有朝內就不用翻轉法向量
if is_white_surface_facing_inner(hole_reader.GetOutput()):
    hole_normal.SetAutoOrientNormals(False)
    hole_normal.SetConsistency(True)
    hole_normal.SplittingOff()
    print("缺陷牙不翻轉法向量")
else:
    hole_normal.SetAutoOrientNormals(False)
    hole_normal.SetFlipNormals(True)
    hole_normal.SetConsistency(True)
    hole_normal.SplittingOff()
    print("缺陷牙翻轉法向量")
hole_normal.Update()


# 翻轉法向的嵌體表面
inlay_surface_flip_normal = inlay_surface_normal.GetOutput()
# 翻轉法向量的缺陷牙凹洞
hole_file_flip_normal = hole_normal.GetOutput()
merge_file = vtk.vtkAppendPolyData()
merge_file.AddInputData(inlay_surface_flip_normal)
merge_file.AddInputData(hole_file_flip_normal)
merge_file.Update()
# 輸出檔案
writer = vtk.vtkSTLWriter()
writer.SetFileName(f"resources/only_merge/merge_{file_name}.stl")
writer.SetInputData(merge_file.GetOutput())
writer.Write()

