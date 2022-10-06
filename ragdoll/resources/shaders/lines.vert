#version 330

layout (location = 0) in vec4 aPosition;
layout (location = 1) in vec3 aColor; // storing color in the normal attribute

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrix;

uniform vec3 uniformColor;
uniform int useUniformColor;
out vec3 Color;

void main()
{
    if (useUniformColor == 1)
        Color = uniformColor;
    else
        Color = aColor;

    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(aPosition.xyz, 1.0);
    gl_Position.z -= 0.0005;
}