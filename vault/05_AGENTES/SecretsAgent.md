---
tags:
  - agente
  - seguridad
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Secrets Agent

> Escáner de secretos hardcodeados. Solo lee y reporta.

## Contrato

- **Rol:** Escáner de secretos hardcodeados. Solo lee y reporta.
- **Capacidades:** escanear el proyecto con detect-secrets o un heurístico propio (más limitado, avisado)
- **Límites:** borrar o rotar secretos encontrados — decisión del humano

## Acciones

- `run secrets scan`

Fuente: `agents/contracts.py` · `agents.agents.secrets_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
