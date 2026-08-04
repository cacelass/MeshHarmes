---
tags:
  - agente
  - entorno
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Env Agent

> Dueño del entorno: versión de Python, uv sync/lock, dependencias declaradas.

## Contrato

- **Rol:** Dueño del entorno: versión de Python, uv sync/lock, dependencias declaradas.
- **Capacidades:** verificar python, uv sync, uv lock --check, añadir dependencias con uv add
- **Límites:** juzgar si una dependencia está obsoleta o es vulnerable → dependency; tocar la versión del proyecto en pyproject.toml → documentation
- **Necesita:** el nombre del paquete, para añadir una dependencia
- **Recursos:** `uv.lock`, `.venv/`, `pyproject.toml (dependencias)`
- **Colabora con:** [[DependencyAgent|dependency]]

## Acciones

- `run env check_python_version`
- `run env sync`
- `run env check_lock_sync`
- `run env add_dependency`
- `run env info`

Fuente: `agents/contracts.py` · `agents.agents.env_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Mantener el entorno Python sincronizado
2. Verificar la versión de Python
3. Añadir/actualizar dependencias
4. Validar uv.lock

## Dependencias

- Python 3.13
- uv package manager
