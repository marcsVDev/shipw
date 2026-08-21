import pygame

from game_consts import UI_PATH
from ui.dialogue_panel import DialoguePanel
from ui.scene_title import SceneTitle

DIALOGUEPANEL_PATH = UI_PATH + "dialogue_panel.png"
DIALOGUES_P = [
    "ARRUMA A BOSTA DAS AREAS AI", 
    "TO FALANO MEU",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA QUE DIALOGO GOSTOSO"
    ]

def get_dialogue_panel() -> DialoguePanel:
    return DialoguePanel(pygame.image.load(DIALOGUEPANEL_PATH).convert_alpha(), DIALOGUES_P)



def get_scene_title(title: str) -> SceneTitle:
    return SceneTitle(title)