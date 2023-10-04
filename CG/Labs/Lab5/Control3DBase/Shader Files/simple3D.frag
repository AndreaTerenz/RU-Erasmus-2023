varying vec4 v_color;
varying vec4 s, v, h;
varying vec4 norm;
varying vec4 diff_mult, spec_mult, ambient_mult;

vec4 compute_shaded_color()
{
	float lambert = max(0.0, dot(s, norm) / (length(s) * length(norm)));
	vec4 diffuse = diff_mult * lambert;

	vec4 h = (v + s) * .5;
	float phong = max(0.0, dot(h, norm) / (length(h) * length(norm)));
	float shininess = 15.;
	vec4 specular = spec_mult * pow(phong, shininess);

	return ambient_mult + diffuse + specular;
}

void main(void)
{
    gl_FragColor = compute_shaded_color();
}