import vtk
import pymeshlab
def stl_to_obj(input_path, output_path):
    # 讀取 STL
    reader = vtk.vtkSTLReader()
    reader.SetFileName(input_path)
    reader.Update()
    
    # 清理與三角化（保險做法）
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(reader.GetOutput())
    cleaner.Update()
    
    triangulator = vtk.vtkTriangleFilter()
    triangulator.SetInputData(cleaner.GetOutput())
    triangulator.Update()
    
    # 輸出成 OBJ
    writer = vtk.vtkOBJWriter()
    writer.SetInputData(triangulator.GetOutput())
    writer.SetFileName(output_path)
    writer.Write()
    
    print(f"✅ Converted {input_path} to {output_path}")


def remesh_with_pymeshlab(input_obj, output_obj, target_edge_len=0.4):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_obj)

    # 均勻三角重建
    ms.apply_filter('meshing_isotropic_explicit_remeshing', 
                    targetlen=pymeshlab.PureValue(target_edge_len))
    
    ms.save_current_mesh(output_obj)
    print(f"✅ Remeshed mesh saved to {output_obj}")
def auto_remesh_to_target_points(input_path, output_path, target_points, tol=10):
    best_mesh = None
    best_count = float('inf')
    best_len = None

    for edge_len in [0.5, 0.4, 0.35, 0.3, 0.28, 0.26, 0.24, 0.22, 0.2]:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_path)
        ms.apply_filter('meshing_isotropic_explicit_remeshing',
                        targetlen=pymeshlab.PureValue(edge_len))

        v_count = ms.current_mesh().vertex_number()
        print(f"EdgeLen: {edge_len:.3f} → Vertices: {v_count}")

        if abs(v_count - target_points) < abs(best_count - target_points):
            best_mesh = ms
            best_count = v_count
            best_len = edge_len

        if abs(v_count - target_points) <= tol:
            break

    if best_mesh:
        best_mesh.save_current_mesh(output_path)
        print(f"\n✅ Best match: {best_len} → {best_count} points")
        print(f"Saved to: {output_path}")
    else:
        print("❌ No suitable remesh found.")
def auto_remesh_to_target_points_v2(input_path, output_path, target_points, tol=10):
    best_mesh = None
    best_count = float('inf')
    best_len = None

    for edge_len in [0.5, 0.4, 0.35, 0.3, 0.28, 0.26, 0.24, 0.22, 0.2]:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_path)
        ms.apply_filter('meshing_isotropic_explicit_remeshing',
                        targetlen=pymeshlab.PureValue(edge_len))

        v_count = ms.current_mesh().vertex_number()
        if abs(v_count - target_points) < abs(best_count - target_points):
            best_mesh = ms
            best_count = v_count
            best_len = edge_len

        if abs(v_count - target_points) <= tol:
            break

    if best_mesh:
        best_mesh.save_current_mesh(output_path)
        return best_len, best_count, output_path
    else:
        return None, None, None

# Remesh repair mesh to match 4058 points
remesh_input_path = 'resources/template_model/template_defect_4200_repair_edit.obj'
remesh_output_path = 'resources/template_model/template_defect_4200_repair.obj'
target_points = 3987

best_len, best_count, saved_path = auto_remesh_to_target_points_v2(
    remesh_input_path, remesh_output_path, target_points, tol=5
)

best_len, best_count, saved_path

# 亂猜法resamole
# remesh_with_pymeshlab("resources/template_model/aligned_model_only_align.obj", "resources/template_model/aligned_model_only_template_repair.obj")
# remesh_with_pymeshlab("resources/template_model/data0075down.obj", "resources/template_model/data0075down_template.obj")

# 範例使用
# stl_to_obj("resources/template_model/aligned_model_only_align.stl", "resources/template_model/aligned_model_only_align.obj")
# stl_to_obj("resources/template_model/data0075down.stl", "resources/template_model/data0075down.obj")
# auto_remesh_to_target_points(
#     input_path="resources/template_model/template_defect_4200_repair.obj",
#     output_path="resources/template_model/template_defect_4200_repair.obj",
#     target_points=4200
# )