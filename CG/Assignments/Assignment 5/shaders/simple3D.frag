struct Light
{
	vec4 diffuse,
		 specular,
		 ambient;
	vec4 position;
	float radius;
};
uniform Light u_lights[4];

struct Material
{
	vec4 diffuse_color,
		 specular_color,
		 ambient_color;
	sampler2D diffuse_tex;
	float shininess;
	bool receive_ambient,
		 unshaded,
		 has_texture;
};
uniform Material u_material;

uniform vec4 u_camera_position;
uniform int u_light_count;

uniform float u_time;

varying vec4 v_pos;
varying vec4 v_norm;
varying vec2 v_uv;

vec4 get_base_diffuse()
{
	vec4 tex_color = (u_material.has_texture) ? texture(u_material.diffuse_tex, v_uv) : vec4(1.);
	return u_material.diffuse_color * tex_color;
}

vec4 compute_shaded_color(vec4 s_vec, vec4 v_vec, float d, Light light, vec4 base_diffuse)
{
	if (light.radius > 0. && d > light.radius)
		return vec4(0., 0., 0., 1.);

	vec4 ambient = u_material.receive_ambient ? (light.ambient * u_material.ambient_color) : vec4(0., 0., 0., 1.);

	float lambert = max(0.0, dot(s_vec, v_norm) / (length(s_vec) * length(v_norm)));
	vec4 diffuse = light.diffuse * base_diffuse * lambert;

	vec4 h = (v_vec + s_vec) * .5;
	float phong = max(0.0, dot(h, v_norm) / (length(h) * length(v_norm)));
	vec4 specular = light.specular * u_material.specular_color * pow(phong, u_material.shininess);

	float dist_factor = light.radius <= 0. ? 1. : 1. - d / light.radius;

	return (ambient + diffuse + specular) * dist_factor;
}

void main(void)
{
	vec4 base_diff = get_base_diffuse();

	if (u_material.unshaded)
	{
		gl_FragColor = base_diff;
		return;
	}

	int c = (u_light_count < 4) ? u_light_count : 4;

	vec4 _v = u_camera_position - v_pos;

	for (int i = 0; i < c; i++)
	{
		vec4 _s = u_lights[i].position - v_pos;
		float _d = distance(u_lights[i].position, v_pos);
		gl_FragColor += compute_shaded_color(_s, _v, _d, u_lights[i], base_diff);
	}
}