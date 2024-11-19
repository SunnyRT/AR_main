import wx
import numpy as np
from core.InputCanvas import InputCanvas # Extend your existing BaseCanvas
from core.guiFrame import GUIFrame
from core_ext.rendererDual import RendererDual
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.microscope import Microscope
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


from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from extras.microscopeRig import MicroscopeRig

from registration.registratorICP import RegistratorICP
# from registration.image2d import Image2D
# from registration.projector import Projector
from factory.imagePlaneFactory import ImagePlaneFactory
from factory.contourMeshFactory import ContourMeshFactory
from factory.projectorMeshFactory import ProjectorMeshFactory
from factory.matchMeshFactory import MatchMeshFactory

from mediator.imageMediator import ImageMediator


# from extras.posMarker import PosMarker
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent, screenSize=[1200, 900]):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent, screenSize)


        self.state = 0 # 0 represents CAD engineering, 1 represents surgery
        self.viewport = 0 # 0 represents pinna, 1 represents incus
        
        self.model3d_path = "D:\sunny\Codes\IIB_project\data\michaelmas\ear.ply"

        self.image1_path = "D:\sunny\Codes\IIB_project\data\michaelmas\pinna.png"
        self.contour1_path = "D:\sunny\Codes\IIB_project\data\michaelmas\pinna.sw"
        self.color_pinna = [1.0, 0.64705882, 0.29803922]
        self.res1=0.0003
        self.n1 = 200
        self.f1 = 250
        self.delta1 = 2

        self.image2_path = "D:\sunny\Codes\IIB_project\data\michaelmas\incus.png"
        self.contour2_path = "D:\sunny\Codes\IIB_project\data\michaelmas\incus.sw"
        self.color_incus = [0.1372549,  0.69803922, 0.        ]
        self.res2=0.00015
        self.n2 = 250
        self.f2 = 260
        self.delta2 = 0.5

        rig_ms_z = 250
        self.init_registration = np.eye(4) # TODO: check!!!
        self.init_registration[2][3] = rig_ms_z # TODO: check!!!
        
        self.mediators = []

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
        self.rig_ms = MicroscopeRig()
        self.rig_ms.setWorldPosition(self.init_registration[:,3])        
        self.rig_ms.setWorldRotation(np.array([self.init_registration[0][0:3],
                                             self.init_registration[1][0:3],
                                             self.init_registration[2][0:3]]))
        self.scene.add(self.rig_ms)

        """"""""""""""""""""""""""" 1. Pinna """""""""""""""""""""""""""
        # a) Set up ms1 (microscope1) for pinna 
        texture1 = Texture(self.image1_path)
        self.ms1 = Microscope(texture1, self.n1, self.res1) # chanegd into new extended class of camera
        self.rig_ms.add(self.ms1)
        
        # TODO: NO MORE UPDATES TO MONITOR below this layer
        # 2) Set up imagePlane
        self.imagePFac1 = ImagePlaneFactory(texture1, self.n1, self.res1)
        image1 = self.imagePFac1.createMesh() # DO NOT save imageP1 as attribute (due to constant updates required!!!!)
        self.ms1.add(image1)

        # 3) Set up contourMesh
        self.contourFac1 = ContourMeshFactory(self.contour1_path, texture1, self.n1, self.res1, self.color_pinna, 1)
        contour1 = self.contourFac1.createMesh()
        image1.add(contour1)
        contour1.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # 4) Set up projectorMesh
        self.projectorFac1 = ProjectorMeshFactory(self.ms1, contour1, self.n1, self.f1, self.delta1, self.color_pinna, alpha=0.5)
        projector1 = self.projectorFac1.createMesh()
        self.ms1.add(projector1)
        self.projectorFac1.correctWorldPos() # Correct projector position to align with microscope


        # 5) Set up mediator for event communication between objects
        mediator1 = ImageMediator(self.rig_ms, self.ms1, self.imagePFac1, self.contourFac1, self.projectorFac1, idx=0)
        self.rig_ms.addMediator(mediator1)
        self.ms1.setMediator(mediator1)
        self.mediators.append(mediator1) # index of mediator correspond to state index (0: pinna, 1: incus)


        """"""""""""""""""""""""""" 2. Incus """""""""""""""""""""""""""
        # a) Set up ms1 (microscope2) for incus
        texture2 = Texture(self.image2_path)
        self.ms2 = Microscope(texture2, self.n2, self.res2) # chanegd into new extended class of camera
        self.rig_ms.add(self.ms2)
        
        # TODO: NO MORE UPDATES TO MONITOR below this layer
        # 2) Set up imagePlane
        self.imagePFac2 = ImagePlaneFactory(texture2, self.n2, self.res2)
        image2 = self.imagePFac2.createMesh() # DO NOT save imageP2 as attribute (due to constant updates required!!!!)
        self.ms2.add(image2)

        # 3) Set up contourMesh
        self.contourFac2 = ContourMeshFactory(self.contour2_path, texture2, self.n2, self.res2, self.color_incus, 1)
        contour2 = self.contourFac2.createMesh()
        image2.add(contour2)
        contour2.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # 4) Set up projectorMesh
        self.projectorFac2 = ProjectorMeshFactory(self.ms2, contour2, self.n2, self.f2, self.delta2, self.color_incus, alpha=0.5)
        projector2 = self.projectorFac2.createMesh()
        self.ms2.add(projector2)
        self.projectorFac2.correctWorldPos() # Correct projector position to align with microscope


        # 5) Set up mediator for event communication between objects
        mediator2 = ImageMediator(self.rig_ms, self.ms2, self.imagePFac2, self.contourFac2, self.projectorFac2, idx=1)
        self.rig_ms.addMediator(mediator2)
        self.ms2.setMediator(mediator2)
        self.mediators.append(mediator2) # index of mediator correspond to state index (0: pinna, 1: incus)

        """"""""""""""""""""""""""" 3. Model3d """""""""""""""""""""""""""
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

        """"""""""""""""""""""""""" 4. Registrator """""""""""""""""""""""""""
        # Setup ICP registrator
        projectors = [projector1, projector2] # require updates of registrator attributes via mediator
        self.matchFac = MatchMeshFactory(sceneObject=self.scene)
        self.registrator = RegistratorICP(projectors, self.model3d, self.rig_ms, 10, self.matchFac) # TODO: execution is done by GUIFrame!!!
        for mediator in self.mediators:
            mediator.setMatchMeshFactory(self.matchFac)
            mediator.setRegistrator(self.registrator)

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
            self.state = (self.state + 1) % 2



        """ Rest CAD viewport camera0 to align with different microscope viewports"""
        if self.isKeyDown("i"): 
            self.viewport = (self.viewport + 1) % len(self.mediators) # 0: pinna, 1: incus, 2:etc

            self.rig0.setWorldPosition(self.rig_ms.getWorldPosition())
            self.rig0.setWorldRotation(self.rig_ms.getWorldRotationMatrix())
            self.rig0.lookAttachment.setWorldRotation(self.rig_ms.lookAttachment.getWorldRotationMatrix())
            if self.viewport == 0:
                self.camera0.zoom = 0.5
                self.mediators[0].notify(self, "update visibility", {"object": "image", "is_visible": True})
                self.mediators[1].notify(self, "update visibility", {"object": "image", "is_visible": False})
            elif self.viewport == 1:
                self.camera0.zoom = 1
                self.mediators[1].notify(self, "update visibility", {"object": "image", "is_visible": True})
                self.mediators[0].notify(self, "update visibility", {"object": "image", "is_visible": False})
            self.camera0.setOrthographic()

        """monitor updates"""
        if self.state == 0:

            self.rig0.update(self)
            self.camera0.update(self)
        else:
            self.rig_ms.update(self)
            if self.viewport == 0:
                self.ms1.update(self)
            elif self.viewport == 1:
                self.ms2.update(self)
 
        """Render the scene"""
        self.renderer.render(self.scene, self.camera0, viewportSplit="left")   
        if self.viewport == 0:
            self.renderer.render(self.scene, self.ms1, clearColor = False,viewportSplit="right")
        elif self.viewport == 1:
            self.renderer.render(self.scene, self.ms2, clearColor = False,viewportSplit="right")
        
        
        


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
