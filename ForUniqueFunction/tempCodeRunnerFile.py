# 偵測邊界洞
boundaryEdges = vtk.vtkFeatureEdges()
boundaryEdges.SetInputData(polydata)
boundaryEdges.BoundaryEdgesOn()
boundaryEdges.FeatureEdgesOff()
boundaryEdges.NonManifoldEdgesOff()
boundaryEdges.ManifoldEdgesOff()
boundaryEdges.Update()

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


region_0_pts = component1.GetPoints()
region_1_pts = component2.GetPoints()
print("region_0 點數:", region_0_pts.GetNumberOfPoints())
print("region_1 點數:", region_1_pts.GetNumberOfPoints())