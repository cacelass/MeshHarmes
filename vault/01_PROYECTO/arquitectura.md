# Arquitectura — MeshHarmes

> Cómo se resuelve lo que `objetivo.md` define. Lo rellena `DESIGN-001`.

## Visión

El arnés ya gobierna el ciclo (backlog, puerta, memoria, permisos). Esta
versión añade un **cerebro persistente** (RAG sobre embeddings + grafo de
conocimiento) que se consulta antes de decidir, y adopta la **programación
aumentada** (discusión con la IA) para mejorar la calidad sin obligar a
revisión manual línea a línea. No se cambia la metodología del líder: se
mejora. No se adoptan los modelos concretos de las fuentes: se usan los del
proyecto.

## Piezas del sistema

```
Humano / Asistente
  └── Líder (orquesta el ciclo, lee harness/progress + RAG brain)
        ├── harness (backlog + puerta + evidencia)  [dueño: harness/]
        ├── knowledge / vault (conocimiento estable) [dueño: knowledge]
        │     └── grafo de conocimiento (graphify)  [vault/04_VISUALIZACIONES/]
        ├── rag (índice semántico: embeddings)       [agents/agents/rag_agent.py]
        │     └── embeddings store (chromadb local)  [agents/workspace/rag/]
        ├── research (fuentes externas)              [agents/agents/research_agent.py]
        ├── reviewer (ejecuta puerta + criterios)    [subagente]
        ├── implementer (código + tests)             [subagente]
        └── explorer (investigación solo lectura)    [subagente]
```

### Flujo (una feature)

1. `harness next` elige la feature pendiente con deps en `done`.
2. El líder consulta el **RAG brain** (`rag search` + grafo) con la descripción
   de la feature: recupera decisiones y restricciones pasadas relevantes.
3. Lanza `explorer` (solo lectura) si falta contexto del repo.
4. Lanza `implementer` con la feature, criterios y el contexto recuperado del
   brain.
5. El implementer aplica **programación aumentada**: discute con la IA el
   diseño antes de escribir, sin exigir revisión manual línea a línea.
6. Lanza `reviewer`, que ejecuta `./init.sh` y comprueba criterios uno a uno.
7. `harness finish` cierra con evidencia; `git commit_feature` propone el
   commit (siempre con confirmación).

### El RAG brain

- **Embeddings**: cada decisión cerrada (feature del histórico, nota del vault,
  ADR) se trocea en chunks y se indexa con el modelo de embeddings del
  proyecto. La consulta (`rag search`) devuelve los chunks semánticamente
  cercanos.
- **Grafo**: graphify mantiene relaciones entre decisiones, features y
  ficheros (`vault/04_VISUALIZACIONES/grafo_conocimiento.md`).
- **Uso**: el líder y el implementer consultan el brain antes de decidir;
  evita reinventar arquitectura y repite menos razonamiento.

## Alternativas consideradas y descartadas

1. **Software factory totalmente autónoma (auto-commit a producción).**
   Descartada: el usuario mantiene el control explícito sobre commit y push.
   El arnés puede preparar y proponer, pero la confirmación es humana.
2. **Wiki-LLM (resúmenes generados por LLM) en lugar de RAG con embeddings.**
   Descartada: añade una fase probabilística extra (resumen puede estar mal) y
   coste de regeneración alto cuando cambian los datos. Los embeddings son
   incrementales y más baratos; el grafo cubre la parte estructural.
3. **Revisión manual obligatoria por PR (pair programming estricto).**
   Descartada: el usuario no quiere revisión línea a línea. Se sustituye por
   programación aumentada (discusión con la IA durante la implementación) y
   por la puerta automática (`./init.sh` + criterios).

## Riesgos conocidos

- **Calidad del retrieval**: "lost in the middle", chunking inadecuado, modelo
  de embeddings inconsistente entre indexado y consulta. Mitigación: mismo
  modelo en ambos lados; evaluar con `make eval-rag` y `agents/evals/rag_golden.json`.
- **Grafo desfasado**: si no se reindexa tras cerrar features, el brain miente.
  Mitigación: reindexado incremental (`make index-rag`) al cerrar feature.
- **Prompt injection en contenido indexado**: documentos externos son datos, no
  instrucciones. Mitigación: RAG devuelve bloques delimitados y marca
  `injection_flag`; las acciones irreversibles piden confirmación siempre.
- **Dependencia del modelo de embeddings**: si cambia, hay que reindexar todo.
  Decisión diferida (ver abajo).

## Decisiones diferidas

- Proveedor/modelo de embeddings concreto: se usa el que ya configure el agente
  `rag` del proyecto (no se adoptan los de las fuentes).
- Esquema exacto del grafo (nodos/aristas) y su persistencia: se decide en la
  feature que implemente el brain.
- Granularidad del chunking por tipo de documento (feature, ADR, nota).

## Paquete del proyecto (plantilla Copier)

Este repositorio es también plantilla Copier. El paquete fuente se llama `app/`
y se renombra al `project_slug` del usuario en el paso post-copia
(`_tasks` de `copier.yml`: `mv app <project_slug>`). Por eso aquí `app/` se
mantiene como nombre fuente y `project_slug` por defecto es `app`; `init.sh`
verifica que el directorio coincida con `project_slug`. No se renombra a mano
en la plantilla: rompería el mecanismo de copia.

## Stack

- **Lenguaje:** Python 3.12+ (el `.venv` de referencia es 3.13)
- **Entorno y dependencias:** uv (`uv.lock`)
- **Calidad:** ruff, mypy, pytest, bandit, pip-audit
- **Conocimiento:** vault Obsidian + graphify + RAG local (chromadb)
- **Agentes:** 24 agentes Python (stdlib pura), contratos en `agents/contracts.py`

## Estructura del repositorio

```
app/                   — El código del proyecto (plantilla Copier; se renombra al copiar)
tests/                 — Tests del proyecto

agents/                — Sistema multi-agente del arnés (stdlib pura)
├── contracts.py       — Contratos de rol
├── agents/            — Un módulo por agente
├── tools/             — Herramientas compartidas
├── prompts/           — Skills cargables
├── evals/             — Ruteo, contratos y RAG, medidos
└── workspace/         — Lo que generan los agentes (git-ignored)

harness/               — El arnés: backlog, progreso, memoria
vault/                 — Conocimiento estable (Obsidian)
├── 00_META/           — Índice para IA y plantillas
├── 01_PROYECTO/       — Objetivo, arquitectura, decisiones, roadmap
├── 04_VISUALIZACIONES/— Grafo de conocimiento
├── 05_AGENTES/        — Ficha de cada agente
└── 06_OBSERVACIONES/  — Hallazgos sueltos
docs/                  — Sphinx
```

## Las dos fronteras de seguridad

```
Agentes Python:  run() → agents/permissions.py → acción          (siempre activa)
Asistente:       herramienta → agents/policy_guard.py → Bash/... (opcional, sin cablear)
```

La primera está en código y no se puede rodear. La segunda necesita un hook
`PreToolUse` que este repo no define a propósito. Ninguna de las dos es un
sandbox.