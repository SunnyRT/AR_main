import OpenGL.GL as GL

from material.basicMaterial import BasicMaterial


class SurfaceMaterial(BasicMaterial):
    def __init__(self, properties={}):
        super().__init__()
        # render vertices as surface
        self.settings
        # render both sides? default: False
        # (vertices ordered counter-clockwise)
        self.settings["doubleSide"] = False
        # render triangles as wireframe? default: False
        self.settings["wireframe"] = False
        # line width for wireframe rendering
        self.settings["lineWidth"] = 1.0
        self.setProperties(properties)

    def updateRenderSettings(self):
        
        if self.settings["doubleSide"]:
            GL.glDisable(GL.GL_CULL_FACE)
        else:
            GL.glEnable(GL.GL_CULL_FACE)
        
        if self.settings["wireframe"]:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        
        GL.glLineWidth(self.settings["lineWidth"])
