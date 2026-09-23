from entities.player import Player
from initializations.enemy_waves import (
    stratosphere_waves, near_space_waves, deep_space_waves,
)
from initializations.scenery import (
    get_krasny_mir_background, get_estratosfera_background,
    get_espaco_proximo_background, get_earth_scenery, get_krasny_mir_launch_animation,
    get_stratosphere_exit_animation, get_mars_arrival_animation,
)
from initializations.ui_inits import get_dialogue_panel, get_launch_button, get_scene_title
from events.event_bus import EventBus
from events.events import Events
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
    title = get_scene_title("Estacao Krasny Mir")

    def start_launch():
        title.visible = False
        launch_animation.run()

    phase.default_entities.update({
        "background": get_krasny_mir_background(),
        "launch_animation": launch_animation,
        "title": title,
        "launch_button": get_launch_button(start_launch),
        "dialogue": get_dialogue_panel(1),
    })
    return phase


def get_estratosfera_phase(run_state=None):
    phase = Phase("Estratosfera", 0, 0, {
        "title": get_scene_title("Estratosfera"),
        "background": get_estratosfera_background(), "player": Player(run_state),
        "dialogue": get_dialogue_panel(2),
    }, waves=stratosphere_waves())
    phase.exit_cutscene = get_stratosphere_exit_animation(
        lambda: EventBus.emit(Events.PHASE_COMPLETED, phase))
    phase.default_entities["exit_cutscene"] = phase.exit_cutscene
    return phase


def get_espaco_proximo_phase(run_state=None):
    return Phase("Espaço Próximo", 0, 0, {
        "title": get_scene_title("Espaco Proximo"),
        "background": get_espaco_proximo_background(), "earth": get_earth_scenery(),
        "player": Player(run_state),
        "dialogue": get_dialogue_panel(3),
    }, waves=near_space_waves())


def get_espaco_profundo_phase(run_state=None):
    return Phase("Espaço Profundo", 0, 0, {
        "title": get_scene_title("Espaco Profundo"),
        "background": get_espaco_proximo_background(), "player": Player(run_state),
        "dialogue": get_dialogue_panel(4),
    }, waves=deep_space_waves())


def get_orbita_marte_phase(run_state=None):
    return Phase("Órbita de Marte", 0, 0, {
        "title": get_scene_title("Orbita de Marte"),
        "background": get_espaco_proximo_background(), "player": Player(run_state),
        "dialogue": get_dialogue_panel(5),
    }, boss_fight=True)


def get_mars_arrival_phase(run_state=None):
    landing_dialogue = get_dialogue_panel("6_landing", lambda: EventBus.emit(Events.PHASE_COMPLETED, phase))
    landing_dialogue.visible = False
    phase = Phase("Chegada a Marte", 0, 1, {
        "title": get_scene_title("Chegada a Marte"),
        "player": Player(run_state),
        "dialogue": get_dialogue_panel(6),
        "landing_dialogue": landing_dialogue,
    }, free_movement=False)
    phase.exit_cutscene = get_mars_arrival_animation(
        lambda: setattr(landing_dialogue, "visible", True))
    phase.default_entities["exit_cutscene"] = phase.exit_cutscene
    return phase


def get_phases(run_state=None) -> list[Phase]:
    return [get_launch_phase(run_state), get_estratosfera_phase(run_state),
            get_espaco_proximo_phase(run_state), get_espaco_profundo_phase(run_state),
            get_orbita_marte_phase(run_state), get_mars_arrival_phase(run_state)]
