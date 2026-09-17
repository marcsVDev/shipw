import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from entities.enemy_projectile import EnemyProjectile
from entities.enemy_beam import EnemyBeam
from entities.guided_missile import GuidedMissile
from entities.player import Player
from enemys.mother_ship_enemy import MotherShipEnemy
from events.event_bus import EventBus
from events.events import Events
from initializations.boss_waves import boss_waves
from initializations.enemy_waves import get_enemy_registry
from initializations.phases import get_phases
from system.boss_fight_system import BossFightSystem
from util.run_state import RunState
from util.scene import Scene


class BossAndHealthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1920, 1080))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        EventBus.events.clear()

    def test_run_state_clamps_resets_and_is_shared_by_every_phase(self):
        state = RunState()
        self.assertEqual(state.health, 3)
        for _ in range(5):
            state.damage()
        self.assertEqual(state.health, 0)
        self.assertTrue(state.is_game_over)
        state.reset()
        self.assertEqual(state.health, 3)
        phases = get_phases(state)
        self.assertTrue(all(phase.default_entities["player"].run_state is state
                            for phase in phases))
        for phase in phases:
            for entity in phase.default_entities.values():
                entity.destroy()

    def test_collision_costs_one_hp_and_invulnerability_blocks_followups(self):
        state = RunState()
        player = Player(state)
        player.update(0)
        sources = [EnemyProjectile(player.position, (0, 0)) for _ in range(3)]
        self.assertTrue(player.take_damage(sources))
        self.assertEqual(state.health, 2)
        self.assertTrue(all(source.to_destroy for source in sources))
        self.assertFalse(player.take_damage((EnemyProjectile(player.position, (0, 0)),)))
        self.assertEqual(state.health, 2)
        player.update(1.51)
        self.assertTrue(player.take_damage((EnemyProjectile(player.position, (0, 0)),)))
        self.assertEqual(state.health, 1)
        player.destroy()

    def test_death_is_emitted_once_and_god_mode_preserves_health(self):
        state = RunState()
        player = Player(state)
        deaths = []
        EventBus.connect(Events.PLAYER_DIED, deaths.append)
        player.god_mode = True
        player.take_damage((object(),))
        self.assertEqual(state.health, 3)
        player.god_mode = False
        for expected in (2, 1, 0):
            player.invulnerable_remaining = 0
            player.take_damage(())
            self.assertEqual(state.health, expected)
        player.take_damage(())
        self.assertEqual(deaths, [player])

    def test_missile_accelerates_caps_speed_and_limits_turn(self):
        boss = MotherShipEnemy()
        boss.update(3)
        target = pygame.Vector2(0, boss.launch_position.y)
        missile = GuidedMissile(boss.launch_position, lambda: target, boss)
        missile.elapsed = missile.config.telegraph_duration
        before = missile.direction.copy()
        missile.update(.1)
        self.assertLessEqual(abs(before.angle_to(missile.direction)), missile.config.turn_rate * .1 + 1e-6)
        missile.update(20)
        self.assertLessEqual(missile.speed, missile.config.max_speed)
        self.assertTrue(missile.exploded)
        missile.update(.2)
        self.assertTrue(missile.to_destroy)

    def test_missile_takes_short_turn_across_angle_wrap(self):
        boss = MotherShipEnemy()
        missile = GuidedMissile((960, 600), lambda: (860, 590), boss)
        self.addCleanup(missile.destroy)
        missile.state = "seeking"
        missile.direction = pygame.Vector2(-100, 10).normalize()
        desired = pygame.Vector2(-100, -10).normalize()
        before = abs((missile.direction.angle_to(desired) + 180) % 360 - 180)
        missile.update(1 / 120)
        after = abs((missile.direction.angle_to(desired) + 180) % 360 - 180)
        self.assertLess(after, before)

    def test_every_open_target_can_be_hit_from_below_in_flight(self):
        for name in MotherShipEnemy.TARGETS:
            for fps in (20, 60, 120):
                with self.subTest(target=name, fps=fps):
                    boss = MotherShipEnemy()
                    boss.update(3)
                    boss.open_target(name)
                    point = boss.target_position(name)
                    missile = GuidedMissile(point + (0, 400), lambda: point, boss)
                    self.addCleanup(missile.destroy)
                    missile.state = "seeking"
                    missile.direction = pygame.Vector2(0, -1)
                    missile.flight_time = missile.config.arm_time
                    scene = Scene(True)
                    scene.add_entity(boss)
                    for _ in range(fps * 2):
                        missile.update(1 / fps)
                        missile.resolve_collisions(scene)
                        if missile.exploded:
                            break
                    self.assertEqual(missile.explosion_reason, "boss_target")
                    self.assertEqual(boss.health, 4)

    def test_missile_returns_toward_player_after_dodge(self):
        boss = MotherShipEnemy()
        boss.update(3)
        target = pygame.Vector2(960, 500)
        missile = GuidedMissile((960, 800), lambda: target, boss)
        self.addCleanup(missile.destroy)
        missile.state = "seeking"
        missile.speed = missile.config.max_speed
        scene = Scene(True)
        scene.add_entity(boss)
        for _ in range(120):
            missile.update(1 / 120)
            missile.resolve_collisions(scene)
            if missile.exploded:
                break
        self.assertFalse(missile.exploded)
        self.assertLess(missile.direction.y, 0)
        self.assertLess(missile.position.y, 800)

    def test_missile_motion_is_stable_across_frame_rates(self):
        boss = MotherShipEnemy()
        boss.update(3)
        target = pygame.Vector2(250, 850)

        def simulate(step):
            missile = GuidedMissile(boss.launch_position, lambda: target, boss)
            missile.elapsed = missile.config.telegraph_duration
            elapsed = 0.0
            while elapsed < 2:
                dt = min(step, 2 - elapsed)
                missile.update(dt)
                elapsed += dt
            missile.destroy()
            return missile.position, missile.direction

        fine_position, fine_direction = simulate(1 / 120)
        coarse_position, coarse_direction = simulate(1 / 20)
        self.assertLess(fine_position.distance_to(coarse_position), 1)
        self.assertLess(abs(fine_direction.angle_to(coarse_direction)), .1)

    def test_only_armed_missile_on_open_target_damages_boss(self):
        boss = MotherShipEnemy()
        boss.update(3)
        boss.open_target("core")
        point = boss.target_position("core")
        missile = GuidedMissile(point, lambda: point, boss)
        missile.state = "seeking"
        scene = Scene(True)
        scene.add_entity(boss)
        missile.resolve_collisions(scene)
        self.assertEqual(boss.health, 5)
        self.assertEqual(missile.explosion_reason, "unarmed_target")

        boss.open_target("core")
        armed = GuidedMissile(point, lambda: point, boss)
        armed.state = "seeking"
        armed.flight_time = armed.config.arm_time
        armed.resolve_collisions(scene)
        self.assertEqual(boss.health, 4)
        self.assertEqual(armed.explosion_reason, "boss_target")

    def test_closed_target_is_armor_and_missile_can_destroy_laser_ship(self):
        boss = MotherShipEnemy()
        boss.update(3)
        point = boss.target_position("core")
        scene = Scene(True)
        scene.add_entity(boss)
        closed = GuidedMissile(point, lambda: point, boss)
        closed.state = "seeking"
        closed.flight_time = closed.config.arm_time
        closed.resolve_collisions(scene)
        self.assertEqual(boss.health, 5)
        self.assertEqual(closed.explosion_reason, "armor")

        laser_spawn = boss_waves()[2].spawns[0]
        laser = get_enemy_registry().create(laser_spawn, lambda: pygame.Vector2(960, 900))
        laser.position.update(400, 500)
        laser.update(0)
        scene.add_entity(laser)
        missile = GuidedMissile(laser.position, lambda: laser.position, boss)
        missile.state = "seeking"
        missile.flight_time = missile.config.arm_time
        missile.resolve_collisions(scene)
        self.assertTrue(laser.to_destroy)
        self.assertEqual(missile.explosion_reason, "laser_ship")
        scene.clear_scene()

    def test_boss_has_seven_waves_and_loops_from_seven_to_two(self):
        self.assertEqual(len(boss_waves()), 7)
        scene = Scene(True)
        player = Player(RunState())
        player.update(0)
        scene.add_entity(player)
        system = BossFightSystem(scene, get_enemy_registry())
        phase = get_phases(player.run_state)[4]
        system.load_phase(phase)
        system.wave_index = 6
        system._begin_next_wave()
        self.assertEqual(system.wave_index, 1)
        scene.clear_scene()
        for item in phase.default_entities.values():
            item.destroy()

    def test_fifth_valid_hit_defeats_boss_once(self):
        boss = MotherShipEnemy()
        defeated = []
        EventBus.connect(Events.BOSS_DEFEATED, defeated.append)
        for index in range(5):
            boss.open_target("core")
            self.assertTrue(boss.take_missile_hit("core", True))
            self.assertEqual(boss.health, 4 - index)
        boss.open_target("core")
        self.assertFalse(boss.take_missile_hit("core", True))
        self.assertEqual(defeated, [boss])

    def test_missile_waits_for_pending_spawns_enemies_and_beams(self):
        scene = Scene(True)
        player = Player(RunState())
        scene.add_entity(player)
        self.addCleanup(scene.clear_scene)
        player.time_since_damage = 10
        system = BossFightSystem(scene, get_enemy_registry())
        system.load_phase(SimpleNamespace(boss_fight=True))
        system.intro_remaining = 0
        system._begin_next_wave()
        system.wave_elapsed = 20
        system.pending = [[100, 0, system.waves[0].spawns[0]]]

        def assert_waiting():
            system.update(.1)
            self.assertFalse(system.missile_created)
            self.assertFalse(system.target_warned)
            self.assertEqual(system.rest_remaining, 0)

        assert_waiting()
        for enemy in system.active_enemies:
            enemy.destroy()
        assert_waiting()  # Future reinforcements still belong to the attack wave.
        system.pending.clear()
        beam = Mock(spec=EnemyBeam, to_destroy=False)
        scene.entities.append(beam)
        assert_waiting()
        beam.to_destroy = True
        system.update(.1)
        self.assertTrue(system.missile_created)
        self.assertTrue(system.target_warned)
        missile = system.active_missile
        system.update(10)
        self.assertIs(system.active_missile, missile)
        self.assertEqual(system.wave_index, 0)
        self.assertEqual(system.rest_remaining, 0)
        missile.destroy()
        system.update(.1)
        self.assertGreater(system.rest_remaining, 0)

    def test_boss_system_completes_once_after_defeat_animation(self):
        state = RunState()
        scene = Scene(True)
        player = Player(state)
        player.update(0)
        scene.add_entity(player)
        system = BossFightSystem(scene, get_enemy_registry())
        phase = get_phases(state)[4]
        completed = []
        EventBus.connect(Events.PHASE_COMPLETED, completed.append)
        system.load_phase(phase)
        for _ in range(5):
            system.boss.open_target("core")
            system.boss.take_missile_hit("core", True)
        system.update(4.1)
        system.update(4.1)
        self.assertEqual(completed, [phase])
        self.assertTrue(system.completed)
        scene.clear_scene()
        for entity in phase.default_entities.values():
            entity.destroy()

    def test_player_death_cancels_boss_spawns(self):
        state = RunState()
        scene = Scene(True)
        player = Player(state)
        player.update(0)
        scene.add_entity(player)
        system = BossFightSystem(scene, get_enemy_registry())
        phase = get_phases(state)[4]
        system.load_phase(phase)
        system.intro_remaining = 0
        system._begin_next_wave()
        EventBus.emit(Events.PLAYER_DIED, player)
        self.assertFalse(system.active)
        self.assertFalse(system.pending)
        before = len(scene.entities)
        system.update(100)
        self.assertEqual(len(scene.entities), before)
        scene.clear_scene()
        for entity in phase.default_entities.values():
            entity.destroy()


if __name__ == "__main__":
    unittest.main()
