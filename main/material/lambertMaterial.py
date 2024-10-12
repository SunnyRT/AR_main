from material.material import Material
from OpenGL.GL import *


# Lambert Illumination: consider ambient and diffuse light only (no specular light)
# Phong Shading: lights are calculated per fragment (pixel)
class LambertMaterial(Material):

    def __init__(self, texture=None, properties={}):

        vertexShaderCode = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec2 vertexUV;
            in vec3 vertexNormal;
            out vec3 position;
            out vec2 UV;
            out vec3 normal;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                position = vec3(modelMatrix * vec4(vertexPosition, 1.0));                
                UV = vertexUV;
                normal = normalize(mat3(modelMatrix) * vertexNormal);
            }
        """

        fragmentShaderCode = """
            struct Light {
                // 1 = AMBIENT, 2 = DIRECTIONAL, 3 = POINT
                int lightType;
                // used by all types
                vec3 color;
                // used by directional lights
                vec3 direction;
                // used by point lights
                vec3 position;
                vec3 attenuation;  
            };

            uniform Light light0;
            uniform Light light1;
            uniform Light light2;
            uniform Light light3; // maximum 4 light sources

            vec3 lightCalc(Light light, vec3 pointPosition, vec3 pointNormal) {
                float ambient = 0.0;
                float diffuse = 0.0;
                float specular = 0.0;
                float attenuation = 1.0;
                vec3 lightDirection = vec3(0.0, 0.0, 0.0);

                if (light.lightType == 1) // AMBIENT
                { 
                    ambient = 1.0;
                } 
                else if (light.lightType == 2) // DIRECTIONAL
                {
                    lightDirection = normalize(light.direction);
                } 
                else if (light.lightType == 3) // POINT
                {
                    lightDirection = normalize(pointPosition - light.position);
                    float distance = length(light.position - pointPosition);
                    attenuation = 1.0 / (light.attenuation[0] + light.attenuation[1] * distance + light.attenuation[2] * distance * distance);
                }
                
                if (light.lightType > 1) // directional or point light
                {
                    pointNormal = normalize(pointNormal);
                    diffuse = max(dot(pointNormal, -lightDirection), 0.0);
                    diffuse = diffuse * attenuation;
                }
                return light.color * (ambient + diffuse + specular);
            }


            uniform vec3 baseColor;
            uniform float alpha;
            uniform bool useTexture;
            uniform sampler2D texture;
            in vec3 position;
            in vec2 UV;
            in vec3 normal;
            out vec4 fragColor;
            void main()
            {
                vec4 color = vec4(baseColor, alpha);
                if (useTexture) color *= texture2D(texture, UV);
  
                //calculate total effect of lights on color
                vec3 total = vec3(0.0, 0.0, 0.0);
                total += lightCalc(light0, position, normal);
                total += lightCalc(light1, position, normal);
                total += lightCalc(light2, position, normal);
                total += lightCalc(light3, position, normal);

                color *= vec4(total, 1.0);
                fragColor = color;
            }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)
        
        # add uniforms
        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("float", "alpha", 1.0)
        self.addUniform("Light", "light0", None)
        self.addUniform("Light", "light1", None)
        self.addUniform("Light", "light2", None)
        self.addUniform("Light", "light3", None)
        
        self.addUniform("bool", "useTexture", 0)
        if texture == None:
            self.addUniform("bool", "useTexture", False)
        else:
            self.addUniform("bool", "useTexture", True)
            self.addUniform("sampler2D", "texture", [texture.textureRef, 1])

        self.locateUniforms()

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

            