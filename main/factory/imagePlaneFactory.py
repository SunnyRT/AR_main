from factory.meshFactory import MeshFactory

from material.textureMaterial import TextureMaterial
from geometry.planeGeometry import PlaneGeometry
from mesh.mesh import Mesh


class ImagePlaneFactory(MeshFactory):

    def __init__(self, texture, n, res, alpha=0.5, mediator=None):
        super().__init__(mediator)

        self.material = TextureMaterial(texture, {"alpha": alpha})
        self.texture = texture
        self.n = n
        self.res = res


    def createGeometry(self, texture):
        pxWidth = texture.width
        pxHeight = texture.height
        width, height = self._getWorldDimension(self.n, self.res, pxWidth, pxHeight)
        return PlaneGeometry(width, height, 4, 4, flipY=True)

    def _getWorldDimension(self, n, res, pxWidth, pxHeight):
        width = pxWidth * res * n
        height = pxHeight * res * n
        return width, height
    

    def createMesh(self):
        # override parent class method
        geometry = self.createGeometry(self.texture)
        self.mesh = Mesh(geometry, self.material)
        self.mesh.translate(0, 0, -self.n)
        return self.mesh
    
    def update(self, del_n=None):
        # override parent class method
        if del_n is not None: # update n
            self.n += del_n
        self.mesh = super().update() # calls createMesh()
        return self.mesh # (to be assigned to canvas attribute)
    
    
    


    