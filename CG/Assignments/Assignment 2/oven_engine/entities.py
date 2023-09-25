from abc import ABC, abstractmethod

import shortuuid
from pygame import Color

from oven_engine.utils.collisions import CollisionMode, AABBCollider
from oven_engine.utils.geometry import Vector2D


class Entity(ABC):
    """
    Base Entity class
    """
    
    def __init__(self, position, parent,
                 rotation=0., scale=Vector2D.ONE,
                 color : [Color|str] = "white",
                 name="", collision_mode=CollisionMode.DISABLED,
                 update_pr = 0, draw_pr = 0, events_pr = 0) -> None:
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.parent_app = parent
        #self.collision_manager = parent.cm
        self.color = color
        self._enabled = True
        self.collider = None
        self.collision_mode = collision_mode
        self.__coll_mode_last = collision_mode
        self.draw_priority = draw_pr
        self.update_priority = update_pr
        self.events_priority = events_pr

        if name == "":
            name = shortuuid.uuid()
        self.name = name

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value
        self.collision_mode = CollisionMode.DISABLED if not value else self.__coll_mode_last

    @abstractmethod
    def update(self, delta):
        pass
    
    @abstractmethod
    def display(self):
        pass

    @abstractmethod
    def handle_event(self, ev):
        pass

    def reset(self):
        pass

    @property
    def aabb(self):
        return None

    def __str__(self):
        return f"[{self.name}]"

    def handle_collision(self, other: 'Entity', collision: list):
        pass

class WorldEntity(Entity):
    def __init__(self, position, parent) -> None:
        super().__init__(position, parent, name="ZaWarudo", collision_mode=CollisionMode.RECEIVE_ONLY)
        self.parent_app = parent
        self.parent_app.add_entity(self)
        self.collider = AABBCollider.fromAABB(self.parent_app.aabb, self)

    def update(self, delta):
        pass

    def display(self):
        pass

    def handle_event(self, ev):
        pass