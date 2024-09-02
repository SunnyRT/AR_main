#version 330 core


/*
in vec3 FragPos; // The position of the fragment in world space (input from vert shader)
in vec3 Normal;  // The normal vector in world space (input from vert shader)

uniform vec3 lightPos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor; // Color of object
uniform float alpha;      // Transparency of object



out vec4 FragColor; // The final color of each pixel rgba (output)


void main()
{

    // Ambient lighting
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse lighting
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular lighting
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightColor;
    
    vec3 result = (ambient + diffuse + specular) * objectColor;
    FragColor = vec4(result, alpha); // Apply alpha for transparency

}

*/



out vec4 fragColor;
void main() 
{
    fragColor = vec4(1.0, 1.0, 0.0, 1.0);
}
