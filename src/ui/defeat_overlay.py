import pygame

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


class DefeatOverlay(UI):
    def __init__(self):
        super().__init__()
        self.title = get_font(64).render("MISSÃO FRACASSOU", True, "#ae2334")
        self.help = get_font(28).render("ENTER — REINICIAR     ESC — MENU", True, "white")

    def draw(self, screen):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 185))
        screen.blit(shade, (0, 0))
        screen.blit(self.title, self.title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 45)))
        screen.blit(self.help, self.help.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 45)))
