import wx
import numpy as np
from core.InputCanvas import InputCanvas # Extend your existing BaseCanvas
from core.guiFrame import GUIFrame
from core_ext.rendererDual import RendererDual
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from geometry.planeGeometry import PlaneGeometry
from geometry.rectangleGeometry import RectangleGeometry
from geometry.boxGeometry import BoxGeometry
from geometry.model3dGeometry import Model3dGeometry
from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial
from material.lambertMaterial import LambertMaterial
from material.pointMaterial import PointMaterial


from light.ambientLight import AmbientLight
from light.directionalLight import DirecitonalLight
from light.pointLight import PointLight

from registration.image2d import Image2D

from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from registration.projector import Projector
from extras.posMarker import PosMarker
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent, screenSize=[1200, 900]):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent, screenSize)


        self.cameraIdx = 0
        self.image2d_path = "D:\sunny\Codes\IIB_project\data\michaelmas\pinna.png"
        self.contour_path = "D:\sunny\Codes\IIB_project\data\michaelmas\pinna.sw"
        self.model3d_path = "D:\sunny\Codes\IIB_project\data\michaelmas\ear.ply"
        self.color_pinna = [0.90588235, 0.72156863, 0.09411765]
        self.color_incus = [1, 0, 0] # TODO: to change
        self.n = 200
        self.f = 300
        self.camera1_z = 250
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
        self.rig0.setPosition([10, 10, 400]) # TODO: to change
        self.scene.add(self.rig0)



        # Add lights
        ambient = AmbientLight(color=[0.5, 0.5, 0.5])
        self.scene.add(ambient)
        directionalR = DirecitonalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, 0])
        self.scene.add(directionalR)
        directionalL = DirecitonalLight(color=[0.8, 0.8, 0.8], direction=[1, -1, 0])
        self.scene.add(directionalL)
        point = PointLight(color=[0.3, 0.3, 0.3], position=[0, 20, 16], attenuation=[1, 0.1, 0.1])
        self.scene.add(point)






        # Load 2D texture image

        self.image2d = Image2D(self.image2d_path, resolution=0.0003, near = self.n, far = self.f, camera_z=self.camera1_z, alpha=0.5,
                               contourPath=self.contour_path, contourColor=self.color_pinna, displayStyle='line', contourSize=3)
        self.camera1 = self.image2d.camera
        self.rig1 = self.image2d.rig
        self.scene.add(self.rig1) # Add rig1, and hence the entire image2d object to scene



        ############################################
        # Add projector from camera1 through contour points
        self.projector = Projector(self.camera1, self.image2d.contourMesh, near=self.n, far=self.f, delta=10, lineWidth=1, color=self.color_pinna,
                                   visibleRay=False, visibleCone=True)
        self.camera1.add(self.projector.rayMesh)
        self.projector.rayMesh.translate(0, 0, -self.camera1_z) # FIXME: Move projector to camera1 position (remove offset)
        self.image2d.projectorObject = self.projector # establish link between projector and image2d (for movement of camera1 while keeping projector fixed)
        self.rig1.projectorObject = self.projector # establish link between projector and rig1 (for movement of camera1 while keeping projector fixed)

        # # Add position markers
        # posMarker1 = PosMarker([0, 0, camera1_z], color=[0, 1, 1], size=10)
        # self.scene.add(posMarker1)
        # posMarker2 = PosMarker([0, 0, camera1_z-camera1_d], color=[1, 0, 1], size=10)
        # self.scene.add(posMarker2)
        ############################################


        # Load 3D model
        geometry3d = Model3dGeometry(self.model3d_path)
        lambertMaterial = LambertMaterial(properties={"useVertexColors": True})
        self.mesh3d = Mesh(geometry3d, lambertMaterial)
        self.scene.add(self.mesh3d)
        self.mesh3d.rotateY(pi/2)

        # Grid setup
        grid = GridHelper(size=1024, divisions=64, gridColor=[0.6, 0.6, 0.6], centerColor=[0.5, 0.5, 0.5], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes)
        self.initialized = True

    def update(self):

        

        if not self.initialized:
            self.initialize()


        # Update information displayed in the tool panel
        transform_matrix = self.image2d.imagePlane.getWorldMatrix()
        distance = np.linalg.norm(self.camera1.getWorldPosition())
        view_angle = self.camera1.theta
        self.GetParent().update_tool_panel(transform_matrix, distance, view_angle)

        """ Update the scene and toggle between cameras."""
        if self.isKeyDown("space"):  # Toggle between cameras with spacebar
            self.cameraIdx = (self.cameraIdx + 1) % 2

        if self.cameraIdx == 0:
            self.rig0.update(self)
            self.camera0.update(self)
        else:
            self.rig1.update(self)
            self.camera1.update(self)

        self.image2d.update(self)

        

        self.renderer.render(self.scene, self.camera0, viewportSplit="left")   
        self.renderer.render(self.scene, self.camera1, clearColor = False,viewportSplit="right")
        
        


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
