import math

import pygame

from game_consts import SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


class HealthBar(UI):
    WIDTH = 360
    HEIGHT = 34
    MARGIN = 36

    def __init__(self, run_state):
        super().__init__(position=(self.MARGIN, self.MARGIN))
        self.run_state = run_state
        self.font = get_font(24)
        self.elapsed = 0.0
        self.label = self.font.render("VALENTINA", True, "white")
        self._health = None
        self.value = None
        self.fill = None
        self._rebuild()

    def _rebuild(self):
        self._health = self.run_state.health
        self.value = self.font.render(
            f"{self.run_state.health}/{self.run_state.max_health}", True, "white"
        )
        ratio = self.run_state.health / self.run_state.max_health
        color = "#5ac54f" if ratio > .5 else "#f9c22b" if ratio > .2 else "#ae2334"
        self.fill = None
        if ratio > 0:
            self.fill = pygame.Surface(
                (max(1, int((self.WIDTH - 6) * ratio)), self.HEIGHT - 6),
                pygame.SRCALPHA,
            )
            self.fill.fill(color)

    def update(self, delta, events):
        self.elapsed += max(0.0, delta)
        if self._health != self.run_state.health:
            self._rebuild()

    def draw(self, screen):
        x, y = map(int, self.position)
        screen.blit(self.label, (x, y - 1))
        bar_x = x + 145
        rect = pygame.Rect(bar_x, y, self.WIDTH, self.HEIGHT)
        pygame.draw.rect(screen, (12, 18, 28), rect)
        if self.fill is not None:
            alpha = 255
            if self.run_state.health == 1:
                alpha = int(178 + 77 * (0.5 + 0.5 * math.sin(self.elapsed * 7)))
            self.fill.set_alpha(alpha)
            screen.blit(self.fill, (bar_x + 3, y + 3))
        pygame.draw.rect(screen, "white", rect, 3)
        screen.blit(self.value, (rect.right + 12, y - 1))


class BossHealthBar(UI):
    def __init__(self, boss):
        super().__init__()
        self.boss = boss
        self.font = get_font(26)
        self.label = self.font.render("NAVE-MÃE", True, "white")
        self._health = None
        self.value = None

    def update(self, delta, events):
        if self._health != self.boss.health:
            self._health = self.boss.health
            self.value = self.font.render(
                f"{self.boss.health}/{self.boss.max_health}", True, "white"
            )

    def draw(self, screen):
        if self.boss.to_destroy or not self.boss.health_bar_visible:
            return
        width, height = 520, 32
        x, y = (SCREEN_WIDTH - width) // 2, 330
        screen.blit(self.label, (x - self.label.get_width() - 18, y - 2))
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (12, 18, 28), rect)
        ratio = self.boss.health / self.boss.max_health
        color = "white" if self.boss.damage_flash > 0 else "#ae2334"
        if ratio > 0:
            pygame.draw.rect(screen, color,
                             (x + 3, y + 3, int((width - 6) * ratio), height - 6))
        pygame.draw.rect(screen, "white", rect, 3)
        if self.value is None:
            self.update(0, ())
        screen.blit(self.value, (rect.right + 12, y - 2))
