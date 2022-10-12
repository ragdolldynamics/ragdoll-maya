
cbuffer VS_CONSTANT_BUFFER : register(b0) {
    matrix projectionMatrix;
    matrix viewMatrix;
    matrix viewProjectionTranspose;
    float2 viewportSize;
    float2 empty;
}

cbuffer VS_CONSTANT_BUFFER : register(b1) {
	matrix modelMatrix;
    float4 uniformColor;
    float lineThicknessBROKEN;
    int useUniformColor;
    int usePhongShading;
    float UNUSED;
}


cbuffer VS_CONSTANT_BUFFER : register(b2)
{
    float lineThickness;
    float3 dummy1;
   // bool useMarkerColor;
}
/*
cbuffer VS_CONSTANT_BUFFER : register(b3)
{
    int useMarkerColor;
    float3 dummy12;
   // bool useMarkerColor;
}*/

struct vs_in
{
    float3 in_position : POSITION;
    float3 in_color : COLOR;
};

struct vs_out
{
    float4 position : SV_POSITION;
    float3 color : COLOR;
};


struct gs_out
{
    float4 position : SV_POSITION;
    float3 color : COLOR;
};

vs_out vs_main(vs_in input) {
	
    vs_out output = (vs_out) 0;
	
    output.position = mul(float4(input.in_position, 1), modelMatrix);
    output.position = mul(output.position, viewMatrix);
    output.position = mul(output.position, projectionMatrix);
    output.position.z -= 0.002;
    output.color = input.in_color;
    
	return output;
}

[maxvertexcount(4)]
void gs_main(line vs_out input[2] : SV_POSITION, inout TriangleStream<gs_out> OutputStream)
{
    gs_out gsout = (gs_out) 0;
    gsout.color = input[0].color;
    
    float4 p1 = input[0].position;
    float4 p2 = input[1].position;
       
    float THICC = lineThickness;
    
    float2 dir = normalize((p2.xy / p2.w - p1.xy / p1.w) * viewportSize);
    float2 offset = float2(-dir.y, dir.x) * THICC / viewportSize;
    
    gsout.position = p1 + float4(offset.xy * p1.w, 0.0, 0.0);
  //  gsout.color = input[0].col
    OutputStream.Append(gsout);
    
    gsout.position = p1 - float4(offset.xy * p1.w, 0.0, 0.0);
    OutputStream.Append(gsout);
    
    gsout.position = p2 + float4(offset.xy * p2.w, 0.0, 0.0);
    OutputStream.Append(gsout);
    
    gsout.position = p2 - float4(offset.xy * p2.w, 0.0, 0.0);
    OutputStream.Append(gsout);
       
    OutputStream.RestartStrip();
}

float4 ps_main(vs_out input) : SV_TARGET {
    
    if (useUniformColor)
        return uniformColor;
    else
        return float4(input.color, 1.0);
}