from geometry.geometry import Geometry
import open3d as o3d
import numpy as np

class Model3dGeometry(Geometry):
    def __init__(self, path):
        super().__init__()
        
        # load the .ply file from path
        mesh = o3d.io.read_triangle_mesh(path)
        
        # extract vertex positions from the .ply file
        vertex_positions = np.asarray(mesh.vertices)
        # FIXME: recenter the model3d about its centroid
        centroid = np.mean(vertex_positions, axis=0)
        vertex_positions = [[vertex[0] - centroid[0], vertex[1] - centroid[1], vertex[2] - centroid[2]] for vertex in vertex_positions] 

        # extract vertex colors if available
        if mesh.has_vertex_colors():
            vertex_colors = np.asarray(mesh.vertex_colors)
        else:
            # default to white if no color data is available
            print("No color data found in .ply file. Defaulting to white.")
            vertex_colors = [[1.0, 1.0, 1.0]] * len(vertex_positions)

        # extract vertex normals if available
        if mesh.has_vertex_normals():
            vertex_normals = np.asarray(mesh.vertex_normals)
        else:
            print("No normal data found in .ply file. Computing normals.")
            mesh.compute_vertex_normals()
            vertex_normals = np.asarray(mesh.vertex_normals)

        # compute face normals
        mesh.compute_triangle_normals()
        fnormalData = np.asarray(mesh.triangle_normals)



        # initialize lists to store data grouped by triangle face
        positionData = []
        colorData = []
        vnormalData = []


        face_data = np.asarray(mesh.triangles)
        for face in face_data:
            # get indices of vertices in face
            vertex_indices = face
            # get vertex positions and colors
            for i in range(3):
                vertex_index = vertex_indices[i]
                positionData.append(vertex_positions[vertex_index])
                colorData.append(vertex_colors[vertex_index])
                vnormalData.append(vertex_normals[vertex_index])
                

        print(f"vertexpos: {np.array(positionData).shape}, vertexcolor:{np.array(colorData).shape}, vertexnormal: {np.array(vnormalData).shape}, facenormal: {np.array(fnormalData).shape}")

        

        # add attributes to the geometry object
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.addAttribute("vec3", "vertexNormal", vnormalData)
        self.addAttribute("vec3", "faceNormal", fnormalData)



    