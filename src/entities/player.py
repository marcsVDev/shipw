import pygame
from pygame import Vector2

from entities.character import Character
from events.events import Events
from game_consts import GameConsts
from events.event_bus import EventBus

class Player(Character):    
    INITIAL_POSITION = Vector2(GameConsts.SCREEN_WIDTH // 2, GameConsts.SCREEN_HEIGHT - Character.MIDDLE_SCALE)
    ROTATION_ANGLE = 65
    DEFAULT_SPRITESHEET = GameConsts.PLAYER_IMG_PATH
    FRAME_SIZE = 64

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
        if self.position.x + self.MIDDLE_SCALE > GameConsts.SCREEN_WIDTH:
            self.position.x = GameConsts.SCREEN_WIDTH - self.MIDDLE_SCALE
        elif self.position.x - self.MIDDLE_SCALE < 0:
            self.position.x = self.MIDDLE_SCALE

    def player_collide(self, collisions):
        pass