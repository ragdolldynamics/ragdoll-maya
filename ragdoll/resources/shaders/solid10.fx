// Stick with GLSL syntax
#define vec3 float3
#define vec4 float4
#define mat3 float3x3
#define mat4 float4x4


cbuffer UpdatePerFrame : register(b0) {
    vec3 gLightDir;
    mat4 viewPrjT : ViewProjectionTranspose;
    mat4 viewPrj : ViewProjection;
};

cbuffer UpdatePerObject : register(b1) {
    mat4 gWvpXf : WorldViewProjection < string UIWidget = "None"; >;
    mat4 gWorldXf : World < string UIWidget = "None"; >;
    mat4 gWorldView : ViewProjectionTranspose;
};


struct ToVertex {
    vec3 Position : POSITION;
    vec3 Normal : NORMAL;
    vec4 Color : COLOR0;
};

struct ToPixel {
    vec4 Position : SV_Position;
    vec4 Normal : NORMAL;
    vec4 WorldPosition : TEXCOORD0;
    vec4 Color : COLOR0;
    vec3 FogFactor : TEXCOORD1;
};

struct ToScreen {
    vec4 Color : SV_Target;
};


ToPixel ShaderVertex(ToVertex IN) {
    ToPixel OUT;

    vec3 worldNormal = normalize(mul(IN.Normal, (mat3)gWorldXf));
    OUT.Normal = vec4(worldNormal, 1.0);
    OUT.Color = IN.Color;

    OUT.Position = mul(vec4(IN.Position, 1), gWvpXf);
    OUT.Position.z -= 0.0001;

    OUT.WorldPosition = (mul(vec4(IN.Position,1), gWorldXf));

    return OUT;
}



ToScreen ShaderPixel(ToPixel IN) {
    ToScreen OUT;

    float colorAmount = 0.8;
    float diffuseAmount = 0.2;
    float specularAmount = 0.1;
    float brightness = 1.0;
    float ambient = 0.0;
    int shininess = 2;

    // Diffuse
    vec3 lightColor = vec3(1, 1, 1);
    vec3 norm = normalize(IN.Normal.xyz);
    mat3 worldView = (mat3)gWorldView;
    vec3 lightDir = -normalize(mul(worldView, gLightDir));
    float diff = max(dot(norm, lightDir), ambient);
    vec3 diffuse = diff * lightColor * diffuseAmount * IN.Color.w;

    // Specular
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(lightDir, reflectDir), 0.0), shininess);
    vec3 specular = spec * lightColor * specularAmount * IN.Color.w;

    vec3 objectColor = IN.Color.xyz * colorAmount;
    vec3 result = objectColor + diffuse + specular;

    OUT.Color = vec4(result, 1);

    return OUT;
}

technique11 Main
{
    pass P0
    {
        SetVertexShader(CompileShader(vs_5_0, ShaderVertex()));
        SetPixelShader(CompileShader(ps_5_0, ShaderPixel()));
        SetHullShader(NULL);
        SetDomainShader(NULL);
        SetGeometryShader(NULL);
    }
}
