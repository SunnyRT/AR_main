import wx
import numpy as np
from core.baseInput import InputCanvas # Extend your existing BaseCanvas
from core.baseGUI import GUIFrame
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


from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from extras.projector import Projector
from extras.posMarker import PosMarker
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent, screenSize=[1200, 900]):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent, screenSize)


        self.cameraIdx = 0
        self.image2d_path = "D:/sunny/Codes/IIB_project/data/summer/JPEG0803.jpg"
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

        # Load 3D model
        geometry3d = Model3dGeometry("D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply")
        lambertMaterial = LambertMaterial(properties={"baseColor": [0.2, 0.5, 0.5]})
        self.mesh3d = Mesh(geometry3d, lambertMaterial)
        self.scene.add(self.mesh3d)

        # Load 2D texture image
        texture2d = Texture(self.image2d_path)
        texture2d_height = texture2d.height
        texture2d_width = texture2d.width
        image2d_aspect_ratio = texture2d_width / texture2d_height
        material2d = TextureMaterial(texture2d)
        image2d_height = 64
        image2d_width = image2d_height * image2d_aspect_ratio
        geometry2d = PlaneGeometry(image2d_width, image2d_height, 256, 256)
        self.image2d = Mesh(geometry2d, material2d)



        ############################################
        # Add contour points on 2D image
        pointGeometry = RectangleGeometry(image2d_width, image2d_height)
        pointMaterial = PointMaterial({"pointSize": 5, "useVertexColors": True})
        contourPoints = Mesh(pointGeometry, pointMaterial)
        self.image2d.add(contourPoints)
        ############################################

        
        # Set up second camera: camera1 for surgeon viewport
        camera1_z = 50
        camera1_d = 80
        camera1_theta = 2* np.arctan((image2d_height / 2) / camera1_d) /np.pi * 180
        self.camera1 = Camera(isPerspective=True, angleOfView=camera1_theta, aspectRatio=image2d_aspect_ratio, renderBox=True)
        self.rig1 = MovementRig()
        self.rig1.add(self.camera1)

        
        self.rig1.setPosition([0, 0, camera1_z])
        self.scene.add(self.rig1)    
        self.camera1.add(self.image2d)
        self.image2d.translate(0, 0, -camera1_d)

        # camera1Geometry = BoxGeometry(5, 5, 10)
        # camera1Material = LambertMaterial(properties={"baseColor": [0.8, 0.8, 0]})
        # camera1Box = Mesh(camera1Geometry, camera1Material)
        # self.camera1.add(camera1Box) # Make camera1 visible
        # camera1Box.translate(0, 0, 5) # Move camera1Box to camera1 position (remove offset)


        print(camera1_z)
        print(self.camera1.getWorldPosition())

        ############################################
        # Add projector from camera1 through contour points
        self.projector = Projector(self.camera1, contourPoints, lineWidth=2, color=[1,1,0], ConvertToSurface=False)
        self.camera1.add(self.projector)
        self.projector.translate(0, 0, -camera1_z) # Move projector to camera1 position (remove offset)


        # # Add position markers
        # posMarker1 = PosMarker([0, 0, camera1_z], color=[0, 1, 1], size=10)
        # self.scene.add(posMarker1)
        # posMarker2 = PosMarker([0, 0, camera1_z-camera1_d], color=[1, 0, 1], size=10)
        # self.scene.add(posMarker2)
        ############################################

        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes)

        self.initialized = True

    def update(self):

        if not self.initialized:
            self.initialize()


        transform_matrix = self.image2d.getWorldMatrix()
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
