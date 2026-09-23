from dataclasses import dataclass
import math

import pygame
from pygame import Vector2

from collision.collidable import Collidable
from entities.entity import Entity
from events.event_bus import EventBus
from events.events import Events
from game_consts import ENEMYS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from ui.alert_indicator import AlertIndicator
from util.resources import load_image


@dataclass(frozen=True)
class MotherShipConfig:
    max_health: int = 5
    width_ratio: float = 1.0
    combat_position: tuple[float, float] = (960, 135)
    entry_duration: float = 2.5
    defeat_duration: float = 4.0


class MotherShipEnemy(Entity, Collidable):
    damages_player = True
    is_mother_ship = True

    def __init__(self, config: MotherShipConfig = MotherShipConfig()):
        self.config = config
        source = load_image(ENEMYS_PATH + "navemaeeua.png")
        source = source.subsurface(source.get_bounding_rect()).copy()
        damaged = load_image(ENEMYS_PATH + "navemaedestruida.png")
        damaged = damaged.subsurface(damaged.get_bounding_rect()).copy()
        width = int(SCREEN_WIDTH * config.width_ratio)
        height = round(source.get_height() * width / source.get_width())
        self.image = pygame.transform.scale(source, (width, height))
        self.damaged_image = pygame.transform.scale(damaged, (width, height))
        self.position = Vector2(config.combat_position[0], -height / 2)
        self.start_y = self.position.y
        self.combat_y = config.combat_position[1]
        self.entry_elapsed = 0.0
        self.active = False
        self.health = self.max_health = config.max_health
        self.damage_flash = 0.0
        self.health_bar_visible = False
        self.defeated = False
        self.defeat_elapsed = 0.0
        self._defeat_emitted = False
        self.alert_indicator = AlertIndicator()
        super().__init__()
        self._refresh_collider()

    def update(self, delta):
        delta = max(0.0, delta)
        self.damage_flash = max(0.0, self.damage_flash - delta)
        if not self.active:
            previous_entry_elapsed = self.entry_elapsed
            self.entry_elapsed = min(self.config.entry_duration, self.entry_elapsed + delta)
            progress = self.entry_elapsed / self.config.entry_duration
            smooth = progress * progress * (3 - 2 * progress)
            self.position.y = self.start_y + (self.combat_y - self.start_y) * smooth
            if progress >= 1:
                self.active = True
                self.health_bar_visible = True
            alert_delta = max(
                0.0,
                min(self.entry_elapsed, 1.6) - max(previous_entry_elapsed, 0.4),
            )
            self.alert_indicator.update(alert_delta)
            self._refresh_collider()
        if self.defeated:
            self.defeat_elapsed += delta
            self.position.y -= 34 * delta
            self._refresh_collider()

    def _refresh_collider(self):
        if not self.active or self.defeated:
            self._collider_vertices = []
            return
        rect = self.image.get_rect(center=self.position)
        inset = 45
        self._collider_vertices = [Vector2(rect.left + inset, rect.top + 25),
                                   Vector2(rect.right - inset, rect.top + 25),
                                   Vector2(rect.right - inset, rect.bottom - 30),
                                   Vector2(rect.left + inset, rect.bottom - 30)]

    @property
    def body_rect(self):
        return self.image.get_rect(center=self.position)

    @property
    def launch_position(self):
        rect = self.body_rect
        return Vector2(rect.centerx, rect.bottom + 24)

    def take_missile_hit(self, armed=True):
        if self.defeated or not armed:
            return False
        self.health = max(0, self.health - 1)
        if self.health <= self.max_health / 2:
            self.image = self.damaged_image
        self.damage_flash = 0.15
        EventBus.emit(Events.BOSS_DAMAGED, self, self.health, None)
        if self.health == 0 and not self._defeat_emitted:
            self._defeat_emitted = True
            self.defeated = True
            self.health_bar_visible = False
            self._collider_vertices = []
            EventBus.emit(Events.BOSS_DEFEATED, self)
        return True

    def draw(self, screen):
        if self.entry_elapsed < 0.4:
            shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, int(95 * (1 - self.entry_elapsed / .4))))
            screen.blit(shade, (0, 0))
        screen.blit(self.image, self.image.get_rect(center=self.position))
        if 0.4 <= self.entry_elapsed <= 1.6:
            self.alert_indicator.draw(
                screen, (SCREEN_WIDTH / 2, SCREEN_HEIGHT * .45)
            )
        if self.defeated:
            for index in range(min(5, int(self.defeat_elapsed / .18) + 1)):
                angle = index * 137.5
                radius = 45 + index * 23
                point = self.position + Vector2(radius, 0).rotate(angle)
                size = 18 + int(8 * abs(math.sin(self.defeat_elapsed * 15 + index)))
                pygame.draw.circle(screen, "#f9c22b", point, size)
            if self.defeat_elapsed > 1.1:
                pygame.draw.circle(screen, "white", self.position, int(45 + self.defeat_elapsed * 25), 8)
