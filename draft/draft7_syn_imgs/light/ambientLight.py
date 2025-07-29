from light.light import Light


class AmbientLight(Light):

    def __init__(self, color=[1.0, 1.0, 1.0]):
        super().__init__(Light.AMBIENT)
        self.color = color