from entities.entity import Entity
from enemys.waves import Wave


class Phase:
    def __init__(self, name, starts_at, duration, default_entities: dict[str, Entity], waves: tuple[Wave, ...] = (), free_movement=True, planned_enemies=(), boss_fight=False, auto_complete=True):
        self.name = name
        self.starts_at = starts_at
        self.duration = duration
        self.default_entities = default_entities
        self.waves = waves
        self.free_movement = free_movement
        self.planned_enemies = planned_enemies
        self.boss_fight = boss_fight
        self.auto_complete = auto_complete
