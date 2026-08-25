import pygame
from pygame import Vector2

from entities.enemy import Enemy
from entities.player import Player
from entities.scrollers.moving_object import MovingObject
from events.events import Events
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH, UI_PATH
from initializations.scenery import get_earth_scenery, get_satellite_scenery
from initializations.ui import get_dialogue_panel, get_play_button
from ui.button import Button
from events.event_bus import EventBus
from ui.ui import UI
from util.phase import Phase
from util.progresssion import Progression
from util.scene import Scene

class Game:
    FPS = 60
    FILL_COLOR = (0x17, 0x18, 0x1d)

    def __init__(self):
        pygame.init()  
        pygame.display.set_caption("Shipw")

        EventBus.connect(Events.PHASE_CHANGED, self.load_phase)

        # propriedades
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))         
        self.game_scene = Scene()
        self.running = True

        progression = Progression()             
        
        self.load_phase(progression.PHASES[0])
        self.game_scene.add_system("progression", progression)
        self.game_scene.add_ui(get_play_button(self.play), "play_btn")

        # main loop

        self.loop()

        pygame.quit()

    def loop(self):        
        clock = pygame.time.Clock()
        delta = 0  

        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False                 

            self.screen.fill(self.FILL_COLOR)
            self.game_scene.run(self.screen, delta, events)

            self.fps = clock.get_fps()
            if self.fps < 30:
                print(f"WARNING FPS: {self.fps}")
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        EventBus.emit(Events.GAME_STARTED) 
        self.game_scene.destroy_entity("play_btn")

    def load_phase(self, phase: Phase):
        self.game_scene.clear_scene()
        for key in phase.default_entities.keys():
            match phase.default_entities[key]:
                case UI():
                    self.game_scene.add_ui(phase.default_entities[key], key)                 
                case _:
                    self.game_scene.add_entity(phase.default_entities[key], key)    


GAME = Game()
