from light.light import Light
class DirecitonalLight(Light):
    def __init__(self, color=[1.0, 1.0, 1.0], direction=[0.0, -1.0, 0.0]):
        super().__init__(Light.DIRECTIONAL)
        self.color = color
        self.setDirection(direction)