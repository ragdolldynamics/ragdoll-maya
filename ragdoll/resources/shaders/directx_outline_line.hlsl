
cbuffer VS_CONSTANT_BUFFER : register(b0)
{
    matrix projectionMatrix;
    matrix viewMatrix;
    matrix viewProjectionTranspose;
    float2 viewportSize;
    float2 empty;
}

cbuffer VS_CONSTANT_BUFFER : register(b1)
{
    matrix modelMatrix;
    float4 constantColor;
    float lineThickness;
    int useConstantColor;
    int usePhongShading;
    float UNUSED;
}

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
    output.position.z = 0; // * output.position.w; perspective divide not required because DirectX uses 0 for upper clipspace range, not -1 like OpenGL.
	return output;
}


[maxvertexcount(128)]
void gs_main(triangle vs_out input[3] : SV_POSITION, inout TriangleStream<gs_out> OutputStream)
{
    gs_out gsout = (gs_out) 0;
    
   float pixelWidth = 2.0 / viewportSize.x;
   float pixelHeight = 2.0 / viewportSize.y;
   
    float u_thickness = lineThickness;
    
    pixelWidth *= u_thickness;
    pixelHeight *= u_thickness;
     
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        gsout.position.x += pixelWidth * gsout.position.w;
        OutputStream.Append(gsout);
    }
    
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        gsout.position.x -= pixelWidth * gsout.position.w;
        gsout.color = float4(0, 1, 0, 1);
        OutputStream.Append(gsout);
    }
    
    for (int i = 0; i < 3; i++) {
        gsout.color = float4(1, 1, 0, 1);
        gsout.position = input[i].position;
        gsout.position.y += pixelHeight * gsout.position.w;
        OutputStream.Append(gsout);
    }
    
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        gsout.position.y -= pixelHeight * gsout.position.w;
        gsout.color = float4(0, 1, 0, 1);
        OutputStream.Append(gsout);
    }
    
    // Bottom right corner cap
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.x += pixelWidth * gsout.position.w;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.y -= pixelHeight * gsout.position.w ;
        OutputStream.Append(gsout);
    }
    
    // Bottom left corner cap
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.y -= pixelHeight * gsout.position.w;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.x -= pixelWidth * gsout.position.w;
        OutputStream.Append(gsout);
    }
    
    // Top right corner cap
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.y += pixelHeight * gsout.position.w;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.x += pixelWidth * gsout.position.w;
        OutputStream.Append(gsout);
    }
    
    // Top left corner cap
    for (int i = 0; i < 3; i++) {
        gsout.position = input[i].position;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.y += pixelHeight * gsout.position.w;
        OutputStream.Append(gsout);
        gsout.position = input[i].position;
        gsout.position.x -= pixelWidth * gsout.position.w;
        OutputStream.Append(gsout);
    }
        
    OutputStream.RestartStrip();
}

struct ps_out
{
    float4 color : SV_Target;
};


ps_out ps_main(gs_out input) 
{
    ps_out output = (ps_out) 0;
    output.color = constantColor;
    return output;
}

