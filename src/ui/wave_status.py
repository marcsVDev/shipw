from initializations.misc import get_font
from ui.ui import UI


class WaveStatus(UI):
    def __init__(self, waves):
        super().__init__(position=(24, 80))
        self.waves = waves
        self.font = get_font(26)

    def draw(self, screen):
        system = self.waves
        if system.phase is None:
            return
        if system.scene.player is None:
            text = "Fim de jogo"
        elif not system.phase.waves:
            text = "Missao concluida" if system.finished else system.phase.name
        elif system.finished:
            text = "Todas as ondas concluidas"
        elif system.index < 0:
            text = "Prepare-se"
        else:
            wave = system.phase.waves[system.index]
            alive = sum(not enemy.to_destroy for enemy in system.active)
            text = f"Rodada {system.index + 1}/{len(system.phase.waves)} - {wave.name} - {alive} inimigos"
        screen.blit(self.font.render(text, True, (255, 235, 180)), self.position)
