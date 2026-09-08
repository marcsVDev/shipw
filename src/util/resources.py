"""Recursos compartilhados; timers e canais de reprodução ficam nas entidades."""
from functools import lru_cache

import pygame


@lru_cache(maxsize=64)
def load_image(path):
    return pygame.image.load(path).convert_alpha()


@lru_cache(maxsize=32)
def load_sound(path):
    return pygame.mixer.Sound(path)


@lru_cache(maxsize=512)
def scaled_frame(sheet, frame_size, frame_index, scale):
    frame = sheet.subsurface(pygame.Rect(frame_index * frame_size, 0, frame_size, frame_size))
    return pygame.transform.scale(frame, (int(scale), int(scale)))
