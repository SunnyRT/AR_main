import numpy as np
from geometry.geometry import Geometry  # adapt to your actual import path

class CurveGeometry(Geometry):
    def __init__(self, txt_path):
        """
        txt_path: path to the .txt file containing lines of form:
          comment 48.42099 37.87287 72.20630 -0.90840 0.17427 -0.38006
        """
        super().__init__()

        positions = []
        normals = []

        # Read text file
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("comment CLOSED_LANDCURVE"):
                    # Potentially parse the label or number of points
                    continue
                elif line.startswith("comment"):
                    parts = line.split()
                    if len(parts) == 7:
                        x  = float(parts[1])
                        y  = float(parts[2])
                        z  = float(parts[3])
                        nx = float(parts[4])
                        ny = float(parts[5])
                        nz = float(parts[6])
                        positions.append([x, y, z])
                        normals.append([nx, ny, nz])

        positions = np.array(positions)
        normals   = np.array(normals)

        # Recenter around the centroid
        centroid = np.mean(positions, axis=0)
        positions -= centroid

        # Now store in this geometry's attributes
        self.addAttribute("vec3", "vertexPosition", positions)
        self.addAttribute("vec3", "vertexNormal", normals)

        # If you want to store them separately as 'unique' versions (or for lines instead of faces):
        self.addAttribute("vec3", "uniqueVertexPosition", positions)
        self.addAttribute("vec3", "uniqueVertexNormal", normals)

        # Colors are not in these comment lines, so default them if needed
        # e.g. all white
        default_colors = np.ones_like(positions)  # shape = (n,3) filled with 1.0
        self.addAttribute("vec3", "vertexColor", default_colors)
        self.addAttribute("vec3", "uniqueVertexColor", default_colors)
