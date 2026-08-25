from pygame import Surface
import pygame

from entities.entity import Entity


class Background(Entity):
    def __init__(self, image: Surface, scale: int):
        self.image = pygame.transform.scale_by(image, scale)
        super().__init__()
    def update(self, delta):
        return super().update(delta)
    def draw(self, screen):
        screen.blit(self.image, (0, 0))
        return super().draw(screen)
    