import pymeshlab

ms = pymeshlab.MeshSet() #實體化pymeshlab套件
ms.load_new_mesh("resources/test_stitch/merge_0075.stl") #載入檔案

ms.apply_filter("meshing_isotropic_explicit_remeshing",
                iterations=3, #把 isotropic remesh 操作重複執行 n 次
                targetlen=pymeshlab.PercentageValue(0.5), #讓remesh的網格邊長接近Bounding Box的對角線長度 × 0.5%
                adaptive=True, #細節較多的區域生成較小的三角形；在平坦區域生成較大的三角形
                featuredeg=30, #將30度以上的邊在重網格化時保留
                checksurfdist=True, # 確保新生成的網格與原始網格偏離程度
                maxsurfdist=pymeshlab.PercentageValue(0.5),  # 確保新生成的網格與原始網格偏離程度
                splitflag=True,#提高局部網格的細分程度
                collapseflag=True,#避免生成過於密集的網格
                swapflag=True,#避免奇怪的瘦長形狀的網格
                smoothflag=True,#拉普拉斯平滑
                reprojectflag=True)#避免平滑中頂點偏離原始形狀過多
ms.save_current_mesh("pymeshlab_output_model.stl") # 儲存修改後的網格
