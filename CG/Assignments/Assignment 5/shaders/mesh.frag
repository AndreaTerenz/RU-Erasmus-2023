#version 330

#define BLACK vec4(vec3(0.), 1.)
#define CLEAR vec4(0.)
#define WHITE vec4(1.)
#define FOG_NONE -1
#define FOG_LINEAR 0
#define FOG_EXP 1
#define FOG_EXP2 2
#define TONEMAP_NONE -1
#define TONEMAP_ACES 0
#define TONEMAP_REINHARD 1
#define TONEMAP_UNCHARTED2 2
#define TRANSP_OPAQUE 0
#define TRANSP_CUTOFF 1
#define TRANSP_BLEND 2

struct Environment
{
	vec4 global_ambient;
	float ambient_strength;
	vec4 fog_color;
	float start_fog, end_fog; // Used only for linear fog
	float fog_density; // Used only for exp or exp2 fog
	int fog_mode; // -1 = none, 0 = linear, 1 = exp, 2 = exp2
	int tonemap_mode; // -1 = none, 0 = aces
};
uniform Environment u_env;
uniform samplerCube u_skybox;

struct Light
{
	vec4 diffuse,
		 specular,
		 ambient;
	bool is_sun;
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
	sampler2D diffuse_tex, specular_tex;
	float shininess;
	float alpha_cutoff;
	int transparency_mode; // 0 = opaque, 1 = discard, 2 = normal transparent
	bool receive_ambient,
		 unshaded,
		 use_diff_texture,
		 use_spec_texture;
	bool use_distance_fade;
	float distance_fade[2];
};
uniform Material u_material;

uniform vec4 u_camera_position;
uniform int u_light_count = 0;

uniform float u_time;
uniform vec2 u_uv_offset;
uniform vec2 u_uv_scale;

in vec4 v_pos;
in vec4 v_norm;
in vec2 v_uv;

float rand(vec2 co)
{
	return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

vec4 color_from_light(vec4 view_vec, Light light, vec4 base_diffuse, float spec_tex_value)
{
	float d = distance(light.position, v_pos);

	if (light.radius > 0. && d > light.radius)
		return BLACK;

	vec4 s_vec = light.is_sun ? normalize(light.position) : light.position - v_pos;

	vec4 ambient = u_material.receive_ambient ? (light.ambient * u_material.ambient_color) : BLACK;

	float lambert = max(0.0, dot(s_vec, v_norm) / (length(s_vec) * length(v_norm)));
	vec4 diffuse = light.diffuse * light.intensity * base_diffuse * lambert;

	vec4 h = (view_vec + s_vec) * .5;
	float phong = max(0.0, dot(h, v_norm) / (length(h) * length(v_norm)));
	vec4 specular = light.specular * light.intensity * u_material.specular_color * pow(phong, u_material.shininess) * spec_tex_value;

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
	if (u_env.fog_mode == FOG_NONE)
		return base_color;

	float fog_strength = 0.;

	if (u_env.fog_mode == FOG_EXP)
		fog_strength = exp_fog_factor(dist);
	else if (u_env.fog_mode == FOG_EXP2)
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
		case TONEMAP_ACES:
			return vec4(aces(col), color.a);
		case TONEMAP_REINHARD:
			return vec4(reinhard(col), color.a);
		case TONEMAP_UNCHARTED2:
			return vec4(uncharted2_filmic(col), color.a);
	}

	return clamp(color, 0., 1.);
}

vec4 apply_transparency(vec4 input_color, float alpha)
{
	if (u_material.transparency_mode != TRANSP_BLEND)
		alpha = 1.;

	input_color.a = alpha;

	return input_color;
}

float apply_distance_fade(float input_alpha, float dist)
{
	float min_dist = u_material.distance_fade[0];
	float max_dist = u_material.distance_fade[1];

	if (u_material.transparency_mode == TRANSP_BLEND)
	{
		float fact = (dist-min_dist)/(max_dist - min_dist);

		input_alpha *= min(1., max(0., 1.-fact));
	}
	else if (dist >= (min_dist+max_dist)/2.)
		input_alpha = 0.;

	return input_alpha;
}

//--INJECTION-BEGIN
vec4 get_base_diffuse()
{
	vec4 tex_color = (u_material.use_diff_texture) ? texture(u_material.diffuse_tex, v_uv) : WHITE;
	return u_material.diffuse_color * tex_color;
}
//--INJECTION-END

void main(void)
{
	// compute base diffuse color
	vec4 base_diff = get_base_diffuse();

	// distance fade
	vec4 view_vec = u_camera_position - v_pos;
	float camera_dist = length(view_vec);

	/*if (u_material.use_distance_fade)
		base_diff.a = apply_distance_fade(base_diff.a, camera_dist);*/

	if (u_material.transparency_mode == TRANSP_CUTOFF && base_diff.a < u_material.alpha_cutoff)
		discard;

	if (u_material.unshaded)
	{
		gl_FragColor = apply_transparency(base_diff, base_diff.a);
		return;
	}

	// compute shaded color
	float spec_tex_value = u_material.use_spec_texture ? texture(u_material.specular_tex, v_uv).r : 1.;

	vec4 shaded_color = u_env.global_ambient * base_diff * u_env.ambient_strength;

	for (int i = 0; i < min(u_light_count, 4); i++)
		shaded_color += color_from_light(view_vec, u_lights[i], base_diff, spec_tex_value);

	// apply fog
	vec4 fogged_color = apply_fog(shaded_color, camera_dist);

	// tonemap
	gl_FragColor = apply_transparency(tonemap(fogged_color), base_diff.a);
}