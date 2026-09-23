from dataclasses import dataclass

from events.event_bus import EventBus
from events.events import Events


@dataclass(frozen=True)
class PlayerHealthConfig:
    max_health: int = 3
    invulnerability_duration: float = 1.5
    blink_interval: float = 0.10
    knockback_speed: float = 420.0


class RunState:
    """Estado de uma campanha; não depende de Pygame nem de uma cena."""

    def __init__(self, config: PlayerHealthConfig = PlayerHealthConfig()):
        self.config = config
        self.max_health = config.max_health
        self.health = self.max_health
        self.is_game_over = False

    def reset(self):
        self.health = self.max_health
        self.is_game_over = False
        EventBus.emit(Events.RUN_RESET, self)

    def damage(self, amount: int = 1) -> bool:
        if amount <= 0 or self.is_game_over:
            return False
        previous = self.health
        self.health = max(0, self.health - amount)
        self.is_game_over = self.health == 0
        return self.health != previous
