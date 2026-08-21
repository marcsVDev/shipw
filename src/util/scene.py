from typing import overload

from entities.enemy import Enemy
from entities.entity import Entity
from entities.player import Player
from events.event_bus import EventBus
from events.events import Events
from system.system import System
from ui.ui import UI


class Scene:
    def __init__(self):
        self.entities: list[Entity] = []
        self.ui_items: list[UI] = []
        self.systems: dict[str, System] = {}
        self.blackboard: dict[str, Entity] = {}
        self.player: Player
        self.enemys: list[Enemy] = []

    @overload
    def add_entity(self, entity: Entity) -> None: ...

    @overload
    def add_entity(self, entity: Entity, blackboard_name: str) -> None: ...

    def add_entity(self, entity: Entity, blackboard_name: str | None = None) -> None:
        self.entities.append(entity)

        if isinstance(entity, Player):
            self.player = entity
        elif isinstance(entity, Enemy):
            self.enemys.append(entity)

        if blackboard_name is not None:
            self.blackboard[blackboard_name] = entity

    def get_entity[T](self, entity_name: str, et: type[T]) -> T:
        return self.blackboard[entity_name] 

    @overload
    def add_ui(self, ui: UI) -> None: ...

    @overload
    def add_ui(self, ui: UI, blackboard_name: str) -> None: ...

    def add_ui(self, ui: UI, blackboard_name: str | None = None) -> None:
        self.ui_items.append(ui)

        if blackboard_name is not None:
            self.blackboard[blackboard_name] = ui

    def add_system(self, sys_name: str, sys: System):
        self.systems[sys_name] = sys

    def get_system[T](self, sys_name: str, sys: type[T]) -> T:
        return self.systems.get(sys_name)

    def run(self, screen, delta, events):
        for system in self.systems.values():
            system.update(delta)

        for et in self.entities:
            et.update(delta)

        self.check_collisions()

        for item in self.ui_items:
            item.update(delta, events)
            
        for et in self.entities:
            et.draw(screen)        

        for item in self.ui_items:
            item.draw(screen)

    def check_collisions(self):
        colliding_enemys: list[Enemy] = []
        for enemy in self.enemys:
            if not enemy.visible:
                continue

            if self.player.collide_with(enemy):
                colliding_enemys.append(enemy)

        if len(colliding_enemys) > 0:
            EventBus.emit(Events.PLAYER_COLLIDE, colliding_enemys)

    def clear_scene(self):
        self.entities = []
        self.player = None
        self.enemys = []
        self.ui_items = []
        self.blackboard = {}

