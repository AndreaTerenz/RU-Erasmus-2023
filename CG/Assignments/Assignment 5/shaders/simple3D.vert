attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;

uniform float u_time;

varying vec4 v_pos;
varying vec4 v_norm;
varying vec2 v_uv;

void main(void)
{
	v_uv = a_uv;

	vec4 position = vec4(a_position, 1.0);
	v_norm = vec4(a_normal, 0.0);

	position = u_model_matrix * position;
	v_norm = normalize(u_model_matrix * v_norm);

	v_pos = position;

	position = u_projection_matrix * (u_view_matrix * position);
	gl_Position = position;
}