import pygame
from pygame import Vector2

from collision.collidable import Collidable
from entities.entity import Entity
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH


class EnemyProjectile(Entity, Collidable):
    RADIUS = 7

    def __init__(self, position, velocity):
        super().__init__()
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.age = 0.0
        self.update(0)

    def update(self, delta):
        self.age += delta
        self.position += self.velocity * delta
        r = self.RADIUS
        self._collider_vertices = [self.position + Vector2(x, y)
                                   for x, y in ((-r, -r), (r, -r), (r, r), (-r, r))]
        if (self.age > 8 or not -r <= self.position.x <= SCREEN_WIDTH + r
                or not -r <= self.position.y <= SCREEN_HEIGHT + r):
            self.destroy()

    def draw(self, screen):
        if self.visible:
            pygame.draw.circle(screen, (255, 90, 60), self.position, self.RADIUS)
            pygame.draw.circle(screen, (255, 240, 160), self.position, 3)
