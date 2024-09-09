from core.base import Base
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.planeGeometry import PlaneGeometry
from material.surfaceMaterial import SurfaceMaterial

from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from math import pi

# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800/600)
        # self.camera.setPosition([0.5,1,5])

        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([0.5,1,5])
        self.scene.add(self.rig)

        grid = GridHelper(size=20, gridColor=[1,1,1], centerColor=[1,1,0], lineWidth=1)
        grid.rotateX(-pi/2)
        self.scene.add(grid)

        axes = AxesHelper(axisLength=2, lineWidth=4)
        self.scene.add(axes)




    def update(self):
        self.renderer.render(self.scene, self.camera)
        self.rig.update(self.input)

# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             