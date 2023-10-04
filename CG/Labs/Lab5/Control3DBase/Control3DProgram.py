from pygame.locals import *

from Control3DBase.Base3DObjects import Cube
from Control3DBase.Matrices import ModelMatrix
from Control3DBase.Shaders import *
from Control3DBase.camera import *
from Control3DBase.light import Light
from Control3DBase.utils.geometry import Vector3D, Vector2D
from Control3DBase.utils.gl3d import draw_plane, PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY


# from OpenGL.GL import *
# from OpenGL.GLU import *


class GraphicsProgram3D:
    def __init__(self,
                 win_title   = "BaseApp",
                 win_size    = Vector2D(800,600),
                 clear_color = Color("black"),
                 fov         = math.tau/8.,
                 fullscreen  = True,
                 ambient_color = Color("white")):

        pg.init()

        if fullscreen or win_size == Vector2D.ZERO:
            screen = pg.display.set_mode((0,0), pg.OPENGL|pg.DOUBLEBUF|pg.FULLSCREEN)
            self.win_size = Vector2D(screen.get_size())
        else:
            pg.display.set_mode(tuple(win_size), pg.OPENGL|pg.DOUBLEBUF)
            self.win_size = win_size
        pg.display.set_caption(win_title)

        ratio = self.win_size.aspect_ratio

        self.ambient_color = (1., 1., 1.)#np.array(ambient_color[:3]) / 255.

        self.camera = FPCamera(self, eye=Vector3D(-2., 1., 2.) * 5., look_at=Vector3D.ZERO, ratio=ratio, fov=fov, near=.5, far=100)
        self.light = Light(Vector3D(0., 0., 0.), (1., 1., 1.))
        self.light_angle = 0.

        self.ground_shader = MeshShader(PLANE_POSITION_ARRAY, PLANE_NORMAL_ARRAY, diffuse_color=(.5, .5, .5))

        dist = 3.
        self.objects = [
            Cube(self, origin=Vector3D(0., 0., 1.) * dist, color=(1., 0., 0.)),
            Cube(self, origin=Vector3D(0., 0.,   -1.) * dist, color=(1., 0., 0.)),
            Cube(self, origin=Vector3D(1., 0., 0.) * dist, color=(1., 1., 0.)),
            Cube(self, origin=Vector3D(  -1., 0., 0.) * dist, color=(0., 1., 1.)),
            Cube(self, origin=Vector3D(0., 1., 0.) * dist, color=(0., 0., 1.)),
            Cube(self, origin=Vector3D(0.,   -1., 0.) * dist, color=(0., 0., 1.)),
            Cube(self, origin=Vector3D(0., 0., 0.)),
        ]

        self.objects[-1].scale_by(.1)
        self.objects[-1].shader.use()
        self.objects[-1].shader.set_unshaded(True)
        self.objects[-1].translate_to(self.light.position)

        self.clock = pg.time.Clock()

        self.clear_color = clear_color
        self.white_background = False
        self.ticks = 0

        self.mouse_delta = Vector2D.ZERO

        self.light_movement_keys = {
            pg.K_k: Vector3D.FORWARD,
            pg.K_i: Vector3D.BACKWARD,
            pg.K_j: Vector3D.LEFT,
            pg.K_l: Vector3D.RIGHT,
            pg.K_u: Vector3D.UP,
            pg.K_o: Vector3D.DOWN,
        }
        self.keys_states = {key: False for key in self.light_movement_keys.keys()}

    def update(self):
        delta_time = self.clock.tick(60.) / 1000.0
        self.ticks += 1

        self.camera.update(delta_time)

        # Update light position based on input
        light_dir = Vector3D.ZERO
        for key, _dir in self.light_movement_keys.items():
            state = self.keys_states[key]
            fact = 1. if state else 0.
            light_dir += _dir * fact

        if light_dir != Vector3D.ZERO:
            self.light.position += light_dir * delta_time * 4.
            self.objects[-1].translate_to(self.light.position)

        for obj in self.objects:
            obj.update(delta_time)

    def display(self):
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, self.win_size.x, self.win_size.y)

        for obj in self.objects:
            obj.draw()

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

            if event.type in [pg.KEYDOWN, pg.KEYUP] and event.key in self.keys_states.keys():
                self.keys_states[event.key] = (event.type == pg.KEYDOWN)

            self.camera.handle_event(event)

        return False
    
    def start(self):
        self.program_loop()

    def get_mouse_pos(self):
        return Vector2D(pg.mouse.get_pos()) / self.win_size - Vector2D(0.5, 0.5)

if __name__ == "__main__":
    GraphicsProgram3D().start()