import open3d as o3d
import numpy as np



def _calcVertexNormals(vertex_positions, face_indices):

    vertex_normals = np.zeros_like(vertex_positions)

    for face in face_indices:
        v0, v1, v2 = vertex_positions[face]
        normal = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(normal)
        if norm != 0:
            normal /= norm
        vertex_normals[face] += normal
    
    # Normalize the accumulated normals
    norms = np.linalg.norm(vertex_normals, axis=1, keepdims=True)
    vertex_normals = np.divide(vertex_normals, norms, where=norms != 0)

    return vertex_normals



# Create or load a mesh using Open3D
mesh = o3d.geometry.TriangleMesh.create_sphere()
mesh.compute_vertex_normals()

# Get Open3D-computed normals
o3d_normals = np.asarray(mesh.vertex_normals)

# Run your custom function
vertex_positions = np.asarray(mesh.vertices)
face_indices = np.asarray(mesh.triangles)
custom_normals = _calcVertexNormals(vertex_positions, face_indices)

# Compare results
difference = np.linalg.norm(o3d_normals - custom_normals, axis=1)
print(f"Max difference between custom and Open3D normals: {np.max(difference)}")
