import open3d as o3d
import numpy as np
class MultiwayRegistration:
    def __init__(self, voxel_size=0.0002, max_corr_dist_coarse=30, max_corr_dist_fine=0.05):
        self.voxel_size = voxel_size
        self.max_corr_dist_coarse = max_corr_dist_coarse
        self.max_corr_dist_fine = max_corr_dist_fine
    def icp_registration(self, target, source):
        # 建立平移矩陣
        T_init = np.identity(4)
        # 初始化ICP
        icp_coarse = o3d.pipelines.registration.registration_icp(
            source, target, self.max_corr_dist_coarse, T_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane())
        icp_fine = o3d.pipelines.registration.registration_icp(
            source, target, self.max_corr_dist_fine, icp_coarse.transformation,
            o3d.pipelines.registration.TransformationEstimationPointToPlane())
        final_transformation = icp_fine.transformation
        return final_transformation
    def rotation_matrix_xyz(self, pcd_target_hole, pcd_source_whole):
        # 給予旋轉角度
        x_rad = np.deg2rad(0)
        y_rad = np.deg2rad(-1.2)
        z_rad = np.deg2rad(0)
        Rx = np.array([[1, 0, 0],
                   [0, np.cos(x_rad), -np.sin(x_rad)],
                   [0, np.sin(x_rad), np.cos(x_rad)]])
    
        Ry = np.array([[np.cos(y_rad), 0, np.sin(y_rad)],
                    [0, 1, 0],
                    [-np.sin(y_rad), 0, np.cos(y_rad)]])
        
        Rz = np.array([[np.cos(z_rad), -np.sin(z_rad), 0],
                    [np.sin(z_rad), np.cos(z_rad), 0],
                    [0, 0, 1]])
        

        R = Rz @ Ry @ Rx

        T = np.eye(4)
        T[:3, :3] = R
        print(f"旋轉矩陣:{T}")
        return T
        
        '''
        # 下採樣讓兩個模型點數相同
        pcd_target_hole = pcd_target_hole.voxel_down_sample(voxel_size=0.0002)
        pcd_source_whole = pcd_source_whole.voxel_down_sample(voxel_size=0.0002)
        # 點雲轉換成numpy格式
        source_pts = np.asarray(pcd_source_whole.points)
        target_pts = np.asarray(pcd_target_hole.points)
        min_points = min(len(source_pts), len(target_pts))

        source_pts = source_pts[:min_points]
        target_pts = target_pts[:min_points]
        # 取兩者的質心
        source_center = np.mean(source_pts, axis=0)
        target_center = np.mean(target_pts, axis=0)
        # 中心化處理
        source_centered = source_pts - source_center
        target_centered = target_pts - target_center
        H = source_centered.T @ target_centered
        U,S,Vt = np.linalg.svd(H)
        R = Vt.T @ U.T
        if np.linalg.det(R) < 0:
            Vt[2, :] *= -1
            R = Vt.T @ U.T
        T = np.eye(4)
        T[:3, :3] = R
        return T
        '''
        
    def alignModel(self, mesh_target, mesh_source):
        # 計算缺陷牙質心
        target_hole = np.mean(np.asarray(mesh_target.points), axis=0)
        print(f"缺陷牙質心:{target_hole}")
        # 計算修復牙質心
        source_whole = np.mean(np.asarray(mesh_source.points), axis=0)
        print(f"修復牙質心:{source_whole}")
        # 平移向量
        source_whole[1] = target_hole[1]
        source_whole[2] = target_hole[2]-0.5
        translation_vector =  target_hole - source_whole 
        # 創建平移矩陣
        T = np.eye(4)
        
        # 將平移向量填入平移矩陣
        T[:3, 3] = translation_vector
        print(f"平移矩陣:{T}")
        # 將平移矩陣放入mesh_source_whole
        return T


    def run_registration(self, mesh_target, mesh_source):
        file_name = mesh_target.split("/")[-1].split(".")[0]
        # 讀檔案
        mesh_target_hole = o3d.io.read_triangle_mesh(mesh_target)
        mesh_source_whole = o3d.io.read_triangle_mesh(mesh_source)
        # 缺陷牙是橘色，修復牙是藍色
        mesh_target_hole.paint_uniform_color([1, 0.706, 0])
        mesh_source_whole.paint_uniform_color([0, 0.706, 1])
        # 創建點雲類別
        pcd_target_hole = o3d.geometry.PointCloud()
        pcd_source_whole = o3d.geometry.PointCloud()
        # 設定點雲的頂點
        pcd_target_hole.points = o3d.utility.Vector3dVector(np.array(mesh_target_hole.vertices))
        pcd_source_whole.points = o3d.utility.Vector3dVector(np.array(mesh_source_whole.vertices))
        # 法向量估計
        search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=20, max_nn=40)
        pcd_target_hole.estimate_normals(search_param=search_param)
        pcd_source_whole.estimate_normals(search_param=search_param)
        # 平移ai生成結果
        mesh_source_whole.transform(self.alignModel(pcd_target_hole, pcd_source_whole))
        # 網格旋轉結果轉換成點雲
        pcd_source_whole_aligned = o3d.geometry.PointCloud()
        pcd_source_whole_aligned.points = mesh_source_whole.vertices
        # 旋轉ai生成結果
        mesh_source_whole.transform(self.rotation_matrix_xyz(pcd_target_hole, pcd_source_whole_aligned))
        # 計算法向量
        mesh_target_hole.compute_vertex_normals()
        mesh_source_whole.compute_vertex_normals()
        # 視覺化
        o3d.visualization.draw_geometries([mesh_target_hole, mesh_source_whole], mesh_show_back_face=True)
        # 將點雲轉換成TriangleMesh
        self.save_file(mesh_target_hole, mesh_source_whole,file_name)
    def save_file(self, mesh_target_hole, mesh_source_whole,file_name):
        # 計算法向量
        mesh_target_hole.compute_vertex_normals()
        mesh_source_whole.compute_vertex_normals()
        # 合併
        mesh_combined = mesh_target_hole + mesh_source_whole
        # 存檔
        o3d.io.write_triangle_mesh(f"resources/align_file/smooth_align_{file_name}.stl", mesh_combined)

        '''
        transformation = np.array([
            [1, 0, 0, -9.17178924], 
            [0, 1, 0, -0.02805314], 
            [0, 0, 1, -0.07510228], 
            [0, 0, 0, 1]
        ])
        mesh_source_whole.transform(transformation)
        # 顯示hole以及whole
        '''






if __name__ == "__main__":
    # 替換成你實際的 STL 檔案路徑
    mesh_paths = [
        "resources/00109/data0109down.stl",
        "resources/00109/ai_data0109down_smooth.stl",
    ]
    reg = MultiwayRegistration()
    result = reg.run_registration(mesh_paths[0], mesh_paths[1])


