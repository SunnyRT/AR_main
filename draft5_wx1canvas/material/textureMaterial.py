from material.material import Material
from OpenGL.GL import *

class TextureMaterial(Material):

    def __init__(self, texture, properties={}):

        vertexShaderCode = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec2 vertexUV;
            uniform vec2 reppeatUV;
            uniform vec2 offsetUV;
            out vec2 UV;
            
            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                UV = vertexUV * reppeatUV + offsetUV;
            }
        """

        fragmentShaderCode = """
            uniform vec3 baseColor;
            uniform sampler2D texture;
            in vec2 UV;
            out vec4 fragColor;
            
            void main()
            {
                vec4 color = vec4(baseColor, 1.0) * texture2D(texture, UV); // FIXME: texture2D is a GLSL 1.20 function (deprecated in 1.30)
                if (color.a < 0.1) discard;

                fragColor = color;
            }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)

        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("sampler2D", "texture", [texture.textureRef, 1]) # texture unit 1
        self.addUniform("vec2", "reppeatUV", [1.0, 1.0]) # default value: no repetition
        self.addUniform("vec2", "offsetUV", [0.0, 0.0])
        self.locateUniforms() # locate all uniforms in shader program

        # render both sides?
        self.settings["doubleSided"] = True
        # render triangles as wireframe?
        self.settings["wireframe"] = False
        # line thickness for wireframe rendering
        self.settings["lineWidth"] = 1.0

        self.setProperties(properties)

    def updateRenderSettings(self):

        if self.settings["doubleSided"]:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)
        
        if self.settings["wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glLineWidth(self.settings["lineWidth"])

