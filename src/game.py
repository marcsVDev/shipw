import pygame
from pygame import Vector2

from entities.enemy import Enemy
from entities.player import Player
from entities.vscroller import VScroller
from events.events import Events
from game_consts import GameConsts
from ui.button import Button
from events.event_bus import EventBus
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

        back_img = pygame.transform.scale(pygame.image.load(GameConsts.ASSETS_PATH + "background.jpg"), (1920, 1080))
        btn_img = pygame.transform.scale_by(pygame.image.load(GameConsts.ASSETS_PATH + "button.png"), 5)

        # inicializacao das entidades
    
        player = Player()
        player.can_move = False
        enemys = []
        for i in range(8):
            enemys.append(Enemy(Vector2(i*256, 0), Vector2(GameConsts.SCREEN_WIDTH-(i*268), GameConsts.SCREEN_HEIGHT)))

        back = VScroller(back_img, 1000)     
        btn = Button(btn_img, Vector2(GameConsts.SCREEN_WIDTH//2, GameConsts.SCREEN_HEIGHT//2), 32*5, self.play)      

        # adicao na cena                  

        self.main_scene.add_ui_blackboarded(btn, "play_btn")
        self.main_scene.add_entity_blackboarded(back, "background")        
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

            self.screen.fill((255, 255, 255))
            self.main_scene.run(self.screen, delta, events)
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        EventBus.emit(Events.GAME_STARTED)
        self.main_scene.get_blackboard_entity("background", VScroller).run()        
        self.main_scene.get_blackboard_entity("play_btn", Button).visible = False

GAME = Game()