from core.base import Base
from core.openGLUtils import OpenGLUtils
from core.attribute import Attribute
from core.uniform import Uniform
from core.matrix import Matrix
from math import pi
from OpenGL.GL import *



# move a triangle around the screen
class Test(Base):

    def initialize(self):
        print("Initializing program...")

        ### initialize program ###
        vsCode = """
        in vec3 position;
        uniform mat4 projectionMatrix;
        uniform mat4 modelMatrix;
        void main()
        {
            gl_Position = projectionMatrix * modelMatrix * vec4(position, 1.0);
        }
        """

        fsCode = """
        out vec4 fragColor;
        void main()
        {
            fragColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
        """

        self.programRef = OpenGLUtils.initializeProgram(vsCode, fsCode)

        ### render settings ###
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

        ### set up VAO ###
        vaoRef = glGenVertexArrays(1)
        glBindVertexArray(vaoRef)

        ### set up vertex attributes (VBO) ###
        positionData  = [[0.0, 0.2, 0.0], [0.1, -0.2, 0.0], [-0.1, -0.2, 0.0]]
        self.vertexCount = len(positionData)
        positionAttribute = Attribute('vec3', positionData)
        positionAttribute.associateVariable(self.programRef, 'position')

        ### set up uniform variables ###
        mMatrix = Matrix.makeTranslation(0,0,-1)
        self.modelMatrix = Uniform('mat4', mMatrix)
        self.modelMatrix.locateVariable(self.programRef, 'modelMatrix')

        self.isPerspective = True # toggle perspective/orthographic projection
        self.perspectiveMatrix = Matrix.makePerspective()
        self.orthographicMatrix = Matrix.makeOrthographic()
        self.projectionMatrix = Uniform('mat4', self.perspectiveMatrix)
        self.projectionMatrix.locateVariable(self.programRef, 'projectionMatrix')


    def update(self):

        """ space bar toggles between perspective and orthographic projection
            W/A/S/D for up/left/down/right
            Z/X for forward/backward
            Q/E for anti-clockwise/clockwise rotation
        """

        # perspective vs orthographic projection
        if self.input.isKeyDown('space'):
            self.isPerspective = not self.isPerspective
            if self.isPerspective:
                self.projectionMatrix.data = self.perspectiveMatrix
            else:
                self.projectionMatrix.data = self.orthographicMatrix


        # global translation
        if self.input.isKeyPressed('w'):
            m = Matrix.makeTranslation(0, 0.1, 0)
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('s'):
            m = Matrix.makeTranslation(0, -0.1, 0)
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('a'):
            m = Matrix.makeTranslation(-0.1, 0, 0)
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('d'):
            m = Matrix.makeTranslation(0.1, 0, 0)
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('z'):
            m = Matrix.makeTranslation(0, 0, 0.1)
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('x'):
            m = Matrix.makeTranslation(0, 0, -0.1)
            self.modelMatrix.data = m @ self.modelMatrix.data

        # global rotation 
        if self.input.isKeyPressed('q'):
            m = Matrix.makeRotationZ(pi/180) # rotate 1 degrees
            self.modelMatrix.data = m @ self.modelMatrix.data
        if self.input.isKeyPressed('e'):
            m = Matrix.makeRotationZ(-pi/180) # rotate -1 degrees
            self.modelMatrix.data = m @ self.modelMatrix.data

        # local translation
        if self.input.isKeyPressed('i'):
            m = Matrix.makeTranslation(0, 0.1, 0)
            self.modelMatrix.data = self.modelMatrix.data @ m
        if self.input.isKeyPressed('k'):
            m = Matrix.makeTranslation(0, -0.1, 0)
            self.modelMatrix.data = self.modelMatrix.data @ m
        if self.input.isKeyPressed('j'):
            m = Matrix.makeTranslation(-0.1, 0, 0)
            self.modelMatrix.data = self.modelMatrix.data @ m
        if self.input.isKeyPressed('l'):
            m = Matrix.makeTranslation(0.1, 0, 0)
            self.modelMatrix.data = self.modelMatrix.data @ m
        

        # local rotation
        if self.input.isKeyPressed('u'):
            m = Matrix.makeRotationZ(pi/180) 
            self.modelMatrix.data = self.modelMatrix.data @ m
        if self.input.isKeyPressed('o'):
            m = Matrix.makeRotationZ(-pi/180)
            self.modelMatrix.data = self.modelMatrix.data @ m


        ### render scene ###
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.programRef)

        self.projectionMatrix.uploadData()
        self.modelMatrix.uploadData()
        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)


# instantiate the class and run the program
Test().run()
    

