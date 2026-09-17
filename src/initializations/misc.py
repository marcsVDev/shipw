import pygame

from game_consts import ASSETS_PATH

FONT_PATH = ASSETS_PATH + "fonts/PixelifySans-VariableFont_wght.ttf"

def get_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(FONT_PATH, size)