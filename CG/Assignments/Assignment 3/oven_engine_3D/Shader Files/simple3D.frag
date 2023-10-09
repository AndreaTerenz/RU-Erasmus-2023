uniform vec4 u_light_diffuse;
uniform vec4 u_light_specular;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_specular;
uniform vec4 u_ambient;
uniform float u_shininess;
uniform float u_time;

uniform bool receive_ambient;
uniform bool unshaded;

varying vec4 v_color;
varying vec4 s, v, h;
varying vec4 norm;

vec4 compute_shaded_color()
{
	vec4 ambient = (u_ambient * float(receive_ambient) * .05);

	float lambert = max(0.0, dot(s, norm) / (length(s) * length(norm)));
	vec4 diffuse = u_light_diffuse * u_material_diffuse * lambert;

	vec4 h = (v + s) * .5;
	float phong = max(0.0, dot(h, norm) / (length(h) * length(norm)));
	float shininess = u_shininess;
	vec4 specular = u_light_specular * u_material_specular * pow(phong, shininess);

	return ambient + diffuse; // + specular;
}

void main(void)
{
    gl_FragColor = unshaded ? u_material_diffuse : compute_shaded_color();
}