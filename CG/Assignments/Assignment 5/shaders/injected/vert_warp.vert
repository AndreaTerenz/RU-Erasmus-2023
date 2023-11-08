vec4 get_position(vec4 pos)
{
	float dir = (pos.y > 0.) ? 1. : -1;
	float fac = 2. * sin(u_time * 15.) * dir;

	return pos + vec4(fac, 0., 0., 0.);
}
vec3 get_normal(vec3 nor)
{
	return nor;
}
vec2 get_uv(vec2 uv)
{
	return uv;
}