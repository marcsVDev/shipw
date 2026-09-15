# Documentação do Shipw

Shipw é um shooter arcade 2D em Pygame sobre a travessia de Valentina
Tereshkova rumo a Marte, em uma história alternativa da Guerra Fria.

## Documentos

- [Visão do jogo e estado atual](status-atual.md): proposta narrativa, fases,
  conteúdo implementado, lacunas conhecidas e prioridades.
- [Arquitetura do sistema](arquitetura.md): loop, cenas, progressão, entidades,
  ondas, eventos, colisão e assets.
- [Inimigos e ondas](enemy-waves.md): catálogo técnico de ondas, padrões,
  ataques e como estender o combate.
- [Guia para agentes](../AGENT.md): convenções de contribuição, execução e
  validação.

## Acesso rápido

```powershell
python src/game.py
python -B -m unittest discover -s tests -v
```

O código-fonte está em `src/`, os testes em `tests/` e os recursos em `assets/`.
