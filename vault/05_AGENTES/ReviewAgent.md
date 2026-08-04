---
tags:
  - agente
  - codigo
  - calidad
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Review Agent

> Revisor de código: encuentra problemas y los reporta. Solo lee, nunca modifica.

## Contrato

- **Rol:** Revisor de código: encuentra problemas y los reporta. Solo lee, nunca modifica.
- **Capacidades:** detectar funciones largas, exceso de argumentos, except desnudos, duplicación, TODO/FIXME
- **Límites:** modificar código → refactor; ejecutar tests → test; juzgar decisiones de producto o de arquitectura → el humano
- **Colabora con:** [[RefactorAgent|refactor]]

## Acciones

- `run review review_package`
- `run review review_file`

Fuente: `agents/contracts.py` · `agents.agents.review_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Escanear el código fuente en busca de anti-patrones
2. Reportar hallazgos sin modificar archivos
3. Derivar issues a refactor cuando sea necesario

## #graphify-flow

Las revisiones pueden referenciar nodos del grafo.
