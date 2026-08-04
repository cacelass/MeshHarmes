---
tags:
  - agente
  - diagnostico
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Doctor Agent

> Diagnóstico integral del proyecto: agrega las verificaciones de los demás.

## Contrato

- **Rol:** Diagnóstico integral del proyecto: agrega las verificaciones de los demás.
- **Capacidades:** checkup completo (python, git, estructura, tests, dependencias, disco)
- **Límites:** arreglar lo que encuentra por su cuenta → cada dueño (pipeline fix lo orquesta)
- **Colabora con:** [[EnvAgent|env]], [[TestAgent|test]], [[DependencyAgent|dependency]], [[GitAgent|git]]

## Acciones

- `run doctor checkup`
- `run doctor disk_usage`
- `run doctor summary`

Fuente: `agents/contracts.py` · `agents.agents.doctor_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
