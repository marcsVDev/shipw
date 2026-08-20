from pygame import Rect, Surface, Vector2
import pygame

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


class DialoguePanel(UI):
    MULTIPLIER = 8
    SCALE = (128 * MULTIPLIER, 64 * MULTIPLIER)
    POSITION = Vector2(SCREEN_WIDTH//2 - SCALE[0]//2, SCREEN_HEIGHT - SCALE[1] - 50)
    FONT_COLOR = (0, 0, 0)
    FONT_SIZE = 40
    TEXT_CHARACTERS_PER_SECOND = 40

    DIALOGUE_AREA = Rect(6 * MULTIPLIER + POSITION.x, 6 * MULTIPLIER + POSITION.y, 74 * MULTIPLIER, 51 * MULTIPLIER)
    PICTURE_AREA = Rect(93 * MULTIPLIER + POSITION.x, 9 * MULTIPLIER + POSITION.y, 25 * MULTIPLIER, 29 * MULTIPLIER)
    NAME_POSITION = Vector2(106 * MULTIPLIER + POSITION.x, 49 * MULTIPLIER + POSITION.y)

    def __init__(self, image: Surface, _, dialogues: list[str]):
        self.dialogues: list[str] = dialogues
        self.pressed = False
        self.current_dialogue = 0
        self.visible_characters = 0.0
        self.font = get_font(self.FONT_SIZE)
        self._wrapped_dialogues = [
            self.wrap_text(dialogue)
            for dialogue in self.dialogues
        ]
        self._dialogue_characters_count = [
            sum(len(line) for line in dialogue_lines)
            for dialogue_lines in self._wrapped_dialogues
        ]
        self._visible_dialogue_surfaces: list[Surface] = []
        self.render_visible_text()

        super().__init__(image, self.POSITION)

        self.scale(self.SCALE)
        self.align_rect()

    def update(self, delta, events):
        if not self.visible: return
        self.animate_text(delta)

        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_SPACE]:
            self.next_dialogue()
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:                
                    self.pressed = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:                
                    self.next_dialogue()

                    self.pressed = False
                

        return super().update(delta, events)
    
    def draw(self, screen):
        if not self.visible: return

        screen.blit(self._image, (self.position.x, self.position.y))

        y = self.DIALOGUE_AREA.y
        for line_surface in self._visible_dialogue_surfaces:
            if y + line_surface.get_height() > self.DIALOGUE_AREA.bottom:
                break

            screen.blit(line_surface, (self.DIALOGUE_AREA.x, y))
            y += line_surface.get_height()

        pygame.draw.circle(screen, (0xff,0xff,0xff), self.NAME_POSITION, 1)
        pygame.draw.rect(screen, (0xFF, 0, 0), self.PICTURE_AREA, 1)
        return super().draw(screen)

    def scale(self, by):
        self._image = pygame.transform.scale(self._image, by)

    def align_rect(self):
        self._rect = self._image.get_rect(center=self.position)

    def wrap_text(self, text: str) -> list[str]:
        lines: list[str] = []

        for paragraph in text.splitlines() or [""]:
            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}".strip()
                if self.font.size(candidate)[0] <= self.DIALOGUE_AREA.width:
                    line = candidate
                    continue

                if line:
                    lines.append(line)
                    line = ""

                while self.font.size(word)[0] > self.DIALOGUE_AREA.width:
                    fitting = ""
                    for character in word:
                        if self.font.size(fitting + character)[0] > self.DIALOGUE_AREA.width:
                            break
                        fitting += character

                    lines.append(fitting)
                    word = word[len(fitting):]

                line = word

            lines.append(line)

        return lines

    def animate_text(self, delta: float):
        previous_visible_characters = int(self.visible_characters)
        dialogue_characters_count = self._dialogue_characters_count[self.current_dialogue]
        self.visible_characters = min(
            self.visible_characters + self.TEXT_CHARACTERS_PER_SECOND * delta,
            dialogue_characters_count,
        )

        if int(self.visible_characters) > previous_visible_characters:
            # TODO: SFX
            self.render_visible_text()

    def render_visible_text(self):
        remaining_characters = int(self.visible_characters)
        self._visible_dialogue_surfaces = []

        for line in self._wrapped_dialogues[self.current_dialogue]:
            if remaining_characters <= 0:
                break

            visible_line = line[:remaining_characters]
            self._visible_dialogue_surfaces.append(
                self.font.render(visible_line, True, self.FONT_COLOR)
            )
            remaining_characters -= len(line)

    def next_dialogue(self):
        if self.visible_characters < self._dialogue_characters_count[self.current_dialogue]:
            self.visible_characters = self._dialogue_characters_count[self.current_dialogue]
            self.render_visible_text()
            return

        if self.current_dialogue + 1 < len(self.dialogues):
            self.current_dialogue += 1
            self.visible_characters = 0.0
            self.render_visible_text()
        else:
            self.current_dialogue = 0
            self.visible_characters = 0.0
            self.render_visible_text()
            self.visible = False 
