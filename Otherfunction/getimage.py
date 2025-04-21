import cv2
import numpy as np

def apply_blue_mask(original_image_array, blue_mask_array,outdata_name):
    # original_image = cv2.imread(os.path.join(original_image_path))
    # blue_mask_filename = os.path.join(blue_mask_path)
    # 將原始圖像的白色部分變為黑色
    white_mask = cv2.inRange(original_image_array, np.array([255]), np.array([255]))
    original_image_array[np.where(white_mask > 0)] = [0]

    # 應用藍色區塊掩碼
    blue_mask_gray = cv2.cvtColor(blue_mask_array, cv2.COLOR_BGR2GRAY)
    _, thresholded_mask = cv2.threshold(blue_mask_gray, 1, 255, cv2.THRESH_BINARY)
    
    # 使用藍色掩碼到原始圖像
    result_image_array = cv2.bitwise_and(original_image_array, original_image_array, mask=thresholded_mask)

    cv2.imwrite(outdata_name, result_image_array)



# # 原始图像文件夹和蓝色区块图像文件夹
# original_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/combineimage/"
# blue_mask_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/bluemask/"
# output_folder = "D:/Users/user/Desktop/papergan/paper/crown/traincode/final/"

# # 确保输出文件夹存在
# os.makedirs(output_folder, exist_ok=True)

# # 遍历原始图像文件夹
# for filename in os.listdir(original_folder):
#     if filename.endswith(".png"):  # 确保是PNG文件
#         original_image = cv2.imread(os.path.join(original_folder, filename))
#         blue_mask_filename = os.path.join(blue_mask_folder, filename)

#         # 处理一些白色部分并将其变为黑色
#         white_mask = cv2.inRange(original_image, (255, 255, 255), (255, 255, 255))
#         original_image[np.where(white_mask > 0)] = [0, 0, 0]

#         # 查找对应的蓝色区块图像
#         if os.path.exists(blue_mask_filename):
#             blue_mask_image = cv2.imread(blue_mask_filename)
#             blue_mask_gray = cv2.cvtColor(blue_mask_image, cv2.COLOR_BGR2GRAY)
#             _, thresholded_mask = cv2.threshold(blue_mask_gray, 1, 255, cv2.THRESH_BINARY)
#             # 应用掩码
#             result_image = cv2.bitwise_and(original_image, original_image, mask=thresholded_mask)
#             result_image_8bit = cv2.convertScaleAbs(result_image)

#             # 保存结果图像到输出文件夹
#             output_filename = os.path.join(output_folder, filename)
#             cv2.imwrite(output_filename, result_image_8bit)
#             # cv2.imwrite(output_filename, result_image)
           

# print("操作完成。")
