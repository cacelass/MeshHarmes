---
tags:
  - agente
  - make
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Make Agent

> Dueño del Makefile: valida targets y la cadena del pipeline, sugiere targets nuevos.

## Contrato

- **Rol:** Dueño del Makefile: valida targets y la cadena del pipeline, sugiere targets nuevos.
- **Capacidades:** verificar que los targets declarados existen y que las cadenas de dependencias del Makefile son coherentes
- **Límites:** generar workflows de CI → cicd; ejecutar el pipeline completo — sugiere, el humano ejecuta
- **Recursos:** `Makefile`
- **Colabora con:** [[CICDAgent|cicd]]

## Acciones

- `run make validate`
- `run make check_core_targets`
- `run make suggest_targets`
- `run make run`
- `run make list_targets`

Fuente: `agents/contracts.py` · `agents.agents.make_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
