attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec4 u_camera_position;
uniform vec4 u_light_position;
uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_specular;
uniform vec4 u_ambient;

uniform bool receive_ambient;
uniform bool unshaded;

varying vec4 v_color;  //Leave the varying variables alone to begin with

vec4 compute_shaded_color(vec4 position, vec4 normal)
{
	vec4 s = u_light_position - position;
	float lambert = max(0.0, dot(s, normal) / (length(s) * length(normal)));
	vec4 diffuse = u_light_diffuse * u_material_diffuse * lambert;

	vec4 v = u_camera_position - position;
	vec4 h = (v + s) * .5;
	float phong = max(0.0, dot(h, normal) / (length(h) * length(normal)));
	float shininess = 10.;
	vec4 specular = u_light_specular * u_material_specular * pow(phong, shininess);

	return (u_ambient * float(receive_ambient) * .005) + diffuse; //+ specular;
}

void main(void)
{
	vec4 position = vec4(a_position, 1.0);
	vec4 normal = vec4(a_normal, 1.0);

	position = u_model_matrix * position;
	normal = u_model_matrix * normal;

	v_color = unshaded ? u_material_diffuse : compute_shaded_color(position, normal);

	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}