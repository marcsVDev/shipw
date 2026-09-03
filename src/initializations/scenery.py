import pygame

from entities.background import Background
from entities.scrollers.infinite_vertical_scroller import InfiniteVerticalScroller
from entities.scrollers.moving_object import MovingObject
from game_consts import SCENERY_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from util.animatedSprite import AnimatedSprite

EARTH_FRAME_SIZE = 128
EARTH_SCALE = 8
EARTH_SPEED = 2.5

S4_SCALE = 4
S128_FRAME_SIZE = 128

def darken_image(image: pygame.Surface, amount: int = 100) -> pygame.Surface:
    """Retorna uma copia escurecida da imagem sem alterar a original.

    ``amount`` deve estar entre 0 (sem alteracao) e 255 (preto).
    """
    amount = max(0, min(255, amount))
    darkened_image = image.copy()
    brightness = 255 - amount
    darkened_image.fill(
        (brightness, brightness, brightness, 255),
        special_flags=pygame.BLEND_RGBA_MULT,
    )
    return darkened_image

def get_earth_scenery():
    earth_img = pygame.image.load(SCENERY_PATH + "earth.png").convert_alpha()
    earth_img.set_alpha(170)
    earth_img = pygame.transform.scale_by(earth_img, EARTH_SCALE)

    earth_size = earth_img.get_width()

    earth = MovingObject(
        AnimatedSprite(earth_img, 1, earth_size),
        pygame.Vector2(SCREEN_WIDTH - earth_size, SCREEN_HEIGHT - earth_size),
        pygame.Vector2(0, 1),
        EARTH_SPEED
    )

    earth.run()

    return earth

def get_venus_scenery():
    venus_img = pygame.image.load(SCENERY_PATH + "venus.png").convert_alpha()
    venus_img = pygame.transform.scale_by(venus_img, S4_SCALE)

    venus_size = venus_img.get_width()

    venus = MovingObject(
        AnimatedSprite(darken_image(venus_img, 60), 1, venus_size),
        pygame.Vector2(SCREEN_WIDTH - venus_size // 2, 0),
        pygame.Vector2(1, 0.1),
        4
    )
    venus.run()
    
    return venus

def get_satellite_scenery():
    sat_img = pygame.image.load(SCENERY_PATH + "satelite.png").convert_alpha()
    sat_img = pygame.transform.scale_by(sat_img, S4_SCALE)

    sat_size = sat_img.get_width()    

    sat = MovingObject(
        AnimatedSprite(darken_image(sat_img, 50), 1, sat_size),
        pygame.Vector2(SCREEN_WIDTH + sat_size // 2, 100),
        pygame.Vector2(-1, 0.1),
        90
    )
    sat.run()
    
    return sat

def get_krasny_mir_background():
    return Background(pygame.image.load(SCENERY_PATH + "krasny_mir_station.png").convert_alpha(), 4)

def get_espaco_proximo_background():
    image = pygame.image.load(SCENERY_PATH + "espaco_proximo.png").convert_alpha()
    image = pygame.transform.scale_by(image, 1.14)
    return InfiniteVerticalScroller(darken_image(image), 5, True)

def get_estratosfera_background():
    image = pygame.image.load(SCENERY_PATH + "estratosfera.png").convert_alpha()
    image = pygame.transform.scale_by(image, 1.1)
    return InfiniteVerticalScroller(image, 500, True)
