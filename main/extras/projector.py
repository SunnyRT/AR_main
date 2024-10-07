from core_ext.mesh import Mesh
from geometry.geometry import Geometry
from material.lineMaterial import LineMaterial
import numpy as np



class Projector(Mesh):

    def __init__(self, camera, contourMesh, lineWidth=1, color=[0,0,0]):
        # create geometry
        geo = Geometry()
        positionData = []
        colorData = []

        cameraPos= camera.getWorldPosition()
        contourPos = contourMesh.getWorldPosition()

        # extract vertices positions from contourMesh
        contourVertPos = contourMesh.geometry.attributes["vertexPosition"].data
        contourVertWorldPos = np.array(contourVertPos) + contourPos
        

        for vertPos in contourVertWorldPos:
            positionData.append(cameraPos)
            positionData.append(vertPos)
            colorData.append(color)
            colorData.append(color)


        geo.addAttribute("vec3", "vertexPosition", positionData)
        geo.addAttribute("vec3", "vertexColor", colorData)
        
        # create material
        mat = LineMaterial({"useVertexColors":True,
                            "lineWidth":lineWidth,
                            "lineType":"segments"})
        mat.updateRenderSettings()
        
        # intialize mesh
        super().__init__(geo, mat)
        