#version 330

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

uniform vec2  viewportSize;
uniform float lineThickness;

in vec3[2] Color;
out vec3 ColorGSOut;

void main()
{
    ColorGSOut = Color[0];
    vec4 p1 = gl_in[0].gl_Position;
    vec4 p2 = gl_in[1].gl_Position;

    vec2 dir    = normalize((p2.xy/p2.w - p1.xy/p1.w) * viewportSize);
    vec2 offset = vec2(-dir.y, dir.x) * lineThickness / viewportSize;
  
    gl_Position = p1 + vec4(offset.xy * p1.w, 0.0, 0.0);
    EmitVertex();
    gl_Position = p1 - vec4(offset.xy * p1.w, 0.0, 0.0);
    EmitVertex();
    gl_Position = p2 + vec4(offset.xy * p2.w, 0.0, 0.0);
    EmitVertex();
    gl_Position = p2 - vec4(offset.xy * p2.w, 0.0, 0.0);
    EmitVertex();

    EndPrimitive();
}