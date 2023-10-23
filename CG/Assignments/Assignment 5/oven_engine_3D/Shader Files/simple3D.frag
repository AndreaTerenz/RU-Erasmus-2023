struct Light
{
	vec4 diffuse,
		 specular,
		 ambient;
	vec4 position;
	float radius;
};
uniform Light u_lights[4];

uniform sampler2D u_tex;
uniform bool u_sample_texture;

uniform vec4 u_camera_position;
uniform vec4 u_material_diffuse;
uniform vec4 u_material_specular;
uniform vec4 u_material_ambient;
uniform float u_shininess;
uniform int u_light_count;

uniform bool receive_ambient;
uniform bool unshaded;

varying vec4 v_pos;
varying vec4 v_norm;
varying vec2 v_uv;

vec4 compute_shaded_color(vec4 s_vec, vec4 v_vec, float d, Light light)
{
	if (light.radius > 0. && d > light.radius)
		return vec4(0., 0., 0., 1.);

	vec4 diff = u_material_diffuse;

	if (u_sample_texture)
	{
		diff *= texture(u_tex, v_uv);
	}

	vec4 ambient = receive_ambient ? (light.ambient * u_material_ambient) : vec4(0., 0., 0., 1.);

	float lambert = max(0.0, dot(s_vec, v_norm) / (length(s_vec) * length(v_norm)));
	vec4 diffuse = light.diffuse * diff * lambert;

	vec4 h = (v_vec + s_vec) * .5;
	float phong = max(0.0, dot(h, v_norm) / (length(h) * length(v_norm)));
	float shininess = u_shininess;
	vec4 specular = light.specular * u_material_specular * pow(phong, shininess);

	float dist_factor = light.radius <= 0. ? 1. : 1. - d / light.radius;

	return (ambient + diffuse + specular) * dist_factor;
}

void main(void)
{
	vec2 x = v_uv;

	if (unshaded)
	{
		gl_FragColor = u_material_diffuse;
		return;
	}

	int c = (u_light_count < 4) ? u_light_count : 4;

	vec4 _v = u_camera_position - v_pos;

	for (int i = 0; i < c; i++)
	{
		vec4 _s = u_lights[i].position - v_pos;
		float _d = distance(u_lights[i].position, v_pos);
		gl_FragColor += compute_shaded_color(_s, _v, _d, u_lights[i]);
	}
}