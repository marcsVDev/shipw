import pygame
from pygame import Rect, Surface, Vector2

from game_consts import GameConsts
from util.animatedSprite import AnimatedSprite
from entities.entity import Entity

class Player(Entity):
    def __init__(self):
        self.idle_image: Surface = pygame.image.load(GameConsts.PLAYER_IMG_PATH).convert_alpha()
        self.animation = AnimatedSprite(self.idle_image, 0.15, 48)        
        self.scale = 128
        self.position: Vector2 = Vector2((1920/2) - self.scale, (1080/2) - self.scale)
        self.speed = 500
        self.can_move = True

        super().__init__()

    def update(self, delta):
        if self.can_move: 
            self.movement(delta)

        self.animation.update_frame(delta)

    def draw(self, screen: Surface):
        if not self.visible: 
            return

        screen.blit(pygame.transform.scale(self.animation.get_current_frame(), (self.scale, self.scale)), (self.position.x, self.position.y))

    def movement(self, delta):
        keys = pygame.key.get_pressed()

        direction = Vector2(0, 0)

        if keys[pygame.K_w]:
            direction.y -= 1

        if keys[pygame.K_s]:
            direction.y += 1

        if keys[pygame.K_a]:
            direction.x -= 1

        if keys[pygame.K_d]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.position += direction * self.speed * delta