"""Catálogo de inimigos e rodadas por ambiente; coordenadas relativas à resolução."""
from functools import partial

from pygame import Vector2

from enemys.attacks import VolleyAttack
from enemys.drone_enemy import DroneEnemy
from enemys.gaivota_enemy import GaivotaEnemy
from entities.enemy import Enemy
from enemys.patterns.charge import Charge
from enemys.patterns.move_to import MoveTo
from enemys.patterns.wait import Wait
from enemys.waves import EnemyRegistry, EnemySpawn, Wave
from game_consts import SCREEN_HEIGHT as H, SCREEN_WIDTH as W
from util.resources import load_image, load_sound


def get_enemy_registry():
    registry = EnemyRegistry()
    for name, enemy_type in (("drone", DroneEnemy), ("gaivota", GaivotaEnemy), ("asteroid", Enemy)):
        # As ondas fornecem seus próprios movimentos; não carregar o TMJ legado.
        registry.register(name, partial(enemy_type, patterns=[]))
        load_image(enemy_type.DEFAULT_SPRITESHEET)
        if enemy_type.DEFAULT_SFX_PATH:
            load_sound(enemy_type.DEFAULT_SFX_PATH)
    return registry


def formation_path(slot, count, layout, duration, charge_speed=1800):
    column, row = slot % 6, slot // 6
    x = W * (.10 + column * .16)
    y = H * (.16 + row * .16)
    if layout == "v":
        y += abs(column - 2.5) * H * .045
    elif layout == "diagonal":
        y += column * H * .035
    start = Vector2(x, -160 - row * 150)
    anchor = Vector2(x, y)
    side = -1 if slot % 2 else 1
    sweep = Vector2(max(100, min(W - 100, x + side * W * .12)), y + H * .08)
    if layout == "pincer":
        start = Vector2(-160 if column < 3 else W + 160, y)
    elif layout == "cross":
        sweep = Vector2(W - x, y + H * .14)
    elif layout == "dive":
        sweep = Vector2(W - x, H * .62)
    if layout == "charge":
        return [MoveTo(start, anchor, 1.4), Wait(anchor, 1 + slot * .22),
                Charge(anchor, speed=charge_speed)]
    return [MoveTo(start, anchor, 2), Wait(anchor, duration * .3),
            MoveTo(anchor, sweep, duration * .35),
            MoveTo(sweep, anchor, duration * .35),
            MoveTo(anchor, Vector2(x, H + 180), 3)]


def make_wave(name, layout, species, count, duration, interval, speed, angles, aimed, charge_speed=1800):
    return Wave(name, tuple(
        EnemySpawn(species[i % len(species)],
                   partial(formation_path, i, count, layout, duration, charge_speed),
                   partial(VolleyAttack, interval, speed, angles, aimed, 3 + i * .11)
                   if species[i % len(species)] == "drone" else no_attack)
        for i in range(count)
    ))


def no_attack():
    return None


def launch_waves():
    return ()


def stratosphere_waves():
    return (
        make_wave("Bando em V", "v", ("gaivota",), 12, 10, 2, 360, (0,), False),
        make_wave("Chuva de asteroides", "diagonal", ("asteroid",), 18, 8, 2, 360, (0,), False),
        make_wave("Gaivotas em investida", "charge", ("gaivota",), 18, 10, 2, 360, (0,), True, 1900),
    )


def near_space_waves():
    return (
        make_wave("Cerco orbital", "pincer", ("drone",), 18, 16, 1.6, 400, (-10, 10), True),
        make_wave("Intercepcao veloz", "charge", ("drone",), 12, 12, 1.8, 430, (0,), True, 2100),
        make_wave("Orbitas cruzadas", "cross", ("drone",), 18, 16, 1.5, 430, (-25, 0, 25), False),
    )


def deep_space_waves():
    return (
        make_wave("Patrulha distante", "diagonal", ("drone",), 18, 14, 1.5, 430, (-12, 12), True),
        make_wave("Ataque de ruptura", "charge", ("drone",), 18, 12, 1.6, 450, (0,), True, 2300),
        make_wave("Cerco profundo", "pincer", ("drone",), 18, 18, 1.4, 440, (-20, 0, 20), False),
    )


def mars_orbit_waves():
    # Escolta disponível; nave-mãe será integrada quando seu inimigo existir.
    return (
        make_wave("Escolta de Marte", "v", ("drone",), 18, 16, 1.4, 450, (-15, 15), True),
        make_wave("Investida da escolta", "charge", ("drone",), 18, 12, 1.5, 470, (0,), True, 2500),
        make_wave("Ultimo bloqueio", "cross", ("drone",), 18, 20, 1.4, 450, (-18, 0, 18), True),
    )
