import pygame
from pygame import Vector2

from entities.enemy import Enemy
from entities.player import Player
from entities.scrollers.moving_object import MovingObject
from events.events import Events
from game_consts import SCREEN_HEIGHT, SCREEN_WIDTH, UI_PATH
from initializations.scenery import get_earth_scenery, get_satellite_scenery
from initializations.ui import get_dialogue_panel
from ui.button import Button
from events.event_bus import EventBus
from util.phase import Phase
from util.progresssion import Progression
from util.scene import Scene

class Game:
    FPS = 60

    def __init__(self):
        pygame.init()  
        pygame.display.set_caption("Shipw")

        EventBus.connect(Events.PHASE_CHANGED, self.load_phase)

        # propriedades
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))         
        self.game_scene = Scene()
        self.running = True

        # inicializacao de imagens

        btn_img = pygame.transform.scale_by(pygame.image.load(UI_PATH + "play.png"), 5)
        
        #inicialização de UI

        btn = Button(btn_img, Vector2(SCREEN_WIDTH-64*5, SCREEN_HEIGHT-64*4), 64*5, self.play, (58*5, 21*5))      

        #inicializacao dos Sistemas

        progression = Progression() 

        # adicao na cena

        #self.main_scene.add_ui_item(get_dialogue_panel())        
        self.game_scene.add_system("progression", progression)
        self.game_scene.add_ui_blackboarded(btn, "play_btn")
        self.load_phase(progression.PHASES[0])

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

            self.screen.fill((0x17, 0x18, 0x1d))
            self.game_scene.run(self.screen, delta, events)

            self.fps = clock.get_fps()
            if self.fps < 30:
                print(f"WARNING FPS: {self.fps}")
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        EventBus.emit(Events.GAME_STARTED)
        self.game_scene.get_blackboard_entity("earth", MovingObject).run()      
        self.game_scene.get_blackboard_entity("sat", MovingObject).run()      
        self.game_scene.get_blackboard_entity("play_btn", Button).visible = False # TODO adicionar o ui blackboard

    def load_phase(self, phase: Phase):
        self.game_scene.clear_entities()
        for entity in phase.default_entities:
            self.game_scene.add_entity(entity)

GAME = Game()