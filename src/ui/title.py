from pygame import Surface, Vector2
import pygame

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH, UI_PATH
from ui.ui import UI


class Title(UI):
    M = 5
    SIZE = (128*M, 64*M)
    TITLE_PATH = UI_PATH + "title.png"
    POSITION = (SCREEN_WIDTH // 2 - SIZE[0] // 2, SCREEN_HEIGHT // 2 - SIZE[1] // 2)

    def __init__(self):
        self._image: Surface = pygame.image.load(self.TITLE_PATH).convert_alpha()
        self._image = pygame.transform.scale_by(self._image, self.M)
        super().__init__()

    def update(self, delta, events):
        return super().update(delta, events)
    
    def draw(self, screen):
        screen.blit(self._image, self.POSITION)
        return super().draw(screen)