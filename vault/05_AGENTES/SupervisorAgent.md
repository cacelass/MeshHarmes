---
tags:
  - agente
  - coordinacion
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Supervisor Agent

> Coordina workers en paralelo: los pone a COMPETIR y arbitra, o los abre en abanico y SINTETIZA.

## Contrato

- **Rol:** Coordina workers en paralelo: los pone a COMPETIR y arbitra, o los abre en abanico y SINTETIZA.
- **Capacidades:** lanzar propuestas que compiten (p. ej. búsquedas de papers en paralelo) y elegir la mejor; abrir en abanico varias perspectivas sobre lo mismo y devolverlas integradas (acuerdos, desacuerdos y lo que cada una necesita) — el diamante fan-out/fan-in
- **Límites:** orquestar un encargo secuencial paso a paso → plan (él delega a dueños, no arbitra); hacer el trabajo de los workers él mismo — solo coordina y evalúa; interpretar lo que sintetiza — agrupa hechos; razonar sobre ellos es de la capa de arriba
- **Necesita:** la tarea a poner en competición y el criterio de evaluación
- **Colabora con:** [[ResearchAgent|research]]

## Acciones

- `run supervisor research`
- `run supervisor compete`
- `run supervisor synthesize`

Fuente: `agents/contracts.py` · `agents.agents.supervisor_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
