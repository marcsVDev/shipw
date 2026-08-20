import pygame
from pygame import Vector2

from entities.character import Character
from events.events import Events
from game_consts import PLAYER_IMG_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from events.event_bus import EventBus

class Player(Character):    
    SCALE = 128
    INITIAL_POSITION = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - Character.MIDDLE_SCALE)
    ROTATION_ANGLE = 65
    DEFAULT_SPRITESHEET = PLAYER_IMG_PATH
    FRAME_SIZE = 128
    DRAW_COLLIDER = True
    MIDDLE_VECTOR = Vector2(SCALE // 2,SCALE // 2)
    MIDDLE_VERTICES = [
        Vector2(62, 7) - MIDDLE_VECTOR,     # TL
        Vector2(65, 7) - MIDDLE_VECTOR,     # TR
        Vector2(67, 29) - MIDDLE_VECTOR,    # MR
        Vector2(78, 53) - MIDDLE_VECTOR,    # MMR
        Vector2(78, 75) - MIDDLE_VECTOR,    # BR
        Vector2(85, 112) - MIDDLE_VECTOR,   # BBR
        Vector2(42, 112) - MIDDLE_VECTOR,   # BBL
        Vector2(49, 75) - MIDDLE_VECTOR,    # BL
        Vector2(49, 53) - MIDDLE_VECTOR,    # MML
        Vector2(60, 29) - MIDDLE_VECTOR,    # ML
    ]

    ROTATION_WEIGHT = 8
    SPEED = 1000

    def __init__(self):
        EventBus.connect(Events.PLAYER_COLLIDE, self.player_collide)

        super().__init__()

    def update(self, delta):
        self.screen_collide() 

        return super().update(delta)

    def draw(self, screen):
        return super().draw(screen)
    
    def movement(self, delta):
        keys = pygame.key.get_pressed()

        direction = Vector2(0, 0)        

        if keys[pygame.K_a]:
            direction.x -= 1
            self._rotation = pygame.math.lerp(self._rotation, self.ROTATION_ANGLE, self.ROTATION_WEIGHT * delta)            

        if keys[pygame.K_d]:
            direction.x += 1
            self._rotation = pygame.math.lerp(self._rotation, -self.ROTATION_ANGLE, self.ROTATION_WEIGHT * delta)           

        if direction.length_squared() > 0:
            direction = direction.normalize()

        if direction.x == 0:
            self._rotation = pygame.math.lerp(self._rotation, 0, self.ROTATION_WEIGHT * delta)

        self.position += direction * self.SPEED * delta

    def screen_collide(self):
        if self.position.x + self.MIDDLE_SCALE > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - self.MIDDLE_SCALE
        elif self.position.x - self.MIDDLE_SCALE < 0:
            self.position.x = self.MIDDLE_SCALE

    def player_collide(self, collisions):
        pass