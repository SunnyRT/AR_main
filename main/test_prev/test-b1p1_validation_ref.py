import wx
import numpy as np
from core.InputCanvas import InputCanvas # Extend your existing BaseCanvas
from core.guiFrame import GUIFrame
from core_ext.rendererDual import RendererDual
from core_ext.scene import Scene
from core_ext.camera import Camera
from core_ext.microscope import Microscope
from mesh.mesh import Mesh

from geometry.model3dGeometry import Model3dGeometry
from geometry.curveGeometry import CurveGeometry
from core_ext.texture import Texture
from material.model3dMaterial import Model3dMaterial
from material.lineMaterial import LineMaterial


from light.ambientLight import AmbientLight
from light.directionalLight import DirecitonalLight
from light.pointLight import PointLight


from extras.axesHelper import AxesHelper
from extras.gridHelper import GridHelper
from extras.movementRig import MovementRig
from extras.microscopeRig import MicroscopeRig

from registration.registratorICP import RegistratorICP
from registration.validatorICP import ValidatorICP
from factory.imagePlaneFactory import ImagePlaneFactory
from factory.contourMeshFactory import ContourMeshFactory
from factory.projectorMeshFactory import ProjectorMeshFactory
from factory.matchMeshFactory import MatchMeshFactory

from mediator.imageMediator import ImageMediator
from mediator.validationMediator import ValidationMediator


# from extras.posMarker import PosMarker
from math import pi


# Extend your previous BaseCanvas instead of creating a new MyGLCanvas
class MyCanvas(InputCanvas):
    def __init__(self, parent, screenSize=[1200, 900]):
        # Call the constructor of the parent BaseCanvas
        super().__init__(parent, screenSize)


        self.state = 0 # 0 represents CAD engineering, 1 represents surgery
        self.viewport = 0 # 0 represents pinna, 1 represents incus

        self.res = []
        self.ns = []
        self.fs = []
        self.deltas = []

        self.model3d_path = "D:\\sunny\\Codes\\IIB_project\\data\\michaelmas\\ear.ply"
        self.rwn_path = "D:\\sunny\\Codes\\IIB_project\\data\\lent\\rwnContour_center.txt"

        self.image0_path = "D:\\sunny\\Codes\\IIB_project\\data\\christmas\\Images_02122024\\Bone1\\Position1\\x0.4_Pinna.BMP"
        self.contour0_path = "D:\\sunny\\Codes\\IIB_project\\data\\christmas\\Images_02122024\\Bone1\\Position1\\x0.4_Pinna.sw"
        self.color_pinna = [1.0, 0.64705882, 0.29803922]
        res0 = 0.000117 #FIXME:????
        n0 = 200
        f0 = 230
        delta0 = 2
        self.res.append(res0)
        self.ns.append(n0)
        self.fs.append(f0)
        self.deltas.append(delta0)

        self.image1_path = "D:\\sunny\\Codes\\IIB_project\\data\\christmas\\Images_02122024\\Bone1\\Position1\\x0.4_Bone.BMP"
        self.contour1_path = "D:\\sunny\\Codes\\IIB_project\\data\\christmas\\Images_02122024\Bone1\\Position1\\x0.4_Bone.sw"
        self.color_incus = [0.1372549,  0.69803922, 0.        ]
        res1= 0.000117 #FIXME:????
        n1 = 240
        f1 = 250
        delta1 = 0.5
        self.res.append(res1)
        self.ns.append(n1)
        self.fs.append(f1)
        self.deltas.append(delta1)

        rig_ms_z = 200
        self.init_registration = np.eye(4) # TODO: check!!!
        self.init_registration[2][3] = rig_ms_z # TODO: check!!!
        
        # self.mediators = []
        # self.projectorFacs = []
        self.initialized = False  # Ensure scene isn't initialized multiple times


    def initialize(self):
        """ Initialize the scene with lights, cameras, objects, etc."""
        print("Initializing program...")

        # Initialize renderer, scene, and cameras
        self.renderer = RendererDual(glcanvas=self, clearColor=[1,1,1])
        self.scene = Scene()
        projectors = [] # require updates of registrator attributes via mediator
        projectorsVal = [] # require updates of validator attributes via mediator
        self.mediators=[] # clear mediators list for each initialization
        self.mediatorsReg = [] 
        self.mediatorsVal = [] 

        self.projectorFacs = [] # clear projectorFacs list for each initialization


        # Set up camera: camera for CAD engineering viewport
        self.camera = Camera(isPerspective=False, aspectRatio=600/900, zoom=0.5)
        self.rig_cm = MovementRig() # MovementRig for CAD camera
        self.rig_cm.add(self.camera)
        self.rig_cm.setPosition([-100, 50, 500]) 
        self.rig_cm.lookAt([0, 0, 0])
        self.scene.add(self.rig_cm)



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
        # 1) Set up ms0 (microscope1) for pinna 
        texture0 = Texture(self.image0_path)
        self.ms0 = Microscope(texture0, self.ns[0], self.res[0]) # chanegd into new extended class of camera
        self.rig_ms.add(self.ms0)
        
        # TODO: NO MORE UPDATES TO MONITOR below this layer
        # 2) Set up imagePlane
        self.imagePFac0 = ImagePlaneFactory(texture0, self.ns[0], self.res[0])
        image0 = self.imagePFac0.createMesh() # DO NOT save imageP0 as attribute (due to constant updates required!!!!)
        self.ms0.add(image0)

        # 3) Set up contourMesh
        self.contourFac0 = ContourMeshFactory(self.contour0_path, texture0, self.ns[0], self.res[0], self.color_pinna, 3)
        contour0 = self.contourFac0.createMesh()
        image0.add(contour0)
        contour0.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # 4) Set up projectorMesh
        self.projectorFac0 = ProjectorMeshFactory(self.ms0, contour0, self.ns[0], self.fs[0], self.deltas[0], self.color_pinna, alpha=0.5)
        self.projectorFacs.append(self.projectorFac0)
        projector0 = self.projectorFac0.createMesh()
        projectors.append(projector0)
        self.ms0.add(projector0)
        self.projectorFac0.correctWorldPos() # Correct projector position to align with microscope


        # 5) Set up mediator for event communication between objects
        mediator0 = ImageMediator(self.rig_ms, self.ms0, self.imagePFac0, self.contourFac0, self.projectorFac0, idx=0)
        self.rig_ms.addMediator(mediator0)
        self.ms0.setMediator(mediator0)
        self.mediators.append(mediator0) # index of mediator correspond to state index (0: pinna, 1: incus)
        self.mediatorsReg.append(mediator0) 

        """"""""""""""""""""""""""" 2. Incus """""""""""""""""""""""""""
        # 1) Set up ms1 (microscope1) for incus
        texture1 = Texture(self.image1_path)
        self.ms1 = Microscope(texture1, self.ns[1], self.res[1]) # chanegd into new extended class of camera
        self.rig_ms.add(self.ms1)
        
        # TODO: NO MORE UPDATES TO MONITOR below this layer
        # 2) Set up imagePlane
        self.imagePFac1 = ImagePlaneFactory(texture1, self.ns[1], self.res[1])
        image1 = self.imagePFac1.createMesh() # DO NOT save image1 as attribute (due to constant updates required!!!!)
        self.ms1.add(image1)

        # 3) Set up contourMesh
        self.contourFac1 = ContourMeshFactory(self.contour1_path, texture1, self.ns[1], self.res[1], self.color_incus, 3)
        contour1 = self.contourFac1.createMesh()
        image1.add(contour1)
        contour1.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # 4) Set up projectorMesh
        self.projectorFac1 = ProjectorMeshFactory(self.ms1, contour1, self.ns[1], self.fs[1], self.deltas[1], self.color_incus, alpha=0.5)
        self.projectorFacs.append(self.projectorFac1)
        projector1 = self.projectorFac1.createMesh()
        projectors.append(projector1)
        self.ms1.add(projector1)
        self.projectorFac1.correctWorldPos() # Correct projector position to align with microscope


        # 5) Set up mediator for event communication between objects
        mediator1 = ImageMediator(self.rig_ms, self.ms1, self.imagePFac1, self.contourFac1, self.projectorFac1, idx=1)
        self.rig_ms.addMediator(mediator1)
        self.ms1.setMediator(mediator1)
        self.mediators.append(mediator1) # index of mediator correspond to state index (0: pinna, 1: incus)
        self.mediatorsReg.append(mediator1)


        """"""""""""""""""""""""""" 3. (Validation) Facial Nerve """""""""""""""""""""""""""
        # 1) Set up ms0 (microscope1) for pinna 
        self.ms2 = Microscope(texture1, self.ns[1], self.res[1]) 
        self.rig_ms.add(self.ms2)
        
        # 2) Set up imagePlane
        self.imagePFac2 = ImagePlaneFactory(texture1, self.ns[1], self.res[1], alpha=0.1)
        image2 = self.imagePFac2.createMesh() # DO NOT save imageP0 as attribute (due to constant updates required!!!!)
        self.ms2.add(image2)

        # Set up contourMesh
        contour2_path = "D:\\sunny\\Codes\\IIB_project\\data\\lent\\x0.4_Bone_facial_nerve.sw"
        color_facial_nerve = [0.94901961, 0.94901961, 0.        ]
        self.contourFac2 = ContourMeshFactory(contour2_path, texture1, self.ns[1], self.res[1], color_facial_nerve, 3)
        contour2 = self.contourFac2.createMesh()
        image2.add(contour2)
        contour2.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # Set up projectorMesh
        self.projectorFac2 = ProjectorMeshFactory(self.ms2, contour2, self.ns[1], self.fs[1], self.deltas[1], color_facial_nerve, alpha=0.5)
        self.projectorFacs.append(self.projectorFac2)
        projector2 = self.projectorFac2.createMesh()
        projectorsVal.append(projector2)
        self.ms2.add(projector2)
        self.projectorFac2.correctWorldPos() # Correct projector position to align with microscope

        # Set up mediator for event communication between objects
        mediator2 = ValidationMediator(self.rig_ms, self.ms2, self.imagePFac2, self.contourFac2, self.projectorFac2, idx=0)
        self.rig_ms.addMediator(mediator2)
        self.ms2.setMediator(mediator2)
        self.mediators.append(mediator2) # index of mediator correspond to state index (0: pinna, 1: incus, 2: facial nerve)
        self.mediatorsVal.append(mediator2) 

        

        """"""""""""""""""""""""""" 3. (Validation) Sigmoid Sinus """""""""""""""""""""""""""
        # 1) Set up ms0 (microscope1) for pinna 
        self.ms4 = Microscope(texture1, self.ns[1], self.res[1]) 
        self.rig_ms.add(self.ms4)
        
        # 2) Set up imagePlane
        self.imagePFac4 = ImagePlaneFactory(texture1, self.ns[1], self.res[1], alpha=0.1)
        image4 = self.imagePFac4.createMesh() # DO NOT save imageP0 as attribute (due to constant updates required!!!!)
        self.ms4.add(image4)

        # Set up contourMesh
        contour4_path = "D:\\sunny\\Codes\\IIB_project\\data\\lent\\x0.4_Bone_sigmoid_sinus.sw"
        color_sigmoid_sinus = [0.0, 0.50196078, 0.75294118] 
        self.contourFac4 = ContourMeshFactory(contour4_path, texture1, self.ns[1], self.res[1], color_sigmoid_sinus, 3)
        contour4 = self.contourFac4.createMesh()
        image4.add(contour4)
        contour4.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # Set up projectorMesh
        self.projectorFac4 = ProjectorMeshFactory(self.ms4, contour4, self.ns[1], self.fs[1], self.deltas[1], color_sigmoid_sinus, alpha=0.5)
        self.projectorFacs.append(self.projectorFac4)
        projector4 = self.projectorFac4.createMesh()
        projectorsVal.append(projector4)
        self.ms4.add(projector4)
        self.projectorFac4.correctWorldPos() # Correct projector position to align with microscope

        # Set up mediator for event communication between objects
        mediator4 = ValidationMediator(self.rig_ms, self.ms4, self.imagePFac4, self.contourFac4, self.projectorFac4, idx=1)
        self.rig_ms.addMediator(mediator4)
        self.ms4.setMediator(mediator4)
        self.mediators.append(mediator4) # index of mediator correspond to state index (0: pinna, 1: incus, 2: facial nerve)
        self.mediatorsVal.append(mediator4) 



        # """"""""""""""""""""""""""" 3. (Validation) RWN """""""""""""""""""""""""""
        # # 1) Set up ms0 (microscope1) for pinna 
        # self.ms3 = Microscope(texture1, self.ns[1], self.res[1]) 
        # self.rig_ms.add(self.ms3)
        
        # # 2) Set up imagePlane
        # self.imagePFac3 = ImagePlaneFactory(texture1, self.ns[1], self.res[1], alpha=0.1)
        # image3 = self.imagePFac3.createMesh() # DO NOT save imageP0 as attribute (due to constant updates required!!!!)
        # self.ms3.add(image3)

        # # Set up contourMesh
        # contour3_path = "D:\\sunny\\Codes\\IIB_project\\data\\lent\\x0.4_Bone_rwn.sw"
        # color_rwn = [1, 0, 0] # FIXME: 
        # self.contourFac3 = ContourMeshFactory(contour3_path, texture1, self.ns[1], self.res[1], color_rwn, 3)
        # contour3 = self.contourFac3.createMesh()
        # image3.add(contour3)
        # contour3.translate(0, 0, 0.1) # Move contour slightly above the image plane

        # # Set up projectorMesh
        # self.projectorFac3 = ProjectorMeshFactory(self.ms3, contour3, self.ns[1], self.fs[1], self.deltas[1], color_rwn, alpha=0.5)
        # self.projectorFacs.append(self.projectorFac3)
        # projector3 = self.projectorFac3.createMesh()
        # projectorsVal.append(projector3)
        # self.ms3.add(projector3)
        # self.projectorFac3.correctWorldPos() # Correct projector position to align with microscope

        # # Set up mediator for event communication between objects
        # mediator3 = ValidationMediator(self.rig_ms, self.ms3, self.imagePFac3, self.contourFac3, self.projectorFac3, idx=2)
        # self.rig_ms.addMediator(mediator3)
        # self.ms3.setMediator(mediator3)
        # self.mediators.append(mediator3) # index of mediator correspond to state index (0: pinna, 1: incus, 2: facial nerve)
        # self.mediatorsVal.append(mediator3) 

















        """"""""""""""""""""""""""" 3. Model3d + RWN"""""""""""""""""""""""""""
        # Load 3D model
        geometry3d = Model3dGeometry(self.model3d_path)
        model3dMaterial = Model3dMaterial(properties={"useVertexColors": True})
        self.model3d = Mesh(geometry3d, model3dMaterial)

        # Load round window niche (RWN) contour
        geometryRWN = CurveGeometry(self.rwn_path)
        materialRWN = LineMaterial(properties={"useVertexColors": True, "lineWidth": 3})
        rwn = Mesh(geometryRWN, materialRWN)
        self.model3d.add(rwn)

        self.scene.add(self.model3d)
        self.model3d.rotateY(pi/2)
        self.model3d.translate(0, 0, -40, localCoord=False) # TODO: pinna front surface around world origin


        # Grid setup
        grid = GridHelper(size=1024, divisions=64, gridColor=[0.6, 0.6, 0.6], centerColor=[0.5, 0.5, 0.5], lineWidth=1)
        grid.rotateX(-pi / 2)
        # self.scene.add(grid)

        # Axes helper
        axes = AxesHelper(axisLength=128, lineWidth=2)
        # self.scene.add(axes)
        self.initialized = True


        """"""""""""""""""""""""""" 4. Registrator """""""""""""""""""""""""""
        # Setup ICP registrator
        self.matchFac = MatchMeshFactory(sceneObject=self.scene)
        self.registrator = RegistratorICP(projectors, self.model3d, self.rig_ms, 10, self.matchFac) # TODO: execution is done by GUIFrame!!!
        for mediator in self.mediatorsReg:
            mediator.setRegistrator(self.registrator)
            mediator.setMatchMeshFactory(self.matchFac)

        
        """"""""""""""""""""""""""" 4. Validator """""""""""""""""""""""""""
        self.matchFacVal = MatchMeshFactory(sceneObject=self.scene, color=(1,0,0))
        self.validator = ValidatorICP(projectorsVal, self.model3d, self.rig_ms, 10, self.matchFacVal) 
        for mediator in self.mediatorsVal:
            mediator.setValidator(self.validator)
            mediator.setMatchMeshFactory(self.matchFacVal)

    def update(self):

        
        if not self.initialized:
            self.initialize()


        """ Update information displayed in the tool panel"""
        transform_matrix = self.rig_ms.getWorldMatrix()
        distance = np.linalg.norm(self.rig_ms.getWorldPosition())
        # view_angle = self.ms1.theta
        match_count = self.registrator.matchCount
        mean_error = self.registrator.meanError
        mean_norm_measure = self.registrator.meanNormMeasure
        mean_error_val = self.validator.meanError
        mean_norm_measure_val = self.validator.meanNormMeasure

        
        self.GetParent().update_tool_panel(transform_matrix, distance, 
                                           match_count, 
                                           mean_error, mean_norm_measure,
                                           mean_error_val, mean_norm_measure_val)


        """ Update the scene and toggle between cameras."""
        if self.isKeyDown("space"):  # Toggle between cameras with spacebar
            self.state = (self.state + 1) % 2



        """ Rest CAD viewport camera to align with different microscope viewports"""
        if self.isKeyDown("i"): 
            self.viewport = (self.viewport + 1) % len(self.mediators) # TODO: 0: pinna, 1: incus, 2:etc

            self.rig_cm.setWorldPosition(self.rig_ms.getWorldPosition())
            self.rig_cm.setWorldRotation(self.rig_ms.getWorldRotationMatrix())
            self.rig_cm.lookAttachment.setWorldRotation(self.rig_ms.lookAttachment.getWorldRotationMatrix())
            if self.viewport == 0:
                self.camera.zoom = 0.5
            else:
                self.camera.zoom = 1
            self.camera.setOrthographic()

        """monitor updates"""
        if self.state == 0:

            self.rig_cm.update(self)
            self.camera.update(self)
        else:
            self.rig_ms.update(self)
            if self.viewport == 0:
                self.ms0.update(self)
            elif self.viewport == 1:
                self.ms1.update(self)
            elif self.viewport == 2:
                self.ms2.update(self)
            elif self.viewport == 3:
                self.ms4.update(self)
 
        """Render the scene"""
        self.renderer.render(self.scene, self.camera, viewportSplit="left")   
        if self.viewport == 0:
            self.renderer.render(self.scene, self.ms0, clearColor = False,viewportSplit="right")
        elif self.viewport == 1:
            self.renderer.render(self.scene, self.ms1, clearColor = False,viewportSplit="right")
        elif self.viewport == 2:
            self.renderer.render(self.scene, self.ms2, clearColor = False,viewportSplit="right")
        elif self.viewport == 3:
            self.renderer.render(self.scene, self.ms4, clearColor = False,viewportSplit="right")
        # print(f"scene update(): {self.matchFac.mesh.visible}")
        
        


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
