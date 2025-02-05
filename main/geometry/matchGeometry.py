from geometry.geometry import Geometry

class MatchGeometry(Geometry): # connecting lines to visualize match pairs in ICP algorithm

    def __init__(self, matchPairs, color=(1, 1, 1)):
        super().__init__()

        
        positionData = [point for pair in matchPairs for point in pair]


        colorData = [color] * len(positionData)
        # print(f"matchcolor: {color}")

        self.addAttribute
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.countVertices()