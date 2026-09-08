# Inimigos e rodadas

A jornada segue seis fases. As quatro fases de combate têm três ondas cada,
com 12 a 18 inimigos simultâneos. Estação e chegada não têm ondas nem controle
livre e usam `duration` para concluir a apresentação.

| Fase | Inimigos ativos | Pendentes |
| --- | --- | --- |
| Estação Krasny Mir | Nenhum | — |
| Estratosfera | Gaivotas e asteroides (sprite de meteoro existente) | — |
| Espaço Próximo | Drones | Satélite quebrado e Buran |
| Espaço Profundo | Drones existentes | Novos drones, minas e alienígena |
| Órbita de Marte | Drones de escolta | Nave-mãe/boss |
| Chegada a Marte | Nenhum | Arte e cena final |

`planned_enemies` em cada `Phase` documenta conteúdo futuro; essas chaves
não são registradas nem instanciadas. O espaço profundo e a órbita reutilizam
provisoriamente o fundo espacial disponível, rolando para baixo. A chegada
usa uma tela de texto estática. A campanha atual permite passar pela escolta
e chegar à tela final: isso não representa a implementação da nave-mãe.

Gaivotas atacam por contato e investida; asteroides são perigos de contato,
sem disparos artificiais. Drones combinam projéteis e investidas. A regra
atual continua sendo sobrevivência: contato mata, inimigos saem ao terminar
a trajetória e cada onda espera também seus projéteis desaparecerem.

## Investidas direcionadas

`Charge(position, speed=1800, warning=.55, duration=2.5)` é um `EnemyPattern`.
A factory recebe o alvo via `EnemyRegistry.create(spawn, target=provider)`.
O provider retorna uma posição ou `None`; não conhece a cena. `WaveSystem`
fornece a posição do jogador ativo. Padrões antigos ignoram esse contexto.

Após entrar em formação, os inimigos aguardam intervalos escalonados. Um
anel vermelho avisa a investida. Ao acabar o aviso, capturam a posição atual
do jogador e seguem em linha reta, sem perseguição contínua. As velocidades
são 1900 px/s (gaivotas), 2100 (espaço próximo), 2300 (profundo) e 2500
(órbita). Sem alvo, seguem para baixo; o padrão sempre termina.

## Adicionar um inimigo

1. Crie uma subclasse de `Enemy`, configurando sprite, escala e colisão,
   como `DroneEnemy` e `GaivotaEnemy`.
2. Registre a factory em `get_enemy_registry()`:
   `registry.register("novo", NovoEnemy)`.
3. Use a chave em um `EnemySpawn` ou na lista `species` de `make_wave`.

Nenhuma alteração em `Scene`, `WaveSystem` ou `Progression` é necessária.
O registro rejeita chaves duplicadas e informa nomes desconhecidos.

## Criar padrões e ataques

`EnemySpawn(enemy, movement, attack)` recebe factories sem argumentos.
`movement()` retorna uma lista nova de `EnemyPattern` (por exemplo,
`MoveTo`, `Wait`, `Rotate`, ou padrões carregados do Tiled).
`attack()` retorna um comportamento novo ou `None` para desativar disparos.
Factories evitam compartilhar temporizadores entre instâncias/rodadas.

Um ataque implementa `update(enemy, player, delta, emit_projectile)`.
`VolleyAttack` oferece intervalo, velocidade, ângulos de abertura,
mira no jogador ou direção fixa e atraso inicial. A mira é definida no
instante do disparo; projéteis não perseguem o jogador. `emit_projectile`
insere a entidade na cena, sem acoplar o ataque à implementação da cena.

`Wave(name, spawns, rest=2)` define uma rodada. Passe uma tupla de ondas
em `Phase(..., waves=...)`. `starts_at` permanece por compatibilidade. `duration` só controla fases sem
ondas; nas fases de combate, a última onda controla a transição.
`free_movement=False` bloqueia o controle do jogador nas cenas de abertura e chegada.

`WaveSystem` gerencia rodadas; `EnemyRegistry` cria inimigos; os padrões
movem; os ataques disparam; `Scene` atualiza/remove entidades e verifica
colisões; `Progression` avança as fases. O Event Bus publica
`WAVE_STARTED(phase, index, wave)`, `WAVE_COMPLETED(phase, index)`,
`PHASE_COMPLETED(phase)` e `GAME_COMPLETED()` (índices a partir de zero).

## Validação

Na raiz, com Python 3.12+ e pygame-ce instalado:

```sh
python -B -m unittest discover -s tests -v
```

A simulação usa vídeo/áudio dummy e percorre as doze ondas com um alvo
imortal para verificar a progressão completa. Outros testes verificam
colisão letal, mira, expiração, ausência de spawns sem jogador, isolamento
dos comportamentos emissão única de conclusão, elenco por fase, bloqueio de movimento e mira
fixada após o aviso da investida. A dificuldade exige
playtest humano; a simulação não mede a possibilidade de desviar de tudo.
