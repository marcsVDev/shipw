from entities.enemy import Enemy
from entities.player import Player
from initializations.scenery import get_earth_scenery, get_satellite_scenery
from util.phase import Phase

def minutes(s): return s * 60

START_TIMES = [0, minutes(0.5), minutes(0.5)]

def get_launch_phase():
    return Phase(
        "Estação Krasny Mir",
        START_TIMES[0],
        START_TIMES[1],
        [
            Player(),
            Enemy(),
            get_earth_scenery(),
            get_satellite_scenery()
        ]
    )

def get_troposphere_phase():
    return Phase(
        "Troposfera",
        START_TIMES[1],
        START_TIMES[2],
        [
            Player()
        ]
    )

def get_phases()-> list[Phase]:
    return [
        get_launch_phase(),
        get_troposphere_phase()
    ]