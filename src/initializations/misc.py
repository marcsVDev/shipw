import pygame

from game_consts import ASSETS_PATH

FONT_PATH = ASSETS_PATH + "fonts/ARCADECLASSIC.TTF"

def get_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(FONT_PATH, size)