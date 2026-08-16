import pygame
from pygame import Rect, Surface, Vector2

from enemys.enemy_pattern import EnemyPattern
from enemys.patterns.move_to import MoveTo
from entities.entity import Entity
from events.event_bus import EventBus
from events.events import Events
from game_consts import GameConsts
from util.collision.collidable import Collidable


class Enemy(Entity, Collidable):    
    SCALE = 128
    MIDDLE_SCALE = SCALE // 2
    MIDDLE_VERTICES = [
        Vector2(-MIDDLE_SCALE, -MIDDLE_SCALE),
        Vector2( MIDDLE_SCALE, -MIDDLE_SCALE),
        Vector2( MIDDLE_SCALE,  MIDDLE_SCALE),
        Vector2(-MIDDLE_SCALE,  MIDDLE_SCALE)
    ]
    DRAW_COLLIDER = False

    def __init__(self, _from: Vector2, _to: Vector2):
        self.position: Vector2 = _from
        self.can_move: bool = False
        self.speed: float = 300

        self._rotation = 0
        self._target: Vector2 = _to
        self._image: Surface = pygame.transform.scale(pygame.image.load(GameConsts.ASSETS_PATH + "foguete.png"), (self.SCALE, self.SCALE))        
        self._rect: Rect = self._image.get_rect(
            center=self.position
        )
        self._patterns: list[EnemyPattern] = [
            MoveTo(Vector2(0, 0), Vector2(GameConsts.SCREEN_WIDTH, GameConsts.SCREEN_HEIGHT), 2),
            MoveTo(Vector2(GameConsts.SCREEN_WIDTH, GameConsts.SCREEN_HEIGHT), Vector2(0, 0), 2)
        ]
        self._current_pattern: int = 0

        EventBus.connect(Events.GAME_STARTED, self.game_started)

        super().__init__()

    def update(self, delta):
        self._collider_vertices = self.get_rotated_vertices()

        if self._patterns[self._current_pattern].finished:
            if self._current_pattern + 1 >= len(self._patterns):
                self.visible = False # TODO apagar inimigo quando acaba patterns ??
                return
            
            self._current_pattern += 1
        
        if self.can_move:
            self._patterns[self._current_pattern].update(delta)
            self.pattern_movement()

        self.align_rect()
            
        return super().update(delta)
    
    def draw(self, screen):
        if not self.visible: 
            return

        if self.DRAW_COLLIDER:
            self.draw_collider()
            
        screen.blit(self._image, self._rect)
        return super().draw(screen)

    def align_rect(self):
        self._rect = self._image.get_rect(center = self.position)

    def pattern_movement(self):
        self.position = self._patterns[self._current_pattern].position

    def game_started(self):
        self.can_move = True

    def get_rotated_vertices(self) -> list[Vector2]:
        return [self.position + vertex.rotate(-self._rotation) for vertex in self.MIDDLE_VERTICES] 
    