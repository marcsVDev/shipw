from entities.entity import Entity
from ui.ui import UI


class Scene:
    def __init__(self, entities = [], ui = []):
        self.entities: list[Entity] = entities
        self.ui_items: list[UI] = ui

    def add_entity(self, entity: Entity):
        self.entities.append(entity)
    def add_ui_item(self, ui: UI):
        self.ui_items.append(ui)

    def run(self, screen, delta, events): # ciclo: update : draw | entidades : UI
        for et in self.entities:
            et.update(delta)

        for item in self.ui_items:
            item.update(delta, events)
            
        for et in self.entities:
            et.draw(screen)        

        for item in self.ui_items:
            item.draw(screen)