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
    def __init__(self, imagePath, resolution, near, far, camera_z, alpha=0.5, cameraDisplay=True,
                 contourPath=None, contourColor = [1, 0, 0], displayStyle = 'line', contourSize = 1):    

        print("Initializing Image2D...")

        # 0. Initialize parameters
        texture2d = Texture(imagePath)
        self.pxWidth = texture2d.width
        self.pxHeight = texture2d.height
        self.resolution = resolution
        self.n = near # near clipping plane = focal length (i.e. distance between camera and image plane)
        self.f = far # far clipping plane
        self.aspectRatio = self.pxWidth / self.pxHeight

        # 1. Add movementRig and microscopic camera 
        self.rig = MovementRig()

        # 2. Add microscopic camera
        camera_theta = self._calcCameraTheta()
        self.camera = Camera(isPerspective=True, angleOfView=camera_theta, aspectRatio=self.aspectRatio, renderBox=cameraDisplay)
        

        # 3. Load 2D texture plane mesh from image file
        self.material2d = TextureMaterial(texture2d, {"alpha": alpha})
        self.imagePlane = self._createImagePlane()


        # 4. Load contourMesh from sw contour file
        self.contourColor = contourColor
        if contourPath is not None:
            self._loadContourInfo(contourPath, contourColor, displayStyle, contourSize)
            self.contourMesh = self._createContour()
        else:
            self.contourMesh = None


        
        # 5. Parent relationship 
        # rig -> camera -> imagePlane -> contourMesh
        self.rig.add(self.camera)
        self.camera.add(self.imagePlane)
        if self.contourMesh is not None:
            self.imagePlane.add(self.contourMesh)
        
        # 6. initial positioning
        self.rig.setPosition([0, 0, camera_z])
        self.imagePlane.translate(0, 0, -self.n)
        self.contourMesh.translate(0, 0, 0.1) # TODO: Move contour slightly above imagePlane


        self.projectorObject = None

        print("Image2D initialized")











    def _calcCameraTheta(self):
        width, height = self._getWorldDimensions()
        theta = 2 * np.arctan((height / 2) / self.n) / np.pi * 180
        return theta
    
    def _getWorldDimensions(self):
        width = self.pxWidth * self.resolution * self.n
        height = self.pxHeight * self.resolution * self.n
        return width, height



    def _createImagePlane(self):
        width, height = self._getWorldDimensions()
        geometry2d = PlaneGeometry(width, height, 4, 4, flipY=True)
        imagePlane = Mesh(geometry2d, self.material2d)
        return imagePlane
    
    
    def _updateImagePlane(self):
        if self.imagePlane in self.camera.children:
            self.camera.remove(self.imagePlane)
        self.imagePlane = self._createImagePlane()
        self.camera.add(self.imagePlane)
        self.imagePlane.translate(0, 0, -self.n)
    


    def _loadContourInfo(self, sw_path, contourColor, displayStyle, contourSize):
        with open(sw_path, 'r') as f:
            lines = f.readlines()
        
        # for line in lines:
        #     if line.startswith('CONT'):
        #         parts = line.strip().split()[4:]  # TODO: Skip the first 4 elements: "CONT 0 0 1"

        #         # Extract pairs of (px_x, px_y) pixel coordinates and convert to 3D numpy array
        #         px_coords = np.array([(float(parts[i]), float(parts[i + 1]), 0) for i in range(0, len(parts), 2)])
        #         break

        """FIXME: load multiple contour line!!!!!!!!"""
        self.all_px_coords = []
        self.all_px_coords_segments = np.empty((0,3))

        for line in lines:
            if line.startswith('CONT'):
                parts = line.strip().split()[4:]  # TODO: Skip the first 4 elements: "CONT 0 0 1"

                # Extract pairs of (px_x, px_y) pixel coordinates and convert to 3D numpy array
                px_coords = np.array([(float(parts[i]), float(parts[i + 1]), 0) for i in range(0, len(parts), 2)])
                self.all_px_coords.append(px_coords) # TODO: list of (M,3) arrays, where each array is a contour line segment

                # Modify px_coords data structure to repeat intermediate points (to form segments)
                px_coords_segments = np.empty((0,3))
                for i in range(len(px_coords)-1):
                    px_coords_segments = np.vstack([px_coords_segments, px_coords[i], px_coords[i+1]])

                print(f"added one line of contour with shape {px_coords_segments.shape}")
                self.all_px_coords_segments = np.vstack([self.all_px_coords_segments, px_coords_segments]) if len(self.all_px_coords_segments) > 0 else px_coords_segments
                


        print(f"final contour segments array shape: {self.all_px_coords_segments.shape}")
        print(f"final contour lists shape: {len(self.all_px_coords)}, {[len(segment) for segment in self.all_px_coords]}")

        # if displayStyle == 'point':
        #     self.contourMaterial = PointMaterial({"pointSize": contourSize, "baseColor": contourColor, "roundedPoints": True})
        # elif displayStyle == 'line':
        self.contourMaterial = LineMaterial({"lineWidth": contourSize, "baseColor": contourColor, "lineType": "segments"})



    def _createContour(self):
        width, height = self._getWorldDimensions()
        contourGeometry = ContourGeometry(self.all_px_coords_segments, width, height, self.resolution, self.n, self.contourColor, flipY=True)
        contourMesh = Mesh(contourGeometry, self.contourMaterial)

        return contourMesh

    def _updateContour(self):
        if self.contourMesh in self.imagePlane.children:
            self.imagePlane.remove(self.contourMesh)
        self.contourMesh = self._createContour()
        self.imagePlane.add(self.contourMesh)
        self.contourMesh.translate(0, 0, 0.1)









    def update(self, inputObject):

        # Handle shift and ctrl + mouse scroll to manipulate near and far clipping planes
        shiftMouseScroll = inputObject.getShiftMouseScroll()
        ctrlMouseScroll = inputObject.getCtrlMouseScroll()
        if shiftMouseScroll != 0:
            self.n += 10*shiftMouseScroll

            # update projectorObject coneMesh with new near plane
            if self.projectorObject is not None:
                self.projectorObject.n = self.n
                self.projectorObject._updateConeMesh()
            # print(f"shiftMouseScroll: {shiftMouseScroll}, near: {self.n}")

            # update imagePlane
            self._updateImagePlane()

            # update contourMesh
            if self.contourMesh is not None:
                self._updateContour()

        if ctrlMouseScroll != 0:
            self.f += 10*ctrlMouseScroll

            # update projectorObject coneMesh with new far plane
            if self.projectorObject is not None:
                self.projectorObject.f = self.f
                self.projectorObject._updateConeMesh()
            # print(f"ctrlMouseScroll: {ctrlMouseScroll}, far: {self.f}")

    
    
        # Handle alt + mouse scroll to move camera (rig) while keeping the near and far clipping planes at the same distance
        altSroll = inputObject.getAltMouseScroll()
        if altSroll != 0:
            print(f"altSroll: {altSroll}")
            if self.projectorObject is not None:
                self.rig.translate(0, 0, -altSroll * 10, localCoord=True)
                self.n -= altSroll * 10
                self.f -= altSroll * 10
                self.projectorObject.n -= altSroll * 10
                self.projectorObject.f -= altSroll * 10
                # self.camera.theta = self._calcCameraTheta() # theta would not be affected by camera movement

                self.projectorObject._updateConeMesh()
                self._updateImagePlane()
                if self.contourMesh is not None:
                    self._updateContour()
                print(f"near: {self.projectorObject.n}, far: {self.projectorObject.f}, camera moved: {altSroll * 10}")
            else:
                print("MovementRig.update() error: projectorObject is None")
