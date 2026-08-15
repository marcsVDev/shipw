import pygame
from pygame import Vector2

from entities.entity import Entity
from entities.player import Player
from game_consts import GameConsts
from util.collision.collidable import Collidable


class Enemy(Entity, Collidable):
    def __init__(self, player):
        self.image = pygame.transform.scale(pygame.image.load(GameConsts.ASSETS_PATH + "foguete.png"), (128, 128))
        self.position: Vector2 = Vector2(GameConsts.SCREEN_WIDTH - 128, GameConsts.SCREEN_HEIGHT - 128)
        self._rect = self.image.get_rect(
            center=self.position
        )

        self.player: Player = player
        super().__init__()
    def update(self, delta):
        self.update_vertices_from_rect(self._rect)

        if self.collide_with(self.player):
            self.visible = False
        else:
            self.visible = True
            
        return super().update(delta)
    def draw(self, screen):
        if not self.visible: 
            return
        
        screen.blit(self.image, self.position)
        return super().draw(screen)
    