from pygame import Surface
import pygame

from entities.entity import Entity


class Background(Entity):
    def __init__(self, image: Surface, scale: int):
        self.image = pygame.transform.scale_by(image, scale)
        super().__init__()
    def update(self, delta):
        pass

    def draw(self, screen):
        self.draw_image(screen, self.image, (0, 0))
