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

from light.ambientLight import AmbientLight
from light.directionalLight import DirecitonalLight
from light.pointLight import PointLight
from material.flatMaterial import FlatMaterial
from material.lambertMaterial import LambertMaterial
from material.phongMaterial import PhongMaterial



# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800/600)
        self.camera.setPosition([0,0,6])

        # four light sources
        ambient = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient)
        directional = DirecitonalLight(color = [1, 1, 1], direction = [-1,-1,-2])
        self.scene.add(directional)
        point1 = PointLight(color = [0.9, 0, 0], position = [1,1,0.8], attenuation = [1,0,0])
        self.scene.add(point1)
        point2 = PointLight(color = [0, 0.9, 0], position = [-1,1,0.8], attenuation = [1,0,0])
        self.scene.add(point2)


        
        flatMaterial = FlatMaterial(properties={"baseColor": [0.6, 0.2, 0.2]})
        # grid = Texture("grid.png") # TODO: image
        lambertMaterial = LambertMaterial(properties={"baseColor": [0.2, 0.5, 0.5]})
        phongMaterial = PhongMaterial(properties={"baseColor": [ 0.5, 0.5, 1]})
        
        sphereGeometry = BoxGeometry()
        sphere1 = Mesh(sphereGeometry, flatMaterial)
        sphere1.setPosition([-2.2,0,0])
        self.scene.add(sphere1)

        sphere2 = Mesh(sphereGeometry, lambertMaterial)
        sphere2.setPosition([0,0,0])
        self.scene.add(sphere2)

        sphere3 = Mesh(sphereGeometry, phongMaterial)
        sphere3.setPosition([2.2,0,0])
        self.scene.add(sphere3)


    def update(self):
        self.renderer.render(self.scene, self.camera)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             