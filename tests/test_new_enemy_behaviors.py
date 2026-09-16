import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from enemys.behaviors import (AlienFlyByConfig, AsteroidRainConfig, CircularFormationConfig, EvilDroneWaveConfig, FlyByConfig, MineFloatConfig,
    PursuitConfig, SatelliteConfig, SideAttackConfig, ZigZagConfig, circular_angles, circular_formation,
    alien_flybys, asteroid_rain, evil_drone_sweeps, floating_mines, pursuit_wave, safe_flybys, satellite_flyby,
    side_attack, zigzag_wave)
from enemys.broken_satellite_enemy import BrokenSatelliteEnemy
from enemys.patterns import Float, FlyBy, Orbit, Pursuit, TelegraphedFlyBy, ZigZag
from initializations.enemy_waves import get_enemy_registry
from system.wave_system import WaveSystem
from util.scene import Scene


class NewEnemyBehaviorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): pygame.init(); pygame.display.set_mode((1920, 1080))
    @classmethod
    def tearDownClass(cls): pygame.quit()

    def test_registry_contains_every_concrete_type(self):
        registry = get_enemy_registry()
        self.assertEqual(registry.registered, {"drone", "gaivota", "asteroid", "mine",
                                               "broken_satellite", "evil_drone", "alien"})
        satellite = registry.create(satellite_flyby(1920, 1080).spawns[0])
        self.assertIsInstance(satellite, BrokenSatelliteEnemy); satellite.destroy()

    def test_alien_flybys_are_random_lanes_alternating_and_sequential(self):
        config = AlienFlyByConfig(count=20, speed=2600, gap=.2, seed=47)
        wave = alien_flybys(1920, 1080, config)
        patterns = [spawn.movement()[0] for spawn in wave.spawns]

        self.assertEqual(len(wave.spawns), 20)
        self.assertEqual([pattern._direction.x > 0 for pattern in patterns],
                         [index % 2 == 0 for index in range(20)])
        self.assertGreater(len({round(pattern.position.y) for pattern in patterns}), 10)
        for current, following, pattern in zip(wave.spawns, wave.spawns[1:], patterns):
            self.assertGreaterEqual(following.delay, current.delay + pattern.duration)

        alien = get_enemy_registry().create(wave.spawns[0])
        self.assertTrue(alien.MIDDLE_VERTICES)
        alien.destroy()

    def test_evil_drones_are_sequential_and_keep_individual_sweeps(self):
        config = EvilDroneWaveConfig()
        wave = evil_drone_sweeps(1920, 1080, config)
        self.assertEqual([spawn.delay for spawn in wave.spawns],
                         [index * config.spawn_interval for index in range(4)])

        sweeps = [spawn.movement()[2] for spawn in wave.spawns]
        self.assertEqual([(sweep.start_angle, sweep.sweep_angle, sweep.clockwise)
                          for sweep in sweeps],
                         [(0, 90, True), (180, 90, False),
                          (180, 90, True), (0, 90, False)])
        for sweep in sweeps:
            expected = ((sweep.start_angle + (sweep.sweep_angle if sweep.clockwise
                         else -sweep.sweep_angle)) % 360)
            sweep.update(sweep.duration)
            self.assertAlmostEqual(sweep.beam_angle, expected)

    def test_evil_drone_beam_uses_exact_sprite_pixel_and_color(self):
        from entities.enemy_beam import EnemyBeam

        spawn = evil_drone_sweeps(1920, 1080).spawns[0]
        enemy = get_enemy_registry().create(spawn)
        enemy.update(2)
        enemy.update(0)
        enemy.update(.8)
        enemy.update(0)
        sweep = enemy._patterns[enemy._current_pattern]
        beam = EnemyBeam(enemy, sweep)

        local = (pygame.Vector2(85.5, 115) - pygame.Vector2(62)) * 2
        expected_origin = enemy.position + local.rotate(-enemy._rotation)
        self.assertLess(beam.origin.distance_to(expected_origin), .001)
        self.assertEqual(beam.color, pygame.Color("#ae2334"))
        self.assertTrue(beam._collider_vertices)
        beam.destroy()
        enemy.destroy()

    def test_evil_drone_beam_collides_with_player(self):
        from entities.enemy_beam import EnemyBeam
        from entities.player import Player

        enemy = get_enemy_registry().create(evil_drone_sweeps(1920, 1080).spawns[0])
        enemy.update(2)
        enemy.update(0)
        enemy.update(.8)
        enemy.update(0)
        sweep = enemy._patterns[enemy._current_pattern]
        beam = EnemyBeam(enemy, sweep)
        player = Player()
        player.position = beam.origin + sweep.beam_direction * 350
        player.update(0)
        scene = Scene(True)
        scene.add_entity(player)
        scene.add_entity(beam)

        scene.check_collisions()
        self.assertTrue(player.to_destroy)

        scene.clear_scene()
        enemy.destroy()

    def test_evil_drone_animates_before_beam_and_holds_last_frame(self):
        enemy = get_enemy_registry().create(evil_drone_sweeps(1920, 1080).spawns[0])
        self.assertEqual(enemy._animation.current_animation, "idle")

        enemy.update(2)
        enemy.update(0)
        self.assertEqual(enemy._animation.current_animation, "prepare_attack")
        self.assertTrue(enemy._animation.is_playing)

        enemy.update(.8)
        self.assertEqual(enemy._animation.frame_index, 7)
        self.assertFalse(enemy._animation.is_playing)
        enemy.update(0)
        self.assertTrue(getattr(enemy._patterns[enemy._current_pattern], "fires_beam", False))
        enemy.update(.5)
        self.assertEqual(enemy._animation.frame_index, 7)
        self.assertFalse(enemy._animation.is_playing)
        enemy.destroy()

    def test_organized_attack_uses_point_two_second_rest(self):
        from enemys.behaviors import organized_attack
        wave = organized_attack("gaivota", 1920, 1080)
        self.assertEqual(wave.rest, .2)

    def test_pursuit_counts_charges_and_is_frame_rate_independent(self):
        def run(dt):
            p = Pursuit((300, 200), charges=3, speed=500, warning=.1,
                        charge_duration=.2, interval=.1)
            p.bind_target(lambda: pygame.Vector2(300, 900))
            while not p.finished: p.update(dt)
            return p
        fine, coarse = run(.01), run(.07)
        self.assertEqual(fine.completed_charges, 3)
        self.assertEqual(coarse.completed_charges, 3)
        self.assertLess(fine.position.distance_to(coarse.position), 1)

    def test_pursuit_waits_at_captured_player_position_before_next_charge(self):
        target = pygame.Vector2(300, 500)
        pursuit = Pursuit((300, 100), charges=2, speed=400, warning=.2,
                          charge_duration=2, interval=.5)
        pursuit.bind_target(lambda: target)

        pursuit.update(1.2)
        self.assertEqual(pursuit.completed_charges, 1)
        self.assertEqual(pursuit.state, "wait")
        self.assertEqual(pursuit.position, pygame.Vector2(300, 500))

        target.update(700, 500)
        pursuit.update(.49)
        self.assertEqual(pursuit.position, pygame.Vector2(300, 500))
        pursuit.update(.21)
        self.assertEqual(pursuit.state, "charge")
        self.assertEqual(pursuit.captured_target, pygame.Vector2(700, 500))
        self.assertEqual(pursuit.position, pygame.Vector2(300, 500))

        pursuit.update(2)
        self.assertTrue(pursuit.finished)
        self.assertGreater(pursuit.position.x, target.x)

    def test_pursuit_owns_facing_until_the_pattern_finishes(self):
        target = pygame.Vector2(700, 300)
        pursuit = Pursuit((300, 300), charges=2, speed=400, warning=.2,
                          charge_duration=.2, interval=.5)
        pursuit.bind_target(lambda: target)

        pursuit.update(.1)
        self.assertTrue(pursuit.locks_facing)
        self.assertAlmostEqual(pursuit.rotation, 90)

        pursuit.update(1.1)
        self.assertEqual(pursuit.state, "wait")
        locked_rotation = pursuit.rotation
        target.update(300, 900)
        pursuit.update(.1)
        self.assertEqual(pursuit.rotation, locked_rotation)

        pursuit.update(.5)
        self.assertEqual(pursuit.state, "warning")
        expected = -pygame.Vector2(0, 1).angle_to(target - pursuit.position)
        self.assertAlmostEqual(pursuit.rotation, expected)

    def test_pursuit_wave_finishes_its_last_charge_outside_the_screen(self):
        pursuit = pursuit_wave(
            "gaivota", 1000, 800, PursuitConfig(count=1, charges=2)
        ).spawns[0].movement()[1]
        pursuit.bind_target(lambda: pygame.Vector2(500, 700))
        while not pursuit.finished:
            pursuit.update(.05)
        self.assertTrue(
            pursuit.position.x < 0 or pursuit.position.x > 1000
            or pursuit.position.y < 0 or pursuit.position.y > 800
        )

    def test_side_queue_alternates_and_uses_intervals(self):
        wave = side_attack("gaivota", 1000, 800, SideAttackConfig(per_side=3, interval=.7))
        self.assertEqual([s.group for s in wave.spawns], list(range(6)))
        self.assertEqual([s.delay for s in wave.spawns], [i*.7 for i in range(6)])
        starts = [s.movement()[0].position.x for s in wave.spawns]
        self.assertEqual([x < 0 for x in starts], [True, False] * 3)

    def test_circle_has_reserved_holes_and_moving_center(self):
        config = CircularFormationConfig(count=18, holes=3, hole_width=30)
        angles = circular_angles(config)
        for hole in (0, 120, 240):
            self.assertTrue(all(abs((a-hole+180)%360-180) >= 15 for a in angles))
        orbit = circular_formation("drone", 1920, 1080, config).spawns[0].movement()[1]
        before = orbit.center.x; orbit.update(1)
        self.assertNotEqual(before, orbit.center.x)

    def test_zigzag_groups_and_trajectory_are_frame_rate_independent(self):
        config = ZigZagConfig(count=8, group_size=3, group_interval=1.5)
        wave = zigzag_wave("drone", 1920, 1080, config)
        self.assertEqual([s.group for s in wave.spawns], [0,0,0,1,1,1,2,2])
        a, b = wave.spawns[0].movement()[0], wave.spawns[0].movement()[0]
        for _ in range(100): a.update(.01)
        for _ in range(10): b.update(.1)
        self.assertLess(a.position.distance_to(b.position), .01)

    def test_satellite_warning_matches_real_path(self):
        pattern = satellite_flyby(1920, 1080, SatelliteConfig(warning=1)).spawns[0].movement()[0]
        self.assertIsInstance(pattern, TelegraphedFlyBy)
        self.assertLess(pattern.start.y, 0)
        self.assertGreater(pattern.end.y, 1080)
        self.assertEqual(pattern.danger_line, (pattern.start, pattern.end))
        pattern.update(pattern.warning / 2); self.assertEqual(pattern.position, pattern.start)
        pattern.update(pattern.warning); self.assertGreater(pattern.position.distance_to(pattern.start), 0)

    def test_satellite_random_origin_is_reproducible_with_seed(self):
        first = satellite_flyby(
            1920, 1080, SatelliteConfig(origin="random", seed=44)
        ).spawns[0].movement()[0]
        second = satellite_flyby(
            1920, 1080, SatelliteConfig(origin="random", seed=44)
        ).spawns[0].movement()[0]
        self.assertEqual(first.start, second.start)
        self.assertEqual(first.end, second.end)
        self.assertIn(first.start.x, (-220, 1920 + 220))

    def test_mine_float_is_separate_from_attraction(self):
        active = floating_mines(1920, 1080, MineFloatConfig(attraction=True)).spawns[0]
        passive = floating_mines(1920, 1080, MineFloatConfig(attraction=False)).spawns[0]
        self.assertIsInstance(active.movement()[1], Float)
        attack = active.attack()
        self.assertIsNotNone(attack); self.assertIsNone(passive.attack())

    def test_mine_attraction_has_no_distance_limit(self):
        attack = floating_mines(1920, 1080).spawns[0].attack()
        enemy = SimpleNamespace(position=pygame.Vector2(100, 100))
        forces = []
        player = SimpleNamespace(position=pygame.Vector2(1900, 1000), apply_force=forces.append)
        attack.update(enemy, player, .1, lambda projectile: None)
        self.assertEqual(len(forces), 1)

    def test_mine_attraction_gets_weaker_with_distance(self):
        attack = floating_mines(1920, 1080).spawns[0].attack()
        enemy = SimpleNamespace(position=pygame.Vector2(100, 100))
        forces = []
        player = SimpleNamespace(position=pygame.Vector2(200, 100), apply_force=forces.append)
        attack.update(enemy, player, .1, lambda projectile: None)
        near_force = forces[-1].length()

        player.position.x = 1000
        attack.update(enemy, player, .1, lambda projectile: None)
        far_force = forces[-1].length()
        self.assertGreater(near_force, far_force)
        self.assertGreater(far_force, 0)

    def test_seeded_flybys_keep_spawn_away_from_player(self):
        player = pygame.Vector2(960, -150)
        config = FlyByConfig(count=6, origins=("top",), safe_distance=300, seed=9)
        wave = safe_flybys("drone", 1920, 1080, player, config)
        self.assertTrue(all(s.movement()[0].position.distance_to(player) >= 300 for s in wave.spawns))

    def test_flyby_keeps_facing_its_straight_trajectory(self):
        flyby = FlyBy((-100, 250), (1100, 250), speed=600)
        self.assertTrue(flyby.locks_facing)
        flyby.update(.1)
        self.assertAlmostEqual(flyby.rotation, -90)

    def test_gaivota_flyby_and_asteroid_face_the_opposite_way(self):
        gaivota = safe_flybys(
            "gaivota", 1920, 1080,
            config=FlyByConfig(count=1, origins=("left",), seed=4),
        ).spawns[0].movement()[0]
        asteroid = asteroid_rain(1920, 1080, AsteroidRainConfig(seed=4)).spawns[0].movement()[0]

        self.assertEqual(gaivota.facing_offset, 180)
        self.assertEqual(asteroid.facing_offset, 180)
        gaivota.update(.1)
        asteroid.update(.1)
        self.assertAlmostEqual(gaivota.rotation, 90)

    def test_asteroid_rain_covers_screen_in_random_sequence(self):
        config = AsteroidRainConfig(direction="left", player_width=100,
                                    player_clearance=2, seed=7)
        wave = asteroid_rain(1000, 800, config)
        starts = [spawn.movement()[0].position.x for spawn in wave.spawns]
        ordered = sorted(starts)
        self.assertNotEqual(starts, ordered)
        self.assertTrue(all(b - a <= 200 for a, b in zip(ordered, ordered[1:])))
        self.assertEqual(wave.spawns[0].delay, 0)
        self.assertTrue(all(a.delay < b.delay for a, b in zip(wave.spawns, wave.spawns[1:])))
        self.assertTrue(all(spawn.movement()[0]._direction.x < 0 for spawn in wave.spawns))

    def test_right_asteroid_rain_flips_sprite_and_direction(self):
        wave = asteroid_rain(1000, 800, AsteroidRainConfig(direction="right", seed=2))
        self.assertTrue(all(spawn.options["flip_x"] for spawn in wave.spawns))
        self.assertTrue(all(spawn.movement()[0]._direction.x > 0 for spawn in wave.spawns))
        enemy = get_enemy_registry().create(wave.spawns[0])
        self.assertTrue(enemy.flip_x)
        enemy.destroy()

    def test_destroyed_sequential_enemy_does_not_block_wave(self):
        wave = pursuit_wave("drone", 1920, 1080, PursuitConfig(count=2, spawn_interval=.5))
        scene = Scene(True); scene.player = SimpleNamespace(position=pygame.Vector2(960,900), to_destroy=False)
        system = WaveSystem(scene, get_enemy_registry()); system.load_phase(SimpleNamespace(waves=(wave,)))
        system.update(2.1); self.assertEqual(len(system.active), 1)
        system.active[0].destroy(); system.update(.6)
        self.assertEqual(len(system.active), 1)
        for enemy in system.active: enemy.destroy()
        system.update(.1); system.update(wave.rest + .1)
        self.assertTrue(system.finished)


if __name__ == "__main__": unittest.main()
