import wx
import numpy as np
from core.InputCanvas import InputCanvas # Extend your existing BaseCanvas
from core.guiFrame import GUIFrame
from core_ext.rendererDual import RendererDual
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.ms1 import ms1
from mesh.mesh import Mesh
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
from registration.registratorICP import RegistratorICP

from factory.imagePlaneFactory import ImagePlaneFactory
from factory.contourMeshFactory import ContourMeshFactory


# from extras.posMarker import PosMarker
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
        self.color_pinna = [1.0, 0.64705882, 0.29803922]
        self.color_incus = [0.1372549,  0.69803922, 0.        ]
        self.res1=0.0003
        self.n1 = 200
        self.f1 = 250
        self.delta1 = 2
        ms1_z = 250
        self.init_registration = np.eye(4) # TODO: check!!!
        self.init_registration[2][3] = ms1_z # TODO: check!!!

        self.initialized = False  # Ensure scene isn't initialized multiple times


    def initialize(self):
        """ Initialize the scene with lights, cameras, objects, etc."""
        print("Initializing program...")

        # Initialize renderer, scene, and cameras
        self.renderer = RendererDual(glcanvas=self, clearColor=[0.8, 0.8, 0.8])
        self.scene = Scene()

        # Set up camera0: camera0 for CAD engineering viewport
        self.camera0 = Camera(isPerspective=False, aspectRatio=600/900, zoom=0.5)
        self.rig0 = MovementRig()
        self.rig0.add(self.camera0)
        self.rig0.setPosition([-100, 50, 500]) 
        self.rig0.lookAt([0, 0, 0])
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


        # Set up microscope rig for surgery viewport
        self.rig_ms = MovementRig()
        self.rig_ms.setWorldPosition(self.init_registration[:,3])        
        self.rig_ms.setWorldRotation(np.array([self.init_registration[0][0:3],
                                             self.init_registration[1][0:3],
                                             self.init_registration[2][0:3]]))
        self.scene.add(self.rig_ms)

        """"""""""""""""""""""""""" 1. Pinna """""""""""""""""""""""""""
        # a) Set up ms1 (microscope1) for pinna 
        texture2d = Texture(self.image2d_path)
        self.ms1 = ms1(self, texture2d) # TODO: chanegd into new extended class of camera
        self.rig_ms.add(self.ms1)
        
        # 2) Set up imagePlane
        self.imagePFac1 = ImagePlaneFactory(texture2d, self.n1, self.res1)
        image1 = self.imagePFac1.createMesh() # DO NOT save imageP1 as attribute (due to constant updates required!!!!)
        self.ms1.add(image1)
        image1.translate(0, 0, -self.n1)

        # 3) Set up contourMesh
        self.contourFac1 = ContourMeshFactory(self.contour_path, texture2d, self.n1, self.res1, self.color_pinna, 1)
        contour1 = self.contourFac1.createMesh()
        image1.add(contour1)
        contour1.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # 4) Set up projectorMesh
        

        # Add projector from ms1 through contour points
        self.projector = Projector(self, self.ms1, self.image2d.contourMesh, 
                                   lineWidth=1, color=self.color_pinna,
                                   alpha=0.5, visibleRay=False, visibleCone=True)
        self.ms1.add(self.projector.rayMesh)

        # Correct projector position and orientation
        ms1_transform = self.ms1.getWorldMatrix()
        ms1_pos = self.ms1.getWorldPosition()
        ms1_inv = np.linalg.inv(ms1_transform)
        projector_transform = self.projector.rayMesh.getWorldMatrix()
        projector_transform = ms1_inv @ projector_transform
        self.projector.rayMesh.setWorldRotation(np.array([projector_transform[0][0:3],
                                                            projector_transform[1][0:3],
                                                            projector_transform[2][0:3]]))
        self.projector.rayMesh.translate(-ms1_pos[0], -ms1_pos[1], -ms1_pos[2])

        # self.projector.rayMesh.translate(0, 0, -self.ms1_z) # Move projector to ms1 position (remove offset)
        self.image2d.projectorObject = self.projector # establish link between projector and image2d (for movement of ms1 while keeping projector fixed)
        self.rig_ms.projectorObject = self.projector # establish link between projector and rig_ms (for movement of ms1 while keeping projector fixed)


        


        # Load 3D model
        geometry3d = Model3dGeometry(self.model3d_path)
        lambertMaterial = LambertMaterial(properties={"useVertexColors": True})
        self.model3d = Mesh(geometry3d, lambertMaterial)
        self.scene.add(self.model3d)
        self.model3d.rotateY(pi/2)

        # Grid setup
        grid = GridHelper(size=1024, divisions=64, gridColor=[0.6, 0.6, 0.6], centerColor=[0.5, 0.5, 0.5], lineWidth=1)
        grid.rotateX(-pi / 2)
        self.scene.add(grid)

        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        self.scene.add(axes)
        self.initialized = True


        # Setup ICP registrator
        self.registrator = RegistratorICP(self.projector.coneMesh, self.model3d, self.scene, self.rig_ms) # TODO: execution is done by GUIFrame!!!

    def update(self):

        
        if not self.initialized:
            self.initialize()


        """ Update information displayed in the tool panel"""
        transform_matrix = self.rig_ms.getWorldMatrix()
        distance = np.linalg.norm(self.rig_ms.getWorldPosition())
        view_angle = self.ms1.theta
        match_count = self.registrator.matchCount
        mean_error = self.registrator.meanError
        mean_norm_measure = self.registrator.meanNormMeasure
        
        self.GetParent().update_tool_panel(transform_matrix, distance, view_angle, 
                                           match_count, mean_error, mean_norm_measure)

        """ Update the scene and toggle between cameras."""
        if self.isKeyDown("space"):  # Toggle between cameras with spacebar
            self.cameraIdx = (self.cameraIdx + 1) % 2

        if self.cameraIdx == 0:
            self.rig0.update(self)
            self.camera0.update(self)
        else:
            self.rig_ms.update(self)
            self.ms1.update(self)
            # update projector coneMesh vertices when only ms1 moves
            if self.rig_ms.isUpdated or self.ms1.isUpdated:
                # print("ms1 moved")
                self.registrator.updateMatch(updateMesh1Vertices=True) 

        """ Rest CAD viewport camera0 to align with ms1 """
        if self.isKeyDown("i"): 
            self.rig0.setWorldPosition(self.rig_ms.getWorldPosition())
            self.rig0.setWorldRotation(self.rig_ms.getWorldRotationMatrix())
            self.rig0.lookAttachment.setWorldRotation(self.rig_ms.lookAttachment.getWorldRotationMatrix())
            self.camera0.zoom = 0.5 # reset zoom
            self.camera0.setOrthographic()

           


        """ Update image2d object """ 
        # - shift / ctrl + mousescroll to move near and far planes for projector conemseh
        # - alt + mousescroll to move ms1 along its local z-axis w/o moving projector
        self.image2d.update(self, self.registrator) # --> image2d.update() triggers registrator.intialize() and thus registrator.updateMatch() when coneMesh get updated


        self.renderer.render(self.scene, self.camera0, viewportSplit="left")   
        self.renderer.render(self.scene, self.ms1, clearColor = False,viewportSplit="right")
        
        


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
