import vtk
import numpy as np
class Stitching:
    def __init__(self,renderer,interactor):
        self.renderer = renderer
        self.interactor = interactor
        self.geometry_filter = vtk.vtkGeometryFilter()

    # 接收選取可見區域、輸入模型
    def stitching_func(self,visible_area,poly_data):
        """選取的網格"""
        # 後續需要紀錄選取的網格
        selection_node = vtk.vtkSelectionNode()
        # 設定選取的網格
        selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
        # 設定網格對應的id
        selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
        # 取得visible對應的id
        selection_node.SetSelectionList(visible_area)
        
        # 把選取網格獨立出來的容器
        selection = vtk.vtkSelection()
        # 設定選取的網格
        selection.AddNode(selection_node)

        # 過濾我要的範圍visible_area
        extract = vtk.vtkExtractSelection()
        extract.SetInputData(0, poly_data)
        extract.SetInputData(1, selection)
        extract.Update()

        # 取得選取的網格
        selected = vtk.vtkUnstructuredGrid()
        selected.ShallowCopy(extract.GetOutput())
        
        # 取得選取的網格數量
        print(f"stitching func select:{selected.GetNumberOfCells()}")
        # 呼叫縫合功能，回傳縫合後的網格
        # self.boundary_stitching(selected)
        # 計算曲率
        # self.calCurve(selected)
        """非選取的網格"""
        # 啟用反向選取模式
        selection_node.GetProperties().Set(vtk.vtkSelectionNode.INVERSE(), 1)
        extract.Update()
        # 取得非選取的網格
        unselected = vtk.vtkUnstructuredGrid()
        unselected.ShallowCopy(extract.GetOutput())
        # 取得非選取的網格數量
        print(f"stitching func unselect:{unselected.GetNumberOfCells()}")
        # 呼叫提取邊界功能
        # self.extractTwoCurve(selected,self.calCurve(selected))
        # 呼叫連接功能
        # self.connect_vertices(selected)
        # 計算法向量
        self.calNormal(selected)

        # 合併細分後的選取範圍網格+未細分的非選取範圍網格 
    def connect_vertices(self,selected):
        # 將vtkUnstructuredGrid轉換為vtkPolyData
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(selected)
        geometry_filter.Update()
        # 尋找範圍內的相鄰點
        locator = vtk.vtkPointLocator()
        locator.SetDataSet(geometry_filter.GetOutput())
        locator.BuildLocator()
        # 從選取網格尋找相鄰點
        for i in range(geometry_filter.GetOutput().GetNumberOfPoints()):
            # 取得點座標
            point = geometry_filter.GetOutput().GetPoint(i)
            # 尋找相鄰點
            id = locator.FindClosestPoint(point)
            # 取得相鄰點座標
            neighbor = geometry_filter.GetOutput().GetPoint(id)
            # 連接兩點
            self.connect_two_points(point, neighbor)
        # 印出相鄰點座標
        print(f"point:{point},neighbor:{neighbor}")
        self.connect_two_points(point, neighbor)
    # 連接兩點
    def connect_two_points(self,point,neighbor):
        # 創建線
        line = vtk.vtkLine()
        # 設定線的兩個點
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 1)
        # 創建線的點
        points = vtk.vtkPoints()
        # 加入兩個點
        points.InsertNextPoint(point)
        points.InsertNextPoint(neighbor)
        # 創建線的拓樸
        lines = vtk.vtkCellArray()
        # 加入線
        lines.InsertNextCell(line)
        # 創建線的polydata
        polydata = vtk.vtkPolyData()
        # 加入點
        polydata.SetPoints(points)
        # 加入線
        polydata.SetLines(lines)
        # 創建mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        # 創建actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        # 加入渲染器
        self.renderer.AddActor(actor)
        # 更新渲染器
        self.interactor.GetRenderWindow().Render()

    # 暫時不使用，這是細分功能；先不用解決
    def boundary_stitching(self,selected):
        # 轉換型別為vtkPolyData
        selectedToPolyData = vtk.vtkGeometryFilter()
        selectedToPolyData.SetInputData(selected)
        selectedToPolyData.Update()
        # 線性細分濾波器
        subdivision = vtk.vtkLinearSubdivisionFilter()
        subdivision.SetInputConnection(selectedToPolyData.GetOutputPort())
        subdivision.SetNumberOfSubdivisions(1)
        subdivision.Update()
        # 將vtkPolyData轉換為vtkUnstructuredGrid
        polyToUnstructured = vtk.vtkAppendFilter()
        polyToUnstructured.AddInputData(subdivision.GetOutput())
        polyToUnstructured.Update()
        # 回傳縫合後、型別為vtkUnstructuredGrid的網格
        unstructure_subdivision = polyToUnstructured.GetOutput()
        # 取得縫合後的網格數量
        print(f"after subdivision:{unstructure_subdivision.GetNumberOfCells()}")
        # 取得縫合前的網格數量
        print(f"subdivision original:{selected.GetNumberOfCells()}")
    def calCurve(self,selected):
        # 轉換型別為vtkPolyData
        selectedToPolyData = vtk.vtkGeometryFilter()
        selectedToPolyData.SetInputData(selected)
        selectedToPolyData.Update()

        # 計算曲率
        curvature = vtk.vtkCurvatures()
        curvature.SetInputConnection(selectedToPolyData.GetOutputPort())
        curvature.SetCurvatureTypeToGaussian()
        curvature.Update()

        # 取得曲率
        curvature_poly_data = curvature.GetOutput()
        # 取得曲率數據
        curvature_array = curvature_poly_data.GetPointData().GetScalars()
        # 轉換為numpy
        self.convertToNumpy(curvature_array)
        # 箭頭顯示曲率
        # self.arrowShowCurve(curvature)
        print(f"curvature:{curvature_array}")
        return curvature
    def convertToNumpy(self,curvature_array):
        # 取得曲率數據的數量
        num_points = curvature_array.GetNumberOfTuples()
        # 存放num_points，曲率值的列表
        curvature_list = []
        # 迭代曲率數據
        for i in range(num_points):
            # 取得曲率值
            curvature = curvature_array.GetValue(i)
            # 加入列表
            curvature_list.append(curvature)
        # 將curvate_list轉換為numpy
        curvature_np = np.array(curvature_list)
        # 取得有多少個曲率
        print(f"curvature_np:{num_points}")
        # 取得前10個曲率
        print(f"curvature_np:{curvature_np[:10]}")
    def arrowShowCurve(self,curvature):
        # 創建箭頭
        arrowSource = vtk.vtkArrowSource()
        arrowSource.SetTipResolution(16)
        arrowSource.SetTipLength(0.3)
        arrowSource.SetTipRadius(0.1)
        # giyph3D代表標記點，本身不具備任何形狀，需要設定source
        glyph3D = vtk.vtkGlyph3D()
        # 讓glyph3D顯示箭頭
        glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
        # 使用曲率資料，設定箭頭分布
        glyph3D.SetInputData(curvature.GetOutput())
        # 箭頭方向
        glyph3D.SetVectorModeToUseNormal()
        # 箭頭大小
        glyph3D.SetScaleFactor(0.00001)
        # 更新
        glyph3D.Update()

        # 箭頭顏色為紅色
        arrowMapper = vtk.vtkPolyDataMapper()
        arrowMapper.SetInputConnection(glyph3D.GetOutputPort())
        arrowActor = vtk.vtkActor()
        arrowActor.SetMapper(arrowMapper)
        arrowActor.GetProperty().SetColor(1,0,0)

        self.renderer.AddActor(arrowActor)
        self.interactor.GetRenderWindow().Render()
    def extractTwoCurve(self,selected,selected_curvature):
        # 最後存放嵌體曲率座標的位置
        inlay_edge_polydata = vtk.vtkPolyData()
        # 最後存放缺陷牙齒曲率座標的位置
        teeth_with_hole_edge_polydata = vtk.vtkPolyData()
        # 儲存嵌體曲率座標的點
        inlay_points = vtk.vtkPoints()
        # 儲存缺陷牙齒曲率座標的點
        teeth_with_hole_points = vtk.vtkPoints()
        #  儲存嵌體曲率的array
        inlay_curvature = vtk.vtkFloatArray()
        # 儲存缺陷牙齒曲率的array
        teeth_with_hole_curvature = vtk.vtkFloatArray()
        # selected_curvature是VTK過濾器，這邊要先取得vtkPolyData
        curvature_poly_data = selected_curvature.GetOutput()
        # 從 vtkPolyData 取得曲率數據
        selected_curvature_arr = curvature_poly_data.GetPointData().GetScalars()
        # 設定分離邊界的閾值
        threshold = 1
        # 取得邊界的點
        for i in range(selected_curvature_arr.GetNumberOfTuples()):
            # 選區範圍的點
            pt = curvature_poly_data.GetPoint(i)
            # 取得曲率
            curvature = selected_curvature_arr.GetTuple1(i)

            # 如果曲率大於閾值，代表是嵌體邊界，因為嵌體邊界彎曲比較大
            if curvature > threshold:
                # 嵌體曲率的座標
                inlay_points.InsertNextPoint(pt)
                # 嵌體曲率的值
                inlay_curvature.InsertNextValue(curvature)
                print(f"inlay curvature:{curvature}")
               
            # 如果曲率小於閾值，代表是缺陷牙齒邊界，因為邊界比較平滑，曲率比較小
            else:
                # 缺陷牙齒曲率的座標    
                teeth_with_hole_points.InsertNextPoint(pt)
                # 缺陷牙齒曲率的值
                teeth_with_hole_curvature.InsertNextValue(curvature)
                print(f"teeth_with_hole curvature:{curvature}")
        # 嵌體曲率的座標放入inlay_edge_polydata
        inlay_edge_polydata.SetPoints(inlay_points)
        # 缺陷牙齒曲率的座標放入teeth_with_hole_edge_polydata
        teeth_with_hole_edge_polydata.SetPoints(teeth_with_hole_points)
        # 嵌體曲率的值放入inlay_edge_polydata
        inlay_edge_polydata.GetPointData().SetScalars(inlay_curvature)
        # 缺陷牙齒曲率的值放入teeth_with_hole_edge_polydata
        teeth_with_hole_edge_polydata.GetPointData().SetScalars(teeth_with_hole_curvature)


        
       
        # 設定箭頭
        arrow_source = vtk.vtkArrowSource()

        # 建立 Glyph3D
        inlay_edge_glyph3D = vtk.vtkGlyph3D()
        inlay_edge_glyph3D.SetSourceConnection(arrow_source.GetOutputPort())
        inlay_edge_glyph3D.SetInputData(inlay_edge_polydata)
        inlay_edge_glyph3D.SetColorModeToColorByScalar() 
        inlay_edge_glyph3D.SetScaleFactor(0.00001)
        inlay_edge_glyph3D.Update()

        teeth_with_hole_edge_glyph3D = vtk.vtkGlyph3D()
        teeth_with_hole_edge_glyph3D.SetSourceConnection(arrow_source.GetOutputPort())
        teeth_with_hole_edge_glyph3D.SetInputData(teeth_with_hole_edge_polydata)
        teeth_with_hole_edge_glyph3D.SetColorModeToColorByScalar() 
        teeth_with_hole_edge_glyph3D.SetScaleFactor(0.00001)
        teeth_with_hole_edge_glyph3D.Update()
        print(f"Scalars: {inlay_edge_polydata.GetPointData().GetScalars()}")
        print(f"Scalars: {teeth_with_hole_edge_polydata.GetPointData().GetScalars()}")

        # 設定 Mapper
        inlay_edge_mapper = vtk.vtkPolyDataMapper()
        inlay_edge_mapper.SetInputConnection(inlay_edge_glyph3D.GetOutputPort())

        teeth_with_hole_edge_mapper = vtk.vtkPolyDataMapper()
        teeth_with_hole_edge_mapper.SetInputConnection(teeth_with_hole_edge_glyph3D.GetOutputPort())
        # 設定 LookupTable 讓曲率影響顏色
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(2)
        # 如果曲率 < 1，設定為藍色
        lut.SetTableValue(0, 0, 0, 1, 1)  # 藍色
        # 如果曲率 >= 1，設定為紅色
        lut.SetTableValue(1, 1, 0, 0, 1)  # 紅色
        # 設定曲率的範圍
        lut.SetTableRange(-1, 2)
        lut.Build()

        inlay_edge_mapper.SetLookupTable(lut)
        teeth_with_hole_edge_mapper.SetLookupTable(lut)


        # 設定 Actor
        inlay_edge_actor = vtk.vtkActor()
        inlay_edge_actor.SetMapper(inlay_edge_mapper)

        teeth_with_hole_edge_actor = vtk.vtkActor()
        teeth_with_hole_edge_actor.SetMapper(teeth_with_hole_edge_mapper)

        # 加入 Renderer
        self.renderer.AddActor(inlay_edge_actor)
        self.renderer.AddActor(teeth_with_hole_edge_actor)
        # 更新 Renderer
        self.interactor.GetRenderWindow().Render()
        print(f"number of inlay curve:{inlay_curvature.GetNumberOfTuples()}")
        print(f"number of teeth with hole curve:{teeth_with_hole_curvature.GetNumberOfTuples()}")
    # 取得法向量
    def calNormal(self,selected):
        # 將vtkUnstructuredGrid轉換為polydata
        selectedToPolydata = vtk.vtkGeometryFilter()
        selectedToPolydata.SetInputData(selected)
        selectedToPolydata.Update()
        # 取得點座標
        selected_point_coord = vtk.vtkPoints()
        # 將selected的點座標放入selected_point_coord，從存放選取範圍的selectedToPolydata取得點
        for i in range(selectedToPolydata.GetOutput().GetNumberOfPoints()):
            # 把x,y,z軸座標，放入點座標變數
            selected_point_coord.InsertNextPoint(selectedToPolydata.GetOutput().GetPointData().GetScalars().GetTuple1(i))
        print(f"這是hard的選取範圍座標{selected_point_coord}")





        









        
