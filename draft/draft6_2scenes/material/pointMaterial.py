import OpenGL.GL as GL

from material.basicMaterial import BasicMaterial


class PointMaterial(BasicMaterial):
    def __init__(self, properties={}):
        super().__init__()
        # Render vertices as continuous line by default
        self.settings["drawStyle"] = GL.GL_POINTS
        # Set the line thickness
        self.settings["pointSize"] = 1
        # draw points as rounded
        self.settings["roundedPoints"] = False
        
        self.setProperties(properties)

    def updateRenderSettings(self):
        GL.glPointSize(self.settings["pointSize"])
        if self.settings["roundedPoints"]:
            GL.glEnable(GL.GL_POINT_SMOOTH)
        else:
            GL.glDisable(GL.GL_POINT_SMOOTH)
