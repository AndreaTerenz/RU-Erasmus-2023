from pygame.locals import *

from oven_engine_3D.camera import *
from oven_engine_3D.entities import Skybox, DrawnEntity
from oven_engine_3D.shaders import *
from oven_engine_3D.utils.geometry import Vector2D


class BaseApp3D(ABC):
    def __init__(self,
                 win_title   = "BaseApp",
                 win_size    = Vector2D(800,600),
                 clear_color = "black",
                 fullscreen  = True,
                 ambient_color = None,
                 update_camera = True,
                 face_culling = True,
                 environment : Environment = None,
                 sky_textures = None,
                 ):

        pg.init()

        self.screen = None
        if fullscreen or win_size == Vector2D.ZERO:
            self.screen = pg.display.set_mode((0,0), pg.OPENGL|pg.DOUBLEBUF|pg.FULLSCREEN)
            self.win_size = Vector2D(self.screen.get_size())
        else:
            self.screen = pg.display.set_mode(tuple(win_size), pg.OPENGL|pg.DOUBLEBUF)
            self.win_size = win_size
            pg.display.set_caption(win_title)

        glViewport(0, 0, *self.win_size)

        self.ambient_color = ambient_color if ambient_color is not None else clear_color

        if type(clear_color) is str:
            clear_color = Color(clear_color)

        self.clear_color = clear_color
        glClearColor(*clear_color.normalize())

        self.camera = None
        self.update_camera = update_camera
        self.light = None
        self.lights = []
        self.face_culling = face_culling

        self.clock = pg.time.Clock()
        self.ticks = 0
        self.last_delta = 0.0

        self.mouse_delta = Vector2D.ZERO

        self.keys = [
            pg.K_k,
            pg.K_i,
            pg.K_j,
            pg.K_l,
            pg.K_u,
            pg.K_o,
        ]
        self.keys_states = {key: False for key in self.keys}

        self.avg_fps = 0.
        self.target_fps = 60.

        if environment is None:
            environment = Environment(clear_color)

        self.environment = environment

        self.skybox = None
        if sky_textures is not None and type(sky_textures) is dict:
            cm = TexturesManager.load_cubemap(**sky_textures)
            self.skybox = Skybox(parent_app=self, cubemap_text=cm)

        self.entities = []
        self.opaque = []
        self.transparent = []

    def add_entity(self, ent: Entity):
        self.entities.append(ent)

        if not isinstance(ent, DrawnEntity):
            return

        if ent.shader.transparent:
            self.transparent.append(ent)
        else:
            self.opaque.append(ent)

        return ent

    def _update(self):
        delta = self.clock.tick(self.target_fps) / 1000.0
        self.ticks += 1
        self.last_delta = delta

        self.update(delta)

        for ent in self.entities:
            ent.update(delta)

    @abstractmethod
    def update(self, delta):
        pass

    def _display(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if self.face_culling:
            glEnable(GL_CULL_FACE)
            glFrontFace(GL_CW)
            glCullFace(GL_BACK)
        else:
            glDisable(GL_CULL_FACE)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.display()

        for ent in self.opaque:
            ent.draw()

        if self.skybox is not None:
            self.skybox.draw()

        # Sort transparent entities by distance to camera
        self.transparent.sort(key=lambda e: (e.origin - self.camera.origin).length_sq, reverse=True)
        for ent in self.transparent:
            ent.draw()

        pg.display.flip()

    @abstractmethod
    def display(self):
        pass

    def run(self):

        print("######################### STARTING\n\n")

        exiting = False
        while not exiting:
            exiting = self._handle_events()

            if not exiting:
                self._update()
                self._display()

        pg.quit()

    def _handle_events(self):
        self.mouse_delta *= 0.
        
        for event in pg.event.get():
            if self.check_quit(event):
                return True

            if event.type in [pg.KEYDOWN, pg.KEYUP] and event.key in self.keys_states.keys():
                self.keys_states[event.key] = (event.type == pg.KEYDOWN)
            elif event.type == pg.MOUSEMOTION:
                self.mouse_delta = Vector2D(event.rel) / self.win_size
                self.mouse_delta = self.mouse_delta.snap(.005)

            if self.handle_event(event):
                return True

            for ent in self.entities:
                if ent.handle_event(event):
                    return True

        return False

    def check_quit(self, event):
        if event.type == pg.QUIT:
            print("Quitting")
            return True
        elif event.type == pg.KEYDOWN:
            if event.key == K_ESCAPE:
                print("Quitting")
                return True

        return False

    @abstractmethod
    def handle_event(self, event):
        return False

    def add_keys(self, keycodes):
        for keycode in keycodes:
            if not keycode in self.keys_states.keys():
                self.keys_states[keycode] = False

    def is_key_pressed(self, keycode):
        return self.keys_states.get(keycode, False)

    def get_mouse_pos(self):
        return Vector2D(pg.mouse.get_pos()) / self.win_size - Vector2D(0.5, 0.5)

    @property
    def light_count(self):
        return len(self.lights)
