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
        self.viewport = 0 # 0 represents pinna
                          # 1 represents incus, 
                          # 2: facial nerve (val)
                          # 3: sigmoid sinus (val)
                          # 4: rwn (val)
        
        M = 4 # number of components used for registration AND validation
        self.M = M

        self.res = [0.000117 for _ in range(M)] # FIXME:???
        # self.res = [0.00006 for _ in range(M)]

        self.ns = [240 for _ in range(M)]
        self.ns[0] = 200

        self.fs = [260 for _ in range(M)]
        self.fs[0] = 240

        self.deltas = [0.5 for _ in range(M)]
        self.deltas[0] = 2

        self.model3d_path = "D:\\sunny\\Codes\\IIB_project\\data\\6_CT_data\\micro_ct\\micro_ct_mesh_center.ply"
        self.model3d_shell_path = "D:\\sunny\\Codes\\IIB_project\\data\\6_CT_data\\micro_ct\\shells\\shell_outward_1.0.ply"
        # self.model3d_path = "D:\\sunny\\Codes\\IIB_project\\data\\6_CT_data\\pseudo_ct\\pseudo_ct_mesh_center.ply"
        # self.rwn_path = "D:\\sunny\\Codes\\IIB_project\\data\\lent\\rwnContour_center.txt"

        self.image_paths = ["D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0152-20250221_201412.jpg" for _ in range(M)]
        self.image_paths[0] = "D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0153-20250221_201418.jpg"
        
        self.contour_paths = ["" for _ in range(M)]
        self.contour_paths[0] ="D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0153_pinna.sw"
        self.contour_paths[1] = "D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0152_incus.sw"
        self.contour_paths[2] = "D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0152_facialN.sw"
        self.contour_paths[3] = "D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\A0152_OticCap.sw"
        # self.contour_paths[4] = "D:\\sunny\\Codes\\IIB_project\\data\\7_clear_bone\\.sw"

        self.colors = np.zeros((M,3))
        self.colors[0] = [1.0, 0.64705882, 0.29803922]          # pinna
        self.colors[1] = [0.1372549,  0.69803922, 0.        ]   # incus
        self.colors[2] = [0.94901961, 0.94901961, 0.        ]   # facial nerve
        self.colors[3] = [0.4,        0.29803922, 1.        ]   # otic Capsule
        # self.colors[4] = [1, 0, 1]                              # FIXME: rwn


        rig_ms_z = 210
        self.init_registration = np.eye(4) # TODO: check!!!
        self.init_registration[2][3] = rig_ms_z # TODO: check!!!
        

        self.initialized = False  # Ensure scene isn't initialized multiple times


    def initialize(self):
        """ Initialize the scene with lights, cameras, objects, etc."""
        print("Initializing program...")

        # Initialize renderer, scene, and cameras
        self.renderer = RendererDual(glcanvas=self, clearColor=[1,1,1])
        self.scene = Scene()



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
        self.rig_ms.setWorldRotation(np.array([self.init_registration[0][0:3],
                                             self.init_registration[1][0:3],
                                             self.init_registration[2][0:3]]))
        self.rig_ms.setWorldPosition(self.init_registration[:,3])

        self.scene.add(self.rig_ms)

        self.ms_ls, projectorsReg, projectorsVal, mediatorsReg, mediatorsVal, self.mediators = self.setupComps(self.M, 
                                                                                   self.image_paths,
                                                                                   self.contour_paths, 
                                                                                   self.ns, 
                                                                                   self.fs, 
                                                                                   self.deltas, 
                                                                                   self.res,
                                                                                   self.colors,
                                                                                   self.rig_ms)

        assert (len(self.mediators) == self.M), "Number of mediators does not match number of functional components!"


        """"""""""""""""""""""""""" 3. Model3d + RWN"""""""""""""""""""""""""""
        # Load 3D model
        geometry3d = Model3dGeometry(self.model3d_path)
        model3dMaterial = Model3dMaterial(properties={"useVertexColors": True})
        self.model3d = Mesh(geometry3d, model3dMaterial)

        # # Load round window niche (RWN) contour
        # geometryRWN = CurveGeometry(self.rwn_path, color=[1, 0, 1])
        # materialRWN = LineMaterial(properties={"useVertexColors": True, "lineWidth": 3})
        # rwn = Mesh(geometryRWN, materialRWN)
        # self.model3d.add(rwn)

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

        print(f"number of registrating comp:{len(projectorsReg), len(mediatorsReg)}")
        print(f"number of validating comp:{len(projectorsVal), len(mediatorsVal)}")

        """"""""""""""""""""""""""" 3. Model3d shell"""""""""""""""""""""""""""
        geometry3dShell = Model3dGeometry(self.model3d_shell_path)
        alpha3dShell = 0.25
        model3dShellMaterial = Model3dMaterial(properties={"useVertexColors": True, "alpha": alpha3dShell})
        model3dShell = Mesh(geometry3dShell, model3dShellMaterial)
        self.model3d.add(model3dShell)

        """"""""""""""""""""""""""" 4. Registrator """""""""""""""""""""""""""
        # Setup ICP registrator
        matchFacReg = MatchMeshFactory(sceneObject=self.scene)
        self.registrator = RegistratorICP(projectorsReg, self.model3d, self.rig_ms, 10, matchFacReg) # TODO: execution is done by GUIFrame!!!
        for mediator in mediatorsReg:
            mediator.setRegistrator(self.registrator)
            mediator.setMatchMeshFactory(matchFacReg)

        
        """"""""""""""""""""""""""" 4. Validator """""""""""""""""""""""""""
        matchFacVal = MatchMeshFactory(sceneObject=self.scene, color=(1,0,0))
        self.validator = ValidatorICP(projectorsVal, self.model3d, self.rig_ms, 10, matchFacVal) 
        for mediator in mediatorsVal:
            mediator.setValidator(self.validator)
            mediator.setMatchMeshFactory(matchFacVal)



    def setupComp(self, img_path, contour_path, n, f, delta, res, color, rig_ms, function, idx):
        # 1) Set up microscope(ms)
        texture = Texture(img_path)
        ms = Microscope(texture, n, res)
        rig_ms.add(ms)

        # 2) Set up imagePlane
        imagePFac = ImagePlaneFactory(texture, n, res)
        image = imagePFac.createMesh()
        ms.add(image)

        # 3) Set up contourMesh
        contourFac = ContourMeshFactory(contour_path, texture, n, res, color, 3)
        contour = contourFac.createMesh()
        image.add(contour)
        contour.translate(0,0,0.01)

        # 4) Set up projectorMesh
        projectorFac = ProjectorMeshFactory(ms, contour, n, f, delta, color, alpha=0.5) 
        projector = projectorFac.createMesh()
        ms.add(projector)
        projectorFac.correctWorldPos()

        # 5) Set up mediator for event communication between objects
        if function == "Reg":
            mediator = ImageMediator(rig_ms, ms, imagePFac, contourFac, projectorFac, idx)
        elif function == "Val":
            mediator = ValidationMediator(rig_ms, ms, imagePFac, contourFac, projectorFac, idx)
        else:
            raise ValueError("Component function can only be 'Reg' or 'Val'!")
        rig_ms.addMediator(mediator)
        ms.setMediator(mediator)

        return ms, projector, mediator




    def setupComps(self, M, img_paths, contour_paths, ns, fs, deltas, res_ls, colors, rig_ms):
        ms_ls = [None for _ in range(M)]
        projectorsReg = []
        projectorsVal = []
        mediatorsReg = []
        mediatorsVal = []

        for i in range(M):
            if i <= 1:
                ms_ls[i], projector, mediator = self.setupComp(img_paths[i], contour_paths[i], ns[i], fs[i], deltas[i], res_ls[i], colors[i], 
                            rig_ms, "Reg", i)
                projectorsReg.append(projector)
                mediatorsReg.append(mediator)
                print(f"index{i} gives a Registrating obejct")
            else:
                ms_ls[i], projector, mediator = self.setupComp(img_paths[i], contour_paths[i], ns[i], fs[i], deltas[i], res_ls[i], colors[i], 
                            rig_ms, "Val", i-2)
                projectorsVal.append(projector)
                mediatorsVal.append(mediator)
                print(f"index{i} gives a Validating obejct")
                
        mediators = mediatorsReg + mediatorsVal 
        return ms_ls, projectorsReg, projectorsVal, mediatorsReg, mediatorsVal, mediators
    




    def update(self):

        
        if not self.initialized:
            self.initialize()


        """ Update information displayed in the tool panel"""
        transform_matrix = self.rig_ms.getWorldMatrix()
        distance = np.linalg.norm(self.rig_ms.getWorldPosition())
        view_angle = self.ms_ls[self.viewport].theta
        match_count = self.registrator.matchCount
        mean_error = self.registrator.meanError
        mean_norm_measure = self.registrator.meanNormMeasure
        mean_error_val = self.validator.meanError
        mean_norm_measure_val = self.validator.meanNormMeasure

        
        self.GetParent().update_tool_panel(transform_matrix, distance, 
                                           match_count, 
                                           view_angle,
                                           mean_error, mean_norm_measure,
                                           mean_error_val, mean_norm_measure_val)


        """ Update the scene and toggle between cameras."""
        if self.isKeyDown("space"):  # Toggle between cameras with spacebar
            self.state = (self.state + 1) % 2



        """ Rest CAD viewport camera to align with different microscope viewports"""
        if self.isKeyDown("i"): 
            self.viewport = (self.viewport + 1) % len(self.mediators) # TODO: 0: pinna, 1: incus, 2:etc

            self.rig_cm.setWorldRotation(self.rig_ms.getWorldRotationMatrix())
            self.rig_cm.lookAttachment.setWorldRotation(self.rig_ms.lookAttachment.getWorldRotationMatrix())
            self.rig_cm.setWorldPosition(self.rig_ms.getWorldPosition())

            if self.viewport == 0:
                self.camera.zoom = 0.5 # pinna
            else:
                self.camera.zoom = 1 # other components
            self.camera.setOrthographic()

        """monitor updates"""
        if self.state == 0: # CAD view

            self.rig_cm.update(self)
            self.camera.update(self)
        else: # Surgical view
            self.rig_ms.update(self)
            self.ms_ls[self.viewport].update(self)
 
        """Render the scene"""
        self.renderer.render(self.scene, self.camera, viewportSplit="left")  
        self.renderer.render(self.scene, self.ms_ls[self.viewport], clearColor=False, viewportSplit="right") 
        
        


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
