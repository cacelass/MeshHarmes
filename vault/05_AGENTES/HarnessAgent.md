---
tags:
  - agente
  - arnes
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Harness Agent

> Dueño mecánico del arnés: mantiene el backlog y el progreso, y ejecuta la puerta init.sh.

## Contrato

- **Rol:** Dueño mecánico del arnés: mantiene el backlog y el progreso, y ejecuta la puerta init.sh.
- **Capacidades:** leer y actualizar harness/featureslist.json (abrir, cerrar, bloquear y añadir features); escribir harness/progress/current.md y añadir entradas a harness/progress/history.md; guardar los informes de los subagentes en harness/progress/<agente>-<FEATURE-ID>.md; ejecutar ./init.sh y devolver el veredicto estructurado; rechazar el cierre de una feature si la puerta no pasa o si no hay evidencia
- **Límites:** decidir QUÉ feature toca ni cómo implementarla → eso lo razonan los agentes markdown del arnés (lider, explorer, implementer, reviewer); escribir código del producto → 'refactor' y el implementer; ejecutar los tests por su cuenta → los ejecuta init.sh, o el agente 'test'; cerrar una feature sin evidencia → devuelve needs, nunca la da por buena
- **Necesita:** el id de la feature; la evidencia real de verificación para cerrarla
- **Recursos:** `harness/featureslist.json`, `harness/progress/`, `harness/memory.md`
- **Colabora con:** [[PlanAgent|plan]], [[TestAgent|test]], [[ReviewAgent|review]], [[MemoryAgent|memory]]

## Acciones

- `run harness status`
- `run harness next`
- `run harness start`
- `run harness finish`
- `run harness block`
- `run harness record`
- `run harness gate`
- `run harness add`

Fuente: `agents/contracts.py` · `agents.agents.harness_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Por qué existe

La regla «ninguna feature se cierra sin la puerta en verde» no es un prompt:
la aplica `finish()` en Python. Un LLM editando JSON a mano se equivoca; este
agente hace determinista la parte que no debe improvisarse.

## Comandos

- `uv run python -m agents --json run harness next`
- `uv run python -m agents --json run harness start --id FEAT-001`
- `uv run python -m agents --json run harness record --agent explorer --id FEAT-001 --content "..."`
- `uv run python -m agents --json run harness finish --id FEAT-001 --evidence "$(make test 2>&1 | tail -5)"`
