from enemys.drone_enemy import DroneEnemy
from enemys.gaivota_enemy import GaivotaEnemy
from entities.player import Player
from initializations.scenery import get_espaco_proximo_background, get_krasny_mir_background, get_satellite_scenery, get_earth_scenery, get_venus_scenery
from initializations.ui_inits import get_dialogue_panel, get_scene_title
from util.phase import Phase

def minutes(m): return m * 60

START_TIMES = [0, 1, 2]

def get_launch_phase():
    return Phase(
        "Estação Krasny Mir",
        START_TIMES[0],
        1,
        {
            "title": get_scene_title("Estacao Krasny Mir"),            
            "background": get_krasny_mir_background(),
            "drone": DroneEnemy(),
            "player": Player(),            
        }
    )

def get_estratosfera_phase():
    return Phase(
        "Estratosfera",
        START_TIMES[1],
        1,
        {
            "title": get_scene_title("Estratosfera"),            
            "earth": get_earth_scenery(),
            "gaivota": GaivotaEnemy(),
            "player": Player()
        }
    )
def get_espaco_proximo_phase():
    return Phase(
        "Espaço Próximo",
        START_TIMES[2],
        1,
        {
            "title": get_scene_title("Espaco Proximo"),
            "background": get_espaco_proximo_background(),
            "venus": get_venus_scenery(),
            "sat": get_satellite_scenery(),            
            "player": Player()
        }
    )

def get_phases() -> list[Phase]:
    return [
        get_launch_phase(),
        get_estratosfera_phase(),
        get_espaco_proximo_phase()
    ]
