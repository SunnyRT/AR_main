from core.base import Base
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.planeGeometry import PlaneGeometry
from geometry.sphereGeometry import SphereGeometry
from material.surfaceMaterial import SurfaceMaterial
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial

# from light.ambientLight import AmbientLight
# from light.directionalLight import DirectionalLight
# from light.pointLight import PointLight
# from material.flatMaterial import FlatMaterial
# from material.lambertMaterial import LambertMaterial
# from material.phongMaterial import PhongMaterial

from extras.movementRig import MovementRig

# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()

        # Two cameras in the scene
        self.cameraIdx = 0

        self.camera0 = Camera(isPerspective=False, aspectRatio=800/600)
        # self.camera1.setPosition([0,0,4])
        self.rig0 = MovementRig()
        self.rig0.add(self.camera0)
        self.rig0.setPosition([0,0,10])
        self.scene.add(self.rig0)

        self.camera1 = Camera(isPerspective=True, aspectRatio=800/600)
        # self.camera2.setPosition([1,1,1])
        self.rig1 = MovementRig()
        self.rig1.add(self.camera1)
        self.rig1.setPosition([0,10,0])
        self.rig1.rotateX(-1.57)
        self.scene.add(self.rig1)

        



        geometry3d = BoxGeometry()
        material3d = SurfaceMaterial(
            {"useVertexColors": True})
        self.model3d = Mesh(geometry3d, material3d)
        self.scene.add(self.model3d)

        geometry2d = PlaneGeometry(4,4,8,8)
        material2d = SurfaceMaterial(
            {"useVertexColors": True})
        self.image2d = Mesh(geometry2d, material2d)
        self.image2d.translate(0,0,-15)
        self.camera1.add(self.image2d) # add the image to the second camera
        




    def update(self):
        # self.mesh.rotateY(0.0514) 
        # self.mesh.rotateX(0.0337)
        if self.input.isKeyDown("space"):
            self.cameraIdx = (self.cameraIdx + 1) % 2 # toggle between 0 and 1
        
        if self.cameraIdx == 0:
            self.rig0.update(self.input)
            self.camera0.update(self.input)
            self.renderer.render(self.scene, self.camera0)

        else:
            self.rig1.update(self.input)
            self.camera1.update(self.input)
            self.renderer.render(self.scene, self.camera1)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             