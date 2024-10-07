import OpenGL.GL as GL

from material.basicMaterial import BasicMaterial


class PointMaterial(BasicMaterial):
    def __init__(self, properties={}):
        super().__init__()
        # Render vertices as continuous line by default
        self.settings["drawStyle"] = GL.GL_POINT
        # Set the line thickness
        self.settings["pointSize"] = 1
        
        self.setProperties(properties)

    def updateRenderSettings(self):
        GL.glPointSize(self.settings["pointSize"])
        self.settings["drawStyle"] = GL.GL_POINTS