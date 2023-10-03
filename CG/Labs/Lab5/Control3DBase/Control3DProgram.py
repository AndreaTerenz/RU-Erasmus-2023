from pygame.locals import *

from Control3DBase.Base3DObjects import Cube1, Cube2, Cube3
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import *
from Control3DBase.camera import *
from Control3DBase.utils.geometry import Vector3D, Vector2D
from Control3DBase.utils.gl3d import draw_plane, PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY


# from OpenGL.GL import *
# from OpenGL.GLU import *


class GraphicsProgram3D:
    def __init__(self,
                 win_title   = "BaseApp",
                 win_size    = Vector2D(720,720),
                 clear_color = Color("black"),
                 fov         = math.tau/8.,
                 fullscreen = True):

        pg.init()

        if fullscreen:
            screen = pg.display.set_mode((0,0), pg.OPENGL|pg.DOUBLEBUF|pg.FULLSCREEN)
            self.win_size = Vector2D(screen.get_size())
        else:
            pg.display.set_mode(tuple(win_size), pg.OPENGL|pg.DOUBLEBUF)
            self.win_size = win_size
        pg.display.set_caption(win_title)

        ratio = self.win_size.aspect_ratio

        self.ground_shader = MeshShader(color=(0.5, 0.5, 0.5))
        self.camera = FPCamera(self, eye=Vector3D(-2., 1., 2.) * 5., look_at=Vector3D.ZERO, ratio=ratio, fov=fov, near=.5, far=100)

        self.cubes = [
            Cube1(self, size=0.4),
            Cube2(self, origin=Vector3D(-3., 0., 0.), size=0.4),
            Cube3(self, origin=Vector3D(0., 2., 0.), size=0.4),
        ]

        self.clock = pg.time.Clock()

        self.clear_color = clear_color
        self.white_background = False
        self.ticks = 0

        self.mouse_delta = Vector2D.ZERO

    def update(self):
        delta_time = self.clock.tick(60.) / 1000.0
        self.ticks += 1

        self.camera.update(delta_time)

        for cube in self.cubes:
            cube.update(delta_time)

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.win_size.x, self.win_size.y)

        draw_plane(self.camera, shader=self.ground_shader, offset=Vector3D.DOWN * 4., color=(0.5, 0.5, 0.5), scale=Vector3D(10, 0, 10))

        for cube in self.cubes:
            cube.shader.get_projview(self.camera)
            cube.draw()

        pg.display.flip()

    def program_loop(self):
        exiting = False
        while not exiting:
            exiting = self.handle_events()

            if not exiting:
                self.update()
                self.display()

        #OUT OF GAME LOOP
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            self.mouse_delta *= 0.
            if event.type == pg.QUIT:
                print("Quitting!")
                return True
            elif event.type == pg.KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Escaping!")
                    return True
            elif event.type == pg.MOUSEMOTION:
                self.mouse_delta = Vector2D(event.rel) / self.win_size
                self.mouse_delta = self.mouse_delta.snap(.005)

            self.camera.handle_event(event)

        return False
    
    def start(self):
        self.program_loop()

    def get_mouse_pos(self):
        return Vector2D(pg.mouse.get_pos()) / self.win_size - Vector2D(0.5, 0.5)

if __name__ == "__main__":
    GraphicsProgram3D().start()