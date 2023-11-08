vec4 get_base_diffuse()
{
	vec2 uv = v_uv + vec2(u_time/5., 0.);

	vec4 tex_color = (u_material.use_diff_texture) ? texture(u_material.diffuse_tex, uv) : WHITE;
	vec4 col = u_material.diffuse_color * tex_color;

	return col;
}