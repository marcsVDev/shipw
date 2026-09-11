import pygame

from initializations.enemy_waves import get_enemy_registry
from system.wave_system import WaveSystem
from events.events import Events
from game_consts import BACKGROUND_MUSIC_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from initializations.ui_inits import get_initial_menu_background, get_play_button
from events.event_bus import EventBus
from ui.title import Title
from ui.ui import UI
from ui.wave_status import WaveStatus
from util.phase import Phase
from util.progresssion import Progression
from util.scene import Scene

class Game:
    FPS = 60
    FILL_COLOR = (0,0,0) #(0x4d, 0x9b, 0xe6)
    BACKGROUND_MUSIC_VOLUME = 0.35

    def __init__(self):
        pygame.init()  
        pygame.display.set_caption("Projeto Cosmonauta")
        pygame.mixer.init()
        self.start_background_music()

        EventBus.connect(Events.PHASE_CHANGED, self.load_phase)

        # propriedades
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.scenes: dict[str, Scene] = {}
        self.current_scene: str = "menu"
        self.running = True

        inital_menu = Scene(game_scene=False) 

        inital_menu.add_ui(get_play_button(self.play))
        inital_menu.add_entity(get_initial_menu_background())
        inital_menu.add_ui(Title())
        self.scenes["menu"] = inital_menu

        game_scene = Scene(game_scene=True)

        progression = Progression()
        
        game_scene.add_system("progression", progression)
        game_scene.add_system("waves", WaveSystem(game_scene, get_enemy_registry()))
        self.scenes["game"] = game_scene

        # main loop

        self.loop()

        pygame.mixer.music.stop()
        pygame.quit()

    def start_background_music(self):
        """Inicia uma única trilha contínua para menu e campanha."""
        pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
        pygame.mixer.music.set_volume(self.BACKGROUND_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

    def loop(self):        
        clock = pygame.time.Clock()
        delta = 0  

        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

            self.screen.fill(self.FILL_COLOR)
            self.scenes[self.current_scene].run(self.screen, delta, events)

            self.fps = clock.get_fps()
            if self.fps < 30:
                print(f"WARNING FPS: {self.fps}")
            
            pygame.display.flip()

            delta = clock.tick(self.FPS) / 1000

    def play(self):
        if self.current_scene != "menu":
            return
        EventBus.emit(Events.GAME_STARTED) 

        self.load_phase(self.scenes["game"].get_system("progression", Progression).phases[0])
        self.scenes["game"].destroy_entity("play_btn")
        self.change_scene_to("game")

    def handle_keydown(self, key: int):
        if self.current_scene == "menu" and key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.play()
        elif self.current_scene == "game" and key == pygame.K_ESCAPE:
            self.return_to_menu()

    def return_to_menu(self):
        """Limpa a partida atual e prepara uma campanha nova para o próximo play."""
        if self.current_scene != "game":
            return
        game_scene = self.scenes["game"]
        game_scene.clear_scene()
        game_scene.get_system("waves", WaveSystem).reset()
        game_scene.get_system("progression", Progression).reset()
        self.change_scene_to("menu")

    def load_phase(self, phase: Phase):
        game_scene = self.scenes["game"]
        game_scene.clear_scene()
        print(phase.name)
        for key in phase.default_entities.keys():
            match phase.default_entities[key]:
                case UI():
                    game_scene.add_ui(phase.default_entities[key], key)
                case _:
                    game_scene.add_entity(phase.default_entities[key], key)

        game_scene.player.free_movement = phase.free_movement
        game_scene.get_system("waves", WaveSystem).load_phase(phase)
        game_scene.add_ui(WaveStatus(game_scene.get_system("waves", WaveSystem)))

    def change_scene_to(self, name: str):
         self.current_scene = name
         
if __name__ == "__main__":
    GAME = Game()
