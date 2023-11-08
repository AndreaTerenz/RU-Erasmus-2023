vec3 rgb2hsv(vec3 col)
{
	vec4 K = vec4(0., -1. / 3., 2. / 3., -1.);
	vec4 p = mix(vec4(col.bg, K.wz), vec4(col.gb, K.xy), step(col.b, col.g));
	vec4 q = mix(vec4(p.xyw, col.r), vec4(col.r, p.yzx), step(p.x, col.r));

	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6. * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c)
{
	vec4 K = vec4(1., 2. / 3., 1. / 3., 3.);
	vec3 p = abs(fract(c.xxx + K.xyz) * 6. - K.www);
	return c.z * mix(K.xxx, clamp(p - K.xxx, 0., 1.), c.y);
}

vec4 get_base_diffuse()
{
	vec4 tex_color = (u_material.use_diff_texture) ? texture(u_material.diffuse_tex, v_uv) : WHITE;
	vec3 col = (u_material.diffuse_color * tex_color).rgb;
	float alpha = (u_material.diffuse_color * tex_color).a;

	vec3 tmp = rgb2hsv(col);

	tmp.x += u_time * 2.;

	col = hsv2rgb(tmp);

	return vec4(hsv2rgb(tmp), alpha);
}