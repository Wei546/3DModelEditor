import cv2
import numpy as np

# 定義一個函數，用於處理一對影像，其中第一張影像包含紅色邊框，第二張影像是深度圖像
# 這個函數將從第二張影像中提取邊框，並將其填充為白色，同時保留原始深度值
# 最後，將處理後的影像保存到指定的路徑
# 因為原本的深度圖 在白色區域內有些會有破洞 透過邊框內方式填滿255
def process_image_pair(img1, img2_path, output_path):
    # 將第一張影像從 RGB 轉換為 BGR 格式
    img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
    
    # 讀取第二張影像，將其轉為灰階
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    # 提取第二張影像的紅色通道，並進行二值化，將邊框部分設為白色（255），其餘部分為黑色（0）
    _, binary_mask = cv2.threshold(img2, 1, 255, cv2.THRESH_BINARY)

    # 根據二值化的邊框，找到輪廓
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 創建一個與 img2 同大小的空白遮罩圖像
    mask = np.zeros(img2.shape, dtype=np.uint8)

    # 在遮罩上繪製所有的輪廓，並將輪廓內部填滿（255表示白色）
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)

    # 將原始影像 (img2) 複製一份，並對遮罩內的深度值為0的像素設為255
    result = img2.copy()
    result[(mask > 0) & (img2 == 0)] = 255
    
    # 處理圖像中某些區域的像素，使得那些從小於220變為255，再從255變回小於220的區間內的像素被重置為0。
    # 這通常用於去除某些圖像中的小區域，圖像邊緣或不需要的干擾部分。
    # 找出從像素值小於220變為255的位置（起點）
    start_positions = (result[:, :-1] < 220) & (result[:, 1:] == 255)
    
    # 找出從像素值為255變為小於220的位置（終點）
    end_positions = (result[:, :-1] == 255) & (result[:, 1:] < 220)

    # 遍歷每一行，將找到的區間（從小於220變為255）設為0
    for row in range(result.shape[0]):
        # 找到該行中的起點和終點位置
        starts = np.where(start_positions[row])[0]
        ends = np.where(end_positions[row])[0]

        # 確保每行的起點和終點數量一致
        if len(starts) == len(ends):
            for start, end in zip(starts, ends):
                # 將起點和終點之間的區間內的像素值設為0
                result[row, start:end+1] = 0

    # 儲存處理後的影像到指定路徑
    cv2.imwrite(output_path, result)

#     # 保存結果
# folder1 = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Downred/' # 包含第一張圖（紅色邊框）的資料夾
# folder2 = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Down/' # 包含第二張圖（深度圖）的資料夾
# output_folder = 'D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/remesh/c++bug/Downfill/' # 輸出結果的資料夾

# # 確保輸出資料夾存在
# if not os.path.exists(output_folder):
#  os.makedirs(output_folder)

# # 遍歷資料夾
# for filename in os.listdir(folder1):
#     if filename.endswith(('.png', '.jpg', '.jpeg')): # 可以根據需要調整檔案類型
#         img1_path = os.path.join(folder1, filename)
#         img2_path = os.path.join(folder2, filename)

#         # 檢查對應的檔案是否存在
#         if os.path.exists(img2_path):
#             output_path = os.path.join(output_folder, filename)
#             process_image_pair(img1_path, img2_path, output_path)
#             print(f"Processed: {filename}")
#         else:
#             print(f"Skipped: {filename} (No matching file in folder2)")

# print("Processing completed.")


