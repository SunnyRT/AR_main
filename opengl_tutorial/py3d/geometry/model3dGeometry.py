from geometry.geometry import Geometry
from plyfile import PlyData

class Model3dGeometry(Geometry):
    def __init__(self, path):
        super().__init__()
        
        # load the .ply file from path
        with open(path, 'rb') as file:
            plyData = PlyData.read(file)
        
        # extract vertex positions from the .ply file
        vertex_data = plyData['vertex']
        vertex_positions = [[vertex['x'], vertex['y'], vertex['z']] for vertex in vertex_data]

        # extract vertex colors if available
        if 'red' in vertex_data.dtype.names:
            vertex_colors = [[vertex['red'], vertex['green'], vertex['blue']] for vertex in vertex_data]
        else:
            # default to white if no color data is available
            print("No color data found in .ply file. Defaulting to white.")
            vertex_colors = [[1, 1, 1]] * len(vertex_positions)


        # extract normal data if available
        if 'nx' in vertex_data.dtype.names:
            vertex_normals = [[vertex['nx'], vertex['ny'], vertex['nz']] for vertex in vertex_data]
        else:
            # compute normals if no normal data is available
            print("No normal data found in .ply file. Computing normals.")
            vertex_normals = []

            

        # initialize lists to store data grouped by triangle face
        positionData = []
        colorData = []

        face_data = plyData['face']
        for face in face_data:
            # get indices of vertices in face
            vertex_indices = face[0]
            # get vertex positions and colors
            for i in range(3):
                vertex_index = vertex_indices[i]
                positionData.append(vertex_positions[vertex_index])
                colorData.append(vertex_colors[vertex_index])
        
