from geometry.geometry import Geometry

class RectangleGeometry(Geometry): 

    def __init__(self, width=1, height=1, position=[0,0], alignment=[0.5,0.5]):  
        super().__init__()

        self.w = width
        self.h = height
        x,y = position
        a,b = alignment

        P0 = [x+ (-a)*width, y+ (-b)*height, 0]
        P1 = [x+(1-a)*width, y+ (-b)*height, 0]
        P2 = [x+ (-a)*width, y+(1-b)*height, 0]
        P3 = [x+(1-a)*width, y+(1-b)*height, 0]
        

        C0, C1, C2, C3 = [1,1,1], [1,0,0], [0,1,0], [0,0,1]
        positionData = [P0, P1, P3, P0, P3, P2]
        # colorData = [C0, C1, C3, C0, C3, C2]
        colorData = [C0,C0,C0,C3,C3,C3]

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.countVertices()