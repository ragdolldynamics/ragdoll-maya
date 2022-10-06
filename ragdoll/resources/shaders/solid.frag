#version 330

out vec4 FragColor;

uniform mat4 modelMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat4 viewProjectionTranspose;

uniform bool phongShading;
uniform vec3 uniformColor;
in vec4 Normal;

void main()
{
        float ObjectShading = 1;
        vec3 gColor = uniformColor;

        float colorAmount = 0.8;
        float diffuseAmount = 0.2;
        float specularAmount = 0.1;
        float ambient = 0.0;
        int shininess = 2;
        vec3 gLightDir = vec3(0.07, -0.26, 1.0);
        
        mat4 gWorldView = viewProjectionTranspose;

        // Diffuse
        vec3 lightColor = vec3(1, 1, 1);
        vec3 norm = normalize(Normal.xyz);
        vec3 lightDir = -normalize(mat3(gWorldView) * gLightDir);

        float diff = max(dot(norm, lightDir), ambient);
        vec3 diffuse = diff * lightColor * diffuseAmount * ObjectShading;

        // Specular
        vec3 viewDir = lightDir;
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
        vec3 specular = spec * lightColor * specularAmount * ObjectShading;
        vec3 objectColor = gColor * colorAmount;

        // Composite
        vec3 result = objectColor + diffuse + specular;

        // Gamma correction
       //if (gGamma > 0.1) result = pow(result, vec3(1.0 / gGamma));
       
        FragColor = vec4(result, 1.0);

        if (!phongShading)
            FragColor = vec4(gColor, 1.0);
}