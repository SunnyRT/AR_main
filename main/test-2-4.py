from core.base import Base
from core.openGLUtils import OpenGLUtils
from core.attribute import Attribute
from OpenGL.GL import *

# render 2 shapes
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        ### initialize program ###
        vsCode = """
        in vec3 position; 
        void main() 
        {
            gl_Position = vec4(
                position.x, position.y, position.z, 1.0
            );
        }
        """

        fsCode = """
        out vec4 fragColor;
        void main() 
        {
            fragColor = vec4(0.0, 0.0, 1.0, 1.0);
        }
        """

        self.programRef = OpenGLUtils.initializeProgram(vsCode, fsCode)

        ### render settings (optional) ###
        glLineWidth(5.0)

        ### set up vertex array object - triangle ###
        self.vaoTri = glGenVertexArrays(1)
        glBindVertexArray(self.vaoTri)
        positionDataTri = [[-0.5, 0.8, 0.0], [-0.2, 0.2, 0.0], [-0.8, 0.2, 0.0]]
        self.vertexCountTri = len(positionDataTri)
        positionAttributeTri = Attribute('vec3', positionDataTri)
        positionAttributeTri.associateVariable(self.programRef, 'position')

        ### set up vertex array object - square ###
        self.vaoSqr = glGenVertexArrays(1)
        glBindVertexArray(self.vaoSqr)
        positionDataSqr = [[0.2, 0.8, 0.0], [0.8, 0.8, 0.0], [0.8, 0.2, 0.0], [0.2, 0.2, 0.0]]
        self.vertexCountSqr = len(positionDataSqr)
        positionAttributeSqr = Attribute('vec3', positionDataSqr)
        positionAttributeSqr.associateVariable(self.programRef, 'position')

    def update(self):
        # using same program for both shapes
        glUseProgram(self.programRef)

        # render triangle
        glBindVertexArray(self.vaoTri)
        glDrawArrays(GL_LINE_LOOP, 0, self.vertexCountTri)

        # render square
        glBindVertexArray(self.vaoSqr)
        glDrawArrays(GL_LINE_LOOP, 0, self.vertexCountSqr)

# instantiate this class and run the program
Test().run()