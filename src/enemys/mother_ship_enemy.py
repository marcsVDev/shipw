from dataclasses import dataclass
import math

import pygame
from pygame import Vector2

from collision.collidable import Collidable
from entities.entity import Entity
from events.event_bus import EventBus
from events.events import Events
from game_consts import ENEMYS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from util.resources import load_image


@dataclass(frozen=True)
class MotherShipConfig:
    max_health: int = 5
    width_ratio: float = 0.88
    combat_position: tuple[float, float] = (960, 135)
    entry_duration: float = 2.5
    target_radius: float = 52.0
    defeat_duration: float = 4.0


class MotherShipEnemy(Entity, Collidable):
    damages_player = True
    is_mother_ship = True

    TARGETS = {
        "left_hangar": (0.29, 0.19),
        "left_cannon": (0.40, 0.23),
        "core": (0.50, 0.17),
        "right_cannon": (0.60, 0.23),
        "right_hangar": (0.71, 0.19),
    }

    def __init__(self, config: MotherShipConfig = MotherShipConfig()):
        self.config = config
        source = load_image(ENEMYS_PATH + "navemaeeua.png")
        source = source.subsurface(source.get_bounding_rect()).copy()
        width = int(SCREEN_WIDTH * config.width_ratio)
        height = round(source.get_height() * width / source.get_width())
        self.image = pygame.transform.smoothscale(source, (width, height))
        self.position = Vector2(config.combat_position[0], -height / 2)
        self.start_y = self.position.y
        self.combat_y = config.combat_position[1]
        self.entry_elapsed = 0.0
        self.active = False
        self.health = self.max_health = config.max_health
        self.target_states = {name: "closed" for name in self.TARGETS}
        self.active_target = None
        self.target_warning = 0.0
        self.damage_flash = 0.0
        self.hit_flash_target = None
        self.hit_flash_remaining = 0.0
        self.health_bar_visible = False
        self.defeated = False
        self.defeat_elapsed = 0.0
        self._defeat_emitted = False
        super().__init__()
        self._refresh_collider()

    def update(self, delta):
        delta = max(0.0, delta)
        self.damage_flash = max(0.0, self.damage_flash - delta)
        self.hit_flash_remaining = max(0.0, self.hit_flash_remaining - delta)
        if self.hit_flash_remaining == 0:
            self.hit_flash_target = None
        if not self.active:
            self.entry_elapsed = min(self.config.entry_duration, self.entry_elapsed + delta)
            progress = self.entry_elapsed / self.config.entry_duration
            smooth = progress * progress * (3 - 2 * progress)
            self.position.y = self.start_y + (self.combat_y - self.start_y) * smooth
            if progress >= 1:
                self.active = True
                self.health_bar_visible = True
            self._refresh_collider()
        if self.target_warning > 0:
            self.target_warning = max(0.0, self.target_warning - delta)
            if self.target_warning == 0 and self.active_target is not None:
                self.target_states[self.active_target] = "open"
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

    def target_position(self, name):
        ratio_x, ratio_y = self.TARGETS[name]
        return Vector2(SCREEN_WIDTH * ratio_x, SCREEN_HEIGHT * ratio_y)

    def warn_target(self, name, duration=0.8):
        self.close_target()
        if name not in self.target_states:
            raise ValueError(f"Alvo desconhecido: {name}")
        self.active_target = name
        self.target_states[name] = "warning"
        self.target_warning = duration

    def open_target(self, name):
        self.warn_target(name, 0.0)
        self.target_states[name] = "open"

    def close_target(self):
        if self.active_target is not None:
            self.target_states[self.active_target] = "closed"
        self.active_target = None
        self.target_warning = 0.0

    def open_target_at(self, point):
        if self.active_target is None or self.target_states[self.active_target] != "open":
            return None
        if self.target_position(self.active_target).distance_to(point) <= self.config.target_radius:
            return self.active_target
        return None

    def take_missile_hit(self, target, armed=True):
        if (self.defeated or not armed or target != self.active_target
                or self.target_states.get(target) != "open"):
            return False
        self.target_states[target] = "hit"
        self.hit_flash_target = target
        self.hit_flash_remaining = 0.20
        self.health = max(0, self.health - 1)
        self.damage_flash = 0.15
        EventBus.emit(Events.BOSS_DAMAGED, self, self.health, target)
        self.close_target()
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
            font = pygame.font.Font(None, 72)
            alert = font.render("ALERTA", True, "#ff3344")
            screen.blit(alert, alert.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * .45)))
        if self.active_target is not None:
            state = self.target_states[self.active_target]
            if state in ("warning", "open"):
                center = self.target_position(self.active_target)
                visible = state == "open" or int(self.target_warning * 10) % 2 == 0
                if visible:
                    color = "#ffffff" if state == "open" else "#f9c22b"
                    pygame.draw.circle(screen, color, center, int(self.config.target_radius), 5)
                    pygame.draw.circle(screen, "#ae2334", center, 14)
        if self.hit_flash_target is not None:
            pygame.draw.circle(screen, "white", self.target_position(self.hit_flash_target),
                               int(self.config.target_radius + 12), 8)
        if self.defeated:
            for index in range(min(5, int(self.defeat_elapsed / .18) + 1)):
                angle = index * 137.5
                radius = 45 + index * 23
                point = self.position + Vector2(radius, 0).rotate(angle)
                size = 18 + int(8 * abs(math.sin(self.defeat_elapsed * 15 + index)))
                pygame.draw.circle(screen, "#f9c22b", point, size)
            if self.defeat_elapsed > 1.1:
                pygame.draw.circle(screen, "white", self.position, int(45 + self.defeat_elapsed * 25), 8)
