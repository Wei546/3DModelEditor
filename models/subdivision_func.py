import vtk
import os
import open3d as o3d
class ForStitchBetter:
    def __init__(self,stitchModel,onlyMergeModel):
        self.stitch_model_path = stitchModel
        self.onlyMerge_model_path = onlyMergeModel
    def icp(self,source_only_merge,target_stitch):
        icp = vtk.vtkIterativeClosestPointTransform()
        icp.SetSource(source_only_merge)
        icp.SetTarget(target_stitch)
        icp.GetLandmarkTransform().SetModeToRigidBody()
        icp.Update()

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputData(source_only_merge)
        transform_filter.SetTransform(icp)
        transform_filter.Update()
        self.writeDifferentFile(transform_filter.GetOutput(),f"icp_{self.onlyMerge_model_path}")
        print(f"icp complete")



        return transform_filter.GetOutput()
    '''
    def booleanDifference(self,icp_only_merge_poly_data,stitch_poly_data):
        boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()
        boolean_filter.SetOperationToDifference()
        boolean_filter.SetInputData(0, stitch_poly_data)
        boolean_filter.SetInputData(1, icp_only_merge_poly_data)
        boolean_filter.Update()

        print(f"boolean complete")

        return boolean_filter.GetOutput()
    '''

    def open3dBooleanDifference(self,icp_only_merge_path,stitch_path):
        mesh_icp_only_merge = o3d.io.read_triangle_mesh(icp_only_merge_path)
        mesh_stitch = o3d.io.read_triangle_mesh(stitch_path)

        mesh_icp_only_merge_t = o3d.t.geometry.TriangleMesh.from_legacy(mesh_icp_only_merge)
        mesh_stitch_t = o3d.t.geometry.TriangleMesh.from_legacy(mesh_stitch)

        result = mesh_stitch_t.boolean_difference(mesh_icp_only_merge_t, tolerance=0.01)
        result = result.to_legacy()
        o3d.io.write_triangle_mesh(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ForBetterPatchResult", "boolean_result.stl"), result)
        print(f"boolean complete")
    
    def betterFilter(self,stitch_patch):
        #stitch_patch細分
        subdivision_filter = vtk.vtkLoopSubdivisionFilter()
        subdivision_filter.SetInputData(stitch_patch)
        subdivision_filter.SetNumberOfSubdivisions(2)
        subdivision_filter.Update()
        #平滑
        smoothing_filter = vtk.vtkSmoothPolyDataFilter()
        smoothing_filter.SetInputData(subdivision_filter.GetOutput())
        smoothing_filter.SetNumberOfIterations(10)
        smoothing_filter.SetRelaxationFactor(0.1)
        smoothing_filter.Update()
        #平滑後的patch
        smooth_patch = smoothing_filter.GetOutput()

        print(f"better filter complete")
        return smooth_patch

    def appendPolyData(self,smooth_patch,only_merge_poly_data):
        append_filter = vtk.vtkAppendPolyData()
        append_filter.AddInputData(smooth_patch)
        append_filter.AddInputData(only_merge_poly_data)
        append_filter.Update()

        print(f"append complete")
        return append_filter.GetOutput()

    def readDifferentFile(self,file_path):
        """讀取不同格式的模型"""
        extension = file_path.split('.')[-1].lower()
        readers = {
            'vtp': vtk.vtkXMLPolyDataReader,
            'obj': vtk.vtkOBJReader,
            'ply': vtk.vtkPLYReader,
            'stl': vtk.vtkSTLReader
        }
        if extension not in readers:
            raise ValueError("不支援的檔案格式.")
        reader = readers[extension]()
        reader.SetFileName(file_path)
        reader.Update()
        return reader.GetOutput()

    def writeDifferentFile(self,poly_data,save_file_name):
        """儲存不同格式的模型"""
        # 取得副檔名
        extension = save_file_name.split('.')[-1].lower()
        output_name = save_file_name.split("/")[-1]
        writers = {
            'vtp': vtk.vtkXMLPolyDataWriter,
            'obj': vtk.vtkOBJWriter,
            'ply': vtk.vtkPLYWriter,
            'stl': vtk.vtkSTLWriter
        }
        if extension not in writers:
            raise ValueError("不支援的檔案格式.")
        current_path = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(current_path, "ForBetterPatchResult")
        if not os.path.exists(output_file_path):
            os.makedirs(output_file_path)
        # 儲存檔案
        writer = writers[extension]()
        writer.SetFileName(os.path.join(output_file_path, f"{output_name}.{extension}"))
        writer.SetInputData(poly_data)
        writer.Write()


    def processPartialBetter(self):
        #讀取檔案
        stitch = self.readDifferentFile(self.stitch_model_path)
        only_merge = self.readDifferentFile(self.onlyMerge_model_path)

        self.writeDifferentFile(stitch,self.stitch_model_path)
        self.writeDifferentFile(only_merge,self.onlyMerge_model_path)


        extension_stitch = self.stitch_model_path.split('.')[-1].lower()
        extension_only_merge = self.onlyMerge_model_path.split('.')[-1].lower()

        name_stitch = self.stitch_model_path.split("/")[-1]
        name_only_merge = self.onlyMerge_model_path.split("/")[-1]
        new_stitch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ForBetterPatchResult", f"{name_stitch}.{extension_stitch}")
        new_only_merge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ForBetterPatchResult", f"{name_only_merge}.{extension_only_merge}")

        only_merge_poly_data = self.readDifferentFile(new_only_merge_path)
        stitch_poly_data = self.readDifferentFile(new_stitch_path)


        #將only_merge模型轉換為vtkPolyData格式
        self.icp(only_merge_poly_data,stitch_poly_data)


        #進行布林運算
        # boolean_result = self.booleanDifference(icp_only_merge_poly_data,stitch_poly_data)
        self.open3dBooleanDifference(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ForBetterPatchResult", "icp_only_merge"),(new_stitch_path))

        boolean_result = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ForBetterPatchResult", "boolean_result.stl")

        #對布林運算結果進行細分和光滑處理
        smooth_patch = self.betterFilter(boolean_result)

        #將平滑後的patch與only_merge模型合併
        final_result = self.appendPolyData(smooth_patch,only_merge_poly_data)

        #儲存結果
        self.writeSTLFile(final_result)


for_stitch_model = ForStitchBetter("for_test_stitched_better_merge_inlay_surface_0075.stl","resources/only_merge/merge_inlay_surface_flip_0075.stl")
for_stitch_model.processPartialBetter()

