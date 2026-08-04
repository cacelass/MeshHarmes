---
tags:
  - agente
  - auditoria
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Audit Agent

> Auditor del equipo: mide a los demás agentes con el log de ejecuciones y propone mejoras.

## Contrato

- **Rol:** Auditor del equipo: mide a los demás agentes con el log de ejecuciones y propone mejoras.
- **Capacidades:** informe de uso: ejecuciones, tasa de éxito y duración media por agente/acción; listar los fallos recientes con su mensaje; sugerir mejoras con heurísticas (acciones que fallan mucho, agentes sin uso, acciones lentas)
- **Límites:** arreglar él mismo lo que detecta → doctor (diagnóstico), refactor (código), o el humano; auditar llamadas directas a métodos que no pasaron por run() — quedan fuera del log

## Acciones

- `run audit report`
- `run audit failures`
- `run audit suggest_improvements`

Fuente: `agents/contracts.py` · `agents.agents.audit_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
