// GLSL syntax
#define vec3 float3
#define vec4 float4
#define mat3 float3x3
#define mat4 float4x4

cbuffer VS_CONSTANT_BUFFER : register(b0) {
	mat4 projectionMatrix;
	mat4 viewMatrix;
    mat4 viewProjectionTranspose;
}

cbuffer VS_CONSTANT_BUFFER : register(b1)
{
    matrix modelMatrix;
    float4 uniformColor;
    float lineThickness;
    int useUniformColor;
    int usePhongShading;
    float UNUSED;
}

struct vs_in
{
    float3 in_position : POSITION;
    float3 in_normal : NORMAL;
};

struct vs_out
{
	float4 position : SV_POSITION;
    float4 normal : NORMAL;
};

vs_out vs_main(vs_in input) {
	
    vs_out output = (vs_out) 0;
	
	vec3 worldNormal = normalize(mul(input.in_normal, (mat3) modelMatrix));
    output.normal = vec4(worldNormal, 1.0);

    output.position = mul(float4(input.in_position, 1), modelMatrix);
    output.position = mul(output.position, viewMatrix);
    output.position = mul(output.position, projectionMatrix);
    output.position.z -= 0.001;
    
	return output;
}

float4 ps_main(vs_out input) : SV_TARGET
{
    if (usePhongShading) {
        float colorAmount = 0.8;
        float diffuseAmount = 0.2;
        float specularAmount = 0.1;
        float brightness = 1.0;
        float ambient = 0.0;
        int shininess = 2;
        vec3 gLightDir = vec3(0.07, -0.26, 1.0);
        mat4 gWorldView = viewProjectionTranspose;
        float4 gColor = uniformColor;

        // Diffuse
        vec3 lightColor = vec3(1, 1, 1);
        vec3 norm = normalize(input.normal.xyz);
        mat3 worldView = (mat3) gWorldView;
        vec3 lightDir = -normalize(mul(worldView, gLightDir));
        float diff = max(dot(norm, lightDir), ambient);
        vec3 diffuse = diff * lightColor * diffuseAmount;

        // Specular
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(lightDir, reflectDir), 0.0), shininess);
        vec3 specular = spec * lightColor * specularAmount;

        vec3 objectColor = gColor * colorAmount;
        vec3 result = objectColor + diffuse + specular;

        return vec4(result, 1);
    }
    else {
        return uniformColor;
    }
}