import pygame
from pygame import Rect, Surface, Vector2

from animatedSprite import AnimatedSprite
from entity import Entity

class Player(Entity):
    def __init__(self):
        self.image: Surface = pygame.image.load("player.png").convert_alpha()
        self.animation = AnimatedSprite(self.image, 0.01, 48)
        self.position: Vector2 = Vector2(0, 0)
        self.scale = 128
        self.speed = 500
        self.can_move = True

    def update(self, delta):
        if self.can_move: 
            self.movement(delta)

        self.animation.update_frame(delta)

    def draw(self, screen: Surface):
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