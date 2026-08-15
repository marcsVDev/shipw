import pygame
from pygame import Rect, Surface, Vector2

from events.events import Events
from game_consts import GameConsts
from util.animatedSprite import AnimatedSprite
from entities.entity import Entity
from events.event_bus import EventBus
from util.collision.collidable import Collidable

class Player(Entity, Collidable):
    SCALE = 128
    MIDDLE_SCALE = SCALE / 2
    SPEED = 1000
    ROTATION_WEIGHT = 8
    ANGLE = 65

    def __init__(self):
        self.position: Vector2 = Vector2(GameConsts.SCREEN_WIDTH / 2, GameConsts.SCREEN_HEIGHT - self.MIDDLE_SCALE)
        self.can_move: bool = True

        self._idle_image: Surface = pygame.image.load(GameConsts.PLAYER_IMG_PATH).convert_alpha()
        self._idle_animation = AnimatedSprite(self._idle_image, 0.15, 64)        
        self._rotation: float = 0
        self._image: Surface = self._idle_animation.get_current_frame()
        self._rect: Rect

        EventBus.connect(Events.GAME_STARTED, self.game_started)

        super().__init__()

    def update(self, delta):
        self._idle_animation.update_frame(delta)
        self._image = self._idle_animation.get_current_frame()

        if self.can_move: 
            self.move_and_rotation(delta)

        self.scale()
        self.rotate()        
        self.align_rect()        

        self.screen_collide()
        self.update_vertices_from_rect(self._rect)        

    def draw(self, screen: Surface):
        if not self.visible:
            return        

        screen.blit(self._image, self._rect)

    def move_and_rotation(self, delta):
        keys = pygame.key.get_pressed()

        direction = Vector2(0, 0)        

        if keys[pygame.K_a]:
            direction.x -= 1
            self._rotation = pygame.math.lerp(self._rotation, self.ANGLE, self.ROTATION_WEIGHT * delta)            

        if keys[pygame.K_d]:
            direction.x += 1
            self._rotation = pygame.math.lerp(self._rotation, -self.ANGLE, self.ROTATION_WEIGHT * delta)           

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

    def game_started(self):
        self.can_move = True
        print("game started")

    def scale(self):
        self._image = pygame.transform.scale(
            self._image,
            (self.SCALE, self.SCALE)
        )

    def rotate(self):
        self._image = pygame.transform.rotate(
            self._image,
            self._rotation
        )

    def align_rect(self):
        self._rect = self._image.get_rect(
            center=self.position
        )