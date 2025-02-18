from vedo import Mesh, show

# Load your mesh (e.g., from a file)
mesh = Mesh("resources/test_input/GUITAR.stl")

# Subdivide the mesh (nsub specifies the number of subdivision iterations)
subdivided_mesh = mesh.subdivide(nsub=2)

# Display the original and subdivided mesh
show(mesh, subdivided_mesh, axes=1)
