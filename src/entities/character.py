from abc import abstractmethod

from pygame import Rect, Surface, Vector2
import pygame

from entities.entity import Entity
from events.event_bus import EventBus
from events.events import Events
from util.animatedSprite import AnimatedSprite
from collision.collidable import Collidable


class Character(Entity, Collidable):
    SCALE = 128
    MIDDLE_SCALE = SCALE // 2
    MIDDLE_VERTICES = [
        Vector2(-MIDDLE_SCALE, -MIDDLE_SCALE),
        Vector2( MIDDLE_SCALE, -MIDDLE_SCALE),
        Vector2( MIDDLE_SCALE,  MIDDLE_SCALE),
        Vector2(-MIDDLE_SCALE,  MIDDLE_SCALE)
    ]
    INITIAL_POSITION = None
    DRAW_COLLIDER = False    
    ANIMATION_FRAME_DURATION = 0.15
    ROTATION_ANGLE = None
    FRAME_SIZE = None
    DEFAULT_SPRITESHEET = None    

    def __init__(self):
        self.position: Vector2 = self.INITIAL_POSITION
        self.can_move: bool = False

        self._idle_image: Surface = pygame.image.load(self.DEFAULT_SPRITESHEET).convert_alpha()
        self._idle_animation = AnimatedSprite(self._idle_image, self.ANIMATION_FRAME_DURATION, self.FRAME_SIZE)     
        self._image = self._idle_animation.get_current_frame()
        
        self._original_image = self._image
        self._rotation = 0
        self._rect: Rect 

        EventBus.connect(Events.GAME_STARTED, self.game_started)

        super().__init__()

    def update(self, delta):
        self._idle_animation.update_frame(delta)
        self._image = self._idle_animation.get_current_frame()

        if self.can_move: 
            self.movement(delta) 

        self.scale(self.SCALE)
        self.rotate()        
        self.align_rect()  

        self._collider_vertices = self.get_rotated_vertices()
        
        return super().update(delta)

    def draw(self, screen: Surface):
        if not self.visible:
            return        

        if self.DRAW_COLLIDER:
            self.draw_collider(screen) 

        screen.blit(self._image, self._rect)   

    @abstractmethod
    def movement(delta):
        ...

    def scale(self, by):
        self._image = pygame.transform.scale(self._image, (by, by))
    
    def rotate(self):
        self._image = pygame.transform.rotate(self._image, self._rotation)

    def align_rect(self):
        self._rect = self._image.get_rect(center=self.position)

    def get_rotated_vertices(self) -> list[Vector2]:
        return [self.position + vertex.rotate(-self._rotation) for vertex in self.MIDDLE_VERTICES] 

    def game_started(self):
        self.can_move = True