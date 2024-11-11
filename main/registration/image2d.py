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
    def __init__(self, texture2d, rig, camera, resolution, near, far, alpha=0.5,
                 contourPath=None, contourColor = [1, 0, 0], displayStyle = 'line', contourSize = 1):    

        print("Initializing Image2D...")

        # 0. Initialize parameters
        self.rig = rig
        self.camera = camera
        self.pxWidth = texture2d.width
        self.pxHeight = texture2d.height
        self.resolution = resolution
        self.n = near # near clipping plane = focal length (i.e. distance between camera and image plane)
        self.f = far # far clipping plane
        self.aspectRatio = self.pxWidth / self.pxHeight



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


        
        # 5. Scene graph parent relationship 
        # rig -> camera -> imagePlane -> contourMesh
        self.camera.add(self.imagePlane)
        if self.contourMesh is not None:
            self.imagePlane.add(self.contourMesh)
        
        # 6. initial positioning
        self.imagePlane.translate(0, 0, -self.n)
        # self.contourMesh.translate(0, 0, 0.1) # TODO: Move contour slightly above imagePlane


        self.projectorObject = None

        print("Image2D initialized")







    
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

        """ load multiple contour line!!!!!!!!"""
        self.all_px_coords_segments = [] # irregular list of (M,3) arrays, where each array is a contour line segment
        self.all_px_coords = np.empty((0,3)) # (N,3) array, where N is the total number of contour vertices (for all segments)

        for line in lines:
            if line.startswith('CONT'):
                parts = line.strip().split()[4:]  # TODO: Skip the first 4 elements: "CONT 0 0 1"

                # Extract pairs of (px_x, px_y) pixel coordinates and convert to 3D numpy array
                px_coords_segment = np.array([(float(parts[i]), float(parts[i + 1]), 0) for i in range(0, len(parts), 2)])
                self.all_px_coords_segments.append(px_coords_segment) # TODO: list of (M,3) arrays, where each array is a contour line segment

                # Modify px_coords_segment data structure to repeat intermediate points (to form segments)
                px_coords = np.empty((0,3))
                for i in range(len(px_coords_segment)-1):
                    px_coords = np.vstack([px_coords, px_coords_segment[i], px_coords_segment[i+1]])

                # print(f"added one line of contour with shape {px_coords.shape}")
                self.all_px_coords = np.vstack([self.all_px_coords, px_coords]) if len(px_coords) > 0 else self.all_px_coords
                


        # print(f"final contour segments array shape: {self.all_px_coords.shape}")
        print(f"final contour lists shape: {len(self.all_px_coords_segments)}, {[segment.shape for segment in self.all_px_coords_segments]}")

        # if displayStyle == 'point':
        #     self.contourMaterial = PointMaterial({"pointSize": contourSize, "baseColor": contourColor, "roundedPoints": True})
        # elif displayStyle == 'line':
        self.contourMaterial = LineMaterial({"lineWidth": contourSize, "baseColor": contourColor, "lineType": "segments"})



    def _createContour(self):
        width, height = self._getWorldDimensions()
        contourGeometry = ContourGeometry(self.all_px_coords, self.all_px_coords_segments, width, height, self.resolution, self.n, self.contourColor, flipY=True)
        contourMesh = Mesh(contourGeometry, self.contourMaterial)

        return contourMesh

    def _updateContour(self):
        if self.contourMesh in self.imagePlane.children:
            self.imagePlane.remove(self.contourMesh)
            del self.contourMesh
        self.contourMesh = self._createContour()
        self.imagePlane.add(self.contourMesh)
        self.contourMesh.translate(0, 0, 0.1)













    def update(self, inputObject, registratorObject=None):

        # Handle shift and ctrl + mouse scroll to manipulate near and far clipping planes
        shiftMouseScroll = inputObject.getShiftMouseScroll()
        ctrlMouseScroll = inputObject.getCtrlMouseScroll()
        if shiftMouseScroll != 0:
            self.n += 10*shiftMouseScroll
            self.camera.n = self.n

            # update projectorObject coneMesh with new near plane
            if self.projectorObject is not None:
                self.projectorObject.n = self.n
                self.projectorObject._updateConeMesh()
            # print(f"shiftMouseScroll: {shiftMouseScroll}, near: {self.n}")

            # update registratorObject with new coneMesh(mesh1)
            if registratorObject is not None:
                registratorObject.updateMesh1(self.projectorObject.coneMesh)

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

            # update registratorObject with new coneMesh(mesh1)
            if registratorObject is not None:
                registratorObject.updateMesh1(self.projectorObject.coneMesh)
    
    
        # Handle alt + mouse scroll to move camera (rig) while keeping the near and far clipping planes at the same distance
        altSroll = inputObject.getAltMouseScroll()
        if altSroll != 0:
            print(f"altSroll: {altSroll}")
            if self.projectorObject is not None:
                self.rig.translate(0, 0, -altSroll * 10, localCoord=True)
                self.n -= altSroll * 10
                self.camera.n = self.n
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
        
            # update registratorObject with new coneMesh(mesh1)
            if registratorObject is not None:
                registratorObject.updateMesh1(self.projectorObject.coneMesh)

        
