import math
import os.path
from abc import ABC
from enum import Enum
from itertools import chain

import numpy as np
import pywavefront as pwf
from OpenGL.GL import *

from oven_engine_3D.shaders import BaseShader
from oven_engine_3D.utils.geometry import Vector3D


class Mesh(ABC):
    def __init__(self, positions, normals, uvs, verts_per_face, face_count, attrib_order = None):
        self.__vbo = Mesh.vbo_from_data(positions, normals, uvs)

        self.vertex_positions = positions
        self.vertex_normals = normals
        self.vertex_uvs = uvs
        self.verts_per_face = verts_per_face
        self.face_count = face_count

        self.attrib_order = attrib_order if attrib_order is not None else \
            [BaseShader.POS_ATTRIB_ID, BaseShader.NORM_ATTRIB_ID, BaseShader.UV_ATTRIB_ID]

    @staticmethod
    def vbo_from_data(pos, nor, uv):
        if not(nor is None and uv is None):
            tmp = [(*p, *n, *u) for p, n, u in zip(pos, nor, uv)]
            tmp = list(chain.from_iterable(tmp))
        else:
            tmp = pos

        vbo_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_id)
        glBufferData(GL_ARRAY_BUFFER, np.array(tmp, dtype="float32"), GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        return vbo_id

    def draw(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        for k in range(self.face_count):
            mode = GL_TRIANGLES if self.verts_per_face == 3 else GL_TRIANGLE_FAN
            glDrawArrays(mode, k * self.verts_per_face, self.verts_per_face)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    @property
    def vbo(self):
        return self.__vbo

class CubeMesh(Mesh):
    CUBE_POSITION_ARRAY = np.array(
        # back
        [[1, -1, -1],
         [1, 1, -1],
         [-1, 1, -1],
         [-1, -1, -1],
         # front
         [-1, -1, 1],
         [-1, 1, 1],
         [1, 1, 1],
         [1, -1, 1],
         # bottom
         [-1, -1, -1],
         [-1, -1, 1],
         [1, -1, 1],
         [1, -1, -1],
         # top
         [-1, 1, 1],
         [-1, 1, -1],
         [1, 1, -1],
         [1, 1, 1],
         # left
         [-1, -1, -1],
         [-1, 1, -1],
         [-1, 1, 1],
         [-1, -1, 1],
         # right
         [1, -1, 1],
         [1, 1, 1],
         [1, 1, -1],
         [1, -1, -1], ])

    CUBE_NORMAL_ARRAY = np.array([list(Vector3D.BACKWARD)] * 4 +
                                 [list(Vector3D.FORWARD)] * 4 +
                                 [list(Vector3D.DOWN)] * 4 +
                                 [list(Vector3D.UP)] * 4 +
                                 [list(Vector3D.LEFT)] * 4 +
                                 [list(Vector3D.RIGHT)] * 4)

    CUBE_UV_ARRAY = np.array([[0., 0.],
                              [0., 1.],
                              [1., 1.],
                              [1., 0.], ] * 6)

    # Coordinates for a cross-shaped UV map
    CUBE_UV_ARRAY2 = np.array([[3./4., 1./3.],
                                 [3./4., 2./3.],
                                 [1., 2./3.],
                                 [1., 1/3.],

                                 [1./4., 1./3.],
                                 [1./4., 2./3.],
                                 [1./2., 2./3.],
                                 [1./2., 1./3.],

                                 [1./4., 0],
                                 [1./4., 1./3.],
                                 [1./2., 1./3.],
                                 [1./2., 0.],

                                 [1./4., 2./3.],
                                 [1./4., 1],
                                 [1./2., 1],
                                 [1./2., 2./3.],

                                 [0., 1./3.],
                                 [0., 2./3.],
                                 [1./4., 2./3.],
                                 [1./4., 1./3.],

                                 [1./2., 1./3.],
                                 [1./2., 2./3.],
                                 [3./4., 2./3.],
                                 [3./4., 1./3.],])

    class UVMode(Enum):
        SAME = 0
        CROSS = 1

    def __init__(self, uv_mode = UVMode.SAME):
        uvs = (CubeMesh.CUBE_UV_ARRAY if uv_mode == CubeMesh.UVMode.SAME else CubeMesh.CUBE_UV_ARRAY2)

        pos = CubeMesh.CUBE_POSITION_ARRAY
        nor = CubeMesh.CUBE_NORMAL_ARRAY

        super().__init__(pos, nor, uvs,
                         4, 6)


class PlaneMesh(Mesh):
    PLANE_POSITION_ARRAY = np.array([[-1, 0, -1],
                                     [1, 0, -1],
                                     [1, 0, 1],
                                     [-1, 0, 1],])
    PLANE_NORMAL_ARRAY = np.array([list(Vector3D.UP)] * 4)
    PLANE_UV_ARRAY = np.array([[0., 0.],
                               [0., 1.],
                               [1., 1.],
                               [1., 0.]])

    def __init__(self):
        super().__init__(PlaneMesh.PLANE_POSITION_ARRAY, PlaneMesh.PLANE_NORMAL_ARRAY, PlaneMesh.PLANE_UV_ARRAY, 4, 1)

class SphereMesh(Mesh):
    def __init__(self, n_slices, n_stacks = 0):
        pos_tmp = []
        nor_tmp = []
        uv_tmp = []

        if n_stacks == 0:
            n_stacks = n_slices
        else:
            n_stacks *= 2

        slice_step = math.tau / n_slices
        stack_step = math.tau / n_stacks

        for i in range(n_stacks+1):
            stack_angle = (math.tau / 4.) - i * stack_step
            xy = math.cos(stack_angle)
            z = math.sin(stack_angle)

            for j in range(n_slices + 1):
                slice_angle = j * slice_step

                x = xy * math.cos(slice_angle)
                y = xy * math.sin(slice_angle)

                pos_tmp.append([x, z, y])
                nor_tmp.append([x, z, y])

                # LMAO THIS WORKS FOR REAL????? LOOOOOOOL
                s = - float(j) / n_slices
                t = 2. * float(i) / n_stacks

                uv_tmp.append([s, t])

        indices = []
        for i in range(n_stacks):
            k1 = i * (n_slices + 1)
            k2 = k1 + n_slices + 1

            for j in range(n_slices):
                if i != 0:
                    indices += [k1+1, k2, k1]

                if i != (n_slices - 1):
                    indices += [k2+1, k2, k1+1]

                k1 += 1
                k2 += 1

        positions = [pos_tmp[i] for i in indices]
        normals = [nor_tmp[i] for i in indices]
        uvs = [uv_tmp[i] for i in indices]

        face_count = n_stacks * n_slices * 2

        super().__init__(positions, normals, uvs, 3, face_count)

class OBJMesh(Mesh):
    __create_key = object()

    loaded = {}

    def __init__(self, file_name, key):
        assert (key == OBJMesh.__create_key), "OBJMesh objects must be created using OBJMesh.load"

        scene = pwf.Wavefront(file_name, collect_faces=True)
        # ASSUME 1 MESH
        face_count = len(scene.mesh_list[0].faces)
        # ASSUME 1 MATERIAL
        material = scene.mesh_list[0].materials[0]
        # ASSUME T2F_N3F_V3F FORMAT
        verts = material.vertices
        verts = [verts[i:i + 8] for i in range(0, len(verts), 8)]
        verts = [[(v[0], v[1]), (v[4], v[3], v[2]), (v[7], v[6], v[5])] for v in verts]

        positions = np.array([v[2] for v in verts])
        normals = np.array([v[1] for v in verts])
        uvs = np.array([v[0] for v in verts])

        super().__init__(positions, normals, uvs, 3, face_count)

        print("done")

    @staticmethod
    def load(file_name):
        print(f"Loading mesh from {file_name}...", end="")

        file_name = os.path.abspath(file_name)

        if file_name in OBJMesh.loaded.keys():
            print("done (mesh already loaded)")
            return OBJMesh.loaded[file_name]

        mesh = OBJMesh(file_name, OBJMesh.__create_key)
        OBJMesh.loaded[file_name] = mesh

        return mesh

if __name__ == '__main__':
    scene = pwf.Wavefront('../res/models/cylinder.obj', collect_faces=True)

    print(*scene.mesh_list[0].__dict__.items(), sep="\n")
    print()
    print(*scene.mesh_list[0].materials[0].__dict__.items(), sep="\n")
    print(scene.mesh_list[0].materials[0].vertex_format)


    """# Iterate vertex data collected in each material
    for name, material in scene.materials.items():
        print(name)
        # Contains the vertex format (string) such as "T2F_N3F_V3F"
        # T2F, C3F, N3F and V3F may appear in this string
        print(material.vertex_format)
        verts = material.vertices
        verts = [verts[i:i + 8] for i in range(0, len(verts), 8)]
        verts = [[(v[0], v[1]), (v[2], v[3], v[4]), (v[5], v[6], v[7])] for v in verts]
        verts = [[v[2], v[1], v[0]] for v in verts]

        print(len(verts))
        print(*verts, sep="\n")"""


        # Contains the vertex list of floats in the format described above
        #print(material.vertices)
        # Material properties
        #material.diffuse
        #material.ambient
        #material.texture