from .plybb import   get_depth_from_gray_value
from plyfile import PlyData
import numpy as np
from stl import mesh
from PIL import Image



class DentalModelReconstructor:
    def __init__(self, image_path, ply_path, stl_output_path):
        self.image_path = image_path
        self.ply_path = ply_path
        self.stl_output_path = stl_output_path
        self.image = None
        self.vertices = None
        self.bounds = None
        
        
    def preprocess_image(self):
        """增強圖像預處理，專門針對牙齒模型特徵"""
        # 讀取並轉換為灰階
        self.image = Image.open(self.image_path).convert('L')
        # img_array = np.array(self.image)
        
        # self.image = Image.fromarray(img_array)
        
        
    def generate_point_cloud(self):
        vertices_list = []
        image = self.image
        width, height = image.size
        min_x_value, max_x_value = width, 0
        max_value, min_value = 0, 255
        width, height = image.size
        for y in range(height):
            for x in range(width):
                pixel_value = image.getpixel((x, y))
                max_value = max(max_value, pixel_value)
                min_value = min(min_value, pixel_value)
                if pixel_value != 0:
                    min_x_value = min(min_x_value, x)
                    max_x_value = max(max_x_value, x)

        ply_data = PlyData.read(self.ply_path)
        vertices = np.vstack([ply_data['vertex']['x'],
                            ply_data['vertex']['y'],
                            ply_data['vertex']['z']]).T
        
        min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
        min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
        min_z, max_z = np.min(vertices[:, 2]), np.max(vertices[:, 2])
        
        for y in range(height-1, -1, -1):
            for x in range(width-1, -1, -1):
                gray_value = image.getpixel((x, y))
                new_x = get_depth_from_gray_value(x, max_x_value, min_x_value, min_x, max_x)
                new_y = get_depth_from_gray_value(height - y - 1, 255, 0, min_y, max_y)
                new_z = get_depth_from_gray_value(gray_value, max_value, min_value, min_z, max_z)
                vertices_list.append([new_x, new_y, new_z])
        return np.array(vertices_list)
    

        
    def generate_mesh(self, points):
        """生成三角形網格，並反轉法向量方向"""
        height, width = int(np.sqrt(len(points))), int(np.sqrt(len(points)))
        faces = []
        
        for y in range(height - 1):
            for x in range(width - 1):
                # 計算頂點索引
                v0 = y * width + x
                v1 = v0 + 1
                v2 = (y + 1) * width + x
                v3 = v2 + 1
                
                # 計算對角線長度來決定三角形的分割方式
                d1 = np.linalg.norm(points[v0] - points[v3])
                d2 = np.linalg.norm(points[v1] - points[v2])
                
                # 選擇較短的對角線作為分割線，並反轉三角形頂點順序以顛倒法向量
                if d1 < d2:
                    faces.extend([[v0, v3, v1], [v0, v2, v3]])  # 順序反轉
                else:
                    faces.extend([[v0, v2, v1], [v1, v2, v3]])  # 順序反轉
                    
            # 移除多餘的網格
        min_z_depth = np.min([point[2] for point in points])
        new_faces = []
        for face in faces:
            # 提取頂點座標
            triangle_points = [points[idx] for idx in face]
            z_values = [point[2] for point in triangle_points]
            x_values = [point[0] for point in triangle_points]
            y_values = [point[1] for point in triangle_points]

            # 判斷是否應移除 (完全平坦或超出範圍的網格)
            skip_triangle = (
                sum(z == min_z_depth for z in z_values) == 3 or
                min(x_values) == max(x_values) or
                min(y_values) == max(y_values)
            )

            if not skip_triangle:
                new_faces.append(face)
        # 創建和保存STL網格，計算時保留反轉後的法向量
        mesh_data = mesh.Mesh(np.zeros(len(new_faces), dtype=mesh.Mesh.dtype))
        for i, face in enumerate(new_faces):
            for j in range(3):
                mesh_data.vectors[i][j] = points[face[j]]
            
            # 手動反轉法向量方向
            normal = np.cross(
                mesh_data.vectors[i][1] - mesh_data.vectors[i][0],
                mesh_data.vectors[i][2] - mesh_data.vectors[i][0]
            )
            mesh_data.normals[i] = -normal / np.linalg.norm(normal)  # 反轉法向量
            
        mesh_data.save(self.stl_output_path)
        
    def reconstruct(self):
        """執行完整的重建過程"""
        self.preprocess_image()
        points = self.generate_point_cloud()
        self.generate_mesh(points)


# # Define file paths
# image_path = './data0176.png'
# ply_path = './data0176.ply'
# stl_output_path = './data0176.stl'

# image = Image.open(image_path).convert('L')
# width, height = image.size
# min_x_value, max_x_value = width, 0
# max_value, min_value = 0, 255

# for y in range(height):
#     for x in range(width):
#         pixel_value = image.getpixel((x, y))
#         max_value = max(max_value, pixel_value)
#         min_value = min(min_value, pixel_value)
#         if pixel_value != 0:
#             min_x_value = min(min_x_value, x)
#             max_x_value = max(max_x_value, x)
# # Create an instance of the DentalModelReconstructor
# reconstructor = DentalModelReconstructor(image_path, ply_path, stl_output_path)

# # Call the reconstruct method to process the image and generate the STL file
# reconstructor.reconstruct()