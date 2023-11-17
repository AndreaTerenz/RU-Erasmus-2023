#version 330

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;
layout(location = 2) in vec2 a_uv;

uniform mat4 u_model_matrix;
uniform mat4 u_view_matrix;
uniform mat4 u_projection_matrix;
uniform vec2 u_uv_offset;
uniform vec2 u_uv_scale;

uniform float u_time;

out vec4 v_pos;
out vec4 v_norm;
out vec2 v_uv;

//--INJECTION-BEGIN
vec4 get_position(vec4 pos)
{
	return pos;
}
vec3 get_normal(vec3 nor)
{
	return nor;
}
vec2 get_uv(vec2 uv)
{
	return uv;
}
//--INJECTION-END

void main(void)
{
	v_uv = get_uv(a_uv) * u_uv_scale + u_uv_offset;
	v_norm = normalize(u_model_matrix * vec4(get_normal(a_normal), 0.0));
	v_pos = get_position(u_model_matrix * vec4((a_position), 1.0));

	gl_Position = u_projection_matrix * (u_view_matrix * v_pos);
}