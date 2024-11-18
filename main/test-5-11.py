import wx
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.texture import Texture
from main.mesh.mesh import Mesh
from core_ext.renderTarget import RenderTarget
from geometry.rectangleGeometry import RectangleGeometry
from geometry.sphereGeometry import SphereGeometry
from geometry.boxGeometry import BoxGeometry
from material.textureMaterial import TextureMaterial
from material.surfaceMaterial import SurfaceMaterial
from extras.gridHelper import GridHelper
from extras.axesHelper import AxesHelper
from extras.movementRig import MovementRig
from math import pi
from main.core.InputCanvas import InputCanvas, InputFrame  


class TestCanvas(InputCanvas):  # Extend the existing BaseCanvas
    def __init__(self, parent):
        super().__init__(parent)
        self.scene_initialized = False  # Ensure scene isn't initialized multiple times

    def initialize_scene(self):
        print("Initializing program...")

        self.renderer = Renderer(glcanvas=self)
        self.scene = Scene()
        self.camera = Camera(isPerspective=True, aspectRatio=512 / 512)

        # Add movement rig and camera
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.rig.setPosition([0, 1, 4])
        

        # Add sky camera
        self.skyCamera = Camera(isPerspective=True, aspectRatio=512/512)
        self.skyCamera.setPosition([0, 10, 0])
        self.skyCamera.lookAt([0, 0, 0])
        self.scene.add(self.skyCamera)


        # Add grid
        grid = GridHelper(size=20, gridColor=[1, 1, 1], centerColor=[1, 1, 0], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # Add axes helper
        axes = AxesHelper(axisLength=2, lineWidth=4)
        self.scene.add(axes)


        # Add sky and grass
        skyGeometry = SphereGeometry(radius=50)
        skyMaterial = TextureMaterial(texture=Texture("D:/sunny/Codes/IIB_project/AR_main/images/sky-earth.jpg"))
        # skyMaterial = SurfaceMaterial({"useVertexColors": True})
        sky = Mesh(skyGeometry, skyMaterial)
        sky.rotateX(-pi / 2)
        self.scene.add(sky)

        # grassGeometry = RectangleGeometry(width=100, height=100)
        # grassMaterial = TextureMaterial(texture=Texture("D:/sunny/Codes/IIB_project/AR_main/images/grass.jpg"))
        # grass = Mesh(grassGeometry, grassMaterial)
        # grass.rotateX(-pi / 2)
        # self.scene.add(grass)

        # Add sphere and box
        sphereGeometry = SphereGeometry(radius=1)
        sphereMaterial = SurfaceMaterial({"useVertexColors": True})
        self.sphere = Mesh(sphereGeometry, sphereMaterial)
        self.sphere.setPosition([-1.2, 1, 0])
        self.scene.add(self.sphere)

        boxGeometry = BoxGeometry(width=2, height=2, depth=0.2)
        boxMaterial = SurfaceMaterial({"baseColor": [0, 0, 0]})
        self.box = Mesh(boxGeometry, boxMaterial)
        self.box.setPosition([1.2, 1, 0])
        self.scene.add(self.box)


        # television screen
        self.renderTarget = RenderTarget(resolution=[512, 512])
        screenGeometry = RectangleGeometry(width=1.8, height=1.8)
        screenMaterial = TextureMaterial(self.renderTarget.texture)
        screen = Mesh(screenGeometry, screenMaterial)
        screen.setPosition([1.2, 1, 0.11])
        self.scene.add(screen)

        

        self.scene_initialized = True

    def update(self):
        # Check if scene is initialized before rendering
        if not self.scene_initialized:
            self.initialize_scene()
        
        self.sphere.rotateY(0.01337)
        # self.rig.update(self.input)
        self.rig.update(self)

        
        self.renderer.render(self.scene, self.skyCamera, renderTarget=self.renderTarget)
        
        self.renderer.render(self.scene, self.camera)


class TestFrame(InputFrame):  # Extend the existing BaseFrame
    def __init__(self, parent, title, size):
        # Call the wx.Frame constructor with title and size
        wx.Frame.__init__(self, parent, title=title, size=size)

        # Initialize the TestCanvas as the main canvas
        self.canvas = TestCanvas(self)
        self.Show()


# Instantiate the wxPython app and run it
class App(wx.App):
    def OnInit(self):
        self.frame = TestFrame(None, title="Movement Rig Test", size=(512, 512))  # Pass size and title here
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = App(False)
    app.MainLoop()
