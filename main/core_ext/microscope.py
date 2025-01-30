from core_ext.camera import Camera
import numpy as np
# from core.matrix import Matrix
# from numpy.linalg import inv
# from geometry.boxGeometry import BoxGeometry
# from material.lambertMaterial import LambertMaterial
# from core_ext.mesh import Mesh


class Microscope(Camera):
    
    def __init__(self, imageTexture, n, res, isPerspective=True):
        self.pxWidth = imageTexture.width
        self.pxHeight = imageTexture.height
        self.aspectRatio = self.pxWidth / self.pxHeight
        self.n = n 
        self.res = res
        self.isPerspective = isPerspective
        self.mediator = None

        self.initialize()
        self.intialized = True


    
    def initialize(self):
        angleOfView = self._calcCameraTheta(self.pxWidth, self.pxHeight, self.res, self.n) # FIXME: reinitialize if canvas.n changes?????
        super().__init__(isPerspective=self.isPerspective, angleOfView=angleOfView,
                       aspectRatio=self.aspectRatio, 
                       renderBox=True)
        

    def _calcCameraTheta(self, pxWidth, pxHeight, resolution, nearPlane):
        # width = pxWidth * resolution * nearPlane
        height = pxHeight * resolution * nearPlane
        theta = 2 * np.arctan((height / 2) / nearPlane) / np.pi * 180
        return theta
    
    def setMediator(self, mediator):
        self.mediator = mediator
    
    def update(self, inputObject=None, deltaTime=None, del_n=None): 
        # Override update function in parent class Camera 
        # to detect events of changing camera parameters: self.n

        # simply update n, without monitoring inputObject
        if del_n is not None:
            self.n += del_n
            self.initialize()

        elif inputObject is not None: # observe inputObject to detect events of changing camera parameters
            # Handle shift mouse scroll -> set near clipping plane n
            shiftMouseScroll = inputObject.getShiftMouseScroll()
            if shiftMouseScroll != 0:
                self.n += 10*shiftMouseScroll
                if self.mediator:
                    self.mediator.notify(self, "update near plane", data={"shiftScroll": shiftMouseScroll})    
            
            # Handle ctrl mouse scroll -> set far clipping plane f
            # No update on onself
            ctrlMouseScroll = inputObject.getCtrlMouseScroll()
            if ctrlMouseScroll != 0:
                if self.mediator:
                    self.mediator.notify(self, "update far plane", data={"ctrlScroll": ctrlMouseScroll})      


        else:
            raise ValueError("Microscope.update() error: inputObject is None")

        



