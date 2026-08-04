---
tags:
  - agente
  - api
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# API Agent

> Revisor de la API FastAPI (solo con use_api=true): endpoints vs docs + smoke test.

## Contrato

- **Rol:** Revisor de la API FastAPI (solo con use_api=true): endpoints vs docs + smoke test.
- **Capacidades:** cruzar endpoints declarados contra documentados, smoke test con TestClient
- **Límites:** modificar api/main.py — reporta discrepancias; desplegar la API
- **Colabora con:** [[TestAgent|test]]

## Acciones

- `run api check_endpoints_documented`
- `run api smoke_test`

Fuente: `agents/contracts.py` · `agents.agents.api_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Dependencias

- API habilitada: no
