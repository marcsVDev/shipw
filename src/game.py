import pygame
from pygame import Vector2

from entities.enemy import Enemy
from entities.player import Player
from entities.scrollers.moving_object import MovingObject
from events.events import Events
from game_consts import ASSETS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.scenery import get_earth_scenery
from ui.button import Button
from events.event_bus import EventBus
from util.progresssion import Progression
from util.scene import Scene

class Game:
    FPS = 60

    def __init__(self):
        pygame.init()  
        pygame.display.set_caption("Shipw")

        # propriedades
        self.screen = pygame.display.set_mode((1920, 1080))         
        self.main_scene = Scene()
        self.running = True

        # inicializacao de imagens
        btn_img = pygame.transform.scale_by(pygame.image.load(ASSETS_PATH + "play.png"), 5)

        # inicializacao das entidades
    
        player = Player()
        player.can_move = False
        enemys = []
        for _ in range(1):
            enemys.append(Enemy())

        
        #inicialização de UI

        btn = Button(btn_img, Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 64*5, self.play, (58*5, 21*5))      

        #inicializacao dos Sistemas

        progression = Progression() 

        # adicao na cena

        self.main_scene.add_system("progression", progression)
        self.main_scene.add_ui_blackboarded(btn, "play_btn")
        self.main_scene.add_entity_blackboarded(get_earth_scenery(), "earth")        
        self.main_scene.add_entity(player)
        for enemy in enemys:
            self.main_scene.add_entity(enemy)

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
            self.main_scene.run(self.screen, delta, events)

            self.fps = clock.get_fps()
            if self.fps < 30:
                print(f"WARNING FPS: {self.fps}")
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        EventBus.emit(Events.GAME_STARTED)
        self.main_scene.get_blackboard_entity("earth", MovingObject).run()        
        self.main_scene.get_blackboard_entity("play_btn", Button).visible = False

GAME = Game()