from entity import Entity


class Scene:
    def __init__(self, entities = []):
        self.entities: list[Entity] = entities

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def run(self, screen, delta):
        for et in self.entities:
            et.update(delta)
            
        for et in self.entities:
            et.draw(screen)