vec4 get_base_diffuse()
{
	float fac = sin(u_time * .2);
	fac = (fac + 1.)/2.;

	vec2 uv = v_uv * vec2(fac); // + vec2(u_uv_scale) * .5;

	vec4 tex_color = (u_material.use_diff_texture) ? texture(u_material.diffuse_tex, uv) : WHITE;
	vec4 col = u_material.diffuse_color * tex_color;

	return col;
}