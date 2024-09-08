from core_ext.object3d import Object3D


class Light(Object3D):

    AMBIENT = 1
    DIRECTIONAL = 2
    POINT = 3
    def __init__(self, lightType=0):
        super().__init__()
        self.lightType = lightType
        self.color = [1.0, 1.0, 1.0]
        self.attentuation = [1.0, 0.0, 0.0]
    