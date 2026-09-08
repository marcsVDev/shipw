"""Descrições imutáveis: factories sempre criam comportamentos independentes."""
from collections.abc import Callable
from dataclasses import dataclass

from enemys.enemy_pattern import EnemyPattern


@dataclass(frozen=True)
class EnemySpawn:
    enemy: str
    movement: Callable[[], list[EnemyPattern]]
    attack: Callable


@dataclass(frozen=True)
class Wave:
    name: str
    spawns: tuple[EnemySpawn, ...]
    rest: float = 2.0

    def __post_init__(self):
        if not self.spawns or self.rest < 0:
            raise ValueError("Uma onda precisa de inimigos e intervalo não negativo")


class EnemyRegistry:
    def __init__(self):
        self._factories = {}

    def register(self, name, factory):
        if name in self._factories:
            raise ValueError(f"Inimigo já registrado: {name}")
        self._factories[name] = factory

    def create(self, spawn: EnemySpawn, target=None):
        if spawn.enemy not in self._factories:
            raise ValueError(f"Inimigo desconhecido: {spawn.enemy}")
        patterns = spawn.movement()
        for pattern in patterns:
            pattern.bind_target(target)
        return self._factories[spawn.enemy]().configure(patterns, spawn.attack())
