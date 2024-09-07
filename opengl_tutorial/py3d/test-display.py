from core.base import Base
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
# from geometry.boxGeometry import BoxGeometry
from geometry.planeGeometry import PlaneGeometry
from geometry.model3dGeometry import Model3dGeometry
from material.surfaceMaterial import SurfaceMaterial
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial

from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from math import pi

# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        # initialize renderer, scene, camera
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800/600)


        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([10,10,50])
        self.scene.add(self.rig)

        # set up grid 
        grid = GridHelper(size=1024, divisions = 1024, gridColor=[0.5,0.5,0.5], centerColor=[1,1,1], lineWidth=1)
        grid.rotateX(-pi/2)
        self.scene.add(grid)

        # load 3d model
        geometry3d = Model3dGeometry("D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply") # TODO: change path to desired .ply file
        material3d = SurfaceMaterial(
            {"useVertexColors": True})
        self.mesh3d = Mesh(geometry3d, material3d)
        self.scene.add(self.mesh3d)

        # load 2d image
        geometry2d = PlaneGeometry(64,64,256,256)
        texture2d = Texture("D:\\sunny\\Codes\\IIB_project\\data\\summer\\JPEG0836.jpg")
        material2d = TextureMaterial(texture2d)
        self.image2d = Mesh(geometry2d, material2d)
        # self.image2d.translate(0.5,0.5,0)
        self.scene.add(self.image2d)

        # set up axes
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes) 


    def update(self):

        self.mesh3d.rotateY(0.0514) 
        self.mesh3d.rotateX(0.0337)
        
        self.rig.update(self.input)
        self.camera.update(self.input)
        self.renderer.render(self.scene, self.camera)



# instantiate this class and run the program
Test(screenSize=[800,600]).run()

                             