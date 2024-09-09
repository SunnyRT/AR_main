from core.base import Base
from core.openGLUtils import OpenGLUtils
from core.attribute import Attribute
from OpenGL.GL import *

# render 6 points in a hexagon arrangement
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        ### initialize program ###
        vsCode = """
        in vec3 position; // position is an attribute variable which receives data from VBO
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

        ### set up vertex array object ###
        vaoRef = glGenVertexArrays(1)
        glBindVertexArray(vaoRef)

        ### set up vertex buffer object ###
        positionData = [[0.8, 0.0, 0.0], [0.4, 0.6, 0.0], [-0.4, 0.6, 0.0], [-0.8, 0.0, 0.0], [-0.4, -0.6, 0.0], [0.4, -0.6, 0.0]]
        self.vertexCount = len(positionData)
        positionAttribute = Attribute('vec3', positionData)
        positionAttribute.associateVariable(self.programRef, 'position')

    def update(self):
        glUseProgram(self.programRef)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertexCount) # GL_LINE_LOOP | GL_LINE_STRIP | GL_LINES | GL_TRIANGLES | GL_TRIANGLE_STRIP | GL_TRIANGLE_FAN

# instantiate this class and run the program
Test().run()