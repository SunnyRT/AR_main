from core.base import Base
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.planeGeometry import PlaneGeometry
from material.surfaceMaterial import SurfaceMaterial

# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800/600)
        self.camera.setPosition([0,0,4])

        geometry = BoxGeometry()
        material = SurfaceMaterial(
            {"useVertexColors": True})
        self.mesh = Mesh(geometry, material)
        self.scene.add(self.mesh)

    def update(self):
        self.mesh.rotateY(0.0514) 
        self.mesh.rotateX(0.0337)
        self.renderer.render(self.scene, self.camera)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             