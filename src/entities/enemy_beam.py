from math import hypot

import pygame
from pygame import Vector2

from collision.collidable import Collidable
from entities.entity import Entity
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH


class EnemyBeam(Entity, Collidable):
    """Raio contínuo preso a um ponto local do sprite do inimigo."""

    DEFAULT_COLOR = "#ae2334"
    hazard_active = True

    def __init__(self, owner, pattern, source_pixel=(85.5, 115), width=18,
                 color=DEFAULT_COLOR):
        self.owner = owner
        self.pattern = pattern
        self.source_pixel = Vector2(source_pixel)
        self.width = int(round(width))
        self.color = pygame.Color(color)
        self.origin = Vector2()
        self.end = Vector2()
        self.length = hypot(SCREEN_WIDTH, SCREEN_HEIGHT) * 1.35
        super().__init__()
        self.update(0)

    def update(self, delta):
        current = (self.owner._patterns[self.owner._current_pattern]
                   if self.owner._patterns and not self.owner.to_destroy else None)
        if current is not self.pattern or self.pattern.finished:
            self.destroy()
            self._collider_vertices = []
            return

        frame_center = Vector2(self.owner.FRAME_SIZE / 2)
        sprite_scale = self.owner.SCALE / self.owner.FRAME_SIZE
        local_source = (self.source_pixel - frame_center) * sprite_scale
        self.origin = self.owner.position + local_source.rotate(-self.owner._rotation)
        direction = self.pattern.beam_direction
        self.end = self.origin + direction * self.length
        normal = direction.rotate(90) * (self.width / 2)
        self._collider_vertices = [
            self.origin + normal,
            self.end + normal,
            self.end - normal,
            self.origin - normal,
        ]

    def draw(self, screen):
        if not self.visible or self.to_destroy:
            return
        start, end = (round(self.origin.x), round(self.origin.y)), (round(self.end.x), round(self.end.y))
        glow = pygame.Color(self.color)
        glow.a = 80
        pygame.draw.line(screen, glow, start, end, self.width + 8)
        pygame.draw.line(screen, self.color, start, end, self.width)
        pygame.draw.line(screen, (255, 120, 130), start, end, max(2, self.width // 4))
