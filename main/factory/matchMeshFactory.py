from factory.meshFactory import MeshFactory
from geometry.matchGeometry import MatchGeometry
from material.lineMaterial import LineMaterial
from mesh.mesh import Mesh

class MatchMeshFactory(MeshFactory):
    def __init__(self, alpha=1, color=(1,1,1), sceneObject=None, mediator=None):
        super().__init__(mediator)
        self.material = LineMaterial({"lineType": "segments", "lineWidth": 1, "alpha": alpha, "useVertexColors": True})
        self.sceneObject = sceneObject
        self.color = color

    def createMesh(self, matchPairs):
        # override parent class method
        if matchPairs is None or len(matchPairs)==0:
            return
        
        geometry = MatchGeometry(matchPairs, self.color)
        self.mesh = Mesh(geometry, self.material)
        return self.mesh


    def update(self, matchPairs):
        # override parent class method
        if self.mesh is not None:
            parent = self.mesh.parent
            if parent is None:
                parent = self.sceneObject
            else:
                parent.remove(self.mesh)
                del self.mesh
        else: # if mesh is None
            parent = self.sceneObject

        self.mesh = self.createMesh(matchPairs)
        if self.mesh is not None:
            parent.add(self.mesh)
        return self.mesh



