from dataclasses import dataclass
import pygame
from pygame import Vector2

from collision.collidable import Collidable
from entities.entity import Entity
from game_consts import ENEMYS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH, SFX_PATH
from util.resources import load_image, load_sound


@dataclass(frozen=True)
class GuidedMissileConfig:
    telegraph_duration: float = 1.0
    initial_speed: float = 550.0
    max_speed: float = 1450.0
    acceleration: float = 1100.0
    turn_rate: float = 240.0
    arm_time: float = 1.25
    pursuit_duration: float = 8.0
    expiry_warning: float = 0.8
    radius: float = 22.0
    explosion_radius: float = 96.0


class GuidedMissile(Entity, Collidable):
    is_guided_missile = True
    consume_on_player_contact = False
    hazard_active = True

    def __init__(self, position, target_provider, boss,
                 config: GuidedMissileConfig = GuidedMissileConfig()):
        self.config = config
        self.position = Vector2(position)
        self.previous_position = self.position.copy()
        self.target_provider = target_provider
        self.boss = boss
        self.direction = Vector2(0, 1)
        self.speed = config.initial_speed
        self.elapsed = 0.0
        self.flight_time = 0.0
        self.state = "telegraph"
        self.exploded = False
        self.explosion_reason = None
        self.explosion_remaining = 0.0
        self.sound = load_sound(SFX_PATH + "laser.mp3")
        self.image = pygame.transform.scale(load_image(ENEMYS_PATH + "missilbossfinal.png"), (64, 64))
        self.channel = None
        super().__init__()
        self._refresh_collider()

    @property
    def armed(self):
        return self.flight_time >= self.config.arm_time

    def update(self, delta):
        if self.exploded:
            self.explosion_remaining = max(0.0, self.explosion_remaining - max(0.0, delta))
            if self.explosion_remaining == 0:
                self.destroy()
            return
        delta = max(0.0, delta)
        self.previous_position = self.position.copy()
        if self.state == "telegraph":
            self._collider_vertices = []
            remaining_telegraph = self.config.telegraph_duration - self.elapsed
            if delta < remaining_telegraph:
                self.elapsed += delta
                return
            delta -= max(0.0, remaining_telegraph)
            self.elapsed = self.config.telegraph_duration
            self.state = "launch"
            self.channel = self.sound.play(-1)
            if self.channel is not None:
                self.channel.set_volume(.25)

        flight_delta = min(delta, max(0.0, self.config.pursuit_duration - self.flight_time))
        remaining = flight_delta
        while remaining > 0:
            step = min(remaining, 1 / 120)
            target = self.target_provider()
            if target is not None:
                desired = Vector2(target) - self.position
                if desired.length_squared():
                    desired = desired.normalize()
                    signed = (self.direction.angle_to(desired) + 180) % 360 - 180
                    change = max(-self.config.turn_rate * step,
                                 min(self.config.turn_rate * step, signed))
                    self.direction = self.direction.rotate(change).normalize()
            old_speed = self.speed
            self.speed = min(self.config.max_speed,
                             self.speed + self.config.acceleration * step)
            self.position += self.direction * ((old_speed + self.speed) * .5 * step)
            remaining -= step
        self.flight_time += flight_delta
        if self.flight_time >= self.config.pursuit_duration - self.config.expiry_warning:
            self.state = "expiring"
        elif self.flight_time > 0.15:
            self.state = "seeking"
        self._refresh_collider()
        if self.flight_time >= self.config.pursuit_duration:
            self.explode("expired")

    def _refresh_collider(self):
        r = self.config.radius
        self._collider_vertices = [self.position + Vector2(x, y)
                                   for x, y in ((-r, -r), (r, -r), (r, r), (-r, r))]

    def _segment_near(self, point, radius):
        segment = self.position - self.previous_position
        if segment.length_squared() == 0:
            return self.position.distance_to(point) <= radius
        t = max(0.0, min(1.0, (Vector2(point) - self.previous_position).dot(segment)
                             / segment.length_squared()))
        return (self.previous_position + segment * t).distance_to(point) <= radius

    def resolve_collisions(self, scene):
        if self.exploded or self.state == "telegraph":
            return
        body = self.boss.body_rect.inflate(self.config.radius * 2, self.config.radius * 2)
        if body.collidepoint(self.position) or body.clipline(self.previous_position, self.position):
            if self.boss.take_missile_hit(armed=self.armed):
                self.explode("boss")
            else:
                self.explode("armor")
            return

        for entity in tuple(scene.entities):
            if (entity is self or entity is self.boss or entity.to_destroy
                    or not getattr(entity, "is_laser_ship", False)):
                continue
            if self._segment_near(entity.position, self.config.radius + entity.SCALE * .42):
                entity.destroy()
                self.explode("laser_ship")
                return

        player = scene.player
        if player is not None and not player.to_destroy and self._segment_near(
                player.position, self.config.radius + player.MIDDLE_SCALE * .55):
            player.take_damage((self,))
            self.explode("player")
            return

        for entity in tuple(scene.enemys):
            if (entity.to_destroy or getattr(entity, "is_laser_ship", False)
                    or getattr(entity, "is_mother_ship", False)):
                continue
            if self._segment_near(entity.position, self.config.radius + entity.SCALE * .4):
                entity.destroy()
                self.explode("minor_enemy")
                return

        margin = 260
        if (self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin
                or self.position.y < -margin or self.position.y > SCREEN_HEIGHT + margin):
            self.explode("bounds")

    def explode(self, reason):
        if self.exploded:
            return False
        self.exploded = True
        self.state = "exploded"
        self.explosion_reason = reason
        self.explosion_remaining = .18
        self._collider_vertices = []
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
        return True

    def draw(self, screen):
        if self.exploded:
            radius = int(self.config.explosion_radius *
                         (1 - self.explosion_remaining / .18))
            pygame.draw.circle(screen, "#f9c22b", self.position, max(8, radius), 5)
            pygame.draw.circle(screen, "white", self.position, max(4, radius // 2), 3)
            return
        if self.state == "telegraph":
            return
        angle = -Vector2(0, -1).angle_to(self.direction)
        if self.state != "expiring" or int(self.flight_time * 12) % 2 == 0:
            image = pygame.transform.rotate(self.image, angle)
            screen.blit(image, image.get_rect(center=self.position))

    def destroy(self):
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
        super().destroy()
