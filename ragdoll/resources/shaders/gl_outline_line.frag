#version 420 core

layout (location = 0) out vec4 fragOut;
uniform vec3 u_color;
uniform vec3 color;

void main()
{
	fragOut = vec4(color, 1.0);
}  