---
tags:
  - agente
  - docker
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Docker Agent

> Revisor de la configuración Docker: lint de Dockerfile y docker-compose.

## Contrato

- **Rol:** Revisor de la configuración Docker: lint de Dockerfile y docker-compose.
- **Capacidades:** lint de Dockerfile, validación de docker-compose.yml
- **Límites:** construir o ejecutar imágenes — solo análisis estático; editar el Dockerfile — reporta, el humano decide

## Acciones

- `run docker lint_dockerfile`
- `run docker validate_compose`
- `run docker ps`

Fuente: `agents/contracts.py` · `agents.agents.docker_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
