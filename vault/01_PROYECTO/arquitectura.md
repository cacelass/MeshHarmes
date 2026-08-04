# Arquitectura — MeshHarmes

> Arnés de agentes e infraestructura de proyecto para trabajo general en Python.
>
> Este documento lo rellena `DESIGN-001`: cuando el proyecto tenga piezas
> propias, descríbelas aquí junto a las alternativas descartadas y por qué.

## Stack

- **Lenguaje:** Python 3.12+ (el `.venv` de referencia es 3.13)
- **Entorno y dependencias:** uv (`uv.lock`)
- **Calidad:** ruff, mypy, pytest, bandit, pip-audit
- **Conocimiento:** vault Obsidian + graphify + RAG local opcional (chromadb)

## Estructura del repositorio

```
app/                   — El código del proyecto (renómbralo al empezar)
tests/                 — Tests del proyecto

agents/                — Sistema multi-agente del arnés (stdlib pura)
├── contracts.py       — Contratos de rol: can / cannot / needs / owns
├── agents/            — Un módulo por agente
├── tools/             — Herramientas compartidas
├── prompts/           — Skills cargables por el asistente
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
`PreToolUse` que este repo **no** define a propósito: si el comando del hook
falla, el asistente se queda sin herramientas. El snippet para activarla está
en `AGENTS.md`.

Ninguna de las dos es un sandbox: convierten accidentes e inyecciones
evidentes en un error legible. El aislamiento real depende de dónde ejecutes
el asistente.
