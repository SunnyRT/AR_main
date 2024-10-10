from core_ext.mesh import Mesh
from geometry.geometry import Geometry
from material.lineMaterial import LineMaterial
from material.surfaceMaterial import SurfaceMaterial
import numpy as np



class Projector(object):

    def __init__(self, camera, contourMesh, lineWidth=1, color=[1,1,0], near=20, far=100, delta=1):
        

        self.n = near
        self.f = far
        self.delta = delta
        self.color = color
        
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
                            "lineType":"segments"})

        
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
        print(layers.shape) # TODO: debug
        self.verticeInLayers = layers
        

        # Triangulate the surface
        positionData = []
        numRays = layers.shape[0]
        numSamples = layers.shape[1]

        for i in range(numRays-1):
            for j in range(numSamples-1):
                # Create 2 triangles for each quad formed by 2 consecutive layers
                positionData.append([layers[i][j], layers[i+1][j], layers[i][j+1]])
                positionData.append([layers[i][j+1], layers[i+1][j], layers[i+1][j+1]])

        print(len(positionData), len(positionData[0]), len(positionData[0][0])) # TODO: debug
        
        # Flatten the positionData list for easier handling
        positionData = np.array(positionData).reshape(-1, 3)
        print(positionData.shape) # TODO: debug
        colorData = [self.color] * len(positionData)
        colorData = 0.5*np.array(colorData) 


        ##############################################
        # FIXME: compute vertex normals!!!!!!!!!
        ##############################################

        """"""""""""""" create projector cone geometry"""""""""""""""
        coneGeometry = Geometry()
        coneGeometry.addAttribute("vec3", "vertexPosition", positionData)
        coneGeometry.addAttribute("vec3", "vertexColor", colorData)
        
        """""""""""""""create projector cone material"""""""""""""""
        coneMaterial = SurfaceMaterial(properties={"useVertexColors":True})
        
        """"""""""""""" intialize cone mesh """""""""""""""
        self.coneMesh = Mesh(coneGeometry, coneMaterial)
        self.rayMesh.add(self.coneMesh)
        if not visibleRay:
            self.rayMesh.visible = False
            self.coneMesh.visible = True


# FIXME: draw near and far clipping planes!!!!!


        