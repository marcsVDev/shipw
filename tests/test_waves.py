import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from enemys.attacks import AttractionAttack, VolleyAttack
from enemys.mine_enemy import MineEnemy
from enemys.patterns.charge import Charge
from enemys.patterns.fly_by import FlyBy
from entities.enemy_projectile import EnemyProjectile
from events.event_bus import EventBus
from events.events import Events
from initializations.enemy_waves import get_enemy_registry, launch_waves, stratosphere_waves, near_space_waves, deep_space_waves, mars_orbit_waves
from system.wave_system import WaveSystem
from util.scene import Scene
from util.progresssion import Progression


class WavesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1920, 1080))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        EventBus.events.clear()

    def test_all_combat_waves_spawn_move_attack_and_finish(self):
        registry = get_enemy_registry()
        names = set()
        for waves in (stratosphere_waves(), near_space_waves(), deep_space_waves(), mars_orbit_waves()):
            scene = Scene(True)
            # Survival simulation isolates wave progression from player input.
            scene.player = SimpleNamespace(position=pygame.Vector2(960, 900), to_destroy=False)
            system = WaveSystem(scene, registry)
            phase = SimpleNamespace(waves=waves)
            started, completed = [], []
            on_start = lambda phase, index, wave: started.append((index, len(scene.enemys)))
            on_end = lambda phase: completed.append(phase)
            EventBus.connect(Events.WAVE_STARTED, on_start)
            EventBus.connect(Events.PHASE_COMPLETED, on_end)
            system.load_phase(phase)
            shot_count = 0
            for frame in range(4000):
                before = len(scene.entities)
                system.update(.05)
                shot_count += sum(isinstance(e, EnemyProjectile) for e in scene.entities[before:])
                for entity in tuple(scene.entities):
                    if not entity.to_destroy:
                        entity.update(.05)
                scene._remove_destroyed()
                if system.finished:
                    break
            self.assertTrue(system.finished)
            self.assertEqual([index for index, _ in started], [0, 1, 2])
            self.assertTrue(all(count >= 10 for _, count in started))
            self.assertEqual(shot_count, 0)
            self.assertEqual(completed, [phase])
            self.assertFalse(scene.enemys)
            self.assertFalse(EventBus.events.get(Events.GAME_STARTED))
            names.update(w.name for w in waves)
            EventBus.disconnect(Events.WAVE_STARTED, on_start)
            EventBus.disconnect(Events.PHASE_COMPLETED, on_end)
        self.assertEqual(len(names), 12)

    def test_movement_and_attack_state_is_not_shared(self):
        registry = get_enemy_registry()
        spawn = near_space_waves()[0].spawns[0]
        first, second = registry.create(spawn), registry.create(spawn)
        first.update(1)
        self.assertNotEqual(first.position, second.position)
        self.assertIsNot(first._patterns[0], second._patterns[0])
        first.destroy()
        second.destroy()

    def test_aim_and_projectile_collision_kill_player(self):
        from entities.player import Player
        scene = Scene(True)
        player = Player()
        player.update(0)
        scene.add_entity(player)
        enemy = SimpleNamespace(position=pygame.Vector2(960, 100))
        shots = []
        VolleyAttack(delay=0).update(enemy, player, .1, shots.append)
        self.assertGreater(shots[0].velocity.y, 0)
        scene.add_entity(EnemyProjectile(player.position, (0, 0)))
        scene.check_collisions()
        scene._remove_destroyed()
        self.assertIsNone(scene.player)
        self.assertNotIn(player.player_collide, EventBus.events[Events.PLAYER_COLLIDE])
        scene.clear_scene()

    def test_progression_requires_completion_and_finishes_once(self):
        progression = Progression()
        EventBus.emit(Events.GAME_STARTED)
        progression.update(1000)
        self.assertEqual(progression.phase_index, 0)
        completed = []
        EventBus.connect(Events.GAME_COMPLETED, lambda: completed.append(True))
        for phase in progression.phases:
            EventBus.emit(Events.PHASE_COMPLETED, phase)
        EventBus.emit(Events.PHASE_COMPLETED, progression.phases[-1])
        self.assertEqual(completed, [True])
        for phase in progression.phases:
            for entity in phase.default_entities.values():
                entity.destroy()

    def test_charge_locks_target_after_warning_and_crosses_it(self):
        from enemys.patterns.charge import Charge
        target = pygame.Vector2(500, 700)
        charge = Charge((500, 100), speed=2000, warning=.5)
        charge.bind_target(lambda: target)
        charge.update(.4)
        self.assertEqual(charge.position, pygame.Vector2(500, 100))
        self.assertTrue(charge.telegraphing)
        charge.update(.2)
        self.assertAlmostEqual(charge.position.y, 300)
        target.x = 1000
        charge.update(.3)
        self.assertAlmostEqual(charge.position.x, 500)
        self.assertGreater(charge.position.y, 700)
        charge.update(4)
        self.assertTrue(charge.finished)

    def test_phase_roster_and_non_combat_movement(self):
        from initializations.phases import get_phases
        from unittest.mock import patch
        phases = get_phases()
        self.assertEqual(len(phases), 6)
        self.assertEqual({spawn.enemy for wave in phases[1].waves for spawn in wave.spawns},
                         {"gaivota", "asteroid"})
        for phase in phases[2:5]:
            self.assertTrue(phase.free_movement)
        self.assertEqual({spawn.enemy for wave in phases[2].waves for spawn in wave.spawns}, {"drone"})
        self.assertEqual({spawn.enemy for wave in phases[3].waves for spawn in wave.spawns},
                         {"drone", "mine"})
        self.assertEqual({spawn.enemy for wave in phases[4].waves for spawn in wave.spawns}, {"drone"})
        for phase in (phases[0], phases[-1]):
            self.assertFalse(phase.free_movement)
            self.assertFalse(phase.waves)
            player = phase.default_entities["player"]
            player.free_movement = phase.free_movement
            original = player.position.copy()
            with patch("pygame.key.get_pressed", side_effect=AssertionError("Input should be locked")):
                player.movement(1)
            self.assertEqual(player.position, original)
            scene = Scene(True)
            scene.add_entity(player)
            system = WaveSystem(scene, get_enemy_registry())
            system.load_phase(phase)
            system.update(phase.duration - .1)
            self.assertFalse(system.finished)
            system.update(.2)
            self.assertTrue(system.finished)
        for phase in phases:
            for entity in phase.default_entities.values():
                entity.destroy()

    def test_projectiles_expire_and_dead_player_stops_spawning(self):
        shot = EnemyProjectile((500, 500), (0, 10))
        shot.update(9)
        self.assertTrue(shot.to_destroy)
        scene = Scene(True)
        system = WaveSystem(scene, get_enemy_registry())
        system.load_phase(SimpleNamespace(waves=launch_waves(), duration=5))
        system.update(100)
        self.assertFalse(scene.enemys)

    def test_drones_and_gaivotas_never_receive_projectile_attacks(self):
        registry = get_enemy_registry()
        for waves in (stratosphere_waves(), near_space_waves(), deep_space_waves(), mars_orbit_waves()):
            for wave in waves:
                for spawn in wave.spawns:
                    enemy = registry.create(spawn, lambda: pygame.Vector2(960, 900))
                    if spawn.enemy in ("drone", "gaivota"):
                        self.assertIsNone(enemy.attack)
                        self.assertTrue(any(isinstance(pattern, (Charge, FlyBy))
                                            for pattern in enemy._patterns))
                    enemy.destroy()

    def test_mine_attracts_player_and_has_collision_placeholder(self):
        from entities.player import Player
        registry = get_enemy_registry()
        spawn = next(spawn for wave in deep_space_waves() for spawn in wave.spawns
                     if spawn.enemy == "mine")
        mine = registry.create(spawn)
        self.assertIsInstance(mine, MineEnemy)
        self.assertEqual(mine.MIDDLE_VERTICES, [])
        self.assertIsInstance(mine.attack, AttractionAttack)

        player = Player()
        player.position.update(mine.position.x - 200, mine.position.y)
        mine.attack.update(mine, player, .1, lambda projectile: None)
        player.movement(.1)
        self.assertGreater(player.velocity.x, 0)
        mine.destroy()
        player.destroy()

    def test_fast_flybys_cross_the_screen_on_both_axes(self):
        patterns = [spawn.movement()[0] for waves in (near_space_waves(), deep_space_waves())
                    for wave in waves for spawn in wave.spawns]
        flybys = [pattern for pattern in patterns if isinstance(pattern, FlyBy)]
        self.assertTrue(any(abs(pattern._direction.x) == 1 for pattern in flybys))
        self.assertTrue(any(abs(pattern._direction.y) == 1 for pattern in flybys))
        for pattern in flybys:
            pattern.update(pattern.duration + 1)
            self.assertTrue(pattern.finished)

    def test_enemy_look_at_rotates_sprite_and_collision_together(self):
        registry = get_enemy_registry()
        spawn = near_space_waves()[0].spawns[0]
        target = pygame.Vector2()
        enemy = registry.create(spawn, lambda: target)
        target.update(enemy.position.x + 500, enemy.position.y)
        enemy.update(0)

        self.assertTrue(enemy.LOOK_AT_PLAYER)
        self.assertAlmostEqual(enemy._rotation, 90)
        expected = [enemy.position + vertex.rotate(-enemy._rotation)
                    for vertex in enemy.MIDDLE_VERTICES]
        for actual, rotated in zip(enemy._collider_vertices, expected):
            self.assertTrue(actual.distance_to(rotated) < .001)
        self.assertLessEqual(pygame.Vector2(enemy._rect.center).distance_to(enemy.position), 1)
        enemy.destroy()


if __name__ == "__main__":
    unittest.main()
