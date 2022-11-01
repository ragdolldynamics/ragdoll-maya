#version 330

layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

out vec4 Normal;

void main()
{
    vec3 worldNormal = normalize(mat3(modelMatrix) * aNormal);
    Normal = vec4(worldNormal, 1.0);

    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(aPosition.xyz, 1.0);
    gl_Position.z -= 0.001;
}