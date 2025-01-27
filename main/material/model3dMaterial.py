from material.material import Material
from OpenGL.GL import *


# Lambert Illumination: consider ambient and diffuse light only (no specular light)
# Phong Shading: lights are calculated per fragment (pixel)
class Model3dMaterial(Material):

    def __init__(self, texture=None, properties={}):

        vertexShaderCode = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec3 vertexColor;
            in vec2 vertexUV;
            in vec3 vertexNormal;
            out vec3 position;
            out vec3 color;
            out vec2 UV;
            out vec3 normal;

            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                position = vec3(modelMatrix * vec4(vertexPosition, 1.0));                
                color = vertexColor;
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

            
            // Uniforms to control visibility of each component
            uniform bool oticCapsuleVisible;
            uniform bool stapesVisible;
            uniform bool sigmoidSinusVisible;
            uniform bool incusVisible;
            uniform bool malleusVisible;
            uniform bool chordaTympaniVisible;
            uniform bool tensorTympaniVisible;
            uniform bool facialNerveVisible;
            uniform bool pinnaVisible;

            // Constants for component colors
            const vec3 OTIC_CAPSULE_COLOR = vec3(0.4, 0.29803922, 1.0); // (102, 76, 255)
            const vec3 STAPES_COLOR = vec3(0.06666667, 0.48627451, 0.69803922); // (17, 124, 178)
            const vec3 SIGMOID_SINUS_COLOR = vec3(0.0, 0.50196078, 0.75294118); // (0, 128, 192)
            const vec3 INCUS_COLOR = vec3(0.1372549, 0.69803922, 0.0); // (35, 178, 0)
            const vec3 MALLEUS_COLOR = vec3(0.69803922, 0.69803922, 0.1372549); // (178, 178, 35)
            const vec3 CHORDA_TYMPANI_COLOR = vec3(0.90588235, 0.72156863, 0.09411765); // (231, 184, 24)
            const vec3 TENSOR_TYMPANI_COLOR = vec3(0.92156863, 0.62352941, 0.07843137); // (235, 159, 20)
            const vec3 FACIAL_NERVE_COLOR = vec3(0.94901961, 0.94901961, 0.0); // (242, 242, 0)
            const vec3 PINNA_COLOR = vec3(1.0, 0.64705882, 0.29803922); // (255, 165, 76)

            // Epsilon for color comparison to account for floating-point precision
            const float EPSILON = 0.001;

            
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
            uniform bool useVertexColors;
            uniform bool useTexture;
            uniform sampler2D texture;
            in vec3 position;
            in vec3 color;
            in vec2 UV;
            in vec3 normal;
            out vec4 fragColor;
            void main()
            {

                bool renderComponent = true; // Default to render

                if (useVertexColors) {
                    if (distance(color, OTIC_CAPSULE_COLOR) < EPSILON) {
                        renderComponent = oticCapsuleVisible;
                    }
                    else if (distance(color, STAPES_COLOR) < EPSILON) {
                        renderComponent = stapesVisible;
                    }
                    else if (distance(color, SIGMOID_SINUS_COLOR) < EPSILON) {
                        renderComponent = sigmoidSinusVisible;
                    }
                    else if (distance(color, INCUS_COLOR) < EPSILON) {
                        renderComponent = incusVisible;
                    }
                    else if (distance(color, MALLEUS_COLOR) < EPSILON) {
                        renderComponent = malleusVisible;
                    }
                    else if (distance(color, CHORDA_TYMPANI_COLOR) < EPSILON) {
                        renderComponent = chordaTympaniVisible;
                    }
                    else if (distance(color, TENSOR_TYMPANI_COLOR) < EPSILON) {
                        renderComponent = tensorTympaniVisible;
                    }
                    else if (distance(color, FACIAL_NERVE_COLOR) < EPSILON) {
                        renderComponent = facialNerveVisible;
                    }
                    else if (distance(color, PINNA_COLOR) < EPSILON) {
                        renderComponent = pinnaVisible;
                    }
                    // If color does not match any component
                    // Here, choose to render by default
                }

                if (!renderComponent) {
                    discard;
                }            


                vec4 tempColor = vec4(baseColor, alpha);
                if (useTexture) tempColor *= texture2D(texture, UV);
                if (useVertexColors) tempColor *= vec4(color, 1.0);
  
                //calculate total effect of lights on tempColor
                vec3 total = vec3(0.0, 0.0, 0.0);
                total += lightCalc(light0, position, normal);
                total += lightCalc(light1, position, normal);
                total += lightCalc(light2, position, normal);
                total += lightCalc(light3, position, normal);

                tempColor *= vec4(total, 1.0);
                fragColor = tempColor;
            }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)
        
        # add uniforms
        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("float", "alpha", 1.0)
        self.addUniform("bool", "useVertexColors", True)
        self.addUniform("Light", "light0", None)
        self.addUniform("Light", "light1", None)
        self.addUniform("Light", "light2", None)
        self.addUniform("Light", "light3", None)
        
        self.addUniform("bool", "useTexture", 0)
        if texture == None:
            pass
        else:
            print("Warning: Texture support is not implemented for model3d.")
        self.addUniform("bool", "useTexture", False)

        # Add uniforms for component visibility
        # Default to render all components
        self.addUniform("bool", "oticCapsuleVisible", True)
        self.addUniform("bool", "stapesVisible", True)
        self.addUniform("bool", "sigmoidSinusVisible", True)
        self.addUniform("bool", "incusVisible", True)
        self.addUniform("bool", "malleusVisible", True)
        self.addUniform("bool", "chordaTympaniVisible", True)
        self.addUniform("bool", "tensorTympaniVisible", True)
        self.addUniform("bool", "facialNerveVisible", True)
        self.addUniform("bool", "pinnaVisible", True)

        self.locateUniforms()

        # render both sides?
        self.settings["doubleSided"] = True
        # render triangles as wireframe?
        self.settings["wireframe"] = False
        # line thickness for wireframe rendering
        self.settings["lineWidth"] = 1.0

        self.setProperties(properties)

    # alreay defined in (parent) LambertMaterial
    # def updateRenderSettings(self):
            
    #     if self.settings["doubleSided"]:
    #         glDisable(GL_CULL_FACE)
    #     else:
    #         glEnable(GL_CULL_FACE)

    #     if self.settings["wireframe"]:
    #         glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    #     else:
    #         glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
    #     glLineWidth(self.settings["lineWidth"])


    def setComponentVisibility(self, component_name, is_visible):
        """
        Set the visibility of a component.

        Parameters:
        - component_name (str): Name of the component (e.g., "oticCapsule")
        - is_visible (bool): Visibility state
        """
        uniform_name = f"{component_name}Visible"
        if uniform_name in self.uniforms:
            self.setProperties({uniform_name: is_visible})
        else:
            print(f"Warning: Uniform '{uniform_name}' not found in material.")

            