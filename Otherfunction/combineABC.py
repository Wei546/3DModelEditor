import cv2
import numpy as np

def merge_images(image_A, image_B, image_C, output_path):
    # 读取三张图像
    im_A = cv2.imread(image_A, cv2.IMREAD_UNCHANGED)
    im_B = cv2.imread(image_B, cv2.IMREAD_UNCHANGED)
    im_C = cv2.imread(image_C, cv2.IMREAD_UNCHANGED)

    # 检查图像是否成功加载
    if im_A is None or im_B is None or im_C is None:
        raise ValueError("One or more input images could not be loaded.")

    # 确保所有图像都是 256×256
    target_size = (256, 256)
    im_A = cv2.resize(im_A, target_size)
    im_B = cv2.resize(im_B, target_size)
    im_C = cv2.resize(im_C, target_size)

    # 拼接图像 (水平拼接)
    im_ABC = np.concatenate([im_A, im_B, im_C], axis=1)

    # 保存拼接后的图像
    cv2.imwrite(output_path, im_ABC)
    print(f"Saved merged image at {output_path}")

# # 示例用法
# image_A = "path/to/image_A.png"
# image_B = "path/to/image_B.png"
# image_C = "path/to/image_C.png"
# output_path = "path/to/output.png"

# merge_images(image_A, image_B, image_C, output_path)