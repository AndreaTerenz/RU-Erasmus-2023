attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec4 u_camera_position;
uniform vec4 u_light_position;

varying vec4 v_color;
varying vec4 s, v, h;
varying vec4 norm;

void main(void)
{
	vec4 position = vec4(a_position, 1.0);
	vec4 normal = vec4(a_normal, 0.0);

	position = u_model_matrix * position;
	normal = u_model_matrix * normal;

	s = u_light_position - position;
	v = u_camera_position - position;
	norm = normalize(normal);

	//v_color = compute_shaded_color();
	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}