from geometry.geometry import Geometry
import numpy as np

class ProjectorGeometry(Geometry):

    def __init__(self, msPos, contourVertWorldPos_segments, n, f, delta, color):
        super().__init__()
        
        numSamples = int((f-n)/delta) # is +1 needed?
        print(f"projector per-ray numSamples : {numSamples} from n: {n}, f: {f}, delta: {delta}")
        if numSamples <= 0:
            pass # FIXME: throw error

        positionData_segments = []
        colorData_segments = []
        normalData_segments = []
        rayData_segments = []

        vertex_positions_segments = []
        vertex_colors_segments = []
        vertex_normals_segments = []
        vertex_rays_segments = []

        rayIdOffset = 0

        for i, contourVertWorldPos in enumerate(contourVertWorldPos_segments):
            numRays = len(contourVertWorldPos)

            # Calculate sampled points along each ray
            t_values = np.linspace(0, 1, numSamples).reshape(1,-1,1)  # Sampling along the ray
            rayDirs = contourVertWorldPos - msPos
            rayDirsNormalized = rayDirs / np.linalg.norm(rayDirs, axis=1)[:, None]

            nearPoints = msPos + rayDirsNormalized * n
            farPoints = msPos + rayDirsNormalized * f
            sampledPoints = (1 - t_values) * nearPoints[:, None] + t_values * farPoints[:, None] # Shape: (numRays, numSamples, 3)
            vertex_positions = sampledPoints.reshape(-1, 3) # Shape: (numRays*numSamples, 3)
            vertex_rays = np.repeat(np.arange(numRays), numSamples)
            vertex_colors = np.repeat(np.array([color]), numRays*numSamples, axis=0)

            face_indices, rayData, rayIdOffset = self._calcFaceAndRayIndices(numRays, numSamples, rayIdOffset)
            # print(f"numRays: {numRays}, numSamples: {numSamples}, face_indices: {np.array(face_indices).shape}")
            # print(f"rayData values: {np.unique(rayData)}")
            vertex_normals= self._calcVertexNormals(vertex_positions, face_indices)
            # print(f"before arranging, vertexpos: {np.array(vertex_positions).shape}, vertexnormal: {np.array(vertex_normals).shape}")

            positionData, colorData, vnormalData = self._arrangeVertexData(vertex_positions, face_indices, vertex_colors, vertex_normals)
            # print(f"cone vertexpos: {np.array(positionData).shape}, cone vertexcolor:{np.array(colorData).shape}, cone vertexnormal: {np.array(vnormalData).shape}")
            positionData_segments.append(positionData)
            colorData_segments.append(colorData)
            normalData_segments.append(vnormalData)
            rayData_segments.append(rayData)

            vertex_positions_segments.append(vertex_positions)
            vertex_colors_segments.append(vertex_colors)
            vertex_normals_segments.append(vertex_normals)
            vertex_rays_segments.append(vertex_rays)

            # # Debugging:
            # coneMeshNormal = self._createConeNormalMesh(vertex_positions, vertex_normals)
            # self.rayMesh.add(coneMeshNormal)


        positionData_segments = np.concatenate(positionData_segments, axis=0)
        colorData_segments = np.concatenate(colorData_segments, axis=0)
        normalData_segments = np.concatenate(normalData_segments, axis=0)
        rayData_segments = np.concatenate(rayData_segments, axis=0)

        vertex_positions_segments = np.concatenate(vertex_positions_segments, axis=0)
        vertex_colors_segments = np.concatenate(vertex_colors_segments, axis=0)
        vertex_normals_segments = np.concatenate(vertex_normals_segments, axis=0)
        vertex_rays_segments = np.concatenate(vertex_rays_segments, axis=0)
        
        # Debugging print
        # print(f"rayData_segments values: {np.unique(rayData_segments)}")
        # print(f"positionData_segments: {positionData_segments.shape}, colorData_segments: {colorData_segments.shape}, rayData_segments: {rayData_segments.shape}")


        # Add triangulated attributes to the geometry object for shading
        self.addAttribute("vec3", "vertexPosition", positionData_segments)
        self.addAttribute("vec3", "vertexColor", colorData_segments)
        self.addAttribute("vec3", "vertexNormal", normalData_segments)
        self.addAttribute("int", "vertexRay", rayData_segments)
        # self.addAttribute("vec3", "faceNormal", fnormalData) # TODO: add face normals

        # Add non-duplicated attributes to the geometry object for ICP computation
        self.addAttribute("vec3", "uniqueVertexPosition", vertex_positions_segments)
        self.addAttribute("vec3", "uniqueVertexColor", vertex_colors_segments)
        self.addAttribute("vec3", "uniqueVertexNormal", vertex_normals_segments)
        self.addAttribute("int", "uniqueVertexRay", vertex_rays_segments)
        self.countVertices()
                





    def _calcFaceAndRayIndices(self, numRays, numSamples, rayIdOffset):
        faces = []
        rays = []
        # print(f"numRays: {numRays}")
        # print(f"rayidoffset: {rayIdOffset}")
        for i in range(numRays-1):
            for j in range(numSamples-1):
                idx0 = i * numSamples + j       #(i,j)
                idx1 = (i + 1) * numSamples + j #(i+1,j)
                idx2 = idx0 + 1                 #(i,j+1)
                idx3 = idx1 + 1                 #(i+1,j+1)
                faces.append([idx0, idx1, idx2])
                faces.append([idx2, idx1, idx3])
                rays.extend([i, i+1, i])
                rays.extend([i, i+1, i+1])

        rays = np.array(rays) + rayIdOffset
        rayIdOffset += numRays
        return faces, rays, rayIdOffset

                
    def _calcVertexNormals(self, vertex_positions, face_indices):

        vertex_normals = np.zeros_like(vertex_positions)

        for face in face_indices:
            v0, v1, v2 = vertex_positions[face]
            normal = np.cross(v1 - v0, v2 - v0)
            norm = np.linalg.norm(normal)
            if norm != 0:
                normal /= norm
            else:
                print(norm, v0, v1, v2)
            vertex_normals[face] += normal
        
        # Normalize the accumulated normals, setting almost-zero norms to [0, 0, 0]
        norms = np.linalg.norm(vertex_normals, axis=1, keepdims=True)
        vertex_normals = np.where(norms > 1e-8, vertex_normals / norms, 0)

        return vertex_normals
    
    def _arrangeVertexData(self, vertex_positions, face_indices, vertex_colors ,vertex_normals):
        positionData = vertex_positions[face_indices].reshape(-1, 3)
        colorData = vertex_colors[face_indices].reshape(-1, 3)
        vnormalData = vertex_normals[face_indices].reshape(-1, 3)

        return positionData, colorData, vnormalData
    


            