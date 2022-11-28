// GLSL syntax
#define vec3 float3
#define vec4 float4
#define mat3 float3x3
#define mat4 float4x4

cbuffer VS_CONSTANT_BUFFER : register(b0) {
	mat4 projectionMatrix;
	mat4 viewMatrix;
    matrix viewProjectionTranspose;
    float2 viewportSize;
    float2 empty;
}

cbuffer VS_CONSTANT_BUFFER : register(b1) {
    matrix modelMatrix;
}

struct vs_in {
    float3 in_position : POSITION;
    float3 in_normal : NORMAL;
};

struct vs_out {
	float4 position : SV_POSITION;
};


vs_out vs_main(vs_in input) {
    vs_out output = (vs_out) 0;    
    output.position = mul(float4(input.in_position, 1), modelMatrix);
    output.position = mul(output.position, viewMatrix);
    output.position = mul(output.position, projectionMatrix);  
    output.position.z = 1;
	return output;
}

struct ps_out
{
    float4 color : SV_Target;
};


ps_out ps_main(vs_out input) : SV_TARGET
{
    ps_out output = (ps_out) 0;
    output.color = float4(1, 1, 1, 0);
    return output;
}