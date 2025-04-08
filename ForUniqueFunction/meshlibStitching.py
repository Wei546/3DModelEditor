from meshlib import mrmeshpy

file_path = "resources/only_merge/merge_inlay_surface_0109.stl"
#載入 STL 檔案
nonClosedMesh = mrmeshpy.loadMesh(file_path)

original_file_name= file_path.split("/")[-1]
original_file_name = original_file_name.split(".")[0]

# 修復邊界
mrmeshpy.uniteCloseVertices(nonClosedMesh, nonClosedMesh.computeBoundingBox().diagonal() * 1e-6)

# 偏移操作
#設定偏移量
thickness = 0
params = mrmeshpy.GeneralOffsetParameters()  # 修改這裡
params.voxelSize = 1
params.signDetectionMode = mrmeshpy.SignDetectionMode.Unsigned
shell = mrmeshpy.thickenMesh(nonClosedMesh, thickness, params)

# 分析網格的拓撲，找出未封閉的邊界
holes = shell.topology.findHoleRepresentiveEdges()
print("Number of holes detected:", holes.size())
assert holes.size() >= 2
newFaces = mrmeshpy.FaceBitSet()
stitchParams = mrmeshpy.StitchHolesParams()
stitchParams.metric = mrmeshpy.getMinAreaMetric( shell )
stitchParams.outNewFaces = newFaces
# 將holes[0]和holes[1]之間找到對應點，並生成橋接面
mrmeshpy.buildCylinderBetweenTwoHoles(shell,holes[0],holes[1],stitchParams)

# 面細分
subdivSettings = mrmeshpy.SubdivideSettings()
subdivSettings.region = newFaces
subdivSettings.maxEdgeSplits = 10000000 # could be INT_MAX
subdivSettings.maxEdgeLen = 1
mrmeshpy.subdivideMesh(shell,subdivSettings)

# 平滑新面
mrmeshpy.positionVertsSmoothly(shell,mrmeshpy.getInnerVerts(shell.topology,newFaces))

#儲存修改後的網格
mrmeshpy.saveMesh(shell, f"for_test_stitched_{original_file_name}.stl")
