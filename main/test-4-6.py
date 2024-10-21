import wx
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.camera import Camera
from extras.gridHelper import GridHelper
from extras.axesHelper import AxesHelper
from extras.movementRig import MovementRig
from math import pi
from core.InputCanvas import InputCanvas, InputFrame  


class TestCanvas(InputCanvas):  # Extend the existing BaseCanvas
    def __init__(self, parent):
        super().__init__(parent)
        self.scene_initialized = False  # Ensure scene isn't initialized multiple times

    def initialize_scene(self):
        print("Initializing program...")

        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800 / 600)

        # Add movement rig and camera
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([0.5, 1, 5])
        self.scene.add(self.rig)

        # Add grid
        grid = GridHelper(size=20, gridColor=[1, 1, 1], centerColor=[1, 1, 0], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # Add axes helper
        axes = AxesHelper(axisLength=2, lineWidth=4)
        self.scene.add(axes)

        self.scene_initialized = True

    def update(self):
        # Check if scene is initialized before rendering
        if not self.scene_initialized:
            self.initialize_scene()

        # self.input.update()

        # if self.input.isKeyPressed("w"):
        #     print("W key being pressed")

        # if self.input.isMouseLeftDown():
        #     print("Left mouse button down")

        if self.isKeyPressed("w"):
            print("W key being pressed")

        if self.isKeyDown("a"):
            print("A key down")
        
        # self.rig.update(self.input)
        self.rig.update(self)
        
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
        self.frame = TestFrame(None, title="Movement Rig Test", size=(800, 600))  # Pass size and title here
        self.SetTopWindow(self.frame)
        return True


if __name__ == "__main__":
    app = App(False)
    app.MainLoop()
