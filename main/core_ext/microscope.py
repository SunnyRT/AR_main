from core_ext.camera import Camera
import numpy as np
# from core.matrix import Matrix
# from numpy.linalg import inv
# from geometry.boxGeometry import BoxGeometry
# from material.lambertMaterial import LambertMaterial
# from core_ext.mesh import Mesh


class Microscope(Camera):
    
    def __init__(self, imageTexture, resolution, near, isPerspective=True):
        pxWidth = imageTexture.width
        pxHeight = imageTexture.height
        aspectRatio = pxWidth / pxHeight
        angleOfView = self._calcCameraTheta(pxWidth, pxHeight, resolution, near)

        super().__init__(isPerspective=isPerspective, angleOfView=angleOfView,
                       aspectRatio=aspectRatio, 
                       near=near, 
                       renderBox=True)

    def _calcCameraTheta(self, pxWidth, pxHeight, resolution, near):
        # width = pxWidth * resolution * near
        height = pxHeight * resolution * near
        theta = 2 * np.arctan((height / 2) / near) / np.pi * 180
        return theta
    

    def update(self, inputObject, deltaTime=None):
        # Override update function in parent class Camera

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

