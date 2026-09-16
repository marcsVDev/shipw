# Visão do jogo e estado atual

## Proposta

Em plena Guerra Fria, os Estados Unidos chegam primeiro à Lua. Inconformado,
o coronel Dmitri Petrovitch ordena uma missão soviética ainda mais ambiciosa:
alcançar Marte. Ele escolhe Valentina Tereshkova para uma missão que espera que
seja suicida. Valentina sobrevive à viagem, chega ao planeta vermelho e
transforma a sentença de morte em uma conquista impossível.

O jogo é um shooter arcade inspirado em *Space Invaders*, com padrões de
inimigos e um confronto de chefe antes da chegada a Marte. Nas fases de
travessia, a nave de Valentina se move nos dois eixos enquanto o cenário rola
verticalmente, transmitindo a subida e o afastamento da Terra.

## Jornada da campanha

| Fase | Papel na proposta | Estado no código |
| --- | --- | --- |
| Estação de Lançamento — Estação Krasny Mir | Apresentação e lançamento | Implementada como cena de 5 s, sem ondas e com movimento bloqueado. |
| Estratosfera | Gaivotas e asteroides | Implementada com fundo rolável, ondas de gaivotas e chuva de asteroides. |
| Espaço Próximo | Satélite quebrado, Buran e drones | Implementada com drones e satélite quebrado. Buran permanece planejado. |
| Espaço Profundo | Drones e minas espaciais | Implementada com drones, drones do mal com raio giratório e minas gravitacionais. |
| Órbita de Marte | Alienígenas, nave-mãe e drones; batalha final | Implementada com uma onda alienígena e escolta de drones. Nave-mãe/boss ainda não existe. |
| Chegada a Marte | Desfecho da missão | Implementada como tela provisória de 5 s, sem cenário marciano e com movimento bloqueado. |

As fases são declaradas em `src/initializations/phases.py`. A lista
`planned_enemies` registra o conteúdo previsto, mas não o instancia.

## O que está jogável

- Menu inicial com botão Play e atalho Enter.
- Música de fundo contínua, efeitos de motor e efeitos de inimigos existentes.
- Campanha linear com seis fases e avanço automático por duração ou término de
  ondas.
- Movimento da nave com `W`, `A`, `S` e `D`, aceleração, desaceleração,
  inclinação visual e limites da tela.
- Fundos fixos/roláveis; a Estratosfera, o Espaço Próximo e os placeholders das
  duas fases posteriores passam uma sensação de deslocamento vertical.
- Colisão poligonal entre jogador e inimigos/projéteis. A colisão destrói a
  nave e paralisa a progressão da onda.
- Gaivotas, drones, drones do mal, asteroides, satélite quebrado, minas espaciais e alienígenas.
- Formações, investidas, perseguição, passagens rápidas, órbitas, zigue-zague,
  chuva de asteroides e minas que atraem a nave.
- Retorno ao menu com Esc, limpando a cena e recriando a campanha para uma
  nova partida.

## Limitações atuais

- Não há disparo, vida, pontuação, tela de derrota, reinício em jogo ou
  condição visual para fim da campanha.
- A nave-mãe, o Buran e a arte/cena de Marte não
  foram implementados.
- A Órbita de Marte não contém boss fight: as ondas de escolta atuais permitem
  avançar diretamente à tela final provisória.
- Espaço Profundo e Órbita de Marte reutilizam o cenário de Espaço Próximo.
- A Estação Krasny Mir não possui uma sequência explícita de diálogo/cutscene
  integrada à campanha, embora exista componente de painel de diálogo.
- Não há sistema de dano, combate ofensivo ou balanceamento validado por
  playtest. O modelo atual é exclusivamente de sobrevivência.

## Prioridades sugeridas

1. Fechar o ciclo básico de jogo: derrota, reinício, feedback de colisão e
   conclusão de campanha.
2. Implementar a nave-mãe e a batalha da Órbita de Marte antes de ampliar
   inimigos secundários.
3. Criar os cenários próprios de Espaço Profundo, Órbita e chegada a Marte.
4. Integrar narrativa de abertura e encerramento usando o painel de diálogo.
5. Definir se Valentina atira e, caso sim, implementar projétil, dano, vida e
   pontuação como um conjunto coerente.

## Referência de controles

| Ação | Tecla |
| --- | --- |
| Iniciar no menu | Enter ou botão Play |
| Mover a nave | W, A, S, D |
| Voltar ao menu durante a campanha | Esc |
| Avançar diálogo, quando usado | Espaço ou clique esquerdo |
| Ativar/desativar God Mode | Ctrl+Shift+O |

O God Mode é uma ferramenta de teste: permanece ativo durante as trocas de
fase, desativa as colisões do jogador e impede sua destruição. Pressione a
combinação novamente para voltar ao comportamento normal.
