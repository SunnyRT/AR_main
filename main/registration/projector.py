from core_ext.mesh import Mesh
from geometry.geometry import Geometry
from material.lineMaterial import LineMaterial
from material.surfaceMaterial import SurfaceMaterial
from material.lambertMaterial import LambertMaterial

import numpy as np
import open3d as o3d
import pdb



class Projector(object):

    def __init__(self, camera, contourMesh, lineWidth=1, color=[1,1,0], alpha=0.3, near=500, far=750, delta=1, 
                 visibleRay=True, visibleCone=True):
        

        self.n = near
        self.f = far
        self.delta = delta
        self.color = color
        self.alpha = alpha

        
        """"""""""""""" intialize ray mesh """""""""""""""
        self.rayMesh = self._createRayMesh(camera, contourMesh, lineWidth)
        self.coneMesh = self._createConeMesh()
        self.rayMesh.add(self.coneMesh)
        if not visibleRay:
            self.rayMesh.visible = False
        if not visibleCone:
            self.coneMesh.visible = False
        


    def _createRayMesh(self, camera, contourMesh, lineWidth):
        """"""""""""""" create projector ray geometry"""""""""""""""
        rayGeometry = Geometry()
        positionData = []
        colorData = []

        self.cameraPos= camera.getWorldPosition()
        contourPos = contourMesh.getWorldPosition()

        # extract vertices positions from contourMesh
        contourVertPos_segments = contourMesh.geometry.positionData_segments # list of arrays for each segment
        # displace each vertex by the contour position
        contourVertWorldPos_segments = [segment + contourPos for segment in contourVertPos_segments]
        self.contourVertWorldPos_segments = contourVertWorldPos_segments # store for later use

        
        contourVertWorldPos_flatten = np.concatenate(contourVertWorldPos_segments, axis=0) # flatten the list of arrays
        cameraPos_array = np.tile(self.cameraPos, (len(contourVertWorldPos_flatten), 1))
    
        # Stack cameraPos and contourVertWorldPos alternatively
        positionData = np.empty((len(contourVertWorldPos_flatten) * 2, 3), dtype=contourVertWorldPos_flatten.dtype)
        positionData[0::2] = cameraPos_array  # Camera positions in even indices; "0::2" selects every 2nd element starting from 0
        positionData[1::2] = contourVertWorldPos_flatten  # Contour vertices in odd indices; "1::2" selects every 2nd element starting from 1


        colorData = np.tile(self.color, (len(positionData), 1)) 
        


        rayGeometry.addAttribute("vec3", "vertexPosition", positionData)
        rayGeometry.addAttribute("vec3", "vertexColor", colorData)
    
        """""""""""""""create projector ray material"""""""""""""""
        rayMaterial = LineMaterial({"useVertexColors":True,
                            "lineWidth":lineWidth,
                            "lineType":"segments", 
                            "alpha":self.alpha})

        return Mesh(rayGeometry, rayMaterial)




    
    def _createConeMesh(self):

        
        """"""""""""""" create projector cone geometry, iterate for each contour segment!!! """""""""""""""
        print(f"delta in createConeMesh: {self.delta}")
        numSamples = int((self.f-self.n)/self.delta) #FIXME: is +1 needed?
        print(f"nearPlane: {self.n}, farPlane: {self.f}, numSamples: {numSamples}")


        positionData_segments = []
        colorData_segments = []
        normalData_segments = []
        rayData_segments = []

        rayIdOffset = 0



        for i, contourVertWorldPos in enumerate(self.contourVertWorldPos_segments):
            numRays = len(contourVertWorldPos)
            

            # Calculate sampled points along each ray
            t_values = np.linspace(0, 1, numSamples).reshape(1,-1,1)  # Sampling along the ray
            rayDirs = contourVertWorldPos - self.cameraPos
            rayDirsNormalized = rayDirs / np.linalg.norm(rayDirs, axis=1)[:, None]

            nearPoints = self.cameraPos + rayDirsNormalized * self.n
            farPoints = self.cameraPos + rayDirsNormalized * self.f
            sampledPoints = (1 - t_values) * nearPoints[:, None] + t_values * farPoints[:, None] # Shape: (numRays, numSamples, 3)
            vertex_positions = sampledPoints.reshape(-1, 3) # Shape: (numRays*numSamples, 3)

            face_indices, ray_indices, rayIdOffset = self._calcFaceAndRayIndices(numRays, numSamples, rayIdOffset)
            # print(f"numRays: {numRays}, numSamples: {numSamples}, face_indices: {np.array(face_indices).shape}")
            # print(f"ray_indices values: {np.unique(ray_indices)}")
            vertex_normals= self._calcVertexNormals(vertex_positions, face_indices)
            # print(f"before arranging, vertexpos: {np.array(vertex_positions).shape}, vertexnormal: {np.array(vertex_normals).shape}")

            positionData, colorData, vnormalData = self._arrangeVertexData(vertex_positions, face_indices, vertex_normals)
            # print(f"cone vertexpos: {np.array(positionData).shape}, cone vertexcolor:{np.array(colorData).shape}, cone vertexnormal: {np.array(vnormalData).shape}")
            positionData_segments.append(positionData)
            colorData_segments.append(colorData)
            normalData_segments.append(vnormalData)
            rayData_segments.append(ray_indices)

            # # FIXME: debug
            # coneMeshNormal = self._createConeNormalMesh(vertex_positions, vertex_normals)
            # self.rayMesh.add(coneMeshNormal)



        positionData_segments = np.concatenate(positionData_segments, axis=0)
        colorData_segments = np.concatenate(colorData_segments, axis=0)
        normalData_segments = np.concatenate(normalData_segments, axis=0)
        rayData_segments = np.concatenate(rayData_segments, axis=0)
        
        # Debugging print
        # print(f"rayData_segments values: {np.unique(rayData_segments)}")
        # print(f"positionData_segments: {positionData_segments.shape}, colorData_segments: {colorData_segments.shape}, rayData_segments: {rayData_segments.shape}")


        coneGeometry = Geometry()
        coneGeometry.addAttribute("vec3", "vertexPosition", positionData_segments)
        coneGeometry.addAttribute("vec3", "vertexColor", colorData_segments)
        coneGeometry.addAttribute("vec3", "vertexNormal", normalData_segments)
        coneGeometry.addAttribute("int", "vertexRay", rayData_segments)
        # coneGeometry.addAttribute("vec3", "faceNormal", fnormalData) # TODO: add face normals
        
        """""""""""""""create projector cone material"""""""""""""""
        coneMaterial = LambertMaterial(properties={"useVertexColors":True, "alpha":self.alpha})
        
        """"""""""""""" intialize cone mesh """""""""""""""
        # print("projector cone mesh initialized")
        return Mesh(coneGeometry, coneMaterial)


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
    
    def _arrangeVertexData(self, vertex_positions, face_indices, vertex_normals):
        positionData = vertex_positions[face_indices].reshape(-1, 3)
        colorData = [self.color] * len(positionData)
        colorData = np.array(colorData) 
        vnormalData = vertex_normals[face_indices].reshape(-1, 3)

        return positionData, colorData, vnormalData
    




    # # manipulate projector coneMesh: change near and far planes
    # def update(self, inputObject, deltaTime=None): 
    #     if inputObject is None:
    #         print("Projector.update() error: inputObject is None")
    #         return
        
    #     shiftMouseScroll = inputObject.getShiftMouseScroll()
    #     ctrlMouseScroll = inputObject.getCtrlMouseScroll()
    #     if shiftMouseScroll != 0:
    #         self.n += 10*shiftMouseScroll
    #         self._updateConeMesh()
    #         # print(f"shiftMouseScroll: {shiftMouseScroll}, near: {self.n}")
    #     if ctrlMouseScroll != 0:
    #         self.f += 10*ctrlMouseScroll
    #         self._updateConeMesh()
    #         # print(f"ctrlMouseScroll: {ctrlMouseScroll}, far: {self.f}")

            
    
    def _updateConeMesh(self):
        """ update cone mesh with new near and/or far planes, or new delta (called in image2d, or in guiFrame) """
        if self.coneMesh in self.rayMesh.children:
            self.rayMesh.remove(self.coneMesh)
            del self.coneMesh
        self.coneMesh = self._createConeMesh()
        self.rayMesh.add(self.coneMesh)



    # FIXME: DEBUG:
    def _createConeNormalMesh(self, vertex_positions, vertex_normals):
        if vertex_positions.shape[0] != vertex_normals.shape[0]:
            raise ValueError("vertex_positions and vertex_normals must have the same number of vertices")
        vertex_p1 = vertex_positions
        vertex_p2 = vertex_positions + 5*vertex_normals
        # Interleave vertex_p1 and vertex_p2
        positionData = np.empty((2 * len(vertex_p1), 3), dtype=vertex_p1.dtype)
        positionData[0::2] = vertex_p1  # Even indices: start points
        positionData[1::2] = vertex_p2  # Odd indices: end points
        colorData = np.tile([1, 0, 0], (positionData.shape[0], 1)) 
        normalGeometry = Geometry()
        normalGeometry.addAttribute("vec3", "vertexPosition", positionData)
        normalGeometry.addAttribute("vec3", "vertexColor", colorData)
    
        """""""""""""""create projector ray material"""""""""""""""
        normalMaterial = LineMaterial({"useVertexColors":True,
                            "lineWidth":2,
                            "lineType":"segments", 
                            "alpha":1})
                            

        return Mesh(normalGeometry, normalMaterial)
        

        