from pygame.locals import *

from oven_engine_3D.shaders import *
from oven_engine_3D.camera import *
from oven_engine_3D.utils.geometry import Vector3D, Vector2D


from OpenGL.GL import *

class BaseApp3D(ABC):
    def __init__(self,
                 win_title   = "BaseApp",
                 win_size    = Vector2D(800,600),
                 clear_color = Color("black"),
                 fullscreen  = True,
                 ambient_color = None,
                 ):

        pg.init()

        if fullscreen or win_size == Vector2D.ZERO:
            screen = pg.display.set_mode((0,0), pg.OPENGL|pg.DOUBLEBUF|pg.FULLSCREEN)
            self.win_size = Vector2D(screen.get_size())
        else:
            pg.display.set_mode(tuple(win_size), pg.OPENGL|pg.DOUBLEBUF)
            self.win_size = win_size
            pg.display.set_caption(win_title)

        glViewport(0, 0, *self.win_size)

        self.ambient_color = ambient_color if ambient_color is not None else clear_color

        self.clear_color = clear_color
        glClearColor(*clear_color.normalize())

        self.camera = None
        self.light = None

        self.clock = pg.time.Clock()
        self.ticks = 0

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

        self.objects = []

    def _update(self):
        delta = self.clock.tick(60.) / 1000.0
        self.ticks += 1

        self.update(delta)

        if self.light:
            self.light.update(delta)

        if self.camera:
            self.camera.update(delta)

        for obj in self.objects:
            obj.update(delta)

    @abstractmethod
    def update(self, delta):
        pass

    def _display(self):
        glEnable(GL_DEPTH_TEST)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.display()

        for obj in self.objects:
            obj.draw()

        pg.display.flip()

    @abstractmethod
    def display(self):
        pass

    def run(self):
        exiting = False
        while not exiting:
            exiting = self._handle_events()

            if not exiting:
                self._update()
                self._display()

        pg.quit()

    def _handle_events(self):
        for event in pg.event.get():

            self.mouse_delta *= 0.
            if event.type == pg.QUIT:
                print("Quitting")
                return True
            elif event.type == pg.KEYDOWN:
                if event.key == K_ESCAPE:
                    print("Quitting")
                    return True

            if event.type in [pg.KEYDOWN, pg.KEYUP] and event.key in self.keys_states.keys():
                self.keys_states[event.key] = (event.type == pg.KEYDOWN)

            if self.handle_event(event):
                return True

        return False

    @abstractmethod
    def handle_event(self, event):
        return False

    def get_mouse_pos(self):
        return Vector2D(pg.mouse.get_pos()) / self.win_size - Vector2D(0.5, 0.5)
