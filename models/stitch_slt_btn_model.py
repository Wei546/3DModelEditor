import vtk
import numpy as np
from meshlib import mrmeshpy
import os
import pymeshlab

class MeshProcessor:
    def __init__(self, defect_file_path, repair_file_path):
        """初始化函數，使用輸入的STL檔案路徑"""
        self.inlay_file_path = None # 初始化賦予自動摳出inlay_surface的檔案路徑
        self.hole_file_path = None    # 初始化賦予自動摳出hole的檔案路徑
        self.defect_file_path = defect_file_path  # 缺陷牙檔案路徑
        self.repair_file_path = repair_file_path    # 修復牙檔案路徑
        self.file_name = repair_file_path.split("/")[-1].split(".")[0]  # 從修復牙檔案路徑提取檔案名稱（不含路徑和副檔名）
    def align_models_icp(self, source_polydata, target_polydata):
        """
        使用 VTK 的 ICP 對齊 source 到 target
        :param source_polydata: 要移動的模型（修復牙）
        :param target_polydata: 目標模型（缺陷牙）
        :return: 回傳修復牙對齊後的絕對路徑
        """
        icp = vtk.vtkIterativeClosestPointTransform() # 建立 ICP 轉換器
        icp.SetSource(source_polydata) # 設定來源模型修復牙
        icp.SetTarget(target_polydata) # 設定目標模型缺陷牙
        icp.GetLandmarkTransform().SetModeToRigidBody() # 設定轉換模式為剛體
        icp.SetMaximumNumberOfIterations(100) # 設定最大迭代次數
        icp.SetMaximumMeanDistance(0.00001) # 設定最大平均距離
        icp.StartByMatchingCentroidsOn() # 設定從質心開始匹配
        icp.Modified() # 更新轉換器
        icp.Update() # 更新轉換器
        
        transform_filter = vtk.vtkTransformPolyDataFilter() # 套用 ICP 轉換結果到 source
        transform_filter.SetInputData(source_polydata) # 設定輸入資料為修復牙
        transform_filter.SetTransform(icp) # 設定轉換器為 ICP
        transform_filter.Update() # 更新轉換器

        aligned_polydata = vtk.vtkPolyData() # 回傳對齊後的模型
        aligned_polydata.DeepCopy(transform_filter.GetOutput()) #DeepCopy保留原始模型 + 對齊後模型，避免No data to write的警告
        output_file_name = f"./only_align_{self.file_name}.stl" # 設定輸出檔案路徑
        return self.save_to_stitch_folder(output_file_name,aligned_polydata) # 儲存對齊後的模型

    def get_hole(self, defect_teeth, repair_teeth):
        '''以空間距離，根據兩個牙齒模型的距離，計算出接觸面積，取得inlay surface'''
        distance_filter = vtk.vtkDistancePolyDataFilter() # 創建距離濾波器，等等要計算欲測量物以及參考物的距離
        distance_filter.SetInputData(0, defect_teeth) # 缺陷牙為欲測量物
        distance_filter.SetInputData(1, repair_teeth) # 修復牙為參考物
        distance_filter.SignedDistanceOff()  # 只取絕對值
        distance_filter.Update() # 更新濾波器以計算距離

        
        distance_data = distance_filter.GetOutput() # 取得距離資料

        
        threshold = vtk.vtkThreshold() # 選取距離小於一定閾值的 patch（可手動調整）
        threshold.SetInputData(distance_data) # 設定輸入資料為距離資料

        threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN) # 設定閾值函數為介於兩者之間，擷取閾值內的面積
        threshold.SetLowerThreshold(0.5) # 設定下閾值
        threshold.SetUpperThreshold(4) # 設定上閾值
        threshold.Update() # 更新濾波器以計算閾值


        
        geometry_filter = vtk.vtkGeometryFilter() # 將 patch 轉成 PolyData
        geometry_filter.SetInputConnection(threshold.GetOutputPort()) # 設定輸入資料為閾值資料
        geometry_filter.Update() # 更新濾波器以轉換資料
        contact_patch = geometry_filter.GetOutput() # 取得接觸面積資料

        
        connectivity_filter = vtk.vtkConnectivityFilter() # 連通性過濾器，只保留最大區塊；因為邊邊角角會有殘留物，只取inlay_surface
        connectivity_filter.SetInputData(contact_patch) # 設定輸入資料為接觸面積資料
        connectivity_filter.SetExtractionModeToLargestRegion() # 設定擷取模式為最大區域
        connectivity_filter.Update() # 更新濾波器以擷取最大區域
        main_patch = connectivity_filter.GetOutput() # 取得最大區域資料
        
        output_file = f"./hole_{self.file_name}.stl" # 將 main_patch 儲存為 STL 檔案

        return self.save_to_stitch_folder(output_file,main_patch)  # 回傳hole surface的絕對路徑

    def get_merge_source(self):
        repair_file_reader = vtk.vtkSTLReader()  # 創建STL檔案讀取器
        repair_file_reader.SetFileName(self.repair_file_path)  # 設置修復牙檔案路徑
        repair_file_reader.Update()  # 更新以讀取檔案
        defect_file_reader = vtk.vtkSTLReader()  # 創建STL檔案讀取器
        defect_file_reader.SetFileName(self.defect_file_path)  # 設置缺陷牙檔案路徑
        defect_file_reader.Update()  # 更新以讀取檔案
        self.repair_file_path = self.align_models_icp(repair_file_reader.GetOutput(),defect_file_reader.GetOutput())  # 對齊修復牙和缺陷牙
        output_file = f"./only_align_{self.file_name}.stl" # 設定輸出檔案路徑
        align_repair_file_reader = vtk.vtkSTLReader()  # 經過對齊後的修復牙檔案讀取器
        align_repair_file_reader.SetFileName(self.repair_file_path) # 設置對齊後的修復牙檔案路徑
        align_repair_file_reader.Update()  # 更新以讀取檔案

        self.inlay_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"stitchResult","./inlay_surface.stl")  # 取得inlay surface
        self.hole_file_path = self.get_hole(defect_file_reader.GetOutput(), align_repair_file_reader.GetOutput())  # 取得hole surface
        print(f"已儲存合併結果至: {output_file}")  # 列印儲存訊息


    def is_white_surface_facing_down(self, polydata):
        """檢查平均法向量是否朝下（Z軸負方向）"""
        normals_filter = vtk.vtkPolyDataNormals()  # 創建法向量濾波器
        normals_filter.SetInputData(polydata)      # 設置輸入網格資料
        normals_filter.Update()                    # 更新濾波器以計算法向量
        
        poly_with_normals = normals_filter.GetOutput()  # 獲取帶法向量的網格
        normals = poly_with_normals.GetPointData().GetNormals()  # 獲取法向量資料

        avg_normal = np.zeros(3)  # 初始化平均法向量為零向量
        for i in range(normals.GetNumberOfTuples()):  # 遍歷所有法向量
            avg_normal += np.array(normals.GetTuple(i))  # 累加法向量
        avg_normal /= normals.GetNumberOfTuples()  # 計算平均值

        direction = avg_normal / np.linalg.norm(avg_normal)  # 將平均法向量規範化為單位向量
        print("平均法向量方向:", direction)  # 列印平均法向量方向
        return direction[2] < 0  # 檢查Z分量是否為負（朝下）

    def is_white_surface_facing_inner(self, polydata, threshold=0.6):
        """檢查大多數法向量是否朝內"""
        normals_filter = vtk.vtkPolyDataNormals()  # 創建法向量濾波器
        normals_filter.SetInputData(polydata)      # 設置輸入網格資料
        normals_filter.Update()                    # 更新濾波器以計算法向量
        
        polydata = normals_filter.GetOutput()      # 獲取帶法向量的網格
        center = np.array(polydata.GetCenter())    # 計算網格中心點
        points = polydata.GetPoints()              # 獲取所有點
        normals = polydata.GetPointData().GetNormals()  # 獲取法向量資料

        inward_count = 0  # 初始化朝內法向量的計數器
        for i in range(points.GetNumberOfPoints()):  # 遍歷所有點
            pt = np.array(points.GetPoint(i))        # 獲取點座標
            n = np.array(normals.GetTuple(i))        # 獲取該點的法向量
            to_center = center - pt                  # 計算從點到中心的向量
            if np.dot(n, to_center) > 0:             # 如果法向量與指向中心的向量內積大於0，則朝內
                inward_count += 1
        
        ratio = inward_count / points.GetNumberOfPoints()  # 計算朝內法向量的比例
        print(f"朝內法向比例: {ratio}")          # 列印朝內比例
        print(f"閾值: {threshold}")              # 列印閾值
        print(ratio > threshold)                # 列印比較結果
        return ratio > threshold                # 返回是否超過閾值

    def merge_meshes(self):
        """合併嵌體和缺陷牙凹洞網格，並確保正確的法向量方向"""
        # 讀取嵌體網格
        inlay_reader = vtk.vtkSTLReader()       # 創建STL檔案讀取器
        inlay_reader.SetFileName(self.inlay_file_path)  # 設置嵌體檔案路徑
        inlay_reader.Update()                   # 更新以讀取檔案

        # 讀取缺陷牙凹洞網格
        hole_reader = vtk.vtkSTLReader()        # 創建STL檔案讀取器
        hole_reader.SetFileName(self.hole_file_path)  # 設置缺陷牙檔案路徑
        hole_reader.Update()                    # 更新以讀取檔案

        # 處理嵌體法向量
        inlay_normal = vtk.vtkPolyDataNormals()  # 創建法向量處理器
        inlay_normal.SetInputData(inlay_reader.GetOutput())  # 設置輸入資料
        if self.is_white_surface_facing_down(inlay_reader.GetOutput()):  # 檢查是否朝下
            inlay_normal.SetAutoOrientNormals(False)  # 不自動調整法向量
            print("嵌體: 不翻轉法向量")
        else:
            inlay_normal.SetAutoOrientNormals(True)   # 自動調整法向量
            print("嵌體: 翻轉法向量")
        inlay_normal.SetConsistency(True)         # 確保法向量一致性
        inlay_normal.SplittingOff()               # 關閉分割功能
        inlay_normal.Update()                     # 更新處理結果

        # 處理缺陷牙凹洞法向量
        hole_normal = vtk.vtkPolyDataNormals()    # 創建法向量處理器
        hole_normal.SetInputData(hole_reader.GetOutput())  # 設置輸入資料
        if self.is_white_surface_facing_inner(hole_reader.GetOutput()):  # 檢查是否朝內
            hole_normal.SetAutoOrientNormals(False)  # 不自動調整法向量
            print("缺陷牙: 不翻轉法向量")
        else:
            hole_normal.SetAutoOrientNormals(False)  # 不自動調整
            hole_normal.SetFlipNormals(True)        # 翻轉法向量
            print("缺陷牙: 翻轉法向量")
        hole_normal.SetConsistency(True)          # 確保法向量一致性
        hole_normal.SplittingOff()                # 關閉分割功能
        hole_normal.Update()                      # 更新處理結果

        # 合併網格
        merge_file = vtk.vtkAppendPolyData()      # 創建網格合併器
        merge_file.AddInputData(inlay_normal.GetOutput())  # 添加嵌體網格
        merge_file.AddInputData(hole_normal.GetOutput())   # 添加缺陷牙網格
        merge_file.Update()                       # 更新以執行合併

        # 儲存合併結果
        output_file = f"./merge_{self.file_name}.stl"  # 設定輸出檔案路徑
        
        return self.save_to_stitch_folder(output_file, merge_file.GetOutput())  # 儲存合併結果並返回檔案路徑

    def process_merged_mesh(self, merged_file_path, thickness=0):
        """處理合併後的網格：修復、偏移、拼接和平滑"""
        # 載入合併後的網格
        mesh = mrmeshpy.loadMesh(merged_file_path)  # 讀取STL檔案
        original_file_name = merged_file_path.split("/")[-1].split(".")[0]  # 提取檔案名稱

        # 修復邊界
        mrmeshpy.uniteCloseVertices(mesh, mesh.computeBoundingBox().diagonal() * 1e-6)  # 合併靠近的頂點

        # 偏移操作
        params = mrmeshpy.GeneralOffsetParameters()  # 創建偏移參數
        params.voxelSize = 1                        # 設置體素大小
        params.signDetectionMode = mrmeshpy.SignDetectionMode.Unsigned  # 設置無符號檢測模式
        shell = mrmeshpy.thickenMesh(mesh, thickness, params)  # 執行網格加厚

        # 拼接邊界
        holes = shell.topology.findHoleRepresentiveEdges()  # 尋找網格中的洞
        print("檢測到的洞數量:", holes.size())       # 列印洞的數量
        if holes.size() >= 2:                        # 如果有至少兩個洞
            new_faces = mrmeshpy.FaceBitSet()        # 創建新面集合
            stitch_params = mrmeshpy.StitchHolesParams()  # 創建拼接參數
            stitch_params.metric = mrmeshpy.getMinAreaMetric(shell)  # 設置最小面積度量
            stitch_params.outNewFaces = new_faces    # 設置輸出新面
            mrmeshpy.buildCylinderBetweenTwoHoles(shell, holes[0], holes[1], stitch_params)  # 在兩個洞之間建立圓柱體

            # 面細分
            subdiv_settings = mrmeshpy.SubdivideSettings()  # 創建細分設置
            subdiv_settings.region = new_faces         # 設置細分區域
            subdiv_settings.maxEdgeSplits = 10000000   # 設置最大邊分割數
            subdiv_settings.maxEdgeLen = 1             # 設置最大邊長
            mrmeshpy.subdivideMesh(shell, subdiv_settings)  # 執行網格細分

            # 平滑新面
            mrmeshpy.positionVertsSmoothly(shell, mrmeshpy.getInnerVerts(shell.topology, new_faces))  # 平滑新生成的頂點

        # 儲存最終結果
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 獲取當前檔案的絕對路徑
        stitch_dir = os.path.join(current_dir, "stitchResult")  # 設定儲存資料夾路徑
        if not os.path.exists(stitch_dir):                  # 如果資料夾不存在
            os.makedirs(stitch_dir)                         # 創建資料夾
        output_file = os.path.join(current_dir, "stitchResult", f"stitched_{original_file_name}.stl")  # 設定輸出檔案路徑
        mrmeshpy.saveMesh(shell, output_file)            # 儲存最終結果
        print(f"已儲存檔案至: {output_file}")  # 列印儲存訊息
        return output_file                           # 返回輸出檔案路徑
    def save_to_stitch_folder(self,input_file_name,poly_data):
        """將處理後的檔案儲存到指定資料夾"""
        
        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        stitch_dir = os.path.join(current_dir, "stitchResult")  
        if not os.path.exists(stitch_dir):
            os.makedirs(stitch_dir)
        # 建立輸出的完整路徑
        output_path = os.path.join(current_dir, "stitchResult", input_file_name)  # 將檔案儲存到指定資料夾
        # 儲存檔案
        writer = vtk.vtkSTLWriter()  # 創建STL檔案寫入器
        writer.SetFileName(output_path)  # 設定輸出檔案名稱
        writer.SetInputData(poly_data)  # 設定要寫入的資料
        writer.SetFileTypeToBinary()  # 設定檔案類型為二進位
        writer.Write()  # 執行寫入操作
        print(f"已儲存檔案至: {output_path}")  # 列印儲存訊息
        project_dir = os.path.dirname(os.path.abspath(__file__))  # 獲取當前檔案的絕對路徑
        output_path = os.path.join(project_dir, "stitchResult", input_file_name)  # 組合成完整的檔案路徑
        print(f"This is output file:{output_path}")  # 列印輸出檔案的絕對路徑
        return output_path  # 返回輸出檔案的絕對路徑
    def remesh(self,row_final_file):
        ms = pymeshlab.MeshSet() #實體化pymeshlab套件
        ms.load_new_mesh(row_final_file) #載入檔案

        ms.apply_filter("meshing_isotropic_explicit_remeshing",
                        iterations=30, #把 isotropic remesh 操作重複執行 n 次
                        targetlen=pymeshlab.PercentageValue(1), #讓remesh的網格邊長接近Bounding Box的對角線長度 × 0.5%
                        adaptive=False, #細節較多的區域生成較小的三角形；在平坦區域生成較大的三角形
                        featuredeg=30, #將30度以上的邊在重網格化時保留
                        checksurfdist=True, # 確保新生成的網格與原始網格偏離程度
                        maxsurfdist=pymeshlab.PercentageValue(0.5),  # 確保新生成的網格與原始網格偏離程度
                        splitflag=True,#提高局部網格的細分程度
                        collapseflag=True,#避免生成過於密集的網格
                        swapflag=True,#避免奇怪的瘦長形狀的網格
                        smoothflag=True,#拉普拉斯平滑
                        reprojectflag=True)#避免平滑中頂點偏離原始形狀過多
        #取得當前檔案的絕對路徑
        current_dir = os.path.dirname(os.path.abspath(__file__)) #取得當前檔案的絕對路徑
        #設定儲存資料夾路徑
        stitch_dir = os.path.join(current_dir, "stitchResult")
        #如果資料夾不存在
        if not os.path.exists(stitch_dir):
            os.makedirs(stitch_dir)
        #設定輸出檔案路徑
        output_file = os.path.join(current_dir, "stitchResult", f"remesh_{self.file_name}.stl")  # 設定輸出檔案路徑
        #儲存最終結果
        ms.save_current_mesh(output_file) # 儲存最終結果
        print(f"已儲存檔案至: {output_file}")  # 列印儲存訊息
        #儲存最終結果
        return output_file
    def smooth_subdivision(self,remesh_final_file):
        remesh_final_file_reader = vtk.vtkSTLReader()  # 創建STL檔案讀取器
        remesh_final_file_reader.SetFileName(remesh_final_file)  # 設置修復牙檔案路徑
        remesh_final_file_reader.Update()  # 更新以讀取檔案

        #創建平滑濾波器
        smoother = vtk.vtkSmoothPolyDataFilter()
        smoother.SetInputConnection(remesh_final_file_reader.GetOutputPort())
        smoother.SetNumberOfIterations(20)
        smoother.SetRelaxationFactor(0.1)
        smoother.FeatureEdgeSmoothingOff()
        smoother.BoundarySmoothingOn()
        smoother.Update()
        #創建細分濾波器
        subdivision = vtk.vtkLoopSubdivisionFilter()
        subdivision.SetInputConnection(smoother.GetOutputPort())
        subdivision.SetNumberOfSubdivisions(2)
        subdivision.Update()

        output_file = f"./smooth_subdivision_{self.file_name}.stl"
        return self.save_to_stitch_folder(output_file,subdivision.GetOutput())  # 儲存平滑後的網格

        
    def process_complete_workflow(self, thickness=0):
        self.get_merge_source()                    # 獲取合併源檔案
        merged_file = self.merge_meshes()            # 執行網格合併
        row_final_file = self.process_merged_mesh(merged_file, thickness)  # 處理合併後的網格
        remseh_final_file = self.remesh(row_final_file)  # 重網格化處理
        smooth_subdivision_file = self.smooth_subdivision(remseh_final_file)
        return smooth_subdivision_file  

'''
# 示例用法
if __name__ == "__main__":
    processor = MeshProcessor("resources/0075/data0075down.stl", "resources/0075/ai_data0075down_smooth.stl")  # 創建處理器實例，放入缺陷牙；修復牙檔案路徑
    final_output = processor.process_complete_workflow(thickness=0)  # 執行完整工作流程
'''
