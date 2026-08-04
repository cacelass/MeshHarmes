# Knowledge Workflow — Grafo de conocimiento + Obsidian

## Pipeline
```
knowledge build  →  knowledge sync  →  vault/ actualizado
```

## Pasos


| Paso | Comando | Qué hace | Agente |
|------|---------|----------|--------|
| Build | `run knowledge build` | Construye/actualiza el grafo graphify | `knowledge` |
| Build + RAG | `run knowledge build_and_index` | Graphify build + RAG index en un paso | `knowledge`, `rag` |
| Sync | `run knowledge sync` | Fusiona grafo con vault Obsidian | `knowledge` |
| Estado | `run knowledge status` | Estado de caché y bóvedas | `knowledge` |
| RAG index | `run rag index` | Indexa docs en ChromaDB | `rag` |


## Paths
- `vault/` — bóveda Obsidian completa
  - `00_META/IA_index.md` — punto de entrada
  - `01_PROYECTO/` — objetivo, arquitectura, decisiones, roadmap
  - `02_DATOS/` — features, fuentes
  - `04_VISUALIZACIONES/grafo_conocimiento.md` — visualización del grafo
  - `05_AGENTES/` — fichas de cada agente (desde contracts.py)
- `graphify-out/cache/` — caché del grafo
- `.rag-index/` — índice vectorial ChromaDB (gitignored)



## Agente `knowledge` — acciones clave
- `build` — actualiza grafo desde el proyecto
- `build_and_index` — build + RAG index en un paso
- `status` — estado del grafo, caché
- `summarize_parents` — resume hubs (nodos con muchos hijos)
- `sync` — sincroniza grafo con vault (solo con vault)
- `setup_vault` — crea bóveda si no existe (solo con vault)

## Agentes que escriben en vault (vía `knowledge`)
- `data` → `vault/02_DATOS/features.md`, fuentes.md
- `knowledge` → todo lo demás

## Notas
- Los resúmenes son topológicos (grado, vecinos compartidos), no semánticos
- Para extracción semántica: configurar `GEMINI_API_KEY`
- El `git` agent llama a `knowledge sync` antes de cada commit automático
