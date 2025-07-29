import numpy as np
from core.base import Base
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.rectangleGeometry import RectangleGeometry
from material.surfaceMaterial import SurfaceMaterial
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial




from core.matrix import Matrix
from extras.movementRig import MovementRig
from extras.gridHelper import GridHelper





# render a basic scene
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        self.renderer = Renderer()

        self.scene = Scene()
        self.camera = Camera(isPerspective=True, aspectRatio=1000/750)
        # self.camera.setPosition([0,0,4])

        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([0,1,10])
        self.scene.add(self.rig)
        

        boxGeometry = BoxGeometry()
        boxMaterial = SurfaceMaterial(
            {"useVertexColors": True})
        box = Mesh(boxGeometry, boxMaterial)
        self.scene.add(box)

        grid = GridHelper(gridColor=[0.5,0.5,0.5], centerColor=[1,1,0])
        grid.rotateX(-1.57)
        self.scene.add(grid)

        # HUD
        self.hudScene = Scene()
        self.hudCamera = Camera(isPerspective=False, aspectRatio=1000/750, near=1, far=-1)
        self.hudCamera.setOrthographic(left=0, right=800, bottom=0, top=600)
        labelGeo1 = RectangleGeometry(60,80, [0,600], [0,1])
        labelMat1 = SurfaceMaterial({"useVertexColors": True})
        self.label1 = Mesh(labelGeo1, labelMat1)
        label1_w = 60
        label1_h = 80
        self.hudScene.add(self.label1)

        labelGeo2 = RectangleGeometry(100,80, [800,0], [1,0])
        labelMat2 = SurfaceMaterial({"useVertexColors": True})
        self.label2 = Mesh(labelGeo2, labelMat2)
        label2_w = 100
        label2_h = 80
        self.hudScene.add(self.label2)





    def update(self):
        self.rig.update(self.input)
        self.renderer.render(self.scene, self.camera)
        self.renderer.render(self.hudScene, self.hudCamera, clearColor=False)


    

# instantiate this class and run the program
Test(screenSize=[1000,750]).run()

                             