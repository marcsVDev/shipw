from typing import Callable

import pygame

from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH, UI_PATH
from ui.button import Button
from ui.dialogue_panel import DialoguePanel
from ui.scene_title import SceneTitle

DIALOGUEPANEL_PATH = UI_PATH + "dialogue_panel.png"
DIALOGUES_P = [
    "E ai boi?",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA QUE DIALOGO GOSTOSO"
    ]

def get_dialogue_panel() -> DialoguePanel:
    return DialoguePanel(pygame.image.load(DIALOGUEPANEL_PATH).convert_alpha(), DIALOGUES_P)

def get_scene_title(title: str) -> SceneTitle:
    return SceneTitle(title)

PLAY_BUTTON_PATH = UI_PATH + "play.png"

def get_play_button(callable: Callable) -> Button:
    M = 5
    SCALE = 64 * M
    image = pygame.image.load(PLAY_BUTTON_PATH).convert_alpha()
    image = pygame.transform.scale_by(image, M)

    return Button(image, pygame.Vector2(SCREEN_WIDTH//2-SCALE//2, SCREEN_HEIGHT//2-SCALE//2), SCALE, callable, (58*5, 21*5))