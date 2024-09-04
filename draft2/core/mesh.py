import numpy as np
from core.attribute import Attribute
from core.openGLUtils import OpenGLUtils
from core.uniform import Uniform
from OpenGL.GL import *
import plyfile

class Mesh:
    def __init__(self, path):
        self.vertices = None
        self.indices = None
        self.normals = None
        self.colors = None
        self.vertexAttribute = None
        self.normalAttribute = None
        self.colorAttribute = None
        self.indexBuffer = None
        self.programRef = None
        # self.load_ply(path)
        # for debugging with known data: ##
        self.vertices = np.array([
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.0, 0.5, 0.0]
        ], dtype=np.float32)
        self.indices = np.array([0, 1, 2], dtype=np.uint32)

    def load_ply(self, path):
        """ Load a PLY file """

        plydata = plyfile.PlyData.read(path)

        # Extract vertices, face_indices, normals, and colors
        vertices = np.array([(vertex['x'], vertex['y'], vertex['z']) for vertex in plydata['vertex'].data])
        centroid = np.mean(vertices, axis=0)
        self.vertices = vertices - centroid # center the mesh

        self.indices = np.array([face[0] for face in plydata['face'].data])
        print(f"Loaded {self.vertices.shape} vertices and {self.indices.shape} indices")

        if 'nx' in plydata['vertex'].data.dtype.names:
            self.normals = np.array([(vertex['nx'], vertex['ny'], vertex['nz']) for vertex in plydata['vertex'].data])
            print(f"Loaded {self.normals.shape} normals")

        if 'red' in plydata['vertex'].data.dtype.names:
            self.colors = np.array([(vertex['red'], vertex['green'], vertex['blue']) for vertex in plydata['vertex'].data])
            print(f"Loaded {self.colors.shape} colors")

        
        

    
    def initialize(self):
        """ Prepare the shader program and buffers """
        # vsCode = """
        # in vec3 position;
        # in vec3 normal;
        # in vec3 color;

        # out vec3 fragColor;
        # out vec3 fragNormal;
        # out vec3 fragPosition;

        # void main() {
        #     fragColor = color;
        #     fragNormal = normal;
        #     fragPosition = position;
        #     gl_Position = vec4(position, 1.0);
        # }
        # """

        vsCode = """
        in vec3 position;
        void main() {
            gl_Position = vec4(position, 1.0);
        }
        """

        # fsCode = """
        # in vec3 fragColor;
        # in vec3 fragNormal;
        # in vec3 fragPosition;

        # out vec4 finalColor;

        # uniform vec3 lightPosition;
        # uniform vec3 viewPosition;

        # void main() {
        #     // Ambient component
        #     vec3 ambient = 0.1 * fragColor;

        #     // Diffuse component
        #     vec3 lightDir = normalize(lightPosition - fragPosition);
        #     float diff = max(dot(fragNormal, lightDir), 0.0);
        #     vec3 diffuse = diff * fragColor;

        #     // Specular component
        #     vec3 viewDir = normalize(viewPosition - fragPosition);
        #     vec3 reflectDir = reflect(-lightDir, fragNormal);
        #     float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
        #     vec3 specular = spec * vec3(1.0, 1.0, 1.0);

        #     // Combine all components
        #     vec3 result = ambient + diffuse + specular;
        #     finalColor = vec4(result, 1.0);
        # }
        # """
        
        fsCode = """
        out vec4 finalColor;
        void main() {
            finalColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
        """

        self.programRef = OpenGLUtils.initializeProgram(vsCode, fsCode)

        self.vertexAttribute = Attribute('vec3', self.vertices)
        self.normalAttribute = Attribute('vec3', self.normals)
        self.colorAttribute = Attribute('vec3', self.colors)

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
