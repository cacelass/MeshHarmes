---
tags:
  - agente
  - conocimiento
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Knowledge Agent

> Dueño del grafo de conocimiento y la bóveda Obsidian: los construye y mantiene al día.

## Contrato

- **Rol:** Dueño del grafo de conocimiento y la bóveda Obsidian: los construye y mantiene al día.
- **Capacidades:** construir/reconstruir el grafo (graphify), crear la bóveda, resumir nodos padre, sync; poblar vault/05_AGENTES/ con fichas individuales de cada agente desde contracts.py; actualizar vault/04_VISUALIZACIONES/grafo_conocimiento.md tras cada build del grafo
- **Límites:** buscar o navegar por el grafo → doc (absorbió docsearch); buscar papers nuevos → research (knowledge los indexa cuando ya existen)
- **Recursos:** `graphify-out/`, `vault/ (bóveda Obsidian del proyecto — todo vault/00_META/, 01_PROYECTO/, 04_VISUALIZACIONES/, 05_AGENTES/)`
- **Colabora con:** [[DocAgent|doc]], [[ResearchAgent|research]]
- **No se deshacen** (la puerta las bloquea sin `--yes`): `sync_agent_cards`

## Acciones

- `run knowledge status`
- `run knowledge setup_vault`
- `run knowledge sync_agent_cards` ⚠️ pide confirmación
- `run knowledge build`
- `run knowledge build_and_index`
- `run knowledge summarize_parents`
- `run knowledge sync`
- `run knowledge prune`

Fuente: `agents/contracts.py` · `agents.agents.knowledge_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Ejecutar graphify para construir el grafo de conocimiento
2. Generar y mantener el vault Obsidian del proyecto
3. Resumir nodos padre del grafo
4. Sincronizar cambios

## Archivos

- `agents/agents/knowledge_agent.py`
- `agents/contracts.py:` `CONTRACTS["knowledge"]`
