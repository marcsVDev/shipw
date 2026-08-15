from entities.entity import Entity
from util.collision.collidable import Collidable


class Enemy(Entity, Collidable):
    def __init__(self):
        super().__init__()
    def update(self, delta):
        return super().update(delta)
    def draw(self, screen):
        return super().draw(screen)
    