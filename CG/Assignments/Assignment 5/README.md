## Assignment 5

Requires Python 3.11 or higher

### To Do

- [ ] ACES Tonemapping
  - [ ] select multiple tonemapping operators
- [ ] Fog
- [ ] Better light attenuation
  - [ ] use the actual 1/(1+a*d) formula
  - [ ] add attenuation parameter to Light class
- [ ] Use buffer indices instead of having to repeat vertex data for position, normal, uv, etc... 
- [ ] Code to generate additional meshes
  - [x] ~~Sphere~~
    - [ ] Icosphere
    - [ ] Cubesphere
  - [ ] Torus
  - [ ] Cylinder/Prysm
  - [ ] Cone
    - [ ] Truncated cone
  - [ ] Subdivided plane
- [ ] Light types (even just point vs directional)
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