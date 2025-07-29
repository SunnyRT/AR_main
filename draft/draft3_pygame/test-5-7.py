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
from material.flatMaterial import FlatMaterial
from material.lambertMaterial import LambertMaterial
from material.phongMaterial import PhongMaterial


from core.matrix import Matrix
from extras.movementRig import MovementRig





# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(isPerspective=True, aspectRatio=800/600)
        # self.camera.setPosition([0,0,4])

        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([0,1,10])
        self.scene.add(self.rig)
        

        geometry3d = BoxGeometry()
        material3d = SurfaceMaterial(
            {"useVertexColors": True})
        self.model3d = Mesh(geometry3d, material3d)
        self.scene.add(self.model3d)
    

        # load 2d image
        geometry2d = PlaneGeometry(4,4,8,8)
        material2d = SurfaceMaterial(
            {"useVertexColors": True})
        self.image2d = Mesh(geometry2d, material2d)
        self.image2d.translate(0.5,0.5,-1)
        self.scene.add(self.image2d)



    def update(self):
        self.rig.update(self.input)
        self.image2d.lookAt(self.camera.getWorldPosition())
        self.renderer.render(self.scene, self.camera)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             