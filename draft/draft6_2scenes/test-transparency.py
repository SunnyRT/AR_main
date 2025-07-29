import wx
import numpy as np
from core.InputCanvas import InputCanvas # Extend your existing BaseCanvas
from core.guiFrame import GUIFrame
from core_ext.rendererDual import RendererDual
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.planeGeometry import PlaneGeometry
from geometry.model3dGeometry import Model3dGeometry
from geometry.boxGeometry import BoxGeometry
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial
from material.flatMaterial import FlatMaterial
from material.lambertMaterial import LambertMaterial

from light.ambientLight import AmbientLight
from light.directionalLight import DirecitonalLight
from light.pointLight import PointLight


from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent, screenSize=[1200, 900]):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent, screenSize)


        self.initialized = False  # Ensure scene isn't initialized multiple times


    def initialize(self):
        """ Initialize the scene with lights, cameras, objects, etc."""
        print("Initializing program...")

        # Initialize renderer, scene, and cameras
        self.renderer = RendererDual(glcanvas=self, clearColor=[0.8, 0.8, 0.8])
        self.scene = Scene()

        # Set up first camera: camera0 for CAD engineering viewport
        self.camera0 = Camera(isPerspective=False, aspectRatio=600/900)
        self.rig0 = MovementRig()
        self.rig0.add(self.camera0)
        self.rig0.setPosition([10, 10, 50])
        self.scene.add(self.rig0)



        # Add lights
        ambient = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient)
        directional = DirecitonalLight(color=[1, 1, 1], direction=[-1, -1, -2])
        self.scene.add(directional)
        point = PointLight(color=[0.3, 0.3, 0.3], position=[20, 20, 16], attenuation=[1, 0.1, 0.1])
        self.scene.add(point)

        # Grid setup
        grid = GridHelper(size=1024, divisions=512, gridColor=[0.6, 0.6, 0.6], centerColor=[0.5, 0.5, 0.5], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # # Load 3D model
        # geometry3d = Model3dGeometry("D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply")
        # lambertMaterial = LambertMaterial(properties={"baseColor": [0.5, 0.5, 0.2]})
        # self.mesh3d = Mesh(geometry3d, lambertMaterial)
        # self.scene.add(self.mesh3d)

        # # Load 2D texture
        # texture2d = Texture(self.image2d_path)
        # texture2d_height = texture2d.height
        # texture2d_width = texture2d.width
        # image2d_aspect_ratio = texture2d_width / texture2d_height
        # material2d = TextureMaterial(texture2d)
        # image2d_height = 64
        # image2d_width = image2d_height * image2d_aspect_ratio
        # geometry2d = PlaneGeometry(image2d_width, image2d_height, 256, 256)
        # self.image2d = Mesh(geometry2d, material2d)



        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes)

        geometrybox1 = BoxGeometry(10, 10, 10)
        materialbox1 = FlatMaterial(properties={"baseColor": [0.5, 0.5, 0.2], "alpha": 0.5})
        self.box1 = Mesh(geometrybox1, materialbox1)
        self.scene.add(self.box1)
        self.box1.setPosition([10,0,0])

        geometrybox2 = BoxGeometry(10, 10, 10)
        materialbox2 = FlatMaterial(properties={"baseColor": [0.5, 0.5, 0.2]})
        self.box2 = Mesh(geometrybox2, materialbox2)
        self.scene.add(self.box2)
        self.box2.setPosition([-10,0,0])


        self.initialized = True

    def update(self):

        if not self.initialized:
            self.initialize()


        self.rig0.update(self)
        self.camera0.update(self)


        self.renderer.render(self.scene, self.camera0)   
        
        


class MyFrame(GUIFrame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, title=title, size=size)

        # override default InputCanvas with MyCanvas
        self.canvas = MyCanvas(self)
        
        self.create_menu_bar()
        self.create_tool_panel()

        # Use a box sizer to hold both the canvas and the tool panel
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)  # The OpenGL canvas fills most of the window
        self.sizer.Add(self.tool_panel, 0, wx.EXPAND)  # Tool panel on the right side

        # Set the sizer for the frame
        self.SetSizer(self.sizer)
        self.Show()     


# Main App
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="AR Registration", size=(1200, 900))
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
