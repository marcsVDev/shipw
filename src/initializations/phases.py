from entities.player import Player
from initializations.enemy_waves import (
    stratosphere_waves, near_space_waves, deep_space_waves,
)
from initializations.scenery import (
    get_krasny_mir_background, get_estratosfera_background,
    get_espaco_proximo_background, get_krasny_mir_launch_animation,
)
from initializations.ui_inits import get_launch_button, get_scene_title
from events.event_bus import EventBus
from events.events import Events
from ui.ui import UI
from initializations.misc import get_font
from util.phase import Phase


def get_launch_phase(run_state=None):
    phase = Phase(
        "Estação Krasny Mir",
        0,
        0,
        {},
        free_movement=False,
        auto_complete=False,
    )
    launch_animation = get_krasny_mir_launch_animation(
        lambda: EventBus.emit(Events.PHASE_COMPLETED, phase)
    )
    phase.default_entities.update({
        "background": get_krasny_mir_background(),
        "player": Player(run_state),
        "launch_animation": launch_animation,
        "title": get_scene_title("Estacao Krasny Mir"),
        "launch_button": get_launch_button(launch_animation.run),
    })
    return phase


def get_estratosfera_phase(run_state=None):
    return Phase("Estratosfera", 0, 0, {
        "title": get_scene_title("Estratosfera"),
        "background": get_estratosfera_background(), "player": Player(run_state),
    }, waves=stratosphere_waves())


def get_espaco_proximo_phase(run_state=None):
    return Phase("Espaço Próximo", 0, 0, {
        "title": get_scene_title("Espaco Proximo"),
        "background": get_espaco_proximo_background(), "player": Player(run_state),
    }, waves=near_space_waves(), planned_enemies=("buran",))


def get_espaco_profundo_phase(run_state=None):
    return Phase("Espaço Profundo", 0, 0, {
        "title": get_scene_title("Espaco Profundo"),
        "background": get_espaco_proximo_background(), "player": Player(run_state),
    }, waves=deep_space_waves())


def get_orbita_marte_phase(run_state=None):
    return Phase("Órbita de Marte", 0, 0, {
        "title": get_scene_title("Orbita de Marte"),
        "background": get_espaco_proximo_background(), "player": Player(run_state),
    }, boss_fight=True)


def get_mars_arrival_phase(run_state=None):
    # Tela final provisória: não inventa um cenário de Marte sem arte disponível.
    message = get_font(32).render("Valentina sobreviveu. Destino: Marte.", True, (255, 220, 170))
    return Phase("Chegada a Marte", 0, 5, {
        "title": get_scene_title("Chegada a Marte"),
        "message": UI(message, (550, 400)), "player": Player(run_state),
    }, free_movement=False)


def get_phases(run_state=None) -> list[Phase]:
    return [get_launch_phase(run_state), get_estratosfera_phase(run_state),
            get_espaco_proximo_phase(run_state), get_espaco_profundo_phase(run_state),
            get_orbita_marte_phase(run_state), get_mars_arrival_phase(run_state)]
