import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from enemys.asteroid_enemy import AsteroidEnemy
from enemys.drone_enemy import DroneEnemy
from enemys.patterns import Charge, Yell
from initializations.enemy_waves import get_enemy_registry, near_space_waves, stratosphere_waves


class EnemyPatternsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1920, 1080))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_asteroid_uses_its_own_enemy_class(self):
        spawn = next(spawn for wave in stratosphere_waves() for spawn in wave.spawns
                     if spawn.enemy == "asteroid")
        enemy = get_enemy_registry().create(spawn)
        self.assertIsInstance(enemy, AsteroidEnemy)
        enemy.destroy()

    def test_every_charge_is_preceded_by_a_yell(self):
        with patch("enemys.patterns.yell.load_sound", return_value=Mock()):
            spawn = near_space_waves()[1].spawns[0]
            patterns = spawn.movement()
        charge_indexes = [index for index, pattern in enumerate(patterns)
                          if isinstance(pattern, Charge)]
        self.assertTrue(charge_indexes)
        self.assertTrue(all(isinstance(patterns[index - 1], Yell)
                            for index in charge_indexes))

    def test_charge_stops_live_tracking_of_player(self):
        charge = Charge((100, 100))
        enemy = DroneEnemy(patterns=[charge])
        enemy.configure([charge], target=lambda: pygame.Vector2(500, 100))
        enemy.update(.1)
        self.assertEqual(enemy._rotation, charge.rotation)
        enemy.destroy()

    def test_drone_uses_four_frame_animation(self):
        enemy = DroneEnemy(patterns=[Charge((100, 100))])
        self.assertTrue(enemy.DEFAULT_SPRITESHEET.endswith("drone_animation.png"))
        self.assertEqual(enemy._animation.frames_count, 4)
        initial_frame = enemy._animation.frame_index
        enemy.update(enemy.ANIMATION_FRAME_DURATION)
        self.assertNotEqual(enemy._animation.frame_index, initial_frame)
        enemy.destroy()


if __name__ == "__main__":
    unittest.main()
