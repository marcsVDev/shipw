from dataclasses import dataclass

import pygame
from pygame import Rect, Surface, Vector2

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.misc import get_font
from ui.ui import UI


@dataclass(frozen=True)
class DialogueEntry:
    speaker: str
    text: str
    portrait: Surface | None = None


@dataclass(frozen=True)
class DialoguePage:
    speaker: str
    lines: tuple[str, ...]
    portrait: Surface | None = None


class DialoguePanel(UI):
    MULTIPLIER = 8
    SCALE = (128 * MULTIPLIER, 64 * MULTIPLIER)
    POSITION = Vector2(
        SCREEN_WIDTH // 2 - SCALE[0] // 2,
        SCREEN_HEIGHT - SCALE[1] - 50,
    )
    FONT_COLOR = (238, 238, 238)
    FONT_SIZE = 34
    NAME_FONT_SIZE = 28
    TEXT_CHARACTERS_PER_SECOND = 40

    DIALOGUE_AREA = Rect(
        6 * MULTIPLIER + POSITION.x,
        6 * MULTIPLIER + POSITION.y,
        74 * MULTIPLIER,
        51 * MULTIPLIER,
    )
    PICTURE_AREA = Rect(
        93 * MULTIPLIER + POSITION.x,
        9 * MULTIPLIER + POSITION.y,
        25 * MULTIPLIER,
        29 * MULTIPLIER,
    )
    NAME_AREA = Rect(
        91 * MULTIPLIER + POSITION.x,
        44 * MULTIPLIER + POSITION.y,
        30 * MULTIPLIER,
        11 * MULTIPLIER,
    )

    def __init__(self, image: Surface, dialogues: list[DialogueEntry]):
        if not dialogues:
            raise ValueError("DialoguePanel precisa de pelo menos uma fala")

        super().__init__(image, self.POSITION)
        self.modal = True
        self.dialogues = dialogues
        self.pressed = False
        self.current_dialogue = 0
        self.visible_characters = 0.0
        self.font = get_font(self.FONT_SIZE)
        self.name_font = get_font(self.NAME_FONT_SIZE)
        self._pages = self._paginate(dialogues)
        self._dialogue_characters_count = [
            sum(len(line) for line in page.lines)
            for page in self._pages
        ]
        self._visible_dialogue_surfaces: list[Surface] = []
        self._portrait_cache: dict[int, Surface] = {}
        self.render_visible_text()

        self.scale_image(self.SCALE)

    @property
    def current_page(self) -> DialoguePage:
        return self._pages[self.current_dialogue]

    def update(self, delta, events):
        if not self.visible:
            return
        self.animate_text(delta)

        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_SPACE]:
            self.next_dialogue()
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                self.pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
                if self.pressed:
                    self.next_dialogue()
                self.pressed = False

    def draw(self, screen):
        if not self.visible:
            return

        super().draw(screen)

        y = self.DIALOGUE_AREA.y
        for line_surface in self._visible_dialogue_surfaces:
            screen.blit(line_surface, (self.DIALOGUE_AREA.x, y))
            y += self.font.get_linesize()

        portrait = self._get_scaled_portrait(self.current_page.portrait)
        if portrait is not None:
            portrait_rect = portrait.get_rect(center=self.PICTURE_AREA.center)
            screen.blit(portrait, portrait_rect)

        name_surface = self.name_font.render(
            self.current_page.speaker,
            True,
            self.FONT_COLOR,
        )
        name_rect = name_surface.get_rect(center=self.NAME_AREA.center)
        screen.blit(name_surface, name_rect)

    def _paginate(self, dialogues: list[DialogueEntry]) -> list[DialoguePage]:
        pages: list[DialoguePage] = []
        lines_per_page = max(1, self.DIALOGUE_AREA.height // self.font.get_linesize())

        for dialogue in dialogues:
            wrapped_lines = self.wrap_text(dialogue.text)
            for start in range(0, len(wrapped_lines), lines_per_page):
                pages.append(DialoguePage(
                    dialogue.speaker,
                    tuple(wrapped_lines[start:start + lines_per_page]),
                    dialogue.portrait,
                ))

        return pages

    def wrap_text(self, text: str) -> list[str]:
        lines: list[str] = []

        for paragraph in text.splitlines() or [""]:
            if not paragraph:
                lines.append("")
                continue

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
            self.render_visible_text()

    def render_visible_text(self):
        remaining_characters = int(self.visible_characters)
        self._visible_dialogue_surfaces = []

        for line in self.current_page.lines:
            if not line:
                self._visible_dialogue_surfaces.append(
                    self.font.render("", True, self.FONT_COLOR)
                )
                continue
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

        if self.current_dialogue + 1 < len(self._pages):
            self.current_dialogue += 1
            self.visible_characters = 0.0
            self.render_visible_text()
        else:
            self.visible = False

    def _get_scaled_portrait(self, portrait: Surface | None) -> Surface | None:
        if portrait is None:
            return None

        key = id(portrait)
        if key not in self._portrait_cache:
            scale = min(
                self.PICTURE_AREA.width / portrait.get_width(),
                self.PICTURE_AREA.height / portrait.get_height(),
            )
            size = (
                max(1, round(portrait.get_width() * scale)),
                max(1, round(portrait.get_height() * scale)),
            )
            self._portrait_cache[key] = pygame.transform.scale(portrait, size)
        return self._portrait_cache[key]
