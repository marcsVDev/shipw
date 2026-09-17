# PDR de implementação — Sistema de vida e Nave-Mãe

## 1. Identificação

**Projeto:** Shipw  
**Funcionalidade:** vida global da campanha e boss fight da Nave-Mãe  
**Fase:** Órbita de Marte  
**Resolução-base:** 1920×1080  
**Modelo de jogo:** sobrevivência e sabotagem, sem disparo do jogador

## 2. Resumo executivo

Valentina encontra em órbita de Marte uma nave-mãe estadunidense controlada
por robôs. O chefe ocupa permanentemente a parte superior da tela e coordena
gaivotas-robô, naves de escolta, naves laser e mísseis teleguiados.

Valentina não recebe uma arma. Para destruir o chefe, ela deve atrair os
mísseis teleguiados contra uma abertura vulnerável da própria nave-mãe. O
míssil é mais rápido que a nave da jogadora em linha reta, mas gira mais
devagar; a habilidade exigida é acelerar, cruzar diante do alvo vulnerável e
fazer uma esquiva lateral no último instante.

A luta não possui estágios ou transformações disparadas pela vida do chefe.
Ela é um combate contínuo, governado por uma sequência circular de ondas. A
Nave-Mãe mantém uma única barra de 5 pontos de integridade e repete sua lista
de ataques até ser destruída.

Em toda a campanha, Valentina passa a possuir uma única barra de 3 pontos de
vida. O dano não reinicia uma onda e não cria vidas ou respawns separados. Ao
chegar a zero, a campanha termina.

## 3. Objetivos

- Substituir a morte instantânea do jogador por 3 HP durante toda a campanha.
- Preservar o HP atual durante trocas de fase.
- Criar uma boss fight vencida integralmente por movimentação e esquiva.
- Fazer o míssil teleguiado funcionar como perigo e como arma indireta.
- Usar ondas complexas, determinísticas, legíveis e possíveis de desviar.
- Reutilizar a arquitetura de factories, providers de alvo e Event Bus.
- Manter movimento e temporizadores independentes da taxa de quadros.
- Oferecer valores configuráveis para balanceamento sem alterar algoritmos.

## 4. Fora do escopo

- Tiro, munição ou arma ofensiva para Valentina.
- Pontuação, multiplicador, ranking ou itens coletáveis.
- Estágios do chefe determinados por porcentagens de vida.
- Dificuldade adaptativa ou padrões gerados proceduralmente sem limites.
- Checkpoints dentro da campanha.
- Cura automática entre fases.
- Novas cutscenes, diálogos ou arte final de Marte.

## 5. Decisões fechadas

| Tema | Decisão |
| --- | --- |
| Vida de Valentina | 3 HP por campanha |
| Persistência | HP atravessa todas as fases |
| Cura entre fases | Nenhuma |
| Dano padrão | 1 HP por impacto |
| Morte | 0 HP encerra a campanha atual |
| Ataque do jogador | Nenhum |
| Vida da Nave-Mãe | 5 pontos de integridade |
| Dano no chefe | 1 ponto por míssil armado no alvo vulnerável |
| Estrutura do boss | Contínua, sem estágios por HP |
| Continuidade das ondas | Playlist circular até o chefe chegar a 0 HP |
| Mísseis simultâneos | No máximo um |
| Resolução | Valores calibrados para 1920×1080 |

## 6. Experiência desejada

O jogador deve perceber que entrou no território de uma inteligência militar
automatizada. Cada onda parece uma tentativa deliberada de conduzir Valentina
para uma armadilha. Ao mesmo tempo, todos os ataques comunicam antecipadamente
onde ocorrerão e deixam pelo menos uma solução espacial.

A sequência emocional pretendida é:

1. surpresa pela escala da Nave-Mãe;
2. compreensão de que não é possível atirar nela;
3. descoberta de que o míssil pode voltar contra o lançador;
4. domínio progressivo da esquiva de última hora;
5. pressão causada pela sobreposição de formações e lasers;
6. satisfação ao provocar o quinto impacto e desmontar a máquina.

## 7. Sistema global de vida

### 7.1 Estado da campanha

Criar um objeto de estado da campanha, referido neste documento como
`RunState`. Ele é a fonte única de verdade para:

- `max_health = 3`;
- `health`, iniciado em 3;
- `is_game_over`;
- reinício da campanha;
- aplicação de dano;
- futura expansão de dados persistentes da partida.

O estado não deve pertencer a `Player`, `Phase` ou a uma `Scene`. O objeto
deve sobreviver a `Game.load_phase()`, pois esse método limpa a cena e troca a
instância de `Player`.

Ao selecionar Play no menu, `RunState.reset()` define `health = max_health` e
`is_game_over = False`. Trocar de fase não restaura HP. Voltar ao menu e iniciar
uma nova campanha restaura os 3 HP.

### 7.2 Aplicação de dano

Todo perigo jogável causa 1 HP, salvo configuração explícita futura:

- inimigos por contato;
- asteroides e satélite quebrado;
- minas;
- projéteis;
- raios laser;
- míssil teleguiado;
- corpo da Nave-Mãe, caso o jogador alcance seu colisor.

Ao detectar uma ou mais colisões no mesmo frame, aplicar no máximo uma unidade
de dano. Não multiplicar o dano pela quantidade de colisores retornados por
`Scene.check_collisions()`.

Sequência obrigatória de um acerto:

1. ignorar o evento se God Mode estiver ativo;
2. ignorar o evento se o jogador estiver invulnerável;
3. retirar 1 HP do `RunState`;
4. iniciar invulnerabilidade por 1,5 s;
5. iniciar pisca visual por 1,5 s, alternando a cada 0,10 s;
6. aplicar impulso curto para longe do centro médio das ameaças;
7. emitir o evento de dano;
8. se o HP chegar a zero, emitir morte uma única vez.

O impulso não pode ultrapassar os limites da tela nem retirar o controle do
jogador. Valor inicial recomendado: `420 px/s`, somado à velocidade atual e
imediatamente limitado à velocidade máxima normal.

### 7.3 Invulnerabilidade

- Duração: 1,5 s.
- Durante a janela, colisões continuam sendo calculadas, mas não causam dano.
- Projéteis comuns são consumidos ao acertar.
- Inimigos de contato não precisam ser destruídos.
- Lasers permanecem ativos; podem causar novo dano depois da janela caso o
  jogador continue dentro do feixe.
- O míssil explode no primeiro contato, mesmo se o jogador estiver
  invulnerável, mas não reduz HP durante essa janela.
- God Mode continua bloqueando todo dano e não altera o HP.

### 7.4 Morte e derrota

Ao chegar a 0 HP:

- destruir a nave da jogadora;
- parar novos spawns e temporizadores de ondas;
- remover ou congelar perigos ativos;
- mostrar o texto `MISSÃO FRACASSOU`;
- mostrar `ENTER — REINICIAR` e `ESC — MENU`;
- Enter cria uma nova campanha desde a Estação Krasny Mir com 3 HP;
- Esc retorna ao menu;
- nenhum evento de conclusão de onda ou fase pode ser emitido após a morte.

### 7.5 Interface de vida

Exibir no canto superior esquerdo, com margem de 36 px:

```text
VALENTINA  [████████████] 3/3
```

Especificação visual:

- caixa: 360×34 px;
- contorno: 3 px, branco;
- preenchimento proporcional ao HP atual;
- 3 HP: verde `#5ac54f`;
- 2 HP: amarelo `#f9c22b`;
- 1 HP: vermelho `#ae2334`, pulsando entre 70% e 100% de opacidade;
- 0 HP: vazia;
- texto em português usando a fonte existente;
- atualização dirigida por estado/evento, não por reconstrução por frame;
- visível nas quatro fases de combate;
- oculta no menu, na apresentação inicial e na tela final.

## 8. Nave-Mãe

### 8.1 Identidade e apresentação

Usar `assets/enemys/navemaeeua.png` como fonte visual. A Nave-Mãe é uma
aeronave estadunidense autônoma, comandada por robôs, sem tripulação humana.
Ela deve ocupar toda a faixa superior da arena, com largura visual entre 80% e
95% da tela e altura máxima próxima de 32% da tela.

Entrada:

1. a tela escurece levemente por 0,4 s;
2. um alerta vermelho aparece por 1,2 s;
3. a Nave-Mãe desce de `y = -altura/2` até sua posição de combate em 2,5 s;
4. durante a entrada não existem colisões nem ataques;
5. ao estabilizar, a barra de integridade aparece e a primeira onda começa
   após 1,0 s.

Posição de combate recomendada: centro em `(960, 135)`. A escala final deve
ser determinada pela largura da imagem, preservando proporção e sem deformar o
asset.

### 8.2 Integridade

- Integridade máxima: 5.
- Integridade inicial: 5.
- Dano aceito: exclusivamente impacto de míssil armado em alvo vulnerável.
- Dano por impacto válido: 1.
- Contato do jogador não causa dano ao chefe.
- Inimigos menores e lasers não causam dano ao chefe.
- A barra não cria estágios nem modifica estatísticas.

Interface central superior:

```text
NAVE-MÃE  [████████████████████] 5/5
```

A barra deve ficar abaixo da área visual do chefe, sem cobrir as comportas.
Ela pisca em branco por 0,15 s ao receber dano. Os valores de HP podem aparecer
para facilitar testes e permanecer na versão final.

### 8.3 Alvos vulneráveis

Existem cinco posições lógicas na mesma barra de integridade:

| Alvo | Centro relativo à tela | Uso visual |
| --- | --- | --- |
| Hangar esquerdo | `(0,29 W; 0,19 H)` | lançamento de gaivotas |
| Canhão esquerdo | `(0,40 W; 0,23 H)` | emissor laser |
| Núcleo central | `(0,50 W; 0,17 H)` | unidade de comando |
| Canhão direito | `(0,60 W; 0,23 H)` | emissor laser |
| Hangar direito | `(0,71 W; 0,19 H)` | lançamento de escoltas |

Os valores são âncoras de balanceamento e devem ser ajustados ao sprite após
inspeção visual. Cada alvo possui um colisor circular inicial de raio 52 px.

Somente um alvo fica vulnerável por vez. A playlist define qual deles abrirá.
Estados do alvo:

- `closed`: sem colisor de dano, luz apagada;
- `warning`: pisca em âmbar por 0,8 s;
- `open`: núcleo branco/vermelho exposto e colisor ativo;
- `hit`: flash branco de 0,20 s e explosão;
- `cooldown`: fechado até a próxima oportunidade.

O alvo permanece aberto desde 0,8 s antes do lançamento do míssil até o míssil
explodir ou expirar. Se o míssil atingir a blindagem, o alvo fecha normalmente.

### 8.4 Derrota

Ao receber o quinto impacto:

1. cancelar spawns futuros;
2. destruir todos os perigos ativos sem causar dano ao jogador;
3. bloquear novos danos por 4 s;
4. executar cinco explosões pequenas, espaçadas por 0,18 s;
5. executar uma explosão central;
6. mover a Nave-Mãe lentamente para cima ou fazê-la desaparecer em flash;
7. ocultar sua barra;
8. emitir `PHASE_COMPLETED` uma única vez;
9. avançar para Chegada a Marte.

## 9. Inimigos da boss fight

### 9.1 Gaivota-robô

**Chave de registro:** `robot_seagull`  
**Asset:** `assets/enemys/gaivotarobo.png`  
**Papel:** pressão rápida, formação e condução espacial  
**Dano:** 1 HP por contato  
**Ataque à distância:** nenhum

Requisitos:

- criar classe própria, sem substituir `GaivotaEnemy`;
- olhar para a direção do movimento durante formações e para o jogador durante
  uma investida telegrafada;
- possuir colisor poligonal ajustado ao sprite;
- usar escala inicial próxima de 128 px;
- desaparecer ao completar a trajetória ou ultrapassar uma margem de 200 px;
- emitir aviso sonoro antes de investidas, reutilizando SFX compatível até
  existir som próprio.

Padrões usados:

**V quebrado**

- 8 unidades, dois grupos de 4;
- entram pelos hangares com intervalo de 0,12 s;
- formam um V apontando para baixo;
- o lado esquerdo mergulha primeiro, o direito 0,45 s depois;
- velocidade de mergulho: 1.750 px/s;
- deixam aberto um corredor de pelo menos 260 px.

**Tesoura**

- 6 unidades, 3 por lateral;
- laterais entram simultaneamente;
- cruzam no terço inferior em diagonais opostas;
- pares separados por 0,38 s;
- velocidade: 1.600 px/s;
- cruzamentos nunca coincidem com o instante da esquiva final do míssil.

**Hélice dupla**

- 10 unidades, divididas em dois braços;
- trajetórias senoidais espelhadas em torno do centro;
- amplitude horizontal: 360 px;
- frequência: 0,55 Hz;
- velocidade vertical: 520 px/s;
- defasagem entre unidades: 0,18 s;
- corredor central mínimo: 220 px em algum ponto de cada oscilação.

**Funil**

- 8 unidades entram das quatro quinas laterais;
- convergem para a posição registrada do jogador;
- o alvo é capturado no início do aviso e não atualizado depois;
- aviso: 0,65 s;
- após convergir, continuam em linha reta e saem da tela;
- o centro real da formação deve permanecer desviável por uma mudança brusca.

### 9.2 Nave de escolta

**Chave:** reutilizar `drone`  
**Papel:** bloquear corredores e executar pinças  
**Dano:** 1 HP por contato

Não criar outro inimigo se o `DroneEnemy` existente atender ao papel. Usar os
builders e padrões já disponíveis, com configurações próprias da boss fight.

Padrões:

**Pinça orbital**

- 6 drones, 3 por lado;
- entram até `y = 0,38 H`;
- aguardam 0,5 s;
- pares opostos investem em posições registradas do jogador;
- intervalo entre pares: 0,65 s;
- velocidade: 2.300 px/s;
- aviso de investida: 0,6 s.

**Portões móveis**

- 6 drones em duas colunas;
- colunas deslocam-se em direções verticais opostas;
- abertura entre colunas: pelo menos 300 px;
- após 4,5 s, saem pelas laterais;
- não usam projéteis.

### 9.3 Nave laser

**Chave de registro:** `laser_ship`  
**Base visual:** reutilizar `EvilDroneEnemy` e
`assets/enemys/navedomal-sheet.png` se a direção artística for compatível  
**Papel:** dividir a arena e restringir rotas  
**Dano:** 1 HP enquanto o jogador não estiver invulnerável

Estados:

1. `entering`: move-se até a âncora sem raio;
2. `charging`: animação de preparação e linha de aviso;
3. `firing`: raio com colisor;
4. `cooldown`: raio desligado;
5. `leaving`: sai pelo mesmo lado ou pela borda mais próxima.

Tempos padrão:

- entrada: 1,2 s;
- preparação: 0,9 s;
- disparo: 1,8 s;
- resfriamento: 0,5 s;
- saída: 1,1 s;
- largura visual do raio: 18 px;
- largura de colisão: igual à visual;
- o aviso deve mostrar exatamente a trajetória real do feixe.

Ataques:

**Corredor vertical**

- duas naves param no alto;
- emitem raios verticais paralelos;
- corredor livre entre os feixes: 340 px;
- o corredor é deslocado para um dos lados, alternando a cada uso.

**Varredura diagonal**

- uma nave para em uma quina superior;
- o raio gira por arco de 70°;
- preparação: 1,0 s;
- varredura: 2,2 s;
- velocidade angular constante;
- sempre existe espaço atrás do sentido da varredura.

**Portão convergente**

- duas naves em lados opostos;
- os raios começam afastados e giram em direção ao centro;
- distância mínima entre feixes: 280 px;
- os feixes não se cruzam;
- o portão abre novamente antes da próxima ameaça rápida.

Uma nave laser atingida por míssil armado é destruída junto com o míssil. Isso
abre espaço, mas não reduz a integridade da Nave-Mãe.

### 9.4 Míssil teleguiado

**Tipo:** perigo especial e arma indireta  
**Papel:** perseguir o jogador e causar dano no chefe  
**Quantidade simultânea:** 1  
**Representação inicial:** sprite próprio, se fornecido; na ausência dele,
desenho procedural de corpo branco, ponta vermelha e chama amarela

Estados:

1. `telegraph`: comporta pisca e mira aparece no jogador;
2. `launch`: sai da Nave-Mãe em trajetória inicial reta;
3. `seeking`: gira gradualmente para perseguir o jogador;
4. `expiring`: pisca antes de autodestruir;
5. `exploded`: aplica o resultado uma única vez e é removido.

Parâmetros iniciais:

| Parâmetro | Valor |
| --- | ---: |
| Aviso de lançamento | 1,0 s |
| Velocidade inicial | 550 px/s |
| Velocidade máxima | 1.450 px/s |
| Aceleração | 1.100 px/s² |
| Rotação máxima | 240°/s (ajustada após correção da perseguição) |
| Tempo para armar | 1,25 s |
| Duração de perseguição | 8,0 s |
| Aviso de expiração | últimos 0,8 s |
| Raio do colisor | 22 px |
| Raio da explosão visual | 96 px |
| Dano no jogador | 1 HP |
| Dano no chefe | 1 integridade |

Algoritmo de direção:

- calcular a direção desejada até a posição atual do jogador;
- calcular o menor ângulo assinado entre direção atual e desejada;
- limitar a mudança a `turn_rate * delta`;
- normalizar a direção resultante;
- aumentar a velocidade por `acceleration * delta` até `max_speed`;
- mover por `direction * speed * delta`;
- nunca definir diretamente a direção para o jogador;
- o cálculo deve produzir o mesmo comportamento em diferentes FPS.

O míssil não deve usar previsão da velocidade do jogador. A limitação angular
é a principal possibilidade de esquiva.

Telemetria visual:

- mira vermelha sobre Valentina durante `telegraph`;
- trilha amarela enquanto a ogiva não está armada;
- trilha vermelha após 1,25 s;
- brilho branco intermitente durante `expiring`;
- indicador discreto na borda se o míssil sair momentaneamente da tela;
- som de busca contínuo com frequência crescente ao se aproximar.

Colisões, avaliadas nesta prioridade:

1. alvo vulnerável aberto;
2. corpo blindado da Nave-Mãe;
3. nave laser;
4. jogador;
5. inimigo menor;
6. limite/expiração.

Resultados:

- alvo aberto + armado: -1 integridade no chefe;
- alvo fechado ou blindagem: explosão sem dano no chefe;
- nave laser: destrói nave laser e míssil;
- jogador vulnerável: -1 HP e destrói míssil;
- jogador invulnerável: destrói míssil sem reduzir HP;
- inimigo menor: destrói ambos, sem dano no chefe;
- míssil não armado: nunca causa dano ao chefe, mas ainda explode.

## 10. Regras globais de composição

Toda sequência complexa deve obedecer à gramática:

`aviso → ocupação do espaço → pressão → oportunidade de míssil → recuperação`

Restrições obrigatórias:

- nunca mais de um míssil ativo;
- nunca mais de dois raios ativos;
- nunca combinar varredura rápida com investida sem pelo menos 0,6 s de aviso;
- manter corredor navegável mínimo de 220 px;
- não gerar inimigos dentro de 260 px do jogador;
- não lançar míssil durante os 0,75 s posteriores a um dano no jogador;
- após explosão de míssil, reservar pelo menos 1,0 s sem nova ameaça rápida;
- limitar a 12 inimigos menores simultâneos;
- cada posição aleatória deve usar seed configurável em testes;
- perigos novos não podem surgir por baixo da interface;
- avisos devem permanecer legíveis sobre qualquer fundo da fase.

## 11. Playlist de ondas do chefe

A playlist é temporal e não representa estágios. A vida do chefe não altera
os padrões. Ao terminar a onda 7, voltar à onda 2 enquanto a Nave-Mãe ainda
tiver integridade. A onda 1 é tutorial e só ocorre uma vez.

Uma onda termina quando todos os spawns planejados acabaram e não existem
inimigos, lasers ou mísseis ativos. Restos devem terminar suas trajetórias; não
devem ser apagados silenciosamente na troca de onda.

### Onda 1 — Aquisição de alvo

**Objetivo:** ensinar a reversão do míssil.

- mostrar rapidamente a abertura vulnerável com pulso visual;
- abrir o hangar esquerdo;
- lançar 4 gaivotas-robô em V quebrado, sem mergulho;
- esperar a formação sair;
- lançar um míssil;
- manter o alvo aberto durante toda a vida do míssil;
- não usar lasers nem escoltas;
- descanso após o míssil: 1,8 s.

### Onda 2 — Tesoura americana

**Objetivo:** exigir mudança lateral durante perseguição.

- 6 gaivotas-robô no padrão Tesoura;
- lançar o míssil 1,1 s após o primeiro par cruzar;
- alvo vulnerável: hangar direito;
- o último cruzamento ocorre pelo menos 0,7 s antes da aproximação provável ao
  alvo;
- descanso: 1,3 s.

### Onda 3 — Corredor de execução

**Objetivo:** ensinar que o míssil também destrói naves laser.

- duas naves laser executam Corredor vertical;
- corredor com 340 px, deslocado para a esquerda na primeira execução e para a
  direita na repetição;
- lançar um míssil 0,5 s depois dos raios ativarem;
- alvo vulnerável: núcleo central;
- o jogador pode usar o míssil no chefe ou sacrificar a tentativa para destruir
  uma nave laser;
- desligar os raios antes de lançar outra ameaça;
- descanso: 1,5 s.

### Onda 4 — Pinça orbital

**Objetivo:** combinar alvos fixados com perseguição contínua.

- 6 drones em Pinça orbital;
- pares 1 e 2 investem antes do míssil;
- lançar o míssil junto do aviso do terceiro par;
- o terceiro par usa posição capturada; o míssil continua seguindo;
- alvo vulnerável: canhão esquerdo;
- descanso: 1,4 s.

### Onda 5 — Hélice bloqueadora

**Objetivo:** pressão de posicionamento sem tentativa de dano no chefe.

- 10 gaivotas-robô em Hélice dupla;
- uma nave laser executa Varredura diagonal lenta;
- não lançar míssil;
- fechar todos os alvos vulneráveis;
- duração máxima: 8 s;
- recuperação ampliada: 2,2 s.

### Onda 6 — Portão vermelho

**Objetivo:** esquiva final dentro de uma janela móvel.

- duas naves laser executam Portão convergente;
- lançar o míssil quando a distância entre feixes começar a aumentar;
- alvo vulnerável: canhão direito;
- 4 gaivotas-robô em V quebrado entram após o lançamento, sem investida;
- os feixes desligam 0,8 s antes do tempo máximo do míssil;
- descanso: 1,5 s.

### Onda 7 — Funil de comando

**Objetivo:** ápice de leitura sem aumentar estatísticas.

- 8 gaivotas-robô no padrão Funil;
- 4 drones formam Portões móveis;
- lançar o míssil 0,7 s depois da convergência das gaivotas;
- alvo vulnerável alterna entre hangar esquerdo, núcleo e hangar direito;
- somente um laser diagonal pode ser acrescentado, e apenas depois de playtest
  comprovar que há corredor seguro;
- descanso: 2,0 s.

### Repetição

Se o chefe ainda possuir integridade após a onda 7, repetir ondas 2 a 7. Não
aumentar velocidade, quantidade ou dano. Alternar lados e alvos por uma lista
determinística. A dificuldade vem do domínio dos padrões, não de escalada
infinita.

## 12. Fluxo completo da Órbita de Marte

1. carregar cenário, jogador com HP persistido e interfaces;
2. bloquear o diretor de ondas comum para esta fase;
3. executar entrada da Nave-Mãe;
4. iniciar playlist na onda 1;
5. manter a Nave-Mãe presente durante todas as ondas;
6. reduzir sua integridade apenas por impactos válidos;
7. repetir ondas 2–7 enquanto houver integridade;
8. executar derrota do chefe;
9. emitir conclusão da fase;
10. carregar Chegada a Marte preservando o HP, embora a barra fique oculta.

## 13. Arquitetura de implementação

### 13.1 Componentes novos sugeridos

```text
src/
  util/run_state.py
  system/boss_fight_system.py
  entities/guided_missile.py
  entities/mother_ship_target.py
  enemys/mother_ship_enemy.py
  enemys/robot_seagull_enemy.py
  ui/health_bar.py
  ui/boss_health_bar.py
  initializations/boss_waves.py
```

Os nomes podem ser ajustados às convenções locais, mas as responsabilidades
não devem ser misturadas.

### 13.2 Responsabilidades

**`RunState`**

- guarda HP da campanha;
- aplica dano e limita entre 0 e 3;
- reinicia a campanha;
- não conhece Pygame, Scene ou UI.

**`Player`**

- recebe referência/provider do estado;
- controla invulnerabilidade, pisca e impulso;
- não redefine HP no construtor;
- emite dano/morte sem destruir-se em qualquer contato.

**`HealthBar`**

- lê o estado ou reage a eventos;
- desenha a barra;
- não modifica HP.

**`MotherShipEnemy`**

- desenha e anima a nave;
- contém integridade e posições dos alvos;
- oferece operações `open_target`, `close_target` e `take_missile_hit`;
- não agenda ondas;
- nunca consulta diretamente a `Scene`.

**`GuidedMissile`**

- entidade com movimento, colisor e máquina de estados próprios;
- recebe provider do jogador e providers/objetos de colisão necessários;
- registra um único resultado de explosão;
- não conhece a progressão de fases.

**`BossFightSystem`**

- instancia e acompanha a Nave-Mãe;
- executa a playlist e seus atrasos;
- usa `EnemyRegistry` para inimigos menores;
- garante limites de simultaneidade;
- abre e fecha alvos;
- cria o míssil;
- conclui a fase somente após a morte do chefe;
- cancela tudo em derrota, menu ou troca de fase.

### 13.3 Integração com sistemas existentes

- Registrar `robot_seagull`, `laser_ship` e `mother_ship` em
  `get_enemy_registry()` quando forem construídos por factories.
- Reutilizar `drone`, `MoveTo`, `Wait`, `Charge`, `LaserSweep` e builders
  existentes sempre que seus contratos atendam ao padrão.
- Não colocar agendamento do boss em `Scene`.
- Na fase Órbita de Marte, `WaveSystem` não pode emitir conclusão automática.
- `BossFightSystem` torna-se o único emissor de `PHASE_COMPLETED` nessa fase.
- Outras fases continuam usando `WaveSystem` sem mudança de comportamento.
- `Scene.check_collisions()` deve distinguir dano no jogador de colisões
  especiais do míssil contra chefe e inimigos.
- Projéteis especiais não devem depender de `isinstance(EnemyProjectile)` para
  impedir conclusão prematura de ondas; introduzir contrato/tag de perigo
  ativo ou ampliar a verificação de forma explícita.

### 13.4 Eventos sugeridos

Adicionar:

- `PLAYER_DAMAGED(player, health, source)`;
- `PLAYER_DIED(player)`;
- `RUN_RESET()`;
- `BOSS_STARTED(boss)`;
- `BOSS_DAMAGED(boss, health, target)`;
- `BOSS_DEFEATED(boss)`.

Cada evento terminal deve ser emitido uma única vez. Objetos de vida curta
devem desconectar inscrições em `destroy()`.

## 14. Requisitos de colisão

- Preservar SAT para polígonos existentes.
- Criar uma forma clara de consultar categoria e dano da ameaça, evitando que
  toda colisão seja tratada como morte.
- A barra de vida não participa de colisões.
- O corpo da Nave-Mãe deve possuir colisor separado dos alvos vulneráveis.
- O corpo pode causar 1 HP ao jogador, mas nunca perder integridade pelo
  contato.
- O míssil deve fazer teste de movimento contínuo ou subpassos se atravessar
  alvos em um frame; a 1.450 px/s ele percorre cerca de 24 px a 60 FPS.
- Resolver somente uma explosão mesmo se o míssil sobrepuser dois alvos.
- Priorizar alvo vulnerável sobre blindagem para não rejeitar um acerto visual
  correto.

## 15. Áudio e feedback

Reutilizar sons existentes como placeholders sem apagar ou alterar assets.

Feedback mínimo:

- alarme de entrada do chefe;
- som de abertura de comporta;
- tom de aquisição do míssil;
- loop de perseguição do míssil;
- aviso distinto de laser;
- som de dano do jogador;
- explosão curta para impactos comuns;
- explosão mais grave para dano no chefe;
- pausa visual de 0,06 s no impacto válido, sem bloquear áudio ou eventos;
- leve tremor de tela por 0,18 s no dano do chefe e 0,45 s na derrota.

O jogo deve continuar funcional se um SFX novo ainda não existir. Não inventar
caminho para arquivo ausente.

## 16. Balanceamento e telemetria de desenvolvimento

Centralizar parâmetros em dataclasses imutáveis:

- `PlayerHealthConfig`;
- `MotherShipConfig`;
- `GuidedMissileConfig`;
- `RobotSeagullConfig`;
- `LaserShipConfig`;
- uma configuração por onda ou uma `BossWaveConfig` composta.

Em modo de depuração, permitir visualizar:

- collider do jogador;
- collider e vetor de direção do míssil;
- raio de giro previsto;
- alvo vulnerável ativo;
- corredores mínimos dos lasers;
- nome e tempo restante da onda;
- HP atual do jogador e do chefe.

Metas de playtest:

- primeiro jogador entende a reversão até a terceira tentativa;
- luta perfeita dura entre 90 e 150 s;
- uma tentativa média dura entre 2 e 4 minutos;
- o míssil alcança o jogador em reta, mas erra uma curva perpendicular bem
  executada;
- nenhuma combinação exige receber dano;
- o quinto impacto parece deliberado, não acidental.

## 17. Testes automatizados

### 17.1 Vida

- começa em 3;
- uma colisão reduz para 2, não destrói o jogador;
- múltiplos colisores no mesmo frame retiram apenas 1 HP;
- colisões durante 1,5 s não retiram HP;
- novo dano após a janela reduz novamente;
- HP nunca fica abaixo de zero nem acima de três;
- HP persiste após `PHASE_CHANGED`;
- nova campanha restaura 3;
- God Mode não altera HP;
- 0 HP emite morte uma única vez e impede progressão.

### 17.2 Míssil

- acelera sem ultrapassar 1.450 px/s;
- limita giro a 105°/s independentemente do delta;
- segue a posição atual do jogador;
- não causa dano ao chefe antes de 1,25 s;
- causa exatamente 1 ao acertar alvo aberto e armado;
- não causa dano ao acertar blindagem ou alvo fechado;
- destrói nave laser e é consumido;
- causa 1 HP ao jogador vulnerável;
- expira uma única vez após 8 s;
- não permanece referenciado após destruição.

### 17.3 Boss

- inicia com 5 de integridade;
- ignora contatos que não sejam míssil válido;
- abre somente um alvo por vez;
- não muda padrões com base em porcentagem de vida;
- volta da onda 7 para a 2;
- nunca mantém dois mísseis ativos;
- derrota ocorre exatamente no quinto impacto válido;
- `PHASE_COMPLETED` é emitido uma única vez após a animação final;
- não há spawns após derrota ou morte do jogador.

### 17.4 Regressão

- campanhas sem chegar ao boss preservam ondas existentes;
- fases comuns ainda terminam pelo `WaveSystem`;
- raios existentes continuam causando colisão;
- retorno ao menu limpa sons, entidades, pendências e estado do boss;
- simulação completa consegue alcançar Chegada a Marte em God Mode;
- suíte completa existente permanece verde.

## 18. Validação manual obrigatória

1. Jogar cada fase recebendo um dano e confirmar persistência.
2. Confirmar que três impactos separados encerram a campanha.
3. Verificar barra em 1920×1080 e em janela redimensionada, se suportado.
4. Testar esquiva do míssil movendo em reta: deve alcançar o jogador.
5. Testar curva perpendicular: deve ser possível fazê-lo errar.
6. Acertar cada um dos cinco alvos vulneráveis.
7. Bater o míssil na blindagem e confirmar ausência de dano.
8. Destruir uma nave laser com o míssil.
9. Falhar mísseis até a playlist repetir e confirmar que a luta não trava.
10. Vencer com 1 HP e confirmar avanço à chegada em Marte.
11. Morrer durante cada tipo de perigo e confirmar tela de derrota.
12. Ativar God Mode e confirmar que nem vida nem fluxo ficam corrompidos.

## 19. Critérios de aceite

A funcionalidade está concluída somente quando:

- todas as fases de combate usam a barra global de 3 HP;
- nenhum contato isolado destrói Valentina com HP restante;
- HP persiste sem cura entre fases;
- a Órbita de Marte contém a Nave-Mãe visível no topo;
- a Nave-Mãe executa as sete ondas descritas e repete 2–7;
- gaivota-robô, nave laser e míssil funcionam conforme especificado;
- o jogador consegue destruir o chefe apenas redirecionando cinco mísseis;
- não existem estágios vinculados à vida do chefe;
- a derrota e o reinício da campanha funcionam;
- vitória avança para Chegada a Marte;
- testes automatizados novos e antigos passam;
- documentação de estado e ondas é atualizada depois da implementação;
- um playtest confirma que todas as ondas podem ser concluídas sem dano.

## 20. Ordem recomendada de implementação

1. Criar `RunState`, eventos de dano/morte e testes unitários.
2. Alterar `Player` e colisões para dano, invulnerabilidade e morte em 0 HP.
3. Criar barra de vida e tela de derrota/reinício.
4. Garantir persistência entre fases e regressão das ondas existentes.
5. Criar `GuidedMissile` isoladamente e testar movimento/colisões.
6. Criar gaivota-robô e seus quatro padrões.
7. Criar/configurar nave laser e seus três padrões.
8. Criar Nave-Mãe, alvos vulneráveis e barra de integridade.
9. Criar `BossFightSystem` e integrar a Órbita de Marte.
10. Montar as sete ondas e regras de repetição.
11. Implementar sequência de derrota e progressão.
12. Rodar testes, playtest e ajustar somente dataclasses de configuração.

## 21. Prompt final de implementação

Use este prompt em uma tarefa de implementação:

> Implemente integralmente o PDR `docs/pdr-nave-mae.md` no projeto Shipw.
> Preserve a arquitetura descrita em `AGENT.md`, leia primeiro
> `docs/status-atual.md`, `docs/arquitetura.md` e `docs/enemy-waves.md`, e não
> altere nem apague assets existentes. Faça a implementação em incrementos
> coerentes: estado global de 3 HP, dano/invulnerabilidade/UI/derrota;
> míssil teleguiado; gaivota-robô; nave laser; Nave-Mãe; diretor e playlist de
> sete ondas; vitória e progressão. Use factories novas por spawn, providers de
> alvo, movimento dependente de delta e configurações imutáveis. A Nave-Mãe
> deve possuir uma única barra de 5 pontos e uma luta contínua, sem estágios
> baseados em HP. Valentina não pode atirar: cada ponto de dano no chefe deve
> vir de um míssil armado atraído até o alvo vulnerável. Escreva testes para os
> critérios das seções 17 e 19, execute a suíte completa após cada conjunto de
> mudanças e faça um playtest final. Preserve alterações não relacionadas que
> já estiverem no worktree. Ao concluir, atualize `docs/status-atual.md`,
> `docs/enemy-waves.md` e `docs/arquitetura.md` para refletir apenas o que foi
> realmente implementado, e apresente um resumo dos arquivos modificados,
> testes executados e pontos que ainda precisem de balanceamento humano.
