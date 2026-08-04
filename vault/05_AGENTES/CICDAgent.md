---
tags:
  - agente
  - cicd
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# CICD Agent

> Dueño de los workflows de GitHub Actions del proyecto generado.

## Contrato

- **Rol:** Dueño de los workflows de GitHub Actions del proyecto generado.
- **Capacidades:** generar y validar .github/workflows/*.yml cruzando los targets contra el Makefile real; validar expresiones cron, describirlas en lenguaje natural y calcular sus próximas ejecuciones — absorbido de `schedule`, que solo repetía lo que validate_cron ya devolvía
- **Límites:** modificar el Makefile → make; hacer commit del workflow → git
- **Recursos:** `.github/workflows/`
- **Colabora con:** [[MakeAgent|make]], [[GitAgent|git]]

## Acciones

- `run cicd validate_workflow`
- `run cicd generate_workflow`
- `run cicd list_workflows`
- `run cicd validate_cron`

Fuente: `agents/contracts.py` · `agents.agents.cicd_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Generar workflows de CI/CD
2. Validar que los workflows crucen correctamente con targets del Makefile
3. Reportar inconsistencias

## Archivos controlados

- `.github/workflows/*.yml`
