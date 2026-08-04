---
tags:
  - agente
  - conocimiento
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Research Agent

> Investigador externo: busca papers (arXiv/OpenAlex) relacionados con el proyecto. Solo lee.

## Contrato

- **Rol:** Investigador externo: busca papers (arXiv/OpenAlex) relacionados con el proyecto. Solo lee.
- **Capacidades:** extraer keywords del proyecto, buscar papers y rankearlos (necesita internet)
- **Límites:** indexar papers en el grafo o la bóveda → knowledge; decidir qué paper adoptar — presenta candidatos, el humano (o supervisor) elige
- **Colabora con:** [[KnowledgeAgent|knowledge]], [[SupervisorAgent|supervisor]]

## Acciones

- `run research project_keywords`
- `run research find_papers`
- `run research search`

Fuente: `agents/contracts.py` · `agents.agents.research_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Extraer keywords relevantes del proyecto
2. Buscar en arXiv/OpenAlex
3. Rankear resultados por relevancia
4. Presentar candidatos al humano o supervisor

## Dependencias

- Internet (arXiv API, OpenAlex API)
- Knowledge agent (para indexar papers adoptados)
