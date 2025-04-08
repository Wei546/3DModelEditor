import vtk

# 创建STL读取器并读取文件
reader = vtk.vtkSTLReader()
reader.SetFileName('models/stitchResult/remesh_ai_data0075down_smooth.stl')
reader.Update()

# 创建平滑滤波器
smoother = vtk.vtkSmoothPolyDataFilter()
smoother.SetInputConnection(reader.GetOutputPort())
smoother.SetNumberOfIterations(20)  # 设置迭代次数
smoother.SetRelaxationFactor(0.1)   # 设置松弛因子
smoother.FeatureEdgeSmoothingOff()  # 关闭特征边平滑
smoother.BoundarySmoothingOn()      # 开启边界平滑
smoother.Update()

#創建細分器
subdivider = vtk.vtkLoopSubdivisionFilter()
subdivider.SetInputConnection(smoother.GetOutputPort())
subdivider.SetNumberOfSubdivisions(2)  # 设置细分次数
subdivider.Update()
# 创建STL写入器
writer = vtk.vtkSTLWriter()
writer.SetFileName('models/stitchResult/remesh_ai_data0075down_smooth_subdivide.stl')
writer.SetInputConnection(subdivider.GetOutputPort())
writer.Write()
print("Saved file as models/stitchResult/remesh_ai_data0075down_smooth_subdivide.stl")