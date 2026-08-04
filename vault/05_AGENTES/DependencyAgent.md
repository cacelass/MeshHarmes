---
tags:
  - agente
  - entorno
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Dependency Agent

> Vigilante de dependencias: obsolescencia y vulnerabilidades contra PyPI/OSV. Solo lee.

## Contrato

- **Rol:** Vigilante de dependencias: obsolescencia y vulnerabilidades contra PyPI/OSV. Solo lee.
- **Capacidades:** detectar paquetes desactualizados y vulnerabilidades conocidas (necesita internet)
- **Límites:** actualizar o instalar nada → env (dueño de uv.lock)
- **Colabora con:** [[EnvAgent|env]]

## Acciones

- `run dependency check_outdated`
- `run dependency check_vulnerabilities`
- `run dependency check_lock_sync`

Fuente: `agents/contracts.py` · `agents.agents.dependency_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Escanear dependencias contra PyPI (versiones recientes) y OSV (vulnerabilidades)
2. Reportar paquetes desactualizados
3. Reportar vulnerabilidades conocidas
