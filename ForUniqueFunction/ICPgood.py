import open3d as o3d
import numpy as np

class MultiwayRegistration:
    def __init__(self, voxel_size=0.0002, max_corr_dist_coarse=30, max_corr_dist_fine=0.05):
        self.voxel_size = voxel_size
        self.max_corr_dist_coarse = max_corr_dist_coarse
        self.max_corr_dist_fine = max_corr_dist_fine

    def load_point_clouds(self, pointlist):
        pcds = []
        for point in pointlist:
            pcd_down = point.voxel_down_sample(voxel_size=self.voxel_size)
            pcds.append(pcd_down)
        return pcds

    def pairwise_registration(self, source, target):
        print("Apply point-to-plane ICP")
        icp_coarse = o3d.pipelines.registration.registration_icp(
            source, target, self.max_corr_dist_coarse, np.identity(4),
            o3d.pipelines.registration.TransformationEstimationPointToPlane())
        icp_fine = o3d.pipelines.registration.registration_icp(
            source, target, self.max_corr_dist_fine, icp_coarse.transformation,
            o3d.pipelines.registration.TransformationEstimationPointToPlane())
        transformation_icp = icp_fine.transformation
        information_icp = o3d.pipelines.registration.get_information_matrix_from_point_clouds(
            source, target, self.max_corr_dist_fine, icp_fine.transformation)
        return transformation_icp, information_icp

    def full_registration(self, pcds):
        pose_graph = o3d.pipelines.registration.PoseGraph()
        odometry = np.identity(4)
        pose_graph.nodes.append(o3d.pipelines.registration.PoseGraphNode(odometry))
        n_pcds = len(pcds)
        for source_id in range(n_pcds):
            for target_id in range(source_id + 1, n_pcds):
                transformation_icp, information_icp = self.pairwise_registration(
                    pcds[source_id], pcds[target_id])
                print("Build PoseGraph")
                if target_id == source_id + 1:
                    odometry = np.dot(transformation_icp, odometry)
                    pose_graph.nodes.append(
                        o3d.pipelines.registration.PoseGraphNode(np.linalg.inv(odometry)))
                    pose_graph.edges.append(
                        o3d.pipelines.registration.PoseGraphEdge(source_id,
                                                                 target_id,
                                                                 transformation_icp,
                                                                 information_icp,
                                                                 uncertain=False))
                else:
                    pose_graph.edges.append(
                        o3d.pipelines.registration.PoseGraphEdge(source_id,
                                                                 target_id,
                                                                 transformation_icp,
                                                                 information_icp,
                                                                 uncertain=True))
        return pose_graph

    def rotate_around_y_axis(self, pcd, rotation_angle):
        center = np.mean(np.asarray(pcd.points), axis=0)
        pcd.translate(-center)
        axis = np.array([0, 1, 0])
        rotation_vector = axis * rotation_angle
        rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_vector)
        pcd.rotate(rotation_matrix, center=(0, 0, 0))
        return pcd

    def run_registration(self, mesh_target, mesh_source):
        """
        """
        # 讀取三個網格並設定顏色
        mesh1 = o3d.io.read_triangle_mesh(mesh_target)
        mesh2 = o3d.io.read_triangle_mesh(mesh_source)
        mesh1.paint_uniform_color([1, 0.706, 0])
        mesh2.paint_uniform_color([0, 0.706, 1])
        # 轉換成點雲並取得頂點
        source = o3d.geometry.PointCloud()
        target = o3d.geometry.PointCloud()
        third = o3d.geometry.PointCloud()
        target.points = o3d.utility.Vector3dVector(np.array(mesh1.vertices))
        source.points = o3d.utility.Vector3dVector(np.array(mesh2.vertices))

        # 旋轉點雲
        rotation_angle = -np.pi / 2
        source = self.rotate_around_y_axis(source, rotation_angle)
        third = self.rotate_around_y_axis(third, -rotation_angle)

        # 平移調整
        target.translate(-np.mean(np.asarray(target.points), axis=0))
        source.translate(np.array([-5, 0, -2]))
        third.translate(np.array([5, 0, -2]))

        # 法向量估計
        search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=20, max_nn=40)
        source.estimate_normals(search_param=search_param)
        target.estimate_normals(search_param=search_param)
        third.estimate_normals(search_param=search_param)

        # 第一次配準 (source 與 target)
        pcds_down = self.load_point_clouds([source, target])
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
            pose_graph = self.full_registration(pcds_down)

        print("Optimizing PoseGraph ...")
        option = o3d.pipelines.registration.GlobalOptimizationOption(
            max_correspondence_distance=self.max_corr_dist_fine,
            edge_prune_threshold=0.1,
            reference_node=0)
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
            o3d.pipelines.registration.global_optimization(
                pose_graph,
                o3d.pipelines.registration.GlobalOptimizationLevenbergMarquardt(),
                o3d.pipelines.registration.GlobalOptimizationConvergenceCriteria(),
                option)

        # 轉換點雲
        pcds = self.load_point_clouds([source, target])
        pcd_combined = o3d.geometry.PointCloud()
        for point_id in range(len(pcds)):
            pcds[point_id].transform(pose_graph.nodes[point_id].pose)
            pcd_combined += pcds[point_id]
        pcd_combined.translate(-np.mean(np.asarray(pcd_combined.points), axis=0))
        pcd_combined.estimate_normals(search_param=search_param)

        # 第二次配準 (third 與 pcd_combined)
        pcds_down1 = self.load_point_clouds([third, pcd_combined])
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
            pose_graph1 = self.full_registration(pcds_down1)

        print("Optimizing PoseGraph1 ...")
        option1 = o3d.pipelines.registration.GlobalOptimizationOption(
            max_correspondence_distance=self.max_corr_dist_fine,
            edge_prune_threshold=0.1,
            reference_node=0)
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
            o3d.pipelines.registration.global_optimization(
                pose_graph1,
                o3d.pipelines.registration.GlobalOptimizationLevenbergMarquardt(),
                o3d.pipelines.registration.GlobalOptimizationConvergenceCriteria(),
                option1)

        pcds1 = self.load_point_clouds([third, pcd_combined])
        pcd_combined1 = o3d.geometry.PointCloud()
        for point_id in range(len(pcds1)):
            pcds1[point_id].transform(pose_graph1.nodes[point_id].pose)
            pcd_combined1 += pcds1[point_id]

        # 顯示結果
        o3d.visualization.draw_geometries([pcd_combined1])
        o3d.io.write_point_cloud("multiway_registration_all.pcd", pcd_combined1)
        return pcd_combined1
    def save_file(self, pcd_combined1, output_path):
        # 儲存成點雲
        o3d.io.write_point_cloud(output_path, pcd_combined1)
        # 儲存成stl
        pcd_combined1.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        # 點雲重建成網格
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd_combined1, alpha=1)
        # 計算法向量
        mesh.compute_vertex_normals()
        print(type(mesh))
        # 儲存
        o3d.io.write_triangle_mesh("multiway_registration_all.stl", mesh)
        return mesh



if __name__ == "__main__":
    # 替換成你實際的 STL 檔案路徑
    mesh_paths = [
        "resources/0075/data0075down.stl",
        "resources/0075/ai_data0075down.stl",
    ]
    reg = MultiwayRegistration()
    result = reg.run_registration(mesh_paths[0], mesh_paths[1])
    # mesh_result = reg.save_file(result, "models")
    o3d.visualization.draw_geometries([result])
# 使用範例：



