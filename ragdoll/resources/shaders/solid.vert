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

    vec4 pos = vec4(aPosition.xyz, 1.0);


  //  pos.z -= 0.01;

 // pos *= vec4(vec3(1.,1.,1.)*0.9999995,1);
 
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * pos;
   // gl_Position =  pos;
}