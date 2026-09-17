import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from entities.cutscene import Cutscene
from ui.button import Button
from util.animatedSprite import AnimatedSprite


class CutsceneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((32, 18))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_rectangular_animation_plays_once_and_completes(self):
        sheet = pygame.Surface((96, 18))
        sheet.fill((255, 0, 0), (0, 0, 32, 18))
        sheet.fill((0, 255, 0), (32, 0, 32, 18))
        sheet.fill((0, 0, 255), (64, 0, 32, 18))
        animation = AnimatedSprite(
            sheet,
            .1,
            (32, 18),
            {"default": {"frames": range(3), "loop": False}},
        )
        completed = []
        cutscene = Cutscene(animation, display_size=(64, 36), on_complete=lambda: completed.append(True))

        self.assertFalse(animation.is_playing)
        self.assertEqual(animation.get_current_frame().get_size(), (32, 18))
        cutscene.run()
        cutscene.update(.31)
        cutscene.update(.31)

        self.assertFalse(animation.is_playing)
        self.assertEqual(animation.frame_index, 2)
        self.assertEqual(completed, [True])

    @patch("ui.button.pygame.mixer.Sound")
    @patch("ui.button.pygame.mouse.get_pos", return_value=(32, 32))
    def test_one_shot_launch_button_hides_after_click(self, _mouse_position, sound):
        callback = Mock()
        image = pygame.Surface((192, 64))
        button = Button(image, pygame.Vector2(), 64, callback, (64, 64), one_shot=True)

        button.update(0, [pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": pygame.BUTTON_LEFT},
        )])

        callback.assert_called_once_with()
        sound.return_value.play.assert_called_once_with()
        self.assertTrue(button.to_destroy)
        self.assertFalse(button.visible)


if __name__ == "__main__":
    unittest.main()
