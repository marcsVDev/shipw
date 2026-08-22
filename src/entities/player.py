import pygame
from pygame import Vector2

from entities.character import Character
from events.events import Events
from game_consts import PLAYER_IMG_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from events.event_bus import EventBus

class Player(Character):
    MULTIPLIER = 1.2
    SCALE = 128 * MULTIPLIER
    MIDDLE_SCALE = SCALE // 2
    INITIAL_POSITION = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MIDDLE_SCALE)

    DEFAULT_SPRITESHEET = PLAYER_IMG_PATH
    FRAME_SIZE = 128

    DRAW_COLLIDER = False
    MIDDLE_VECTOR = Vector2(MIDDLE_SCALE, MIDDLE_SCALE)
    MIDDLE_VERTICES = [
        Vector2(62, 7) * MULTIPLIER - MIDDLE_VECTOR,     # TL
        Vector2(65, 7)* MULTIPLIER - MIDDLE_VECTOR,      # TR
        Vector2(67, 29) * MULTIPLIER - MIDDLE_VECTOR,    # MR
        Vector2(78, 53) * MULTIPLIER - MIDDLE_VECTOR,    # MMR
        Vector2(78, 75) * MULTIPLIER - MIDDLE_VECTOR,    # BR
        Vector2(85, 112) * MULTIPLIER - MIDDLE_VECTOR,   # BBR
        Vector2(42, 112) * MULTIPLIER - MIDDLE_VECTOR,   # BBL
        Vector2(49, 75) * MULTIPLIER - MIDDLE_VECTOR,    # BL
        Vector2(49, 53) * MULTIPLIER - MIDDLE_VECTOR,    # MML
        Vector2(60, 29) * MULTIPLIER - MIDDLE_VECTOR,    # ML
    ]

    SPEED = 1200
    ACCELERATION = 9000
    BRAKE_ACCELERATION = 2000
    MAX_TILT = 40
    TILT_RESPONSE = 90

    def __init__(self):
        EventBus.connect(Events.PLAYER_COLLIDE, self.player_collide)
        self.velocity = Vector2()

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
        if keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_w]:
            direction.y -= 1                 
        if keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
            target_velocity = direction * self.SPEED
            acceleration = self.ACCELERATION
        else:
            target_velocity = Vector2()
            acceleration = self.BRAKE_ACCELERATION

        self.velocity = self.velocity.move_towards(target_velocity, acceleration * delta)
        self.position += self.velocity * delta

        target_tilt = -(self.velocity.x / self.SPEED) * self.MAX_TILT
        blend = 1 - pow(2, -self.TILT_RESPONSE * delta)
        self._rotation = pygame.math.lerp(self._rotation, target_tilt, blend)

    def screen_collide(self):
        if self.position.x + self.MIDDLE_SCALE > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - self.MIDDLE_SCALE
            self.velocity.x = min(0, self.velocity.x)
        elif self.position.x - self.MIDDLE_SCALE < 0:
            self.position.x = self.MIDDLE_SCALE
            self.velocity.x = max(0, self.velocity.x)

        if self.position.y + self.MIDDLE_SCALE > SCREEN_HEIGHT:
            self.position.y = SCREEN_HEIGHT - self.MIDDLE_SCALE
            self.velocity.y = min(0, self.velocity.y)
        elif self.position.y - self.MIDDLE_SCALE < 0:
            self.position.y = self.MIDDLE_SCALE
            self.velocity.y = max(0, self.velocity.y)

    def player_collide(self, player, collisions):
        if player is not self:
            return

        EventBus.emit(Events.DESTROY_ENTITY, "player")
