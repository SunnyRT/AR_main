from geometry.geometry import Geometry

class ContourGeometry(Geometry):

    def __init__(self, px_coords, width, height, resolution, focalLength, contourColor=[1,0,0]):
        super().__init__()

        # convert pixel coordinates (px_x, px_y, z=0) into world coordinates (x, y, z)
        positionData = px_coords * resolution * focalLength 
        # offset image such that (0, 0) is at the center
        positionData[:, 0] -= width / 2
        positionData[:, 1] -= height / 2
        colorData = [contourColor] * len(px_coords)

        self.addAttribute
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.countVertices()