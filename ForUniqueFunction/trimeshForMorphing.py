# Re-import required modules due to kernel reset
import trimesh
import numpy as np

# Reload meshes
mesh_a = trimesh.load("/mnt/data/tr_reg_013.ply", process=False)
mesh_b = trimesh.load("/mnt/data/tr_reg_014.ply", process=False)

# Ensure vertex counts match
if len(mesh_a.vertices) != len(mesh_b.vertices):
    result = "❌ Vertex count mismatch: cannot perform morphing."
else:
    # Linear interpolation (t=0.5)
    vertices_a = np.array(mesh_a.vertices)
    vertices_b = np.array(mesh_b.vertices)
    vertices_mid = 0.5 * vertices_a + 0.5 * vertices_b
    faces = np.array(mesh_a.faces)

    # Create morphed mesh
    morphed_mesh = trimesh.Trimesh(vertices=vertices_mid, faces=faces, process=False)
    morphed_path = "trimesh.ply"
    morphed_mesh.export(morphed_path)
    result = morphed_path

result
