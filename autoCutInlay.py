from vedo import *

file_path = "resources/align_file/smooth_align_data0075down.stl"
# 載入模型（支援 .stl, .ply, .obj 等）
mesh = load(file_path)
file_name = file_path.split("/")[-1].split(".")[0]
# 顯示模型
show(mesh, f"{file_name}")