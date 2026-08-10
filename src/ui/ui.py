from pygame import Surface, Vector2
import pygame

from entities.entity import Entity


class UI(Entity):
    def __init__(self, image: Surface, position: Vector2):
        self.position: Vector2 = position
        self.image: Surface = image
        super().__init__()

    def draw(self, screen: Surface):
        pass

    def update(self, delta: float, events: list[pygame.event.Event]):
        pass

    