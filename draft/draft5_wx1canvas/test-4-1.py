# main.py
import wx
from core.base import BaseCanvas
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.planeGeometry import PlaneGeometry
from geometry.model3dGeometry import Model3dGeometry
from material.surfaceMaterial import SurfaceMaterial

class TestCanvas(BaseCanvas):
    def initialize(self):
        """Initialize the scene and objects."""
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800/600)
        self.camera.setPosition([0, 0, 100])

        # 3D Model
        # geometry3d = Model3dGeometry("D:\\sunny\\Codes\\IIB_project\\data\\1_summer_discard\\fitted_otic_capsule.ply")
        geometry3d = BoxGeometry(2, 2, 2)  # Example box geometry
        material3d = SurfaceMaterial({"useVertexColors": True})
        self.mesh3d = Mesh(geometry3d, material3d)
        self.scene.add(self.mesh3d)
        

        geometry2 = BoxGeometry(1, 1, 1)  # Example box geometry
        material2 = SurfaceMaterial({"useVertexColors": True})
        self.mesh2= Mesh(geometry2, material2)
        self.mesh3d.add(self.mesh2)
        self.mesh2.setPosition([10, 0, 0])

        # 2D Plane
        geometry2d = PlaneGeometry(64, 64, 256, 256)
        material2d = SurfaceMaterial({"useVertexColors": True})
        self.image2d = Mesh(geometry2d, material2d)
        # self.scene.add(self.image2d)

    def update(self):
        """Update the scene: rotate objects and render."""
        self.mesh3d.rotateY(0.0514)
        self.mesh3d.rotateX(0.0337)
        self.renderer.render(self.scene, self.camera)

class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxPython OpenGL Example", size=(800, 600))

        # Create the canvas
        self.canvas = TestCanvas(self)

        # Create the menu bar
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

        # Bind menu items to methods
        self.Bind(wx.EVT_MENU, self.on_menu)
        
        # Set the menu bar for the frame
        self.SetMenuBar(menubar)

    def on_menu(self, event):
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            self.Close()
        elif event_id == wx.ID_ABOUT:
            wx.MessageBox("This is a simple OpenGL scene with wxPython", "About", wx.OK | wx.ICON_INFORMATION)

class TestApp(wx.App):
    def OnInit(self):
        self.frame = TestFrame()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = TestApp(False)
    app.MainLoop()
