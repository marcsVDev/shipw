import pygame
from pygame import Vector2

from event_bus import EventBus
from player import Player
from scene import Scene
from vscroller import VScroller

pygame.init()
screen = pygame.display.set_mode((1920, 1080))

running = True
clock = pygame.time.Clock()
delta = 0

back_img = pygame.image.load("background.jpg")
back_img = pygame.transform.scale(back_img, (1920, 1080))

player = Player()
back = VScroller(back_img, 500, True)
main_scene = Scene()

main_scene.add_entity(back)
main_scene.add_entity(player)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    main_scene.run(screen, delta)
    
    pygame.display.flip()

    delta = clock.tick(60) / 1000


pygame.quit()

