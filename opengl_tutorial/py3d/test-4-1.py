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

        geometry3d = BoxGeometry()
        material3d = SurfaceMaterial(
            {"useVertexColors": True})
        self.mesh3d = Mesh(geometry3d, material3d)
        self.scene.add(self.mesh3d)

        geometry2d = PlaneGeometry(4,4,64,64)
        material2d = SurfaceMaterial(
            {"useVertexColors": True})
        self.image2d = Mesh(geometry2d, material2d)
        # self.image2d.translate(0.5,0.5,0)
        self.scene.add(self.image2d)

    def update(self):
        self.mesh3d.rotateY(0.0514) 
        self.mesh3d.rotateX(0.0337)
        self.renderer.render(self.scene, self.camera)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             