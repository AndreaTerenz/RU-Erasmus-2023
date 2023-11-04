struct Environment
{
	vec4 global_ambient;
	vec4 fog_color;
	float start_fog, end_fog; // Used only for linear fog
	float fog_density; // Used only for exp or exp2 fog
	int fog_mode; // -1 = none, 0 = linear, 1 = exp, 2 = exp2
	int tonemap_mode; // -1 = none, 0 = aces
};
uniform Environment u_env;

struct Light
{
	vec4 diffuse,
		 specular,
		 ambient;
	float attenuation[3];
	vec4 position;
	float intensity;
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
	vec4 diffuse = light.diffuse * light.intensity * base_diffuse * lambert;

	vec4 h = (view_vec + s_vec) * .5;
	float phong = max(0.0, dot(h, v_norm) / (length(h) * length(v_norm)));
	vec4 specular = light.specular * light.intensity * u_material.specular_color * pow(phong, u_material.shininess);

	float dist_factor = 1.;
	if (light.radius > 0.)
		dist_factor = clamp(1. - pow(d / light.radius, 2.), 0., 1.);

	return (ambient + diffuse + specular) * (dist_factor * dist_factor);
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
	if (u_env.fog_mode == -1)
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

vec3 aces(vec3 x) {
  const float a = 2.51;
  const float b = 0.03;
  const float c = 2.43;
  const float d = 0.59;
  const float e = 0.14;
  return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

vec3 reinhard(vec3 v)
{
    return v / (1.0f + v);
}

vec3 uncharted2_tonemap_partial(vec3 x)
{
    float A = 0.15f;
    float B = 0.50f;
    float C = 0.10f;
    float D = 0.20f;
    float E = 0.02f;
    float F = 0.30f;
    return ((x*(A*x+C*B)+D*E)/(x*(A*x+B)+D*F))-E/F;
}

vec3 uncharted2_filmic(vec3 v)
{
    float exposure_bias = 2.0f;
    vec3 curr = uncharted2_tonemap_partial(v * exposure_bias);

    vec3 W = vec3(11.2f);
    vec3 white_scale = vec3(1.0f) / uncharted2_tonemap_partial(W);
    return curr * white_scale;
}

vec4 tonemap(vec4 color)
{
	vec3 col = color.rgb;

	switch (u_env.tonemap_mode)
	{
		case 0:
			return vec4(aces(col), 1.);
		case 1:
			return vec4(reinhard(col), 1.);
		case 2:
			return vec4(uncharted2_filmic(col), 1.);
	}

	return clamp(color, 0., 1.);
}

void main(void)
{
	// compute base diffuse color
	vec4 base_diff = get_base_diffuse();

	if (u_material.unshaded)
	{
		gl_FragColor = base_diff;
		return;
	}

	// compute shaded color
	vec4 shaded_color = vec4(vec3(0.), 1.);
	vec4 view_vec = u_camera_position - v_pos;

	int c = (u_light_count < 4) ? u_light_count : 4;
	for (int i = 0; i < c; i++)
	{
		shaded_color += color_from_light(view_vec, u_lights[i], base_diff);
	}

	// Add global ambient color
	shaded_color += u_env.global_ambient * base_diff * .5;

	// apply fog
	float camera_dist = length(view_vec);
	vec4 fogged_color = apply_fog(shaded_color, camera_dist);

	// tonemap
	gl_FragColor = tonemap(fogged_color);
}