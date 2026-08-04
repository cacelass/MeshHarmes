---
tags:
  - agente
  - memoria
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Memory Agent

> Memoria proactiva: observa trayectorias de agentes y mantiene un banco de memoria estructurado contra el decaimiento del estado en tareas largas.

## Contrato

- **Rol:** Memoria proactiva: observa trayectorias de agentes y mantiene un banco de memoria estructurado contra el decaimiento del estado en tareas largas.
- **Capacidades:** observar el log de auditoría y extraer hechos, estado y trazas; buscar recuerdos por texto o tipo (facts/state/traces); inyectar recordatorios relevantes en el contexto del agente activo; tomar una instantánea del estado actual del proyecto; almacenar una nota arbitraria en la memoria; olvidar entradas específicas del banco de memoria
- **Límites:** modificar el workspace de otros agentes — solo escribe en agents/workspace/memory/; ejecutar acciones de dominio — solo observa e inyecta contexto
- **Necesita:** el log de auditoría para observar
- **Recursos:** `agents/workspace/memory/`
- **Colabora con:** [[AuditAgent|audit]]

## Acciones

- `run memory status`
- `run memory note`
- `run memory recall`
- `run memory forget`
- `run memory search`
- `run memory snapshot`
- `run memory inject`
- `run memory observe`
- `run memory decay`
- `run memory clear`

Fuente: `agents/contracts.py` · `agents.agents.memory_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Las tres memorias no se pisan

| Dónde | Dueño | Plazo |
|-------|-------|-------|
| `harness/progress/` | `harness` | La feature en curso |
| `agents/workspace/memory/` | `memory` | Trayectorias de ejecución |
| `vault/` | `knowledge` | Conocimiento estable |

## Comandos

- `uv run python -m agents run memory status`
- `uv run python -m agents run memory observe`
