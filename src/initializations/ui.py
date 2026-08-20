import pygame

from game_consts import UI_PATH
from ui.dialogue_panel import DialoguePanel

DIALOGUEPANEL_PATH = UI_PATH + "dialogue_panel.png"
DIALOGUES_P = [
    "ARRUMA A BOSTA DAS AREAS AI", 
    "TO FALANO MEU",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA QUE DIALOGO GOSTOSO"
    ]

def get_dialogue_panel() -> DialoguePanel:
    return DialoguePanel(pygame.image.load(DIALOGUEPANEL_PATH).convert_alpha(), pygame.Vector2(0, 0), DIALOGUES_P)