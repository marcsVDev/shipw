import pygame

from entities.background import Background
from entities.scrollers.moving_object import MovingObject
from game_consts import SCENERY_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from util.animatedSprite import AnimatedSprite

EARTH_FRAME_SIZE = 128
EARTH_SCALE = 8
EARTH_SPEED = 2.5

def get_earth_scenery():
    earth_img = pygame.image.load(SCENERY_PATH + "earth.png").convert_alpha()
    earth_img.set_alpha(170)
    earth_img = pygame.transform.scale_by(earth_img, EARTH_SCALE)

    earth_size = EARTH_FRAME_SIZE * EARTH_SCALE

    return MovingObject(
        AnimatedSprite(earth_img, 1, earth_size),
        pygame.Vector2(SCREEN_WIDTH - earth_size, SCREEN_HEIGHT - earth_size),
        pygame.Vector2(0, 1),
        EARTH_SPEED
    )

SATELLITE_SCALE = 4
SATELLITE_FRAME_SIZE = 90
SATELLITE_SPEED = 100

def get_satellite_scenery():
    sat_img = pygame.image.load(SCENERY_PATH + "sateliteobsdesenho.png").convert_alpha()
    sat_img.set_alpha(90)
    sat_img = pygame.transform.scale_by(sat_img, SATELLITE_SCALE)

    sat_size = SATELLITE_FRAME_SIZE * SATELLITE_SCALE

    sat = MovingObject(
        AnimatedSprite(sat_img, 1, sat_size),
        pygame.Vector2(SCREEN_WIDTH + sat_size // 2, 0),
        pygame.Vector2(-1, 0.1),
        SATELLITE_SPEED
    )
    sat.run()
    
    return sat

def get_krasny_mir_background():
    return Background(pygame.image.load(SCENERY_PATH + "krasny_mir_station.png").convert_alpha(), 4)