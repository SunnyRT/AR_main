from core_ext.object3d import Object3D
from OpenGL.GL import *

class Mesh(Object3D):

    def __init__(self, geometry, material):
        super().__init__()
        self.geometry = geometry
        self.material = material

        # should this object be rendered?
        self.visible = True

        # set up associations between 
        # vertex attributes stored in geometry
        # and shader programs stored in material
        self.vaoRef = glGenVertexArrays(1)
        glBindVertexArray(self.vaoRef)
        for variableName, attributeObject in self.geometry.attributes.items():
            attributeObject.associateVariable(material.programRef, variableName)
        # unbind VAO
        glBindVertexArray(0)


        