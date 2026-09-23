import os
import sys
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from ui.alert_indicator import AlertIndicator


class AlertIndicatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1920, 1080))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_animation_runs_at_twelve_frames_per_second(self):
        alert = AlertIndicator()

        self.assertEqual(alert.frame_index, 0)
        alert.update(1 / 12)
        self.assertEqual(alert.frame_index, 1)
        alert.update(1 / 12)
        self.assertEqual(alert.frame_index, 0)

    def test_offscreen_entry_is_shown_at_matching_screen_edge(self):
        alert = AlertIndicator()

        self.assertEqual(alert.visible_position((-180, 350)), (48, 350))
        self.assertEqual(alert.visible_position((2100, 700)), (1872, 700))


if __name__ == "__main__":
    unittest.main()
