from geometry.geometry import Geometry
import numpy as np

class ContourGeometry(Geometry):

    def __init__(self, px_coords, px_coords_segments, width, height, resolution, focalLength, contourColor=[1,0,0], flipY=False):
        super().__init__()

        # convert pixel coordinates (px_x, px_y, z=0) into world coordinates (x, y, z)
        positionData = px_coords * resolution * focalLength 
        positionData_segments = [segment * resolution * focalLength for segment in px_coords_segments] 
        # print(f"shape for each segment: {[segment.shape for segment in positionData_segments]}")

        # offset image such that (0, 0) is at the center
        positionData[:, 0] -= width / 2
        positionData[:, 1] -= height / 2
        if flipY:
            positionData[:, 1] *= -1 # flip vertically by negating y-coordinates
            
        # offset image such that (0, 0) is at the center    
        for segment in positionData_segments:
            segment[:, 0] -= width / 2
            segment[:, 1] -= height / 2
            if flipY:
                segment[:, 1] *= -1


        colorData = [contourColor] * len(px_coords)

        self.positionData_segments = positionData_segments # store contour coordinates arranged in contour line segments for later use

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.countVertices()