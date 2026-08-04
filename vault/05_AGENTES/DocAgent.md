---
tags:
  - agente
  - conocimiento
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Doc Agent

> Documentación unificada: responde dónde está algo consultando grafo, índice semántico y vault, y navega el grafo.

## Contrato

- **Rol:** Documentación unificada: responde dónde está algo consultando grafo, índice semántico y vault, y navega el grafo.
- **Capacidades:** buscar en las tres fuentes a la vez (graphify, RAG, vault) y fusionar resultados; consultar el grafo estructural de graphify; buscar en el vault Obsidian por texto; informar de qué fuentes están disponibles y cuáles no; navegar el grafo: vecinos de un nodo y listado de referencias (absorbido de `docsearch`, cuya búsqueda repetía la de aquí)
- **Límites:** escribir documentación → eso es de 'documentation' (README, CHANGELOG) o 'knowledge' (vault); construir el grafo ni el índice → delega en 'knowledge' y 'rag'; responder si ninguna fuente está disponible → lo dice, no inventa
- **Necesita:** la pregunta en lenguaje natural
- **Colabora con:** [[RagAgent|rag]], [[KnowledgeAgent|knowledge]]

## Acciones

- `run doc search`
- `run doc graph_query`
- `run doc rag_search`
- `run doc vault_grep`
- `run doc neighbors`
- `run doc list_references`
- `run doc index`
- `run doc status`

Fuente: `agents/contracts.py` · `agents.agents.doc_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Comandos

- `uv run python -m agents run doc search --query "qué se decidió sobre el backlog"`
- `uv run python -m agents run doc sources`
