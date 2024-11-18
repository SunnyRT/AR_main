from core_ext.object3d import Object3D
from OpenGL.GL import *

class Mesh(Object3D):

    def __init__(self, geometry, material, mediator=None):
        super().__init__()
        self.geometry = geometry
        self.material = material
        if mediator is not None:
            self.mediator = mediator

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



        # VBO: store vertex data (attribute: e.g. positions, colors) in buffer on the GPU
        # VAO: store the state that defines how vertex data is accessed, 
        #   i.e. all configurations details about VBOs, including:
        #      - which VBOs are associated with which attributes
        #      - the format of the data in each VBO (e.g., positions as vec3, colors as vec4)
        #      - which vertex attributes are enabled


        # Procdures to use VAO and VBO:
        # 1. Create and bind a VAO (container, or state manager)
        # 2. Configure VBOs while VAO is bound (i.e. associate VBOs with attributes)
        #   a. Create and bind VBOs
        #   b. Upload data to VBOs
        #   c. Configure vertex attribute pointer
        # 3. unbind VAO when done configuring VBOs (to avoid accidental changes)
        # 4. Bind VAO when rendering (to use the configurations)

    def setAlpha(self, alpha):
        self.material.setProperties({"alpha": alpha})

    def setMediator(self, mediator):
        self.mediator = mediator
        