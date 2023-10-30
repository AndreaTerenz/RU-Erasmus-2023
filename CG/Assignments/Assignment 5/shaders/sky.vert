attribute vec3 a_position;

uniform mat4 u_projection;
uniform mat4 u_view;

varying vec3 TexCoords;

void main()
{
    TexCoords = a_position;
    gl_Position = u_projection * u_view * vec4(a_position, 1.0);
} 