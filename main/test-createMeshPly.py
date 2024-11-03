import open3d as o3d
import numpy as np

# Define vertices, normals, and triangular faces
vertices = np.array([
    [10.02307591, 6.63091756, 50.36140433],
    [10.57991346, 6.99930187, 39.27037124],
    [11.13675101, 7.36768618, 28.17933814],
    [11.69358856, 7.73607048, 17.08830505],
    [12.25042611, 8.10445479, 5.99727196],
    [12.80726366, 8.4728391, -5.09376114],
    [13.36410121, 8.84122341, -16.18479423],
    [13.92093876, 9.20960772, -27.27582732],
    [14.47777631, 9.57799203, -38.36686041],
    [15.03461386, 9.94637634, -49.45789351],
    [9.10544681, 5.17647859, 50.27445104],
    [9.61130497, 5.46406073, 39.17858721],
    [10.11716313, 5.75164287, 28.08272338],
    [10.62302128, 6.03922502, 16.98685955],
    [11.12887944, 6.32680716, 5.89099571]
], dtype=np.float64)

normals = np.array([
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.84481859, -0.53448416, 0.02466237],
    [0.79520613, -0.60599094, 0.02054724],
    [0.76789639, -0.64030938, 0.01841273],
    [0.76789639, -0.64030938, 0.01841273],
    [0.76789639, -0.64030938, 0.01841273],
    [0.76789639, -0.64030938, 0.01841273]
], dtype=np.float64)

faces = np.array([
    [0, 10, 1],
    [1, 10, 11],
    [1, 11, 2],
    [2, 11, 12],
    [2, 12, 3],
    [3, 12, 13],
    [3, 13, 4],
    [4, 13, 14],
    [4, 14, 5],
    [5, 14, 15]
], dtype=np.int32)



# Define vertices and faces
vertices = np.array([[-1, 2, 0],
                     [1, 2, 0],
                     [0, 0, 0],
                     [2, 0, 0]])
faces = np.array([[0, 2, 1],
                  [1, 2, 3]], dtype=np.int32)

# Create the Open3D TriangleMesh object
mesh = o3d.geometry.TriangleMesh()
mesh.vertices = o3d.utility.Vector3dVector(vertices)
mesh.triangles = o3d.utility.Vector3iVector(faces)

# Check if the mesh is a vertex manifold
if not mesh.is_vertex_manifold():
    print("The mesh has non-manifold vertices.")
else:
    print("The mesh has no non-manifold vertices.")

# Visualize the mesh
o3d.visualization.draw_geometries([mesh])

# Save the mesh to a PLY file
o3d.io.write_triangle_mesh("test_mesh.ply", mesh)
print("Mesh saved as 'test_mesh.ply'")
