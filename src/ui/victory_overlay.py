import pygame

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


class VictoryOverlay(UI):
    def __init__(self):
        super().__init__()
        self.title = get_font(72).render("OBRIGADO POR JOGAR", True, "#ffddaa")
        self.subtitle = get_font(34).render("VALENTINA CHEGOU A MARTE", True, "white")
        self.help = get_font(28).render("ENTER OU ESC — MENU", True, "white")
        self.modal = True

    def draw(self, screen):
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 190))
        screen.blit(shade, (0, 0))
        for image, offset in ((self.title, -80), (self.subtitle, 10), (self.help, 100)):
            screen.blit(image, image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + offset)))
