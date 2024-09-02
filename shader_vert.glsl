#version 330 core

/*
layout(location = 0) in vec3 aPos; // The position of the vertex (input)
layout(location = 1) in vec3 aNormal; // The normal vector at the vertex (input)

uniform mat4 model; 
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;



void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;

    gl_Position = projection * view * vec4(FragPos, 1.0);


}
*/


void main() 
{
    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
}