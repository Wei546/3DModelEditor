        mesh_stitch.paint_uniform_color([0.0, 1.0, 0.0])          # Green

        # Visualize both meshes together
        o3d.visualization.draw_geometries([mesh_icp_only_merge, mesh_stitch])