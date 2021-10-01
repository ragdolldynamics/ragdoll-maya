#if !HIDE_OGSFX_UNIFORMS

// transform object vertices to world-space:
uniform mat4 gWorldXf : World;

// transform object normals, tangents, & binormals to world-space:
uniform mat4 gWorldITXf : WorldInverseTranspose;

// transform object vertices to view space and project them in perspective:
uniform mat4 gWvpXf : WorldViewProjection;

// provide tranform from "view" or "eye" coords back to world-space:
uniform mat4 gViewIXf : ViewInverse;

// apps should expect this to be normalized
uniform vec3 gLightDirection : DIRECTION = {0.7f, -0.7f, -0.7f};

// Ambient Light
uniform vec3 gAmbient : AMBIENT = { 0.17f, 0.17f, 0.17f };

#endif // HIDE_OGSFX_UNIFORMS

#if !HIDE_OGSFX_STREAMS

/* Data from application vertex buffer */
attribute AppData {
    vec3 Position    : POSITION;
    vec3 Normal    : NORMAL;
    vec4 Color    : COLOR0;
};

/* Data passed from vertex shader to fragment shader */
attribute ToFrag {
    vec3 WorldNormal    : TEXCOORD1;
    vec3 WorldEyeVec    : TEXCOORD2;
    vec4 ObjPos    : TEXCOORD3;
    vec4 DCol : COLOR0;
};

#endif  // HIDE_OGSFX_STREAMS

#if !HIDE_OGSFX_CODE

void main() 
{
    vec3 Nw = normalize((gWorldITXf * vec4(Normal,0.0)).xyz);
    WorldNormal = Nw;
    float lamb = clamp(dot(Nw,-gLightDirection),0.0,1.0);
    DCol = vec4((vec3(lamb) + gAmbient).rgb,1);
    DCol *= Color;
    vec4 Po = vec4(Position.xyz, 1);
    vec3 Pw = (gWorldXf * Po).xyz;
    WorldEyeVec = normalize(gViewIXf[3].xyz - Pw);
    vec4 hpos = gWvpXf * Po;
    gl_Position = hpos;
}

#endif