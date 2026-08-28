import pygame
from pygame import Vector2

from entities.character import Character
from events.events import Events
from game_consts import PLAYER_IMG_PATH, SCREEN_HEIGHT, SCREEN_WIDTH, SFX_PATH
from events.event_bus import EventBus

class Player(Character):
    MULTIPLIER = 1.3
    SCALE = 128 * MULTIPLIER
    MIDDLE_SCALE = SCALE // 2
    INITIAL_POSITION = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - SCALE)

    DEFAULT_SPRITESHEET = PLAYER_IMG_PATH
    FRAME_SIZE = 128

    ANIMATIONS = {
        "default": [0, 1, 2, 3, 4, 5, 6, 7]
    }
    ANIMATION_FRAME_DURATION = 0.10

    DRAW_COLLIDER = False
    MIDDLE_VECTOR = Vector2(MIDDLE_SCALE, MIDDLE_SCALE)
    MIDDLE_VERTICES = [
        Vector2(62, 1) * MULTIPLIER - MIDDLE_VECTOR,     # TL
        Vector2(65, 1) * MULTIPLIER - MIDDLE_VECTOR,     # TR
        Vector2(67, 23) * MULTIPLIER - MIDDLE_VECTOR,    # MR
        Vector2(78, 47) * MULTIPLIER - MIDDLE_VECTOR,    # MMR
        Vector2(78, 69) * MULTIPLIER - MIDDLE_VECTOR,    # BR
        Vector2(85, 106) * MULTIPLIER - MIDDLE_VECTOR,   # BBR
        Vector2(42, 106) * MULTIPLIER - MIDDLE_VECTOR,   # BBL
        Vector2(49, 69) * MULTIPLIER - MIDDLE_VECTOR,    # BL
        Vector2(49, 47) * MULTIPLIER - MIDDLE_VECTOR,    # MML
        Vector2(60, 23) * MULTIPLIER - MIDDLE_VECTOR,    # ML
    ]    

    SPEED = 1200
    ACCELERATION = 9000
    BRAKE_ACCELERATION = 2000
    MAX_TILT = 40
    TILT_RESPONSE = 90

    PLAYER_SFX = SFX_PATH + "player.mp3"
    VOLUME = 80

    def __init__(self):
        EventBus.connect(Events.PLAYER_COLLIDE, self.player_collide)
        self.velocity = Vector2()
        self.sound = pygame.mixer.Sound(self.PLAYER_SFX)   
        self.sound.set_volume(self.VOLUME)

        super().__init__()

    def update(self, delta):
        if self.can_move:
            self.screen_collide() 

        super().update(delta)
    
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

            self.sound.set_volume(self.VOLUME + 30)
        else:
            target_velocity = Vector2()
            acceleration = self.BRAKE_ACCELERATION

        if direction == Vector2(0, 0):
            self.sound.set_volume(self.VOLUME - 80)    

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

        self.sound.stop()

        self.destroy()

    def game_started(self):
        super().game_started()
        self.sound.play(-1)
    