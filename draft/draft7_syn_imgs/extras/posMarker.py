from mesh.mesh import Mesh
from geometry.geometry import Geometry
from material.pointMaterial import PointMaterial



class PosMarker(Mesh):

    def __init__(self, position, color=[1,0,0], size=10):
        # create geometry
        geo = Geometry()
        positionData = [position]
        colorData = [color]
        geo.addAttribute("vec3", "vertexPosition", positionData)
        geo.addAttribute("vec3", "vertexColor", colorData)
        
        # create material
        mat = PointMaterial({"useVertexColors":True,
                             "pointSize":size})
        mat.updateRenderSettings()
        
        # intialize mesh
        super().__init__(geo, mat)
        
    def updatePosition(self, position):
        self.geometry.attributes["vertexPosition"].data = [position]
        self.geometry.updateBuffer("vertexPosition")
        
    def updateColor(self, color):
        self.geometry.attributes["vertexColor"].data = [color]
        self.geometry.updateBuffer("vertexColor")
        
    def updateSize(self, size):
        self.material.uniforms["pointSize"] = size
        self.material.updateRenderSettings()