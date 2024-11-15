import OpenGL.GL as GL

from material.basicMaterial import BasicMaterial


class LineMaterial(BasicMaterial):
    def __init__(self, properties={}):
        super().__init__()
        # Render vertices as continuous line by default
        self.settings["drawStyle"] = GL.GL_LINE_STRIP
        # Set the line thickness
        self.settings["lineWidth"] = 1
        # line type: "connected" | "loop" | "segments"
        self.settings["lineType"] = "connected"
        
        self.setProperties(properties)

    def updateRenderSettings(self):
        GL.glLineWidth(self.settings["lineWidth"])
        if self.settings["lineType"] == "connected":
            self.settings["drawStyle"] = GL.GL_LINE_STRIP
        elif self.settings["lineType"] == "loop":
            self.settings["drawStyle"] = GL.GL_LINE_LOOP
        elif self.settings["lineType"] == "segments":
            self.settings["drawStyle"] = GL.GL_LINES
        else:
            raise Exception("Unknown LineMaterial draw style")