from PIL import Image

def calculate_image_difference(image1, image2, output_image_path=None):
    image1 = Image.open(image1)
    image2 = Image.open(image2)

    # 將圖像數據轉換為像素列表
    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())

    new_data = []

    # 計算像素差異
    for i in range(len(pixels1)):
        new = abs(pixels2[i] - pixels1[i])
        new_data.append(new)

    # 創建新圖像並填充差異數據
    new_image = Image.new(image1.mode, image1.size)
    new_image.putdata(new_data)

    # 如果指定了輸出路徑，則保存圖像
    if output_image_path:
        new_image.save(output_image_path)

    return new_image
# # 資料夾路徑
# folder_path1 = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/depthfordifferentr/DCPRdepth/r=0/Prepfill/"
# folder_path2 = "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/depthfordifferentr/DCPRdepth/r=0/up/"

# # 輸出資料夾
# output_folder =  "D:/Users/user/Desktop/weiyundontdelete/GANdata/trainingdepth/DAISdepth/alldata/depthfordifferentr/DCPRdepth/r=0/combineimage1"

# # 確保輸出資料夾存在
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# # 取得資料夾中所有檔案名稱
# files1 = os.listdir(folder_path1)
# files2 = os.listdir(folder_path2)

# # 遍歷第一個資料夾
# for filename1 in files1:
#     if filename1 in files2:
#         image1 = Image.open(os.path.join(folder_path2, filename1))
#         image2 = Image.open(os.path.join(folder_path1, filename1))

#         pixels1 = list(image1.getdata())
#         pixels2 = list(image2.getdata())

#         new_data = []

#         for i in range(len(pixels1)):
#             new = abs(pixels2[i] - pixels1[i])
#             new_data.append(new)

#         new_image = Image.new(image1.mode, image1.size)
#         new_image.putdata(new_data)

#         # 生成輸出檔案名稱
#         output_filename = os.path.join(output_folder, filename1)

#         new_image.save(output_filename)

# print("處理完成。結果已儲存在output資料夾中。")
