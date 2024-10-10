from core_ext.mesh import Mesh
from core_ext.texture import Texture
from core_ext.camera import Camera
from material.textureMaterial import TextureMaterial
from geometry.planeGeometry import PlaneGeometry
from extras.movementRig import MovementRig

import numpy as np

class Image2D(object):
    def __init__(self, imagePath, resolution, focalLength, camera_z=50, cameraDisplay=True):    

        print("Initializing Image2D...")

        # Load 2D texture plane mesh from image file
        texture2d = Texture(imagePath)
        pxWidth = texture2d.width
        pxHeight = texture2d.height
        self.width = pxWidth * resolution * focalLength
        self.height = pxHeight * resolution * focalLength
        self.aspectRatio = pxWidth / pxHeight
        material2d = TextureMaterial(texture2d)
        geometry2d = PlaneGeometry(self.width, self.height, 4, 4)
        self.imagePlane = Mesh(geometry2d, material2d)
        

        # Add microscopic camera and movementRig attached to imagePlane
        camera_theta = 2 * np.arctan((self.height / 2) / focalLength) / np.pi * 180
        self.camera = Camera(isPerspective=True, angleOfView=camera_theta, aspectRatio=self.aspectRatio, renderBox=cameraDisplay)
        self.rig = MovementRig()
        
        # Parent relationship and positioning
        # rig -> camera -> imagePlane
        self.rig.add(self.camera)
        self.rig.setPosition([0, 0, camera_z])
        self.camera.add(self.imagePlane)
        self.imagePlane.translate(0, 0, -focalLength)

        print("Image2D initialized")



        
