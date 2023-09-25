attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_projection_view_matrix;
uniform vec4 u_color;

varying vec4 v_color;  //Leave the varying variables alone to begin with

void main(void)
{
	vec4 position = vec4(a_position, 1.0);
	vec4 normal = vec4(a_normal, 1.0);

	position = u_model_matrix * position;
	normal = u_model_matrix * normal;

	float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	v_color = (light_factor_1 + light_factor_2) * u_color;

	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
	position = u_projection_view_matrix * position;


	gl_Position = position;
}