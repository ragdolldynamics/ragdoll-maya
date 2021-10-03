#if !HIDE_OGSFX_UNIFORMS

// Find all available variables here
// https://help.autodesk.com/view/MAYAUL/2020/ENU/?guid=GUID-0939A615-81AC-455C-9B23-9ECEC5835F93

// transform object vertices to world-space
uniform mat4 gWorldXf : World;

// transform object vertices to view space and project them in perspective
uniform mat4 gWvpXf : WorldViewProjection;

uniform mat4 gWorldView : ViewProjectionTranspose;

uniform vec3 Light0Pos : POSITION = { 1.0, 1.0, 1.0 };
uniform vec3 Light0Dir : DIRECTION = { 0.0, -1.0, 0.0 };

uniform texture2D SurfaceMask
<
    string ResourceName = "";
    string UIName = "Surface Mask";
    string ResourceType = "2D";
    string UIWidget = "FilePicker";
    string UIGroup = "Surface";
>;

uniform sampler2D SurfaceMaskSampler = sampler_state 
{
    Texture = <SurfaceMask>;
    TEXTURE_MIN_FILTER = LINEAR;
    TEXTURE_MAG_FILTER = LINEAR;
    TEXTURE_WRAP_S = REPEAT;
    TEXTURE_WRAP_T = REPEAT;
    TEXTURE_WRAP_R = REPEAT;
};

uniform mat4 Light0ViewPrj : SHADOWMAPMATRIX
<
    string Object = "Light 0";
    string UIName = "Light 0 Matrix";
    string UIWidget = "None";
>;

uniform texture2D Light0ShadowMap : SHADOWMAP
<
    string ResourceName = "";
    string ResourceType = "2D";
    string UIWidget = "None";
    string Object = "Light 0";
    string UIName = "light0ShadowMap";
>;

uniform sampler2D Light0ShadowMapSampler = sampler_state 
{
    Texture = <Light0ShadowMap>;
    TEXTURE_MIN_FILTER = NEAREST;
    TEXTURE_MAG_FILTER = NEAREST;
    TEXTURE_WRAP_S = REPEAT;
    TEXTURE_WRAP_T = REPEAT;
    TEXTURE_WRAP_R = REPEAT;
};

uniform vec2 ShadowFilterTaps[10] = {{-0.84052, -0.073954}, {-0.326235, -0.40583}, {-0.698464, 0.457259}, {-0.203356, 0.620585}, {0.96345, -0.194353}, {0.473434, -0.480026}, {0.519454, 0.767034}, {0.185461, -0.894523}, {0.507351, 0.064963}, {-0.321932, 0.595435}};

uniform float SurfaceMaskCutoff = 0.0;

#endif // HIDE_OGSFX_UNIFORMS

#if !HIDE_OGSFX_STREAMS

/* Data from application vertex buffer */
attribute AppData {
    vec3 inPosition   : POSITION;
    vec3 inNormal     : NORMAL;
    vec3 inColor      : COLOR0;
};

/* Data passed from vertex shader to fragment shader */
attribute ToColorPass {
    vec4 Normal         : NORMAL;
    vec4 WorldPosition  : TEXCOORD0;
    vec4 Diffuse        : COLOR0;
};

attribute ToShadowPass {
    vec4 outColor       : COLOR0;
};

#endif  // HIDE_OGSFX_STREAMS

#if !HIDE_OGSFX_CODE

void main() 
{
    vec3 worldNormal = normalize(mat3(gWorldXf) * inNormal);
    Normal = vec4(worldNormal, 1.0);
    Diffuse = vec4(inColor, 1);

    vec4 Po = vec4(inPosition, 1);

    WorldPosition = gWvpXf * Po;
    WorldPosition.z -= 0.0001;

    gl_Position = WorldPosition;
}

#endif