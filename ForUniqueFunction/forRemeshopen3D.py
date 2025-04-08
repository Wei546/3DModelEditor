import open3d as o3d


mesh = o3d.io.read_triangle_mesh("models/stitchResult/stitched_merge_ai_data0075down_smooth.stl") #載入 STL 檔案

point_cloud = mesh.sample_points_poisson_disk(number_of_points=5000) # 使用泊松盤取樣從網格生成點雲

point_cloud.estimate_normals() #計算點雲的法線

voxel_size = 0.01 # 設定體素大小
down_point_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size) # 下採樣點雲
down_point_cloud.estimate_normals() # 計算降採樣點雲的法線

voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(down_point_cloud, voxel_size=voxel_size)
o3d.visualization.draw_geometries([voxel_grid], window_name="Point Cloud") # 可視化點雲
