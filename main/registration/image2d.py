from core_ext.mesh import Mesh
from core_ext.texture import Texture
from core_ext.camera import Camera
from material.textureMaterial import TextureMaterial
from geometry.planeGeometry import PlaneGeometry
from geometry.contourGeometry import ContourGeometry
from material.pointMaterial import PointMaterial
from material.lineMaterial import LineMaterial
from extras.movementRig import MovementRig

import numpy as np

class Image2D(object):
    def __init__(self, imagePath, resolution, focalLength, camera_z=50, alpha=0.5, cameraDisplay=True):    

        print("Initializing Image2D...")

        # Load 2D texture plane mesh from image file
        texture2d = Texture(imagePath)
        pxWidth = texture2d.width
        pxHeight = texture2d.height
        self.resolution = resolution
        self.focalLength = focalLength
        self.width = pxWidth * resolution * focalLength
        self.height = pxHeight * resolution * focalLength
        self.aspectRatio = pxWidth / pxHeight
        material2d = TextureMaterial(texture2d, {"alpha": alpha})
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


    def insertContour(self, sw_path, contourColor = [1, 0, 0], displayStyle = 'line', contourSize = 1):
        with open(sw_path, 'r') as f:
            lines = f.readlines()
        
        
        for line in lines:
            if line.startswith('CONT'):
                parts = line.strip().split()[4:]  # TODO: Skip the first 4 elements: "CONT 0 0 1"

                # Extract pairs of (px_x, px_y) pixel coordinates and convert to 3D numpy array
                px_coords = np.array([(float(parts[i]), float(parts[i + 1]), 0) for i in range(0, len(parts), 2)])
                break

        
        
        contourGeometry = ContourGeometry(px_coords, self.width, self.height, self.resolution, self.focalLength, contourColor)
        if displayStyle == 'point':
            contourMaterial = PointMaterial({"pointSize": contourSize, "baseColor": contourColor, "roundedPoints": True})
        elif displayStyle == 'line':
            contourMaterial = LineMaterial({"lineWidth": contourSize, "baseColor": contourColor, "lineType": "connected"})

        self.contourMesh = Mesh(contourGeometry, contourMaterial)
        self.imagePlane.add(self.contourMesh) # rig -> camera -> imagePlane -> contourMesh
        self.contourMesh.translate(0, 0, 0.1) # TODO: Move contour slightly above imagePlane
