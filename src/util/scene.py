from typing import overload

from entities.enemy import Enemy
from entities.entity import Entity
from entities.player import Player
from events.event_bus import EventBus
from events.events import Events
from system.system import System
from ui.ui import UI


class Scene:
    def __init__(self, game_scene: bool):
        self.entities: list[Entity] = []
        self.ui_items: list[UI] = []
        self.systems: dict[str, System] = {}
        self.blackboard: dict[str, Entity] = {}
        self.player: Player
        self.enemys: list[Enemy] = []
        self.game_scene = game_scene

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
            if et.to_destroy:
                self.entities.remove(et)
                continue

            et.update(delta)

        if self.game_scene:
            self.check_collisions()

        for item in self.ui_items:
            if item.to_destroy:
                self.ui_items.remove(item)
                continue

            item.update(delta, events)
            
        for et in self.entities:
            et.draw(screen)        

        for item in self.ui_items:
            item.draw(screen)

    def check_collisions(self):
        if self.player is None:
            return

        colliding_enemys: list[Enemy] = []
        for enemy in self.enemys:
            if not enemy.visible:
                continue

            if self.player.collide_with(enemy):
                colliding_enemys.append(enemy)

        if len(colliding_enemys) > 0:
            EventBus.emit(Events.PLAYER_COLLIDE, self.player, colliding_enemys)

    def clear_scene(self):
        self.entities.clear()
        self.player = None
        self.enemys.clear()
        self.ui_items.clear()
        self.blackboard.clear()

    def destroy_entity(self, name: str):
        item = self.blackboard.pop(name, None)
        if item is None:
            return

        if isinstance(item, UI):
            self.ui_items.remove(item)
        else:
            self.entities.remove(item)

            if item is self.player:
                self.player = None
            if isinstance(item, Enemy):
                self.enemys.remove(item)