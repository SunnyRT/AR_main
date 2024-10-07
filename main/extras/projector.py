from core_ext.mesh import Mesh
from geometry.geometry import Geometry
from material.lineMaterial import LineMaterial
from material.lambertMaterial import LambertMaterial
import numpy as np



class Projector(Mesh):

    def __init__(self, camera, contourMesh, lineWidth=1, color=[1,1,0], ConvertToSurface=False):
        # create geometry
        geo = Geometry()
        positionData = []
        colorData = []

        cameraPos= camera.getWorldPosition()
        contourPos = contourMesh.getWorldPosition()

        # extract vertices positions from contourMesh
        contourVertPos = contourMesh.geometry.attributes["vertexPosition"].data
        contourVertWorldPos = np.array(contourVertPos) + contourPos
        
        if not ConvertToSurface:
            for vertPos in contourVertWorldPos:
                positionData.append(cameraPos)
                positionData.append(vertPos)
                colorData.append(color)
                colorData.append(color)
        else:
            for (i, vertPos) in enumerate(contourVertWorldPos):
                positionData.append(cameraPos)
                positionData.append(vertPos)
                positionData.append(contourVertWorldPos[(i+1)%len(contourVertWorldPos)])
                colorData.append(color)
                colorData.append(color)
                colorData.append(color)



        geo.addAttribute("vec3", "vertexPosition", positionData)
        geo.addAttribute("vec3", "vertexColor", colorData)
        
        # create material
        if not ConvertToSurface:
            mat = LineMaterial({"useVertexColors":True,
                                "lineWidth":lineWidth,
                                "lineType":"segments"})
        else:
            mat = LambertMaterial(properties={"baseColor":color})
        mat.updateRenderSettings()
        
        # intialize mesh
        super().__init__(geo, mat)
        