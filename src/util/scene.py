from entities.enemy import Enemy
from entities.entity import Entity
from entities.player import Player
from events.event_bus import EventBus
from events.events import Events
from ui.ui import UI


class Scene:
    def __init__(self):
        self.entities: list[Entity] = []
        self.ui_items: list[UI] = []
        self.blackboard: dict[str, Entity] = {}
        self.player: Player
        self.enemys: list[Enemy] = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

        if isinstance(entity, Player):
            self.player = entity
        elif isinstance(entity, Enemy):
            self.enemys.append(entity)


    def add_entity_blackboarded(self, entity: Entity, blackboard_name: str):
        self.entities.append(entity)
        self.blackboard[blackboard_name] = entity

    def get_blackboard_entity[T](self, blackboard_name: str, entity_type: type[T]) -> T:
        return self.blackboard.get(blackboard_name)

    def add_ui_item(self, ui: UI):
        self.ui_items.append(ui)

    def add_ui_blackboarded(self, ui: UI, blackboard_name: str):
        self.ui_items.append(ui)
        self.blackboard[blackboard_name] = ui

    def run(self, screen, delta, events):
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