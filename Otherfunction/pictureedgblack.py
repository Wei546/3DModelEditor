from PIL import Image
import os
import numpy as np
from scipy.ndimage import convolve

# base_folder = "D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/"
# input_folders = ["c++bug"]
# output_folder_base_prep = "c++bug//Downred"
# output_folder_base_op = "c++bug//Upyellow"



# 這邊就是找一張圖的邊界，並且填充color的紅色邊界線
def get_image_bound(input_image_path, color=(255, 0, 0)):
    # 打開圖像並轉換為灰階
    img = Image.open(input_image_path).convert('L')
    
    # 將圖像轉換為 NumPy 陣列
    img_array = np.array(img)
    
    # 將像素值小於10的地方設為0
    img_array = np.where(img_array >= 10, img_array, 0)
    
    # 創建一個RGB陣列，初始化為黑色
    boundary_img_array = np.zeros((*img_array.shape, 3), dtype=np.uint8)
    
    # 獲取邊界條件，檢查上下左右是否是邊界點
    up_shift = np.roll(img_array, -1, axis=0)
    down_shift = np.roll(img_array, 1, axis=0)
    left_shift = np.roll(img_array, -1, axis=1)
    right_shift = np.roll(img_array, 1, axis=1)
    
    # 找到邊界像素點
    boundary_mask = ((img_array > 0) & 
                     ((up_shift == 0) | (down_shift == 0) | (left_shift == 0) | (right_shift == 0)))
    
    # 將邊界點設置為指定顏色
    boundary_img_array[boundary_mask] = color
    
    # 將NumPy陣列轉換為PIL圖像並返回
    boundary_img = Image.fromarray(boundary_img_array)
    
    return boundary_img

def mark_boundary_points(input_image_path, output_folder, color=(255, 0, 0)):
    # 開啟影像
    img = Image.open(input_image_path)

    # 確保影像是8位元深度的灰階影像
    if img.mode != 'L':
        img = img.convert('L')

    # 將影像轉換為 numpy 陣列
    img_array = np.array(img)

    # 建立一個新的 RGB 映像用於標記邊界點
    boundary_img_array = np.zeros((img_array.shape[0], img_array.shape[1], 3), dtype=np.uint8)

    # 建立一個遮罩來標記邊界點
    boundary_mask = np.zeros_like(img_array, dtype=bool)

    # 標記所有非零像素點
    non_zero_mask = img_array > 0

    # 使用卷積核來標記邊界點
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    edge_mask = convolve(non_zero_mask.astype(float), kernel, mode='constant', cval=0.0) != 0

    # 更新邊界掩碼
    boundary_mask[edge_mask] = True

    # 將邊界遮罩應用於邊界影像數組
    boundary_img_array[boundary_mask] = color

    # 將 numpy 陣列轉換回影像
    boundary_img = Image.fromarray(boundary_img_array)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 建立輸出檔案路徑
    output_image_path = os.path.join(output_folder, os.path.basename(input_image_path))
    boundary_img.save(output_image_path)

# # 設定輸出資料夾
# output_folder_prep = os.path.join(base_folder, output_folder_base_prep)
# output_folder_op = os.path.join(base_folder, output_folder_base_op)

# # 如果輸出資料夾不存在，則創建它們
# if not os.path.exists(output_folder_prep):
#     os.makedirs(output_folder_prep)

# if not os.path.exists(output_folder_op):
#     os.makedirs(output_folder_op)

# # 遍歷所有指定的資料夾

# for folder_name in input_folders:
#     folder_path = os.path.join(base_folder, folder_name, "Up")

#     # 處理當前資料夾中的圖像
#     image_files = os.listdir(folder_path)
#     for image_file in image_files:
#         if image_file.endswith(".png"):
#             input_image_path = os.path.join(folder_path, image_file)
#             mark_boundary_points(input_image_path, output_folder_op, color=(255, 255, 0)) 


# for folder_name in input_folders:
#     folder_path = os.path.join(base_folder, folder_name, "Down")

#     # 處理當前資料夾中的圖像
#     image_files = os.listdir(folder_path)
#     for image_file in image_files:
#         if image_file.endswith(".png"):
#             input_image_path = os.path.join(folder_path, image_file)
#             mark_boundary_points(input_image_path, output_folder_prep)
