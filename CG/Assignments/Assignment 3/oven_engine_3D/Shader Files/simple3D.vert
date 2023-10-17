attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec4 u_camera_position;
uniform vec4 u_light_position[4];

uniform int u_light_count;

//varying vec4 v_pos;
varying vec4 v_color;
varying vec4 s[4];
varying float dist[4];
varying vec4 v, h;
varying vec4 norm;

float remap(float v, float old_min, float old_max, float new_min, float new_max) {
	return (((v - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min;
}

void main(void)
{
	vec4 position = vec4(a_position, 1.0);
	vec4 normal = vec4(a_normal, 0.0);

	position = u_model_matrix * position;
	normal = u_model_matrix * normal;

	int c = (u_light_count < 4) ? u_light_count : 4;

	for (int i = 0; i < c; i++) {
		s[i] = u_light_position[i] - position;
		dist[i] = distance(u_light_position[i], position);
	}

	v = u_camera_position - position;
	norm = normalize(normal);

	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}