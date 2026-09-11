from entities.player import Player
from initializations.enemy_waves import (
    stratosphere_waves, near_space_waves, deep_space_waves, mars_orbit_waves,
)
from initializations.scenery import (
    get_krasny_mir_background, get_estratosfera_background,
    get_espaco_proximo_background,
)
from initializations.ui_inits import get_scene_title
from ui.ui import UI
from initializations.misc import get_font
from util.phase import Phase


def get_launch_phase():
    return Phase("Estação Krasny Mir", 0, 5, {
        "title": get_scene_title("Estacao Krasny Mir"),
        "background": get_krasny_mir_background(), "player": Player(),
    }, free_movement=False)


def get_estratosfera_phase():
    return Phase("Estratosfera", 0, 0, {
        "title": get_scene_title("Estratosfera"),
        "background": get_estratosfera_background(), "player": Player(),
    }, waves=stratosphere_waves())


def get_espaco_proximo_phase():
    return Phase("Espaço Próximo", 0, 0, {
        "title": get_scene_title("Espaco Proximo"),
        "background": get_espaco_proximo_background(), "player": Player(),
    }, waves=near_space_waves(), planned_enemies=("buran",))


def get_espaco_profundo_phase():
    return Phase("Espaço Profundo", 0, 0, {
        "title": get_scene_title("Espaco Profundo"),
        "background": get_espaco_proximo_background(), "player": Player(),
    }, waves=deep_space_waves(), planned_enemies=("novos_drones", "alienigena"))


def get_orbita_marte_phase():
    return Phase("Órbita de Marte", 0, 0, {
        "title": get_scene_title("Orbita de Marte"),
        "background": get_espaco_proximo_background(), "player": Player(),
    }, waves=mars_orbit_waves(), planned_enemies=("nave_mae",))


def get_mars_arrival_phase():
    # Tela final provisória: não inventa um cenário de Marte sem arte disponível.
    message = get_font(32).render("Valentina sobreviveu. Destino: Marte.", True, (255, 220, 170))
    return Phase("Chegada a Marte", 0, 5, {
        "title": get_scene_title("Chegada a Marte"),
        "message": UI(message, (550, 400)), "player": Player(),
    }, free_movement=False)


def get_phases() -> list[Phase]:
    return [get_launch_phase(), get_estratosfera_phase(), get_espaco_proximo_phase(),
            get_espaco_profundo_phase(), get_orbita_marte_phase(), get_mars_arrival_phase()]
