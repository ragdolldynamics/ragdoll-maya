#version 420 core

layout (location = 0) out vec4 fragOut;
uniform vec3 u_color;

void main()
{
	gl_FragDepth = 0.0;
	fragOut = vec4(u_color, 1.0);
}  