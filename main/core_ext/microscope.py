from core_ext.camera import Camera
import numpy as np
# from core.matrix import Matrix
# from numpy.linalg import inv
# from geometry.boxGeometry import BoxGeometry
# from material.lambertMaterial import LambertMaterial
# from core_ext.mesh import Mesh


class Microscope(Camera):
    
    def __init__(self, imageTexture, isPerspective=True):
        self.pxWidth = imageTexture.width
        self.pxHeight = imageTexture.height
        self.aspectRatio = self.pxWidth / self.pxHeight
        self.isPerspective = isPerspective

        self.initialize()
        self.intialized = True


    
    def initialize(self):
        angleOfView = self._calcCameraTheta(self.pxWidth, self.pxHeight, self.canvas.resolution, self.n) # FIXME: reinitialize if canvas.n changes?????
        super().__init__(isPerspective=self.isPerspective, angleOfView=angleOfView,
                       aspectRatio=self.aspectRatio, 
                       renderBox=True)
        

    def _calcCameraTheta(self, pxWidth, pxHeight, resolution, nearPlane):
        # width = pxWidth * resolution * nearPlane
        height = pxHeight * resolution * nearPlane
        theta = 2 * np.arctan((height / 2) / nearPlane) / np.pi * 180
        return theta
    

    
    def update(self, inputObject, deltaTime=None):
        # Override update function in parent class Camera

        # Handle shift mouse scroll -> set near clipping plane n
        shiftMouseScroll = inputObject.getShiftMouseScroll()
        if shiftMouseScroll != 0:
            self.n += 10*shiftMouseScroll
            self.initialize()
            self.isUpdated = True # FIXME: !!!!!!!!!
            if self.mediator:
                self.mediator.notify(self, "update near plane", data={"shiftScroll": shiftMouseScroll})    


        # FIXME: !!!!!!!!!
        # TODO: track changes in camera parameters (microscopic camera1)
        self.isUpdated = False

        # Assume self.isPerspective = True!!!!
        if inputObject.isKeyPressed('up'):
            self.theta -= 0.1
            self.setPerspective()
            self.isUpdated = True
        if inputObject.isKeyPressed('down'):
            self.theta += 0.1
            self.setPerspective()
            self.isUpdated = True

