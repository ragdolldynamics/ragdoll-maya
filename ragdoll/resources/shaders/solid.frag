#if !HIDE_OGSFX_STREAMS

/* Data passed from vertex shader to fragment shader */
attribute FromVert {
    vec3 WorldNormal    : TEXCOORD1;
    vec3 WorldEyeVec    : TEXCOORD2;
    vec4 ObjPos    : TEXCOORD3;
    vec4 DCol : COLOR0;
};

/* Data output by the fragment shader */
attribute ToScreen 
{
    vec4 colorOut:COLOR0;
}

#endif // HIDE_OGSFX_STREAMS

#if !HIDE_OGSFX_CODE

void main()
{
    colorOut = vec4(DCol.rgb, 1.0);
}

#endif // HIDE_OGSFX_CODE
