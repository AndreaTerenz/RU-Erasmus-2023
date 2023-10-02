# Assignment 2
from bisect import insort

import OpenGL.GLU as glu
from pygame.locals import *

from .entities import Entity
from .resources import TexturesManager
from .utils.gl import *


class BaseApp(ABC):
    def __init__(self, 
                 win_title   = "BaseApp",
                 win_size    = Vector2D(800,600), 
                 clear_color = Color("black"),
                 scaling     = 1.,
                 target_fps  = 60.,
                 enable_fps_print = False,
                 camera_view_size : [float|Vector2D] = 8.) -> None:
        if target_fps <= 0.:
            target_fps = 60.

        if not type(win_size) is Vector2D:
            win_size = Vector2D(win_size, win_size)

        if not type(scaling) is Vector2D:
            scaling = Vector2D(scaling, scaling)

        self.win_size = win_size

        if type(camera_view_size) is float:
            camera_view_size = Vector2D(camera_view_size, camera_view_size / self.win_size.aspect_ratio)

        #self.camera = Camera(self, eye=Vector3D(-3., 3., 3.), look_at=Vector3D.ZERO, view_size=camera_view_size, near=.5, far=100, ortho=False)

        self.scaling = scaling
        self.ortho_size = win_size * (scaling ** -1)
        self.clear_color = clear_color
        self.win_title = win_title
        self.target_fps = target_fps
        self.enable_fps_print = enable_fps_print
        self.avg_fps = 0.
        self.ticks = 0
        self.exit_code = 0
        self.running = True
        self.clock = pg.time.Clock()
        self.clear_on_draw = True
        self.update_entities = True
        self.draw_entities = True
        self.entities = []
        self.draw_order = []
        self.update_order = []
        self.events_order = []
        #self.cm = CollisionManager(world_bounds=self.aabb)
        self.tm = TexturesManager()
        self.last_delta = 0.

        pg.display.init()
        pg.font.init()
        pg.display.set_mode((self.win_size.x, self.win_size.y), DOUBLEBUF|OPENGL)
        pg.display.set_caption(win_title)

        set_clear_color(self.clear_color)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glu.gluOrtho2D(0, self.ortho_size.x, 0, self.ortho_size.y)
        glViewport(0, 0, self.win_size.x, self.win_size.y)

    def __update(self):
        #self.cm.update_collisions()

        self.update()

        for e in self.update_order:
            if (not self.update_entities) or (not e.enabled):
                break
            e.update(self.last_delta)

    def __display(self):
        glEnable(GL_DEPTH_TEST)

        if self.clear_on_draw:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.display_back()

        for e in self.draw_order:
            if (not self.draw_entities) or (not e.enabled):
                break

            push_matrix()

            translate_2D(e.position)
            rotate_2D(e.rotation)
            scale_2D(e.scale)

            if not e.color is None:
                set_draw_color(e.color)

            e.display()

            set_draw_color("white")

            pop_matrix()

        self.display_front()

        # Actually show screen buffer
        pg.display.flip()

    def __handle_event(self, ev):
        if ev.type == pg.QUIT:
            # Handle X button
            self.quit_game()
        elif ev.type == pg.KEYDOWN:
            if ev.key == K_ESCAPE:
                # Handle Esc key
                self.quit_game()

        self.handle_event(ev)

        for e in self.events_order:
            e.handle_event(ev)

    def run(self):
        while self.running:
            for ev in pg.event.get():
                self.__handle_event(ev)

            if self.running:
                delta = self.clock.tick(self.target_fps) / 1000.
                self.last_delta = delta

                fps = 1. / delta
                self.avg_fps += fps
                self.ticks += 1
                
                if self.ticks % 10 == 0:
                    self.avg_fps /= 10
                    fps_target_ratio = self.avg_fps / self.target_fps

                    fps_str = f"FPS: {fps:.2f} ({fps_target_ratio*100:.2f}% of target)"
                    pg.display.set_caption(f"{self.win_title} | {fps_str}")
                    
                    self.avg_fps = 0.
                
                    if self.enable_fps_print:
                        print(fps_str)

                self.__update()
                if self.running:
                    self.__display()

        return self.exit_code

    def add_entity(self, ent: Entity):
        self.entities.append(ent)
        if ent.collider is not None:
            self.cm.add_collider(ent.collider)

        insort(self.draw_order, ent, key=lambda e: e.draw_priority)
        insort(self.update_order, ent, key=lambda e: e.update_priority)
        insort(self.events_order, ent, key=lambda e: e.events_priority)

    def quit_game(self, exit_code = 0):
        print("Quitting")
        pg.quit()
        self.exit_code = exit_code
        self.running = False

    def scrn_to_ogl(self, pos: Vector2D):
        return Vector2D(pos.x, self.win_size.y - pos.y)

    @property
    def mouse_position(self) -> Vector2D:
        m_pos = Vector2D(pg.mouse.get_pos())

        return self.scrn_to_ogl(m_pos)

    @property
    def screen_center(self) -> Vector2D:
        return self.win_size / 2.

    @property
    # FIXME: PROFOUNDLY BROKEN (OpenGL coordinates shenanigans...)
    def aabb(self):
        return AABB(Vector2D(0.), self.win_size, flipped_normals=True)

    def has_point(self, point: Vector2D) -> bool:
        return (0 <= point.x <= self.win_size.x) and (0 <= point.y <= self.win_size.y)

    def has_aabb(self, box: AABB) -> bool:
        return self.has_point(box.tl) and self.has_point(box.br)

    @abstractmethod
    def display_back(self):
        pass

    @abstractmethod
    def display_front(self):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

    @abstractmethod
    def update(self):
        pass
