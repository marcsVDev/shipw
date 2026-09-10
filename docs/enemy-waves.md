# Inimigos e rodadas

A jornada segue seis fases. As quatro fases de combate têm três ondas cada,
com 12 a 18 inimigos simultâneos. Estação e chegada não têm ondas nem controle
livre e usam `duration` para concluir a apresentação.

| Fase | Inimigos ativos | Pendentes |
| --- | --- | --- |
| Estação Krasny Mir | Nenhum | — |
| Estratosfera | Gaivotas e asteroides (sprite de meteoro existente) | — |
| Espaço Próximo | Drones | Satélite quebrado e Buran |
| Espaço Profundo | Drones e minas gravitacionais | Novos drones e alienígena |
| Órbita de Marte | Drones de escolta | Nave-mãe/boss |
| Chegada a Marte | Nenhum | Arte e cena final |

`planned_enemies` em cada `Phase` documenta conteúdo futuro; essas chaves
não são registradas nem instanciadas. O espaço profundo e a órbita reutilizam
provisoriamente o fundo espacial disponível, rolando para baixo. A chegada
usa uma tela de texto estática. A campanha atual permite passar pela escolta
e chegar à tela final: isso não representa a implementação da nave-mãe.

Gaivotas e drones atacam somente por contato, investida ou passagem rápida;
eles não disparam projéteis. Asteroides são perigos de contato. Minas atraem
o jogador enquanto estão no raio de influência. A regra atual continua sendo
sobrevivência: contato com inimigos que possuem colisão mata e cada onda acaba
quando todos completam sua trajetória.

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

`FlyBy(start, end, speed=2200)` cria as passagens rápidas. O inimigo nasce um
pouco além de uma borda, já se move em velocidade constante e é destruído ao
ultrapassar a borda oposta. `fly_by_path(..., "horizontal")` distribui faixas
no eixo Y; `fly_by_path(..., "vertical")` distribui colunas no eixo X. Novos
eixos inválidos geram erro imediatamente.

## Mina espacial e forças externas

`MineEnemy` importa e herda diretamente de `Enemy`. Ela configura somente o
sprite e suas dimensões; `MIDDLE_VERTICES = []` é intencional e marca o ponto
em que o contorno deverá ser implementado. Enquanto a lista estiver vazia,
`Scene` ignora a colisão física da mina, mas seu comportamento continua ativo.

`AttractionAttack(strength=2400, radius=650, minimum_distance=90)` calcula uma
aceleração apontada do jogador para a mina. Dentro do raio, chama
`player.apply_force(acceleration)`. O `Player` acumula forças externas durante
o frame, aplica-as à velocidade no movimento seguinte e limpa o acumulador.
Isso permite criar gravidade, vento ou repulsão sem colocar regras específicas
de inimigo dentro do jogador. Para repulsão, passe o vetor na direção inversa
em outro comportamento.

## Rotação para olhar o jogador

Toda subclasse de `Enemy` possui a constante `LOOK_AT_PLAYER`. Com `False`, a
rotação vem do padrão de movimento. Com `True`, o inimigo consulta o provider
do alvo a cada atualização e gira para olhar a posição atual do jogador.
`DroneEnemy` e `GaivotaEnemy` deixam essa opção ativa; asteroides e minas deixam
inativa. Uma nova classe escolhe o comportamento apenas declarando
`LOOK_AT_PLAYER = True` ou `False`.

O cálculo considera que o sprite aponta para baixo quando a rotação é zero.
`Character.update()` gira a imagem e depois recria `_collider_vertices` usando
a mesma rotação com a convenção de coordenadas do Pygame. Assim o polígono de
colisão acompanha visualmente o inimigo. Classes sem vértices, como a mina
atual, continuam sem colisão até receberem seu contorno.

## Adicionar um inimigo

1. Crie uma subclasse de `Enemy`, configurando sprite, `FRAME_SIZE`, escala,
   som opcional e `MIDDLE_VERTICES`, como `MineEnemy`.
2. Registre a factory em `get_enemy_registry()`:
   `registry.register("novo", NovoEnemy)`.
3. Use a chave em um `EnemySpawn` ou na lista `species` de `make_wave`.

Nenhuma alteração em `Scene`, `WaveSystem` ou `Progression` é necessária.
O registro rejeita chaves duplicadas e informa nomes desconhecidos.

## Criar padrões e ataques

`EnemySpawn(enemy, movement, attack)` recebe factories sem argumentos.
`movement()` retorna uma lista nova de `EnemyPattern` (por exemplo,
`MoveTo`, `Wait`, `Rotate`, ou padrões carregados do Tiled).
`attack()` retorna um comportamento novo ou `None` para não executar ataque.
Factories evitam compartilhar temporizadores entre instâncias/rodadas.

Um ataque implementa `update(enemy, player, delta, emit_projectile)`.
O método pode chamar `player.apply_force`, alterar o estado do inimigo ou usar
`emit_projectile(entity)` para inserir uma entidade na cena sem depender de
`Scene`. Cada instância deve guardar apenas seu próprio temporizador/estado.
`AttractionAttack` é o exemplo sem projétil. `VolleyAttack` permanece disponível
na API para inimigos futuros, com intervalo, velocidade, ângulos, mira e atraso,
mas não está atribuído a drones ou gaivotas nas ondas atuais.

Para adicionar um ataque, crie a classe com esse método e passe sua factory no
terceiro campo de `EnemySpawn`, por exemplo
`partial(MeuAtaque, intensidade=100)`. Use `no_attack` quando o movimento já é
o ataque. A factory deve construir um objeto novo para cada inimigo.

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
