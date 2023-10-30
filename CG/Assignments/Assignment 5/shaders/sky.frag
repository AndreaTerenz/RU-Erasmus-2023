uniform samplerCube cubemap; // cubemap texture sampler

varying vec3 textureDir; // direction vector representing a 3D texture coordinate
varying vec3 texCoords;

void main() {
    gl_FragColor = texture(cubemap, texCoords);
}
