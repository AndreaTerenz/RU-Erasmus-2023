struct Environment
{
	vec4 global_ambient;
	vec4 fog_color;
	float start_fog, end_fog; // Used only for linear fog
	float fog_density; // Used only for exp or exp2 fog
	bool fog_enabled;
	int fog_mode; // 0 = linear, 1 = exp, 2 = exp2
};
uniform Environment u_env;

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

float rand(vec2 co)
{
	return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

vec4 color_from_light(vec4 view_vec, Light light, vec4 base_diffuse)
{
	float d = distance(light.position, v_pos);

	if (light.radius > 0. && d > light.radius)
		return vec4(0., 0., 0., 1.);

	vec4 s_vec = light.position - v_pos;

	vec4 ambient = u_material.receive_ambient ? (light.ambient * u_material.ambient_color) : vec4(0., 0., 0., 1.);

	float lambert = max(0.0, dot(s_vec, v_norm) / (length(s_vec) * length(v_norm)));
	vec4 diffuse = light.diffuse * base_diffuse * lambert;

	vec4 h = (view_vec + s_vec) * .5;
	float phong = max(0.0, dot(h, v_norm) / (length(h) * length(v_norm)));
	vec4 specular = light.specular * u_material.specular_color * pow(phong, u_material.shininess);

	float dist_factor = light.radius <= 0. ? 1. : 1. - d / light.radius;

	return (ambient + diffuse + specular) * dist_factor;
}

float linear_fog_factor(float dist)
{
	float fact = (u_env.end_fog - dist) / (u_env.end_fog - u_env.start_fog);
	return clamp(fact, 0., 1.);
}

float exp_fog_factor(float dist)
{
	float fact = exp(-u_env.fog_density * dist);
	return clamp(fact, 0., 1.);
}

float exp2_fog_factor(float dist)
{
	float fact = exp(-pow(u_env.fog_density * dist, 2.));
	return clamp(fact, 0., 1.);
}

vec4 apply_fog(vec4 base_color, float dist)
{
	if (!u_env.fog_enabled)
		return base_color;

	float fog_strength = 0.;

	if (u_env.fog_mode == 1)
		fog_strength = exp_fog_factor(dist);
	else if (u_env.fog_mode == 2)
		fog_strength = exp2_fog_factor(dist);
	else
		fog_strength = linear_fog_factor(dist);

	return fog_strength * base_color + (1. - fog_strength) * u_env.fog_color;
}

void main(void)
{
	vec4 base_diff = get_base_diffuse();

	if (u_material.unshaded)
	{
		gl_FragColor = base_diff;
		return;
	}

	vec4 shaded_color = vec4(0.);
	vec4 view_vec = u_camera_position - v_pos;

	int c = (u_light_count < 4) ? u_light_count : 4;
	for (int i = 0; i < c; i++)
	{
		shaded_color += color_from_light(view_vec, u_lights[i], base_diff);
	}

	float camera_dist = length(view_vec);
	gl_FragColor = apply_fog(shaded_color, camera_dist);
}