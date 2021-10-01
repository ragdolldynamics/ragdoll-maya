#if !HIDE_OGSFX_STREAMS

/* Data passed from vertex shader to fragment shader */
attribute FromVert {
    vec4 Normal         : NORMAL;
    vec4 WorldPosition  : TEXCOORD0;
    vec4 Diffuse        : COLOR0;
};

/* Data output by the fragment shader */
attribute ToScreen  {
    vec4 colorOut : COLOR0;
}

#endif // HIDE_OGSFX_STREAMS

#if !HIDE_OGSFX_CODE

vec3 GetLightPos(int ActiveLightIndex) { 
    return Light0Pos; 
}

vec3 GetLightDir(int ActiveLightIndex)  {
    return normalize(mat3(gWorldView) * vec3(0, 0, 1));
}

vec3 GetLightVectorFunction(int ActiveLightIndex,
                            vec3 LightPosition,
                            vec3 VertexWorldPosition,
                            int LightType,
                            vec3 LightDirection) {

    bool IsDirectionalLight = (LightType == 4);
    vec3 lerpout = mix((LightPosition - VertexWorldPosition), -(LightDirection), float(IsDirectionalLight));
    return lerpout;
}

struct LambertDiffuseOutput {
    vec3 Color;
};

vec3 LambertDiffuseFunction(int ActiveLightIndex,
                            vec3 AlbedoColor,
                            vec3 Normal,
                            vec3 LightVector) {
    float SatOp = clamp(dot(Normal, LightVector), 0.0, 1.0);
    return (SatOp * AlbedoColor);;
}


vec4 SampleFromShadowMap(int ActiveLightIndex, vec2 UVs) { 
    return textureLod(Light0ShadowMapSampler, UVs, 0); 
}


float ShadowMapFunction(int ActiveLightIndex,
                        int lightType,
                        mat4 LightViewPrj,
                        float ShadowMapBias,
                        vec3 VertexWorldPosition) {
    float outValue = 0.0;
    vec4 VectorConstruct = vec4(VertexWorldPosition, 1.0);
    vec4 MulOp = (LightViewPrj * VectorConstruct);
    vec3 DivOp = (MulOp.xyz / MulOp.w);

    if (DivOp.x > -1.0 && DivOp.x < 1.0 && DivOp.y > -1.0 && DivOp.y < 1.0 && DivOp.z > 0.0 && DivOp.z < 1.0) {
        float Val = 0.5;
        vec2 AddOp = ((Val * DivOp.xy) + Val);
        float SubOp = (DivOp.z - (ShadowMapBias / MulOp.w));
        float ShadowTotal = 0.0;
        for(int i=0; i<10; i+=1)
        {
            vec2 MulOp239 = (0.0009 * ShadowFilterTaps[i]);
            vec4 Sampler = SampleFromShadowMap(ActiveLightIndex, (AddOp + MulOp239));
            float IfElseOp193 = ((SubOp - Sampler.x) >= 0.0) ? (0.0) : (0.1);
            ShadowTotal += IfElseOp193;
        }
        ShadowTotal = mix(1.0, ShadowTotal, 1.0);  
        outValue = ShadowTotal;
    }
    else {
        outValue = 1.0;
    }

    return outValue;
}


vec3 LightContributionFunction(int ActiveLightIndex,
                               vec3 VertexWorldPosition,
                               vec3 LightVectorUN) {
    float _LightIntensity = 1.0;
    float _ShadowMapBias = 0.0;
    bool _LightShadowOn = true;
    int _LightType = 4;

    float decayMult = 1.0;
    float coneMult = 1.0;
    float shadowMult = 1.0;

    mat4 _LightViewPrj = Light0ViewPrj;
    float lightGain = ShadowMapFunction(
        ActiveLightIndex,
        _LightType,
        _LightViewPrj,
        _ShadowMapBias,
        VertexWorldPosition
    );

    vec3 _LightShadowColor = vec3(1, 1, 1);
    float ShadowColorMix = lightGain;
    shadowMult = ShadowColorMix;
    float DecayShadowConeMul = ((shadowMult * coneMult) * decayMult);
    vec3 _LightColor = vec3(1, 1, 1);
    vec3 MulItensity = ((_LightColor * DecayShadowConeMul) * _LightIntensity);
    return MulItensity;
}


void main()
{
    vec4 totalLight = Diffuse;
    totalLight.rgb *= vec3(0.5, 0.5, 0.5);
    for (int idx = 0; idx < 1; ++idx) {
        int  _LightType = 4;  // Directional
        vec3 _LightPos = GetLightPos(idx);
        vec3 _LightDir = GetLightDir(idx);

        vec3 lightVector = GetLightVectorFunction(
            idx, _LightPos, WorldPosition.xyz, _LightType, _LightDir
        );

        vec3 lightNormal = normalize(lightVector);
        vec3 normaled = normalize(Normal.xyz);
        vec3 flippedNormal = mix(-normaled, normaled, float(gl_FrontFacing));

        vec3 diffuse = LambertDiffuseFunction(
            idx, Diffuse.rgb, flippedNormal, lightNormal
        );

        // TODO: Shadows
        // vec3 contrib = LightContributionFunction(
        //     idx, WorldPosition.xyz, lightVector
        // );

        vec3 contrib = vec3(0.5, 0.5, 0.5);

        totalLight.rgb += diffuse * contrib;
    }
    colorOut = vec4(totalLight.rgb, 1.0);
}

#endif // HIDE_OGSFX_CODE
