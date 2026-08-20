import pygame

from entities.scrollers.moving_object import MovingObject
from game_consts import SCENERY_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from util.animatedSprite import AnimatedSprite

EARTH_FRAME_SIZE = 128
EARTH_SCALE = 8
EARTH_SPEED = 2.5

def get_earth_scenery():
    earth_img = pygame.image.load(SCENERY_PATH + "earth.png").convert_alpha()
    earth_img = pygame.transform.scale_by(earth_img, EARTH_SCALE)

    earth_size = EARTH_FRAME_SIZE * EARTH_SCALE

    return MovingObject(
        AnimatedSprite(earth_img, 1, earth_size),
        pygame.Vector2(SCREEN_WIDTH - earth_size, SCREEN_HEIGHT - earth_size),
        pygame.Vector2(0, 1),
        EARTH_SPEED
    )