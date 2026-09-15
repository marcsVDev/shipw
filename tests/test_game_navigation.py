import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from game import Game
from entities.scrollers.infinite_vertical_scroller import InfiniteVerticalScroller
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH


class GameNavigationTest(unittest.TestCase):
    def make_game(self, current_scene):
        game = Game.__new__(Game)
        game.current_scene = current_scene
        game.play = Mock()
        game.return_to_menu = Mock()
        return game

    def test_enter_and_keypad_enter_play_only_from_menu(self):
        game = self.make_game("menu")
        game.handle_keydown(pygame.K_RETURN)
        game.handle_keydown(pygame.K_KP_ENTER)
        self.assertEqual(game.play.call_count, 2)
        game.current_scene = "game"
        game.handle_keydown(pygame.K_RETURN)
        self.assertEqual(game.play.call_count, 2)

    def test_escape_returns_only_from_game(self):
        game = self.make_game("game")
        game.handle_keydown(pygame.K_ESCAPE)
        game.return_to_menu.assert_called_once_with()
        game.current_scene = "menu"
        game.handle_keydown(pygame.K_ESCAPE)
        game.return_to_menu.assert_called_once_with()

    def test_ctrl_shift_o_toggles_god_mode_and_updates_player(self):
        game = self.make_game("game")
        game.god_mode = False
        player = SimpleNamespace(god_mode=False)
        game.scenes = {"game": SimpleNamespace(player=player)}
        combo = pygame.KMOD_CTRL | pygame.KMOD_SHIFT

        game.handle_keydown(pygame.K_o, pygame.KMOD_CTRL)
        self.assertFalse(game.god_mode)
        game.handle_keydown(pygame.K_o, combo)
        self.assertTrue(game.god_mode)
        self.assertTrue(player.god_mode)
        game.handle_keydown(pygame.K_o, combo)
        self.assertFalse(game.god_mode)
        self.assertFalse(player.god_mode)

    def test_return_clears_scene_and_resets_systems(self):
        game = Game.__new__(Game)
        game.current_scene = "game"
        game.change_scene_to = Game.change_scene_to.__get__(game)
        waves, progression = Mock(), Mock()
        scene = Mock()
        scene.get_system.side_effect = lambda name, kind: waves if name == "waves" else progression
        game.scenes = {"game": scene, "menu": Mock()}
        Game.return_to_menu(game)
        scene.clear_scene.assert_called_once_with()
        waves.reset.assert_called_once_with()
        progression.reset.assert_called_once_with()
        self.assertEqual(game.current_scene, "menu")

    @patch("game.pygame.mixer.music")
    def test_background_music_loops_at_configured_volume(self, music):
        game = Game.__new__(Game)
        game.start_background_music()
        music.load.assert_called_once()
        music.set_volume.assert_called_once_with(Game.BACKGROUND_MUSIC_VOLUME)
        music.play.assert_called_once_with(-1)

    def test_infinite_scroller_covers_viewport_and_wraps_after_long_frame(self):
        image = pygame.Surface((100, 100))
        image.fill((10, 20, 30))
        scroller = InfiniteVerticalScroller(image, velocity=500, running=True)

        self.assertGreaterEqual(scroller.image.get_width(), SCREEN_WIDTH)
        self.assertGreaterEqual(scroller.image.get_height(), SCREEN_HEIGHT)

        scroller.update(scroller.height * 5 / scroller.velocity + .25)
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.fill((0, 0, 0))
        scroller.draw(screen)
        self.assertEqual(screen.get_at((SCREEN_WIDTH - 1, 0))[:3], (10, 20, 30))
        self.assertEqual(screen.get_at((SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1))[:3], (10, 20, 30))


if __name__ == "__main__":
    unittest.main()
