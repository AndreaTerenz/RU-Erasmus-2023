struct Environment
{
	int tonemap_mode;
};
uniform Environment u_env;

struct Material
{
	vec4 diffuse_color;
	sampler2D diffuse_tex;
};
uniform Material u_material;

uniform float u_time;

varying vec4 v_pos;
varying vec2 v_uv;

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
    vec4 tex_color = texture(u_material.diffuse_tex, v_uv);
	vec4 base_diff = u_material.diffuse_color * tex_color;

	gl_FragColor = tonemap(base_diff);
}