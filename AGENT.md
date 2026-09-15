# Guia para agentes — Shipw

## Contexto do projeto

**Shipw** é um jogo arcade 2D feito em Python com Pygame. A protagonista,
Valentina Tereshkova, sobrevive a uma missão soviética suicida rumo a Marte
durante uma versão alternativa da Guerra Fria. A referência de design é
*Space Invaders*: navegação por fases, formações de inimigos, sobrevivência e
uma batalha de chefe no fim da jornada.

Leia [docs/index.md](docs/index.md) antes de mudanças de escopo. O estado real
do jogo e os itens ainda planejados estão em [docs/status-atual.md](docs/status-atual.md).

## Estrutura

- `src/game.py`: ponto de entrada, loop, menu e troca de cenas.
- `src/initializations/phases.py`: ordem e composição das seis fases.
- `src/initializations/enemy_waves.py`: catálogo de inimigos e ondas da campanha.
- `src/system/`: progressão da campanha e execução de ondas.
- `src/entities/`: entidades, personagem, jogador, inimigo, cenário e projéteis.
- `src/enemys/`: inimigos concretos, padrões, ataques e builders de comportamento.
- `src/util/scene.py`: atualização, desenho, remoção de entidades e colisões.
- `assets/`: arte, efeitos sonoros e fontes usados em tempo de execução.
- `tests/`: testes automatizados em `unittest`.
- `docs/`: documentação técnica e de produto.

O diretório se chama `enemys` por legado. Não o renomeie sem uma migração
completa, pois os imports atuais dependem desse nome.

## Como executar e validar

Use Python 3.12+ e instale `pygame-ce` no ambiente local.

```powershell
python src/game.py
python -B -m unittest discover -s tests -v
```

Os testes configuram vídeo e áudio SDL falsos; não abra janelas nem reproduza
sons. Ao modificar ondas, padrões, colisões, fases ou progressão, execute a
suíte completa. Faça playtest manual quando alterar velocidade, quantidade,
espaçamento ou telemetria de ataques.

## Convenções de implementação

- Mantenha a resolução-base de `1920x1080` definida em `src/game_consts.py`.
- Atualizações de movimento usam `delta` em segundos e devem ser independentes
  da taxa de quadros.
- Uma `Phase` declara entidades padrão, ondas, duração de cenas sem combate e
  se o jogador pode se mover livremente.
- `WaveSystem` é o único responsável por agendar spawns, acompanhar inimigos
  ativos e emitir eventos de onda/fase. Não coloque essa lógica em `Scene`.
- Registre cada inimigo novo em `get_enemy_registry()` e use uma factory que
  devolva uma instância nova por spawn.
- `EnemySpawn.movement` e `.attack` devem ser factories; nunca compartilhe
  objetos de padrão/ataque que guardem temporizadores entre inimigos.
- Padrões recebem um provider de alvo; não acople padrões ou inimigos à cena.
- Ataques seguem `update(enemy, player, delta, emit_projectile)`. Forças no
  jogador devem usar `player.apply_force(...)`.
- Colisores são polígonos em `MIDDLE_VERTICES`; uma lista vazia desativa a
  colisão daquela entidade. Atualize-a ao incluir arte jogável nova.
- Preserve `planned_enemies` como marcador explícito de conteúdo futuro: não
  o trate como um inimigo disponível no registro.

## Escopo narrativo e de gameplay

A campanha percorre Krasny Mir, Estratosfera, Espaço Próximo, Espaço Profundo,
Órbita de Marte e Chegada a Marte. As cenas inicial e final bloqueiam o
movimento; as demais usam rolagem vertical para sugerir ascensão. Consulte o
status antes de afirmar que um inimigo, chefe, cenário ou cutscene já existe:
diversos elementos da proposta ainda são placeholders.

## Cuidados

- Não altere, apague ou recrie assets sem pedido explícito.
- Não versione `__pycache__`, saídas de execução ou arquivos de IDE.
- Mantenha textos de interface em português e consistentes com a nomenclatura
  das fases.
- Ao acrescentar conteúdo, atualize `docs/status-atual.md` e a documentação
  específica correspondente.
- Realize commits por alteração, em ingles e de forma objetiva
