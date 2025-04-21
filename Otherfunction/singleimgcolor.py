from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import argparse
import json
import base64

parser = argparse.ArgumentParser()
parser.add_argument("--model_dir", help="包含导出模型的目录")
parser.add_argument("--input_file", help="输入 PNG 图像文件")
parser.add_argument("--output_file", help="输出 PNG 图像文件")
a = parser.parse_args()


def apply_gan_model(model_dir, input_file, output_file):
    """
    將 GAN 模型應用於輸入圖片，並將結果保存到指定的輸出檔案中。

    參數：
    - model_dir: 模型檔案目錄路徑。
    - input_file: 輸入 PNG 圖片檔案路徑。
    - output_file: 輸出 PNG 圖片檔案路徑。
    """
    
    # 讀取輸入 PNG 圖像檔案的二進制數據
    with open(input_file, "rb") as f:
        input_data = f.read()

    # 創建包含 base64 編碼的輸入數據的字典
    input_instance = dict(input=base64.urlsafe_b64encode(input_data).decode("ascii"), key="0")
    input_instance = json.loads(json.dumps(input_instance))

    # 啟動 TensorFlow 會話
    with tf.Session() as sess:
        # 找到模型目錄中的最新檢查點
        checkpoint_path = tf.train.latest_checkpoint(model_dir)
        
        # 導入模型元圖並從檢查點恢復會話
        saver = tf.train.import_meta_graph(checkpoint_path + ".meta")
        saver.restore(sess, checkpoint_path)

        # 取得輸入和輸出的 tensor 名稱
        input_vars = json.loads(tf.get_collection("inputs")[0].decode())
        output_vars = json.loads(tf.get_collection("outputs")[0].decode())
        input_tensor = tf.get_default_graph().get_tensor_by_name(input_vars["input"])
        output_tensor = tf.get_default_graph().get_tensor_by_name(output_vars["output"])

        # 將輸入數據轉換為 NumPy 陣列並執行推斷
        input_value = np.array(input_instance["input"])
        output_value = sess.run(output_tensor, feed_dict={input_tensor: np.expand_dims(input_value, axis=0)})[0]

    # 創建包含 base64 編碼的輸出數據的字典
    output_instance = dict(output=output_value.decode("ascii"), key="0")

    # 解碼 base64 並將輸出數據寫入指定的檔案
    b64data = output_instance["output"]
    b64data += "=" * (-len(b64data) % 4)
    output_data = base64.urlsafe_b64decode(b64data.encode("ascii"))

    with open(output_file, "wb") as f:
        f.write(output_data)


# apply_gan_model(
#     model_dir="D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/toothdemo/",
#     input_file="D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/toothdemo/data0220-t.png",
#     output_file="D:/Weekly_Report/Thesis_Weekly_Report/paper/paper_Implementation/toothdemo/data0220-gan.png"
# )
# def main():
#     # 设置模型目录、输入文件和输出文件的默认值
#     a.model_dir = "D:/Users/user/Desktop/VTKcode/GAN/trainingdepth/share_data/Pixtopix0204exporttf2/"
#     a.input_file = "D:/Users/user/Desktop/VTKcode/GAN/trainingdepth/share_data/data0220.png"
#     a.output_file = "D:/Users/user/Desktop/VTKcode/GAN/trainingdepth/share_data/data0220-pixtopix.png"
#     # a.model_dir = input("請輸入模型目錄：")
#     # a.input_file = input("請輸入輸入 PNG 圖片檔案路徑：")
#     # a.output_file = input("請輸入輸出 PNG 影像檔案路徑：")
#     # 读取输入 PNG 图像文件的二进制数据
#     with open(a.input_file, "rb") as f:
#         input_data = f.read()

#     # 创建包含 base64 编码输入数据的输入实例字典
#     input_instance = dict(input=base64.urlsafe_b64encode(input_data).decode("ascii"), key="0")
#     input_instance = json.loads(json.dumps(input_instance))

#     # 启动 TensorFlow 会话
#     with tf.Session() as sess:
#         # 找到模型目录中的最新检查点
#         checkpoint_path = tf.train.latest_checkpoint(a.model_dir)
#         # 导入模型元图并从检查点还原会话
#         saver = tf.train.import_meta_graph(checkpoint_path + ".meta")
#         saver.restore(sess, checkpoint_path)
 
#         input_vars = json.loads(tf.get_collection("inputs")[0].decode())
#         output_vars = json.loads(tf.get_collection("outputs")[0].decode())
#         input_tensor = tf.get_default_graph().get_tensor_by_name(input_vars["input"])
#         output_tensor = tf.get_default_graph().get_tensor_by_name(output_vars["output"])

#         # 将输入数据转换为 NumPy 数组并运行推断
#         input_value = np.array(input_instance["input"])
#         output_value = sess.run(output_tensor, feed_dict={input_tensor: np.expand_dims(input_value, axis=0)})[0]

#     # 创建包含 base64 编码输出数据的输出实例字典
#     output_instance = dict(output=output_value.decode("ascii"), key="0")

#     # 解码 base64 并将输出数据写入指定文件
#     b64data = output_instance["output"]
#     b64data += "=" * (-len(b64data) % 4)
#     output_data = base64.urlsafe_b64decode(b64data.encode("ascii"))

#     with open(a.output_file, "wb") as f:
#         f.write(output_data)

# # 调用主函数
# main()
