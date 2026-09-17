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
| Estação de Lançamento — Estação Krasny Mir | Apresentação e lançamento | Implementada com botão de lançamento, animação de fumaça e movimento bloqueado. |
| Estratosfera | Gaivotas e asteroides | Implementada com fundo rolável, ondas de gaivotas e chuva de asteroides. |
| Espaço Próximo | Satélite quebrado, Buran e drones | Implementada com drones e satélite quebrado. Buran permanece planejado. |
| Espaço Profundo | Drones e minas espaciais | Implementada com drones, drones do mal com raio giratório e minas gravitacionais. |
| Órbita de Marte | Nave-mãe, gaivotas-robô, escoltas, lasers e mísseis | Boss fight implementada com sete ondas temporais e repetição das ondas 2–7. |
| Chegada a Marte | Desfecho da missão | Implementada como tela provisória de 5 s, sem cenário marciano e com movimento bloqueado. |

As fases são declaradas em `src/initializations/phases.py`. A lista
`planned_enemies` registra o conteúdo previsto, mas não o instancia.

## O que está jogável

- Menu inicial com botão Play e atalho Enter.
- Música ambiente na campanha, trilha própria durante a boss fight, efeitos de
  motor e efeitos de inimigos existentes.
- Transição preta de 1 s entre fases, com a cena pausada durante a troca.
- Campanha linear com seis fases; Krasny Mir avança após a animação de
  lançamento e as demais fases avançam por duração, ondas ou chefe.
- Movimento da nave com `W`, `A`, `S` e `D`, aceleração, desaceleração,
  inclinação visual e limites da tela.
- Fundos fixos/roláveis; a Estratosfera, o Espaço Próximo e os placeholders das
  duas fases posteriores passam uma sensação de deslocamento vertical.
- Vida global de 3 HP, preservada entre fases, com 1,5 s de invulnerabilidade,
  pisca, knockback, barra por cores e no máximo um dano por frame.
- Tela de derrota com reinício da campanha por Enter e retorno ao menu por Esc.
- Colisão poligonal entre jogador, inimigos, projéteis, raios e a Nave-Mãe.
- Gaivotas, gaivotas-robô, drones, naves laser, drones do mal, asteroides,
  satélite quebrado, minas espaciais, alienígenas e Nave-Mãe.
- Formações, investidas, perseguição, passagens rápidas, órbitas, zigue-zague,
  chuva de asteroides e minas que atraem a nave.
- Os drones da pinça orbital perseguem a posição atual do jogador dentro de
  margens visíveis, sem atravessar os limites da tela.
- Mísseis do chefe perseguem pelo menor ângulo, com giro limitado a 240°/s;
  os cinco alvos vulneráveis ficam acessíveis na borda inferior do casco.
- Retorno ao menu com Esc, limpando a cena e recriando a campanha para uma
  nova partida.

## Limitações atuais

- Não há disparo, pontuação ou itens coletáveis; Valentina derrota a Nave-Mãe
  somente atraindo mísseis armados para o alvo vulnerável.
- O Buran e a arte/cena final de Marte ainda não foram implementados.
- Espaço Profundo e Órbita de Marte reutilizam o cenário de Espaço Próximo.
- A Estação Krasny Mir possui a cutscene visual de lançamento, mas ainda não
  integra diálogos, embora exista componente de painel de diálogo.
- As velocidades e janelas do boss, incluindo o giro ajustado do míssil, ainda
  precisam de playtest humano para ajuste fino de corredores e duração média.

## Prioridades sugeridas

1. Fazer playtest humano das sete ondas do boss e ajustar apenas as dataclasses
   de balanceamento.
2. Criar os cenários próprios de Espaço Profundo, Órbita e chegada a Marte.
3. Integrar narrativa de abertura e encerramento usando o painel de diálogo.
4. Implementar o Buran sem alterar o modelo de sobrevivência e sabotagem.

## Referência de controles

| Ação | Tecla |
| --- | --- |
| Iniciar no menu | Enter ou botão Play |
| Lançar em Krasny Mir | Botão Play provisório |
| Mover a nave | W, A, S, D |
| Voltar ao menu durante a campanha | Esc |
| Avançar diálogo, quando usado | Espaço ou clique esquerdo |
| Ativar/desativar God Mode | Ctrl+Shift+O |

O God Mode é uma ferramenta de teste: permanece ativo durante as trocas de
fase, desativa as colisões do jogador e impede sua destruição. Pressione a
combinação novamente para voltar ao comportamento normal.
