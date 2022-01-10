// Stick with GLSL syntax
#define vec3 float3
#define vec4 float4
#define mat3 float3x3
#define mat4 float4x4


cbuffer UpdatePerObject : register(b1) {
    mat4 gWvpXf : WorldViewProjection < string UIWidget = "None"; >;
};


struct ToVertex {
    vec3 Position : POSITION;
    vec4 Color : COLOR0;
};

struct ToPixel {
    vec4 Position : SV_Position;
    vec4 Color : COLOR0;
};

struct ToScreen {
    vec4 Color : SV_Target;
};


ToPixel ShaderVertex(ToVertex IN) {
    ToPixel OUT;

    OUT.Color = IN.Color;

    OUT.Position = mul(vec4(IN.Position, 1), gWvpXf);
    OUT.Position.z -= 0.0005;

    return OUT;
}


ToScreen ShaderPixel(ToPixel IN) {
    ToScreen OUT;

    OUT.Color = IN.Color;

    return OUT;
}

technique11 Wireframe
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
