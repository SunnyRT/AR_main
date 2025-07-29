from core_ext.object3d import Object3D


class Light(Object3D):
    
    # Class variables for light types (i.e. attributes of the class ifself, not of instances of the class),
    # which are constants shared by all instances of the class.
    # By placing them outside of the __init__ method: 
        # they can be referenced as Light.AMBIENT, Light.DIRECTIONAL, etc. 
        # without creating an instance of the class.
    # Make it easy to differentiate between light types when creating or managing lights.
    AMBIENT = 1
    DIRECTIONAL = 2
    POINT = 3
    def __init__(self, lightType=0):
        super().__init__()
        self.lightType = lightType
        self.color = [1.0, 1.0, 1.0]
        self.attentuation = [1.0, 0.0, 0.0]
    