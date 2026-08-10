from dataclasses import dataclass

import pygame
from pygame import Vector2

from button import Button
from event_bus import EventBus
from player import Player
from scene import Scene
from vscroller import VScroller


class Game:   
    def __init__(self):
        pygame.init()  
        self.screen = pygame.display.set_mode((1920, 1080)) 

        # inicializacao de imagens

        back_img = pygame.transform.scale(pygame.image.load("background.jpg"), (1920, 1080))
        btn_img = pygame.transform.scale_by(pygame.image.load("button.png"), 5)

        # inicializacao das entidades
    
        player = Player()
        back = VScroller(back_img, 500, True)
        btn = Button(btn_img, Vector2(0, 0), 32 * 5, None)
        self.main_scene = Scene()       

        # adicao na cena                  

        self.main_scene.add_ui_item(btn)
        self.main_scene.add_entity(back)
        self.main_scene.add_entity(player)

        # main loop

        self.loop()
        pygame.quit()

    def loop(self):
        running = True
        clock = pygame.time.Clock()
        delta = 0  

        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((255, 255, 255))
            self.main_scene.run(self.screen, delta, events)
            
            pygame.display.flip()

            delta = clock.tick(60) / 1000

Game()

