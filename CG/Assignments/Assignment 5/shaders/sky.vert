attribute vec3 a_position;

uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform float u_time;

varying vec3 v_uv;

void main(void)
{
	v_uv = a_position;

	gl_Position = (u_projection_matrix * (u_view_matrix * vec4(a_position, 1.0))).xyww;
}