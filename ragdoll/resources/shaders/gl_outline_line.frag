#version 420 core

layout (location = 0) out vec4 fragOut;
uniform vec3 u_color;
uniform vec3 color;

void main()
{
	gl_FragDepth = 0.0;
	fragOut = vec4(color, 1.0);
}  