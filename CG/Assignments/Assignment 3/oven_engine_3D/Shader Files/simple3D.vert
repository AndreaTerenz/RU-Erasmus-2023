attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec4 u_camera_position;
uniform vec4 u_light_position;

//varying vec4 v_pos;
varying vec4 v_color;
varying vec4 s, v, h;
varying vec4 norm;
varying float dist;

float remap(float v, float old_min, float old_max, float new_min, float new_max) {
	return (((v - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min;
}

void main(void)
{
	vec4 position = vec4(a_position, 1.0);
	vec4 normal = vec4(a_normal, 0.0);

	position = u_model_matrix * position;
	normal = u_model_matrix * normal;

	s = u_light_position - position;
	v = u_camera_position - position;
	dist = distance(u_light_position, position);
	norm = normalize(normal);

	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}