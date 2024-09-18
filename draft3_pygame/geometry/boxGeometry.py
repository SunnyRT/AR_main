from geometry.geometry import Geometry


class BoxGeometry(Geometry):
    def __init__(self, width=1, height=1, depth=1):
        super().__init__()
        # vertices
        p0 = [-width / 2, -height / 2, -depth / 2]
        p1 = [width / 2, -height / 2, -depth / 2]
        p2 = [-width / 2, height / 2, -depth / 2]
        p3 = [width / 2, height / 2, -depth / 2]
        p4 = [-width / 2, -height / 2, depth / 2]
        p5 = [width / 2, -height / 2, depth / 2]
        p6 = [-width / 2, height / 2, depth / 2]
        p7 = [width / 2, height / 2, depth / 2]
        # colors for faces in order:
        # x+, x-, y+, y-, z+, z-
        c1, c2 = [1, 0.5, 0.5], [0.5, 0, 0]
        c3, c4 = [0.5, 1, 0.5], [0, 0.5, 0]
        c5, c6 = [0.5, 0.5, 1], [0, 0, 0.5]
        # texture coordinates
        t0, t1, t2, t3 = [0, 0], [1, 0], [0, 1], [1, 1]
        # Each side consists of two triangles
        positionData = [p5, p1, p3, p5, p3, p7,
                         p0, p4, p6, p0, p6, p2,
                         p6, p7, p3, p6, p3, p2,
                         p0, p1, p5, p0, p5, p4,
                         p4, p5, p7, p4, p7, p6,
                         p1, p0, p2, p1, p2, p3]
        colorData = [c1] * 6 + [c2] * 6 + [c3] * 6 + [c4] * 6 + [c5] * 6 + [c6] * 6
        # uvData = [t0, t1, t3, t0, t3, t2] * 6
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        # self.addAttribute("vec2", "vertexUV", uvData)
        # normal vectors for x+, x-, y+, y-, z+, z-
        n1, n2 = [1, 0, 0], [-1, 0, 0]
        n3, n4 = [0, 1, 0], [0, -1, 0]
        n5, n6 = [0, 0, 1], [0, 0, -1]
        normalData = [n1]*6 + [n2]*6 + [n3]*6 + [n4]*6 + [n5]*6 + [n6]*6
        self.addAttribute("vec3", "vertexNormal", normalData)
        self.addAttribute("vec3", "faceNormal", normalData)
