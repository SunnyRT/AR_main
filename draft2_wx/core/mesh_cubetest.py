import numpy as np
from core.attribute import Attribute
from core.openGLUtils import OpenGLUtils
from core.uniform import Uniform
from OpenGL.GL import *
import plyfile

class MeshCube:
    def __init__(self):
        self.vertices = None
        self.indices = None
        # self.normals = None
        # self.colors = None
        self.vertexAttribute = None
        # self.normalAttribute = None
        # self.colorAttribute = None
        self.indexBuffer = None
        self.programRef = None
        # self.load_ply(path)

        # for debugging: simple cube mesh
        self.vertices = np.array([
            [-1.0, -1.0, -1.0], [1.0, -1.0, -1.0], [1.0, 1.0, -1.0], [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0], [1.0, -1.0, 1.0], [1.0, 1.0, 1.0], [-1.0, 1.0, 1.0]
        ], dtype=np.float32)

        self.indices = np.array([
            [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 3, 7, 4]
        ], dtype=np.uint32)

    

    
    def initialize(self):
        """ Prepare the shader program and buffers """


        vsCode = """
        layout(location = 0) in vec3 position;
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        void main() {
            gl_Position = projection * view * model * vec4(position, 1.0);
        }
        """

        
        fsCode = """
        out vec4 fragColor;
        void main() {
            fragColor = vec4(0.5, 0.5, 0.5, 1.0);  // Gray color
        }
        """

        self.programRef = OpenGLUtils.initializeProgram(vsCode, fsCode)

        self.vertexAttribute = Attribute('vec3', self.vertices)
        # self.normalAttribute = Attribute('vec3', self.normals)
        # self.colorAttribute = Attribute('vec3', self.colors)

        # create index buffer
        self.indexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)
        glPointSize(10.0)

    def render(self):
        glUseProgram(self.programRef)

        # # set up attributes
        # self.vertexAttribute.associateVariable(self.programRef, 'position')
        # self.normalAttribute.associateVariable(self.programRef, 'normal')
        # self.colorAttribute.associateVariable(self.programRef, 'color')

        # # set up uniforms
        # self.lightPos = Uniform('vec3', [1.0, 1.0, 1.0])
        # self.lightPos.locateVariable(self.programRef, 'lightPosition')
        # self.viewPos = Uniform('vec3', [0.0, 0.0, 0.0])
        # self.viewPos.locateVariable(self.programRef, 'viewPosition')


        # # draw the mesh
        # glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        # Only use vertex positions for debugging
        self.vertexAttribute.associateVariable(self.programRef, 'position')

        glEnableVertexAttribArray(0)  # Enable the first attribute (position)
        glDrawArrays(GL_POINTS, 0, len(self.vertices))  # Render as points for visibility

        glDisableVertexAttribArray(0)
