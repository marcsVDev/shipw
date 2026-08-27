import time

import pygame

from events.events import Events
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.ui_inits import get_play_button
from events.event_bus import EventBus
from ui.title import Title
from ui.ui import UI
from util.phase import Phase
from util.progresssion import Progression
from util.scene import Scene

class Game:
    FPS = 60
    FILL_COLOR = (0x17, 0x18, 0x1d)

    def __init__(self):
        pygame.init()  
        pygame.display.set_caption("Projeto Cosmonauta")
        pygame.mixer.init()

        EventBus.connect(Events.PHASE_CHANGED, self.load_phase)

        # propriedades
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.scenes: dict[str, Scene] = {}
        self.current_scene: str = "menu"
        self.running = True

        inital_menu = Scene(game_scene=False) 

        inital_menu.add_ui(get_play_button(self.play))
        inital_menu.add_ui(Title())
        self.scenes["menu"] = inital_menu

        game_scene = Scene(game_scene=True)

        progression = Progression()
        
        game_scene.add_system("progression", progression)
        self.scenes["game"] = game_scene

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
            self.scenes[self.current_scene].run(self.screen, delta, events)

            self.fps = clock.get_fps()
            if self.fps < 30:
                print(f"WARNING FPS: {self.fps}")
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        # time.sleep(2)
        EventBus.emit(Events.GAME_STARTED) 

        self.load_phase(self.scenes["game"].get_system("progression", Progression).PHASES[0])
        self.scenes["game"].destroy_entity("play_btn")
        self.change_scene_to("game")        

    def load_phase(self, phase: Phase):
        game_scene = self.scenes["game"]
        game_scene.clear_scene()
        for key in phase.default_entities.keys():
            match phase.default_entities[key]:
                case UI():
                    game_scene.add_ui(phase.default_entities[key], key)                 
                case _:
                    game_scene.add_entity(phase.default_entities[key], key) 

    def change_scene_to(self, name: str):
         self.current_scene = name   


GAME = Game()
