## Assignment 5

Requires Python 3.11 or higher

### To Do

- [x] ~~ACES Tonemapping~~
  - [x] ~~select [multiple tonemapping operators](https://64.github.io/tonemapping)~~
- [x] ~~Fog~~
- [x] ~~[Skybox](https://learnopengl.com/Advanced-OpenGL/Cubemaps)~~
  - [x] ~~Split shader back into "BaseShader" and "MeshShader"~~ (to make the SkyShader a separate subclass)
  - [ ] Compute global ambient color from skybox
  - [ ] Skybox rotation
  - [ ] Add exposure parameter
- [ ] Use buffer indices instead of having to repeat vertex data for position, normal, uv, etc... 
- [ ] Code to generate additional meshes
  - [x] ~~Sphere~~
    - [ ] Icosphere
    - [ ] Cubesphere
  - [ ] Torus
  - [ ] Cylinder/Prysm (also counts for cone if you allow different radius for top & bottom)
  - [ ] Subdivided plane
- [ ] Light types
  - [ ] Directional
  - [ ] Spotlight (maybe...)
- [ ] More textures in shader
  - [x] ~~Specular map~~
  - [ ] Normal map
- [ ] Mesh Loading
  - [x] ~~Mesh are loaded~~
  - [ ] Parse vertex format and act accordingly
  - [ ] Parse material
  - [ ] There's some rotation mismatch....
- [x] ~~UV coordinates in vbo~~
- [x] ~~Find out why face culling is broken~~
- [x] ~~TEXTURES!!!!~~

### To do in theory but would probably take too long

- [ ] Shadows?
  - [ ] hard shadows from a single directional light
  - [ ] self shadowing in objects