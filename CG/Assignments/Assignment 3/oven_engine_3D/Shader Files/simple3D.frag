uniform vec4 u_light_diffuse[4];
uniform vec4 u_light_specular[4];
uniform float u_light_radius[4];
uniform vec4 u_material_diffuse;
uniform vec4 u_material_specular;
uniform vec4 u_ambient;
uniform float u_shininess;
uniform int u_light_count;

uniform bool receive_ambient;
uniform bool unshaded;

//varying vec4 v_pos;
varying vec4 v_color;
varying vec4 s[4];
varying float dist[4];
varying vec4 v, h;
varying vec4 norm;

vec4 snapvec4(vec4 v, float s)
{
	return vec4(floor(v.x / s) * s, floor(v.y / s) * s, floor(v.z / s) * s, floor(v.w / s) * s);
}

vec4 compute_shaded_color(vec4 s_vec, float d, float radius, vec4 light_diffuse, vec4 light_specular)
{
	if (radius > 0. && d > radius)
		return vec4(0., 0., 0., 1.);

	vec4 ambient = (u_ambient * float(receive_ambient) * .1);

	float lambert = max(0.0, dot(s_vec, norm) / (length(s_vec) * length(norm)));
	vec4 diffuse = light_diffuse * u_material_diffuse * lambert;

	vec4 h = (v + s_vec) * .5;
	float phong = max(0.0, dot(h, norm) / (length(h) * length(norm)));
	float shininess = u_shininess;
	vec4 specular = light_specular * u_material_specular * pow(phong, shininess);

	float dist_factor = radius <= 0. ? 1. : max(0., 1.0 - min(d / radius, 1.0));

	return (ambient + diffuse + specular) * dist_factor;
}

void main(void)
{
	if (unshaded)
	{
		gl_FragColor = u_material_diffuse;
		return;
	}

	int c = (u_light_count < 4) ? u_light_count : 4;

	for (int i = 0; i < c; i++)
	{
		gl_FragColor += compute_shaded_color(s[i], dist[i], u_light_radius[i], u_light_diffuse[i], u_light_specular[i]);
	}
}