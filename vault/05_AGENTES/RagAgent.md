---
tags:
  - agente
  - conocimiento
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Rag Agent

> RAG local: indexa código, prompts, docs, vault, la memoria del arnés y URLs externas; busca en lenguaje natural fundiendo similitud vectorial (ChromaDB) con BM25 léxico.

## Contrato

- **Rol:** RAG local: indexa código, prompts, docs, vault, la memoria del arnés y URLs externas; busca en lenguaje natural fundiendo similitud vectorial (ChromaDB) con BM25 léxico.
- **Capacidades:** indexar el proyecto (código de todos los módulos, prompts, docs, vault, README, CHANGELOG, harness/progress/ y harness/featureslist.json) en ChromaDB; reindexar solo lo que cambió, y purgar del índice lo que se borró; indexar URLs externas (documentación de librerías, tutoriales); buscar en el índice con consultas en lenguaje natural; devolver fragmentos relevantes con puntuación de similitud
- **Límites:** construir o modificar el grafo graphify → knowledge; buscar papers académicos nuevos → research; ejecutar código ni modificar archivos del proyecto
- **Necesita:** que exista un índice (ejecutar 'rag index' primero)
- **Recursos:** `.rag-index/ (índice vectorial ChromaDB, gitignored)`
- **Colabora con:** [[KnowledgeAgent|knowledge]], [[DocAgent|doc]], [[PlanAgent|plan]]

## Acciones

- `run rag index`
- `run rag index_urls`
- `run rag search`
- `run rag status`
- `run rag evaluate`

Fuente: `agents/contracts.py` · `agents.agents.rag_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Por qué híbrido

El embedder por defecto está entrenado en inglés y este proyecto se documenta
en español: la mitad de la señal útil es literal (nombres de función, rutas) y
el vector solo no la ve.

## Comandos

- `make index-rag`
- `uv run python -m agents run rag search --query "cómo se cierra una feature?"`
- `make eval-rag`
