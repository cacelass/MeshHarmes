---
tags:
  - agente
  - documentacion
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Documentation Agent

> Dueño de la documentación: CHANGELOG.md, README.md, docs/ y la versión del proyecto.

## Contrato

- **Rol:** Dueño de la documentación: CHANGELOG.md, README.md, docs/ y la versión del proyecto.
- **Capacidades:** actualizar CHANGELOG.md (también entradas por-feature), detectar README ↔ Makefile desincronizados; bump_version en pyproject.toml + README, generar docs Sphinx
- **Límites:** hacer commit de lo que escribe → git; tocar la sección de dependencias de pyproject.toml → env
- **Necesita:** la nueva versión, para bump_version
- **Recursos:** `CHANGELOG.md`, `README.md`, `docs/`, `pyproject.toml (campo version)`
- **Colabora con:** [[GitAgent|git]]

## Acciones

- `run documentation check_readme_makefile_sync`
- `run documentation update_changelog`
- `run documentation build_docs`
- `run documentation bump_version`

Fuente: `agents/contracts.py` · `agents.agents.documentation_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Mantener CHANGELOG.md actualizado
2. Sincronizar README.md con Makefile
3. Gestionar versión del proyecto
4. Generar documentación Sphinx

## Archivos controlados

- `CHANGELOG.md`
- `README.md`
- `docs/`
- `pyproject.toml` (campo `version`)
