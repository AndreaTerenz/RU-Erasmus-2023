attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform float u_time;

varying vec4 v_pos;
varying vec2 v_uv;

void main(void)
{
	v_uv = a_uv;

	vec3 gigio = a_normal; // Here only to avoid warning/error
	vec4 position = u_model_matrix * vec4(a_position, 1.0);

	v_pos = position;
	gl_Position = u_projection_matrix * (u_view_matrix * position);
}