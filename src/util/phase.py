from xml.dom.minidom import Entity


class Phase:
    def __init__(self, name, starts_at, duration, default_entities: list[Entity]):
        self.name: str = name
        self.starts_at: float = starts_at
        self.duration: float = duration
        self.default_entities: list[Entity] = default_entities