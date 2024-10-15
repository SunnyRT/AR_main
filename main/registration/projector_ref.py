from core_ext.mesh import Mesh
from geometry.geometry import Geometry
from material.lineMaterial import LineMaterial
from material.surfaceMaterial import SurfaceMaterial

import numpy as np
import open3d as o3d



class Projector(object):

    def __init__(self, camera, contourMesh, lineWidth=1, color=[1,1,0], alpha=0.3, near=20, far=100, delta=1, ):
        

        self.n = near
        self.f = far
        self.delta = delta
        self.color = color
        self.alpha = alpha
        
        """"""""""""""" create projector ray geometry"""""""""""""""
        rayGeometry = Geometry()
        positionData = []
        colorData = []

        self.cameraPos= camera.getWorldPosition()
        contourPos = contourMesh.getWorldPosition()

        # extract vertices positions from contourMesh
        contourVertPos = contourMesh.geometry.attributes["vertexPosition"].data
        self.contourVertWorldPos = np.array(contourVertPos) + contourPos
        

        for vertPos in self.contourVertWorldPos:
            positionData.append(self.cameraPos)
            positionData.append(vertPos)
            colorData.append(color)
            colorData.append(color)


        rayGeometry.addAttribute("vec3", "vertexPosition", positionData)
        rayGeometry.addAttribute("vec3", "vertexColor", colorData)
        
        """""""""""""""create projector ray material"""""""""""""""
        rayMaterial = LineMaterial({"useVertexColors":True,
                            "lineWidth":lineWidth,
                            "lineType":"segments", 
                            "alpha":self.alpha})

        
        """"""""""""""" intialize ray mesh """""""""""""""
        self.rayMesh = Mesh(rayGeometry, rayMaterial)




    def generateCone(self, visibleRay=False):
        layers = []
        for vertPos in self.contourVertWorldPos:
            # Sample points along the ray and create a cone surface
            rayDir = vertPos - self.cameraPos
            rayDir = rayDir / rayDir[-1] # Normalize ray direction by z component

            # Sample points along the ray within the near and far clipping planes
            nearPoint = self.cameraPos - rayDir * self.n
            farPoint = self.cameraPos - rayDir * self.f
            
            # Sample points between near and far points at intervals of delta
            t_values = np.arange(0, 1, self.delta/(self.f-self.n))  # Sampling along the ray
            sampled_points = (1 - t_values)[:, None] * nearPoint + t_values[:, None] * farPoint
            
            layers.append(sampled_points)

        layers = np.array(layers) # Shape: (numRays=numContourVertices, numSamples, 3)
        vertex_positions = layers.reshape(-1, 3) # Shape: (numRays*numSamples, 3)

        # Triangulate the surface
        numRays = layers.shape[0]
        numSamples = layers.shape[1]
        face_data = [] # List to store face indices for each triangle from flattened vertex_positions

        for i in range(numRays-1):
            for j in range(numSamples-1):
                # Generate face indices for the 2 triangles
                id0 = i*numSamples + j
                id1 = (i+1)*numSamples + j
                id2 = id0 + 1
                id3 = id1 + 1
                face_data.append([id0, id1, id2])
                face_data.append([id2, id1, id3])

        
        # Flatten the positionData list for easier handling
        positionData = []    
        vnormalData = []    
        positionData = np.array(positionData).reshape(-1, 3)
        colorData = [self.color] * len(positionData)
        colorData = 0.5*np.array(colorData) 


        ##############################################
        # FIXME: compute vertex normals!!!!!!!!!
        o3dConeMesh = o3d.geometry.TriangleMesh()
        o3dConeMesh.vertices = o3d.utility.Vector3dVector(vertex_positions)
        o3dConeMesh.triangles = o3d.utility.Vector3iVector(face_data)
        o3dConeMesh.compute_vertex_normals()
        o3dConeMesh.compute_triangle_normals()
        vertex_normals = np.asarray(o3dConeMesh.vertex_normals)
         # grouped as face_data triangles
        for face in face_data:
            vertex_indices = face
            for i in range(3):
                vertex_index = vertex_indices[i]
                vnormalData.append(vertex_normals[vertex_index])
                

        fnormalData = np.asarray(o3dConeMesh.triangle_normals)


        ##############################################

        """"""""""""""" create projector cone geometry"""""""""""""""
        coneGeometry = Geometry()
        coneGeometry.addAttribute("vec3", "vertexPosition", positionData)
        coneGeometry.addAttribute("vec3", "vertexColor", colorData)
        coneGeometry.addAttribute("vec3", "vertexNormal", vnormalData)
        coneGeometry.addAttribute("vec3", "faceNormal", fnormalData)
        
        """""""""""""""create projector cone material"""""""""""""""
        coneMaterial = SurfaceMaterial(properties={"useVertexColors":True, "alpha":self.alpha})
        
        """"""""""""""" intialize cone mesh """""""""""""""
        self.coneMesh = Mesh(coneGeometry, coneMaterial)
        self.rayMesh.add(self.coneMesh)
        if not visibleRay:
            self.rayMesh.visible = False
            self.coneMesh.visible = True


# FIXME: draw near and far clipping planes!!!!!


        