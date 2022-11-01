#version 330

out vec4 FragColor;

in vec3 ColorGSOut;

void main()
{        
	FragColor = vec4(ColorGSOut, 1.0);
}