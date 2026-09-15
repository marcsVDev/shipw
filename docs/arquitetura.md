# Arquitetura atual

## Visão geral

`src/game.py` cria duas cenas: `menu` e `game`. O loop roda a 60 FPS, coleta
eventos do Pygame, delega atualização/desenho à cena ativa e apresenta o frame.
O delta de tempo é convertido para segundos e entregue aos sistemas e entidades.

```text
Game
 ├─ Scene(menu): fundo, título e botão Play
 └─ Scene(game)
     ├─ Progression: escolhe e avança fases
     ├─ WaveSystem: agenda e conclui ondas
     ├─ entidades: Player, Enemy, Background, scrollers, projéteis
     └─ UI: título da fase e estado de onda
```

## Ciclo de fases

Ao iniciar, `Game.play()` emite `GAME_STARTED`, carrega a primeira `Phase` e
troca para a cena de jogo. `Progression` mantém o índice da campanha. Cada
fase fornece entidades padrão, ondas opcionais, duração e `free_movement`.

`Game.load_phase()` limpa a cena anterior, adiciona as entidades da nova fase,
aplica a permissão de movimento ao jogador e entrega a fase ao `WaveSystem`.
Quando o sistema de ondas emite `PHASE_COMPLETED`, `Progression` carrega a
próxima. Depois da sexta fase, emite `GAME_COMPLETED`; atualmente esse evento
não possui uma tela de encerramento conectada.

Para cenas sem ondas, `duration` é a contagem até a conclusão. Em fases de
combate, o sistema inicia a primeira onda após 2 s e troca de onda após o
`rest` configurado em cada `Wave`.

## Atualização de cena

Em cada frame, `Scene.run()` executa, nesta ordem:

1. sistemas;
2. entidades;
3. remoção das entidades marcadas para destruição;
4. colisões, apenas na cena de jogo;
5. atualização da UI;
6. desenho de entidades e UI.

`Scene` mantém listas de entidades, inimigos e itens de UI, uma referência ao
jogador e uma blackboard por nome. O método `clear_scene()` destrói entidades
antes de limpar as coleções, importante para desconectar eventos e parar sons.

## Entidades e colisão

`Entity` define o contrato mínimo de atualização, desenho e destruição.
`Character` acrescenta sprite animado, escala, rotação e colisor. `Player` lê
WASD, limita sua posição à tela e aceita acelerações externas via
`apply_force`. `Enemy` executa uma sequência de padrões e pode receber um
ataque independente.

Antes do teste SAT, a cena faz uma triagem por alcance. Em seguida,
`Collidable` usa os vértices poligonais já rotacionados. Inimigos ou projéteis
que tocam o jogador emitem `PLAYER_COLLIDE`; o jogador se destrói. Uma entidade
sem vértices de colisor não participa da colisão.

## Ondas, padrões e ataques

`Wave` contém `EnemySpawn`s e intervalo de descanso. Cada spawn descreve uma
chave de inimigo e factories de movimento e ataque. `EnemyRegistry` resolve a
chave para uma classe concreta e constrói uma instância isolada: padrões e
ataques não podem compartilhar estado entre spawns.

`WaveSystem` mantém spawns pendentes e inimigos ativos. Ele passa um provider
da posição do jogador aos padrões para que investidas e mira não dependam da
cena. A onda termina quando não há pendências, inimigos ativos nem projéteis
vivos; ao fim da última onda, a fase é concluída.

Os builders de `src/enemys/behaviors.py` produzem as formações usadas pela
campanha. Os padrões ficam em `src/enemys/patterns/` e os ataques em
`src/enemys/attacks.py`. Consulte [enemy-waves.md](enemy-waves.md) para o
catálogo e instruções de extensão.

## Eventos

O `EventBus` é um canal simples de assinaturas em memória. Os eventos atuais
são `GAME_STARTED`, `PLAYER_COLLIDE`, `PHASE_CHANGED`, `PHASE_COMPLETED`,
`WAVE_STARTED`, `WAVE_COMPLETED` e `GAME_COMPLETED`. Inscrições devem ser
desconectadas na destruição de objetos de vida curta.

## Recursos e testes

Os caminhos de recursos são centralizados em `src/game_consts.py`; `assets/`
contém sprites, cenários, UI, fontes e SFX. Os testes em `tests/` usam SDL
dummy e cobrem navegação, progressão, ondas, padrões e novas mecânicas de
inimigos. Execute-os com:

```powershell
python -B -m unittest discover -s tests -v
```
