from ui.ui import UI


class DialoguePanel(UI):
    def __init__(self, image, position, dialogues: list[str]):
        self.dialogues: list[str] = dialogues
        super().__init__(image, position)

    def update(self, delta, events):
        return super().update(delta, events)
    
    def draw(self, screen):
        return super().draw(screen)
