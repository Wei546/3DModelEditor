import vtk
import numpy as np
from scipy.spatial import cKDTree
merged_file_path = "resources/only_merge/merge_inlay_surface_0101.stl"  # 輸入的 STL 檔案路徑
reader = vtk.vtkSTLReader()
reader.SetFileName(merged_file_path)
reader.Update()
polydata = reader.GetOutput()

# 修復邊界（合併重疊點）
cleaner = vtk.vtkCleanPolyData()
cleaner.SetInputData(polydata)
cleaner.SetTolerance(1e-6 * np.linalg.norm(polydata.GetBounds()))  # 根據 bounding box 設定閾值
cleaner.Update()
polydata = cleaner.GetOutput()

# 偵測邊界洞
boundaryEdges = vtk.vtkFeatureEdges()
boundaryEdges.SetInputData(polydata)
boundaryEdges.BoundaryEdgesOn()
boundaryEdges.FeatureEdgesOff()
boundaryEdges.NonManifoldEdgesOff()
boundaryEdges.ManifoldEdgesOff()
boundaryEdges.Update()
boundary_output = boundaryEdges.GetOutput()
print("Number of boundary edge lines:", boundary_output.GetNumberOfCells())

# 將洞分類出來（抓出兩個洞）
connectivity = vtk.vtkConnectivityFilter()
connectivity.SetInputData(boundaryEdges.GetOutput())
connectivity.SetExtractionModeToAllRegions()
connectivity.ColorRegionsOn()
connectivity.Update()
numHoles = connectivity.GetNumberOfExtractedRegions()

# 提取1的邊界
threshold_1 = vtk.vtkThreshold()
threshold_1.SetInputData(connectivity.GetOutput())
threshold_1.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
threshold_1.SetLowerThreshold(0)
threshold_1.SetUpperThreshold(0)
threshold_1.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "RegionId")
threshold_1.Update()
region1_poly_data = vtk.vtkDataSetSurfaceFilter()
region1_poly_data.SetInputData(threshold_1.GetOutput())
region1_poly_data.Update()
component1 = region1_poly_data.GetOutput()
threshold_output_1 = threshold_1.GetOutput()


# 提取2的邊界
threshold_2 = vtk.vtkThreshold()
threshold_2.SetInputData(connectivity.GetOutput())
threshold_2.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
threshold_2.SetLowerThreshold(1)
threshold_2.SetUpperThreshold(1)
threshold_2.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, "RegionId")
threshold_2.Update()
region2_poly_data = vtk.vtkDataSetSurfaceFilter()
region2_poly_data.SetInputData(threshold_2.GetOutput())
region2_poly_data.Update()
component2 = region2_poly_data.GetOutput()
threshold_output_2 = threshold_2.GetOutput()

# ============ component1 ============ #
points1 = component1.GetPoints()
num_points1 = points1.GetNumberOfPoints()
print(f"component1 有 {num_points1} 個點")

point_polydata1 = vtk.vtkPolyData()
point_polydata1.SetPoints(points1)

glyph1 = vtk.vtkVertexGlyphFilter()
glyph1.SetInputData(component1)
glyph1.Update()

glyph_mapper1 = vtk.vtkPolyDataMapper()
glyph_mapper1.SetInputData(glyph1.GetOutput())

glyph_actor1 = vtk.vtkActor()
glyph_actor1.SetMapper(glyph_mapper1)
glyph_actor1.GetProperty().SetColor(1, 0, 0)        # 🔴 紅色點
glyph_actor1.GetProperty().SetPointSize(5)

surface_mapper1 = vtk.vtkPolyDataMapper()
surface_mapper1.SetInputData(component1)

surface_actor1 = vtk.vtkActor()
surface_actor1.SetMapper(surface_mapper1)
surface_actor1.GetProperty().SetColor(1, 1, 1)      # ⚪ 白色面

# ============ component2 ============ #
points2 = component2.GetPoints()
num_points2 = points2.GetNumberOfPoints()
print(f"component2 有 {num_points2} 個點")

point_polydata2 = vtk.vtkPolyData()
point_polydata2.SetPoints(points2)

glyph2 = vtk.vtkVertexGlyphFilter()
glyph2.SetInputData(component2)
glyph2.Update()

glyph_mapper2 = vtk.vtkPolyDataMapper()
glyph_mapper2.SetInputData(glyph2.GetOutput())

glyph_actor2 = vtk.vtkActor()
glyph_actor2.SetMapper(glyph_mapper2)
glyph_actor2.GetProperty().SetColor(0, 0, 1)        # 🔵 藍色點
glyph_actor2.GetProperty().SetPointSize(5)

surface_mapper2 = vtk.vtkPolyDataMapper()
surface_mapper2.SetInputData(component2)

surface_actor2 = vtk.vtkActor()
surface_actor2.SetMapper(surface_mapper2)
surface_actor2.GetProperty().SetColor(0.7, 0.7, 0.7)  # ⚫ 灰色面









    
'''
# 建立 mapper 和 actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(component1)  # 使用 component1 作為 mapper 的輸入

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1, 1, 1)  # 白色或你想要的顏色

# 建立 renderer 和視窗
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# 加入 actor
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.2)  # 深藍背景

# 開始渲染
render_window.Render()
interactor.Start()
'''




