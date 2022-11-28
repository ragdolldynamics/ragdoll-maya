#version 330 core
layout (triangles) in;
layout (triangle_strip, max_vertices=48) out;

uniform vec2 u_viewportSize;
uniform float u_thickness;

void main()
{
    float pixelWidth = 2.0 / u_viewportSize.x;
    float pixelHeight = 2.0 / u_viewportSize.y;

    pixelWidth *= u_thickness;
    pixelHeight *= u_thickness;

   for (int i = 0; i < 3; ++i) {
      gl_Position = gl_in[i].gl_Position;
      gl_Position.x += pixelWidth * gl_Position.w;
      EmitVertex();
   }
   EndPrimitive();
      for (int i = 0; i < 3; ++i) {
      gl_Position = gl_in[i].gl_Position;
      gl_Position.x -= pixelWidth * gl_Position.w;
      EmitVertex();
   }
   EndPrimitive();
      for (int i = 0; i < 3; ++i) {
      gl_Position = gl_in[i].gl_Position;
      gl_Position.y -= pixelHeight * gl_Position.w;
      EmitVertex();
   }
   EndPrimitive();
      for (int i = 0; i < 3; ++i) {
      gl_Position = gl_in[i].gl_Position;
      gl_Position.y += pixelHeight * gl_Position.w;
      EmitVertex();
   }
   EndPrimitive();

    // Caps
    for (int i = 0; i < 3; ++i) {
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.x += pixelWidth * gl_Position.w;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.y -= pixelHeight * gl_Position.w;
        EmitVertex();
    }
    EndPrimitive();

    for (int i = 0; i < 3; ++i) {
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.x -= pixelWidth * gl_Position.w;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.y -= pixelHeight * gl_Position.w;
        EmitVertex();
    }
    EndPrimitive();
    
    for (int i = 0; i < 3; ++i) {
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.x += pixelWidth * gl_Position.w;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.y += pixelHeight * gl_Position.w;
        EmitVertex();
    }
    EndPrimitive();
    
    for (int i = 0; i < 3; ++i) {
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.x -= pixelWidth * gl_Position.w;
        EmitVertex();
        gl_Position = gl_in[i].gl_Position;
        gl_Position.y += pixelHeight * gl_Position.w;
        EmitVertex();
    }
    EndPrimitive();
} 