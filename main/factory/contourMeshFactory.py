from factory.meshFactory import MeshFactory
from geometry.contourGeometry import ContourGeometry
from material.lineMaterial import LineMaterial
from mesh.mesh import Mesh

import numpy as np

class ContourMeshFactory(MeshFactory):
    def __init__(self, sw_path, texture, n, res, contourColor, contourSize, alpha=1, mediator=None):
        super().__init__(mediator)

        self.n = n
        self.res = res
        self.texture = texture # to get width and height (scale dimension of contour)
        self.contourColor = contourColor
        self.material = LineMaterial({"lineWidth": contourSize, "baseColor": contourColor, "lineType": "segments", "alpha": alpha})   
        self.all_px_coords, self.all_px_coords_segments = self._loadContourInfo(sw_path)
        


    def _loadContourInfo(self, sw_path): # one-off calling to load information
        with open(sw_path, 'r') as f:
            lines = f.readlines()

        """ load multiple contour line!!!!!!!!"""
        all_px_coords_segments = [] # irregular list of (M,3) arrays, where each array is a contour line segment
        all_px_coords = np.empty((0,3)) # (N,3) array, where N is the total number of contour vertices (for all segments)

        for line in lines:
            if line.startswith('CONT'):
                parts = line.strip().split()[4:]  # Skip the first 4 elements: "CONT 0 0 1"

                # Extract pairs of (px_x, px_y) pixel coordinates and convert to 3D numpy array
                px_coords_segment = np.array([(float(parts[i]), float(parts[i + 1]), 0) for i in range(0, len(parts), 2)])
                all_px_coords_segments.append(px_coords_segment) # list of (M,3) arrays, where each array is a contour line segment

                # Modify px_coords_segment data structure to repeat intermediate points (to form segments)
                px_coords = np.empty((0,3))
                for i in range(len(px_coords_segment)-1):
                    px_coords = np.vstack([px_coords, px_coords_segment[i], px_coords_segment[i+1]])

                # print(f"added one line of contour with shape {px_coords.shape}")
                all_px_coords = np.vstack([all_px_coords, px_coords]) if len(px_coords) > 0 else all_px_coords
       
        # print(f"final contour lists shape: {len(self.all_px_coords_segments)}, {[segment.shape for segment in self.all_px_coords_segments]}")
        return all_px_coords, all_px_coords_segments             


    def createGeometry(self, texture):
        width = texture.width * self.res * self.n # scale contour to world dimension
        height = texture.height * self.res * self.n
        return ContourGeometry(self.all_px_coords, self.all_px_coords_segments, width, height, self.res, self.n, self.contourColor, flipY=True)
    

    def createMesh(self):
        geometry = self.createGeometry(self.texture)
        self.mesh = Mesh(geometry, self.material)
        return self.mesh

    def update(self, del_n=None, n=None):
        # override parent class method
        if del_n is not None: # update n
            self.n += del_n
        elif n is not None:
            self.n = n
        self.mesh = super().update()
        self.mesh.translate(0, 0, 0.1) # move contour slightly above the image plane
        return self.mesh