from math import pi, sin, cos

from core.matrix import Matrix
from geometry.parametricGeometry import ParametricGeometry


class EllipsoidGeometry(ParametricGeometry):

    def __init__(self, width=1, height=1, depth=1, radiusSegments=32, heightSegments=16):
        def S(u, v):

            return [width / 2 * sin(v) * cos(u),
                    height / 2 * sin(v),
                    depth / 2 * cos(u) * cos(v)]

        super().__init__(uStart=0,
                         uEnd=2*pi,
                         uResolution=radiusSegments,
                         vStart=-pi/2,
                         vEnd=pi/2,
                         vResolution=heightSegments,
                         surfaceFunction=S)
      
