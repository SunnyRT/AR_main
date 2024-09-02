#version 330 core



in vec3 FragPos; // The position of the fragment in world space (input from vert shader)
in vec3 Normal;  // The normal vector in world space (input from vert shader)

uniform vec3 lightPos;
unifrom vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 objectColor; // Color of object
uniform float alpha;      // Transparency of object



out vec4 FragColor; // The final color of each pixel rgba (output)


void main()
{
    
}