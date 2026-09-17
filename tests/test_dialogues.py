import os
import sys
import unittest
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from initializations.dialogues import get_phase_dialogues, load_dialogue_data
from initializations.ui_inits import get_dialogue_panel
from entities.player import Player
from util.scene import Scene


class DialoguesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1920, 1080))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_json_has_dialogues_for_every_phase_and_optional_portraits(self):
        data = load_dialogue_data()

        self.assertEqual(set(data["phases"]), {"1", "2", "3", "4", "5", "6"})
        self.assertTrue(all(data["phases"][phase] for phase in data["phases"]))
        self.assertIsNotNone(data["characters"]["valentina"]["portrait"])
        self.assertIsNone(data["characters"]["petrovitch"]["portrait"])
        self.assertIsNone(data["characters"]["comando"]["portrait"])

    def test_loader_resolves_names_and_available_portraits(self):
        dialogues = get_phase_dialogues(1)
        petrovitch = dialogues[0]
        valentina = next(dialogue for dialogue in dialogues
                         if dialogue.speaker == "VALENTINA")

        self.assertEqual(petrovitch.speaker, "PETROVITCH")
        self.assertIsNone(petrovitch.portrait)
        self.assertIsInstance(valentina.portrait, pygame.Surface)

    def test_long_dialogues_are_paginated_inside_the_text_area(self):
        panel = get_dialogue_panel(1)
        max_lines = panel.DIALOGUE_AREA.height // panel.font.get_linesize()

        self.assertGreater(len(panel._pages), len(panel.dialogues))
        self.assertTrue(all(len(page.lines) <= max_lines for page in panel._pages))

    @patch("ui.dialogue_panel.pygame.key.get_just_pressed")
    def test_space_completes_text_then_advances_and_closes(self, pressed):
        keys = defaultdict(bool, {pygame.K_SPACE: True})
        pressed.return_value = keys
        panel = get_dialogue_panel(2)

        panel.update(0, [])
        self.assertEqual(panel.current_dialogue, 0)
        self.assertEqual(
            panel.visible_characters,
            panel._dialogue_characters_count[0],
        )
        panel.update(0, [])
        self.assertEqual(panel.current_dialogue, 1)

        panel.current_dialogue = len(panel._pages) - 1
        panel.visible_characters = panel._dialogue_characters_count[-1]
        panel.update(0, [])
        self.assertFalse(panel.visible)

    def test_visible_dialogue_pauses_system_and_player(self):
        scene = Scene(game_scene=True)
        system = Mock()
        scene.add_system("test", system)
        player = Player()
        player.update = Mock()
        scene.add_entity(player)
        panel = get_dialogue_panel(2)
        scene.add_ui(panel)

        with patch("ui.dialogue_panel.pygame.key.get_just_pressed",
                   return_value=defaultdict(bool)):
            scene.run(pygame.Surface((1920, 1080)), .1, [])

        system.update.assert_not_called()
        player.update.assert_not_called()

        panel.visible = False
        scene.run(pygame.Surface((1920, 1080)), .1, [])
        system.update.assert_called_once_with(.1)
        player.update.assert_called_once_with(.1)
        scene.clear_scene()
