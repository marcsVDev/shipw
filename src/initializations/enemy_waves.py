"""Catálogo de inimigos e rodadas por ambiente; coordenadas relativas à resolução."""
from functools import partial

from pygame import Vector2

from enemys.attacks import AttractionAttack
from enemys.drone_enemy import DroneEnemy
from enemys.gaivota_enemy import GaivotaEnemy
from enemys.mine_enemy import MineEnemy
from entities.enemy import Enemy
from enemys.patterns.charge import Charge
from enemys.patterns.fly_by import FlyBy
from enemys.patterns.move_to import MoveTo
from enemys.patterns.wait import Wait
from enemys.waves import EnemyRegistry, EnemySpawn, Wave
from game_consts import SCREEN_HEIGHT as H, SCREEN_WIDTH as W
from util.resources import load_image, load_sound


def get_enemy_registry():
    registry = EnemyRegistry()
    for name, enemy_type in (("drone", DroneEnemy), ("gaivota", GaivotaEnemy),
                             ("asteroid", Enemy), ("mine", MineEnemy)):
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


def fly_by_path(slot, count, axis, speed=2200):
    lane = slot % max(1, min(count, 10))
    reverse = slot % 2 == 1
    if axis == "horizontal":
        y = H * (.09 + lane * .09)
        start, end = Vector2(-180, y), Vector2(W + 180, y)
    elif axis == "vertical":
        x = W * (.06 + lane * .098)
        start, end = Vector2(x, -180), Vector2(x, H + 180)
    else:
        raise ValueError(f"Eixo de passagem desconhecido: {axis}")
    if reverse:
        start, end = end, start
    return [FlyBy(start, end, speed + (slot % 3) * 140)]


def enemy_path(enemy, slot, count, layout, duration, charge_speed):
    if layout in ("horizontal", "vertical"):
        return fly_by_path(slot, count, layout, charge_speed)
    path = formation_path(slot, count, layout, duration, charge_speed)
    if enemy in ("drone", "gaivota") and layout != "charge":
        # O único ataque desses inimigos é a investida contra o jogador.
        last_position = path[-1].position.copy()
        path[-1] = Charge(last_position, speed=charge_speed)
    return path


def make_wave(name, layout, species, count, duration, charge_speed=1800):
    return Wave(name, tuple(
        EnemySpawn(enemy := species[i % len(species)],
                   partial(enemy_path, enemy, i, count, layout, duration, charge_speed),
                   partial(AttractionAttack, 2600, 720, 90) if enemy == "mine" else no_attack)
        for i in range(count)
    ))


def no_attack():
    return None


def launch_waves():
    return ()


def stratosphere_waves():
    return (
        make_wave("Bando em V", "v", ("gaivota",), 12, 10, 1900),
        make_wave("Chuva de asteroides", "diagonal", ("asteroid",), 18, 8),
        make_wave("Gaivotas em investida", "charge", ("gaivota",), 18, 10, 1900),
    )


def near_space_waves():
    return (
        make_wave("Cerco orbital", "pincer", ("drone",), 18, 16, 2100),
        make_wave("Intercepcao veloz", "charge", ("drone",), 12, 12, 2100),
        make_wave("Corte horizontal", "horizontal", ("drone",), 18, 16, 2250),
    )


def deep_space_waves():
    return (
        make_wave("Campo gravitacional", "diagonal", ("mine", "drone"), 18, 14, 2300),
        make_wave("Ataque de ruptura", "charge", ("drone",), 18, 12, 2300),
        make_wave("Queda vertical", "vertical", ("mine", "drone"), 18, 18, 2150),
    )


def mars_orbit_waves():
    # Escolta disponível; nave-mãe será integrada quando seu inimigo existir.
    return (
        make_wave("Escolta de Marte", "v", ("drone",), 18, 16, 2500),
        make_wave("Investida da escolta", "charge", ("drone",), 18, 12, 2500),
        make_wave("Ultimo bloqueio", "horizontal", ("drone",), 18, 20, 2500),
    )
