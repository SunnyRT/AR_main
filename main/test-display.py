import wx
from core.baseInput import InputCanvas, InputFrame  # Extend your existing BaseCanvas
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.planeGeometry import PlaneGeometry
from geometry.model3dGeometry import Model3dGeometry
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial

from light.ambientLight import AmbientLight
from light.directionalLight import DirecitonalLight
from light.pointLight import PointLight
from material.lambertMaterial import LambertMaterial

from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent)

        self.initialized = False  # Ensure scene isn't initialized multiple times

        self.cameraIdx = 0
        self.init = False



    def initialize(self):
        """ Initialize the scene with lights, cameras, objects, etc."""
        print("Initializing program...")

        # Initialize renderer, scene, and cameras
        self.renderer = Renderer()
        self.scene = Scene()

        # Set up two cameras
        self.camera0 = Camera(isPerspective=False, aspectRatio=800 / 600)
        self.rig0 = MovementRig()
        self.rig0.add(self.camera0)
        self.rig0.setPosition([10, 10, 50])
        self.scene.add(self.rig0)

        self.camera1 = Camera(isPerspective=True, aspectRatio=800 / 600)
        self.rig1 = MovementRig()
        self.rig1.add(self.camera1)
        self.rig1.setPosition([0, 0, 50])
        self.scene.add(self.rig1)

        # Add lights
        ambient = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient)
        directional = DirecitonalLight(color=[1, 1, 1], direction=[-1, -1, -2])
        self.scene.add(directional)
        point = PointLight(color=[0.3, 0.3, 0.3], position=[20, 20, 16], attenuation=[1, 0.1, 0.1])
        self.scene.add(point)

        # Grid setup
        grid = GridHelper(size=1024, divisions=512, gridColor=[0.8, 0.8, 0.8], centerColor=[0.5, 0.5, 0.5], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # Load 3D model
        geometry3d = Model3dGeometry("D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply")
        lambertMaterial = LambertMaterial(properties={"baseColor": [0.5, 0.5, 0.2]})
        self.mesh3d = Mesh(geometry3d, lambertMaterial)
        self.scene.add(self.mesh3d)

        # Load 2D texture
        geometry2d = PlaneGeometry(64, 64, 256, 256)
        texture2d = Texture("D:\\sunny\\Codes\\IIB_project\\data\\summer\\JPEG0836.jpg")
        material2d = TextureMaterial(texture2d)
        self.image2d = Mesh(geometry2d, material2d)
        self.image2d.translate(0, 0, -60)
        self.camera1.add(self.image2d)

        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes)

        self.initialized = True

    def update(self):

        if not self.initialized:
            self.initialize()

        """ Update the scene and toggle between cameras."""
        if self.isKeyDown("space"):  # Toggle between cameras with spacebar
            self.cameraIdx = (self.cameraIdx + 1) % 2

        if self.cameraIdx == 0:
            self.rig0.update(self)
            self.camera0.update(self)
            self.renderer.render(self.scene, self.camera0)
        else:
            self.rig1.update(self)
            self.camera1.update(self)
            self.renderer.render(self.scene, self.camera1)



# Main Frame with Menu Bar
class MyFrame(InputFrame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, title=title, size=size)

        # Set up the OpenGL canvas using the extended BaseCanvas
        self.canvas = MyCanvas(self)

        # Set up the menu bar
        self.create_menu_bar()

        self.Show()

    def create_menu_bar(self):
        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "&Open")
        file_menu.Append(wx.ID_SAVE, "&Save")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit")

        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")

        # Append menus to the menu bar
        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_menu)
        
        # Set the menu bar for the frame
        self.SetMenuBar(menubar)

    def on_menu(self, event):
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            self.Close()
        elif event_id == wx.ID_ABOUT:
            wx.MessageBox("wxPython OpenGL Example with Menu Bar", "About", wx.OK | wx.ICON_INFORMATION)


# Main App
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="AR Registration", size=(800, 600))
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
