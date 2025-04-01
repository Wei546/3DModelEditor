distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SetInputData(0, repair_teeth)
    distance_filter.SetInputData(1, hole_teeth)