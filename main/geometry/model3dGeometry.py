from geometry.geometry import Geometry
from plyfile import PlyData
import numpy as np

class Model3dGeometry(Geometry):
    def __init__(self, path):
        super().__init__()
        
        # load the .ply file from path
        with open(path, 'rb') as file:
            plyData = PlyData.read(file)
        
        # extract vertex positions from the .ply file
        vertex_data = plyData['vertex'].data
        vertex_positions = [[vertex['x'], vertex['y'], vertex['z']] for vertex in vertex_data]

        # FIXME: recenter the model3d about its centroid
        centroid = np.mean(vertex_positions, axis=0)
        vertex_positions = [[vertex[0] - centroid[0], vertex[1] - centroid[1], vertex[2] - centroid[2]] for vertex in vertex_positions] 

        # extract vertex colors if available
        if 'red' in vertex_data.dtype.names:
            vertex_colors = [[vertex['red'], vertex['green'], vertex['blue']] for vertex in vertex_data]
        else:
            # default to white if no color data is available
            print("No color data found in .ply file. Defaulting to white.")
            vertex_colors = [[1, 0.5, 0]] * len(vertex_positions)

        # extract vertex normals if available
        if 'nx' in vertex_data.dtype.names:
            vertex_normals = [[vertex['nx'], vertex['ny'], vertex['nz']] for vertex in vertex_data]
        else:
            print("No normal data found in .ply file. Computing normals.")
            vertex_normals = None


        # initialize lists to store data grouped by triangle face
        positionData = []
        colorData = []
        fnormalData = []
        vnormalData = []


        face_data = plyData['face'].data
        for face in face_data:
            # get indices of vertices in face
            vertex_indices = face[0]
            # get vertex positions and colors
            for i in range(3):
                vertex_index = vertex_indices[i]
                positionData.append(vertex_positions[vertex_index])
                colorData.append(vertex_colors[vertex_index])

                if vertex_normals is not None:
                    vnormalData.append(vertex_normals[vertex_index])
                

        
        fnormalData = self.calcFaceNormals(positionData)
        # print(f"vertexnormal: {len(vnormalData)}, facenormal: {len(fnormalData)}")

        if vertex_normals is None:
            vertex_normals = self.calcVertexNormals(vertex_positions, fnormalData, face_data)

            # group calculated vertex_normals by triangle face
            for face in face_data:
                vertex_indices = face[0]
                for i in range(3):
                    vertex_index = vertex_indices[i]
                    vnormalData.append(vertex_normals[vertex_index])

        

        # add attributes to the geometry object
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.addAttribute("vec3", "vertexNormal", vnormalData)
        self.addAttribute("vec3", "faceNormal", fnormalData)



    
    def calcFaceNormals(self, positionData):
        # compute normals for each face
        faceNormals = []
        for i in range(0, len(positionData), 3):
            P0 = positionData[i]
            P1 = positionData[i + 1]
            P2 = positionData[i + 2]
            v1 = np.array(P1) - np.array(P0)
            v2 = np.array(P2) - np.array(P0)
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            faceNormals.append(normal)
        return faceNormals
    
    def calcVertexNormals(self, vertex_positions, faceNormals, face_data):
        # Initialize a list of zero vectors for vertex normals
        vertex_count = len(vertex_positions)
        # FIXME: calculate vertex normals from vertex normals!!!!!!!
        vertex_normals = [np.array([0.0, 0.0, 0.0]) for _ in range(vertex_count)]
        
        # For each face, accumulate its normal to the vertices of the face
        for face_idx, face in enumerate(face_data):
            vertex_indices = face[0]  # Get the vertex indices for this face
            normal = faceNormals[face_idx]
            
            # Add the face normal to each vertex's normal
            for i in vertex_indices:
                vertex_normals[i] += normal
        
        # Normalize the accumulated vertex normals
        vertex_normals = [normal / np.linalg.norm(normal) if np.linalg.norm(normal) != 0 else [0.0, 0.0, 0.0] for normal in vertex_normals]
        
        return vertex_normals