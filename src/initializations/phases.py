from entities.player import Player
from initializations.scenery import get_krasny_mir_background, get_satellite_scenery
from initializations.ui_inits import get_dialogue_panel, get_scene_title
from util.phase import Phase

def minutes(m): return m * 60

START_TIMES = [0, 10, minutes(1)]

def get_launch_phase():
    return Phase(
        "Estação Krasny Mir",
        START_TIMES[0],
        START_TIMES[1],
        {            
            "title": get_scene_title("Estacao Krasny Mir"),
            "background": get_krasny_mir_background(),
            "player": Player(),
        }
    )

def get_troposphere_phase():
    return Phase(
        "Troposfera",
        START_TIMES[1],
        START_TIMES[2],
        {
            "title": get_scene_title("Troposfera"),
            "sat": get_satellite_scenery(),
            "dialogue": get_dialogue_panel(),
            "player": Player()
        }
    )

def get_phases() -> list[Phase]:
    return [
        get_launch_phase(),
        get_troposphere_phase()
    ]
