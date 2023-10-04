attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec4 u_camera_position;
uniform vec4 u_light_position;
/*
uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_specular;
uniform vec4 u_ambient;

uniform bool receive_ambient;
uniform bool unshaded;
*/
varying vec4 v_color;
varying vec4 s, v, h;
varying vec4 norm;
/*
vec4 compute_shaded_color()
{
	float lambert = max(0.0, dot(s, norm) / (length(s) * length(norm)));
	vec4 diffuse = u_light_diffuse * u_material_diffuse * lambert;

	vec4 h = (v + s) * .5;
	float phong = max(0.0, dot(h, norm) / (length(h) * length(norm)));
	float shininess = 15.;
	vec4 specular = u_light_specular * u_material_specular * pow(phong, shininess);

	vec4 ambient = (u_ambient * float(receive_ambient) * .05);

	return ambient + diffuse + specular;
}*/

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