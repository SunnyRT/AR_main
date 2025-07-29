from material.material import Material
from core.uniform import Uniform


class BasicMaterial(Material):
    def __init__(self):
    
        vertexShaderCode = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec3 vertexColor;
            out vec3 color;    
                    
            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                color = vertexColor;
            }
        """
    
        fragmentShaderCode = """
            uniform vec3 baseColor;
            uniform float alpha;
            uniform bool useVertexColors;
            in vec3 color;
            out vec4 fragColor;
            
            void main()
            {
                vec4 tempColor = vec4(baseColor, alpha);

                if (useVertexColors) tempColor *= vec4(color, alpha);

                fragColor = tempColor;
            }
        """
        super().__init__(vertexShaderCode, fragmentShaderCode)
        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("float", "alpha", 1.0)
        self.addUniform("bool", "useVertexColors", False)
        self.locateUniforms()
