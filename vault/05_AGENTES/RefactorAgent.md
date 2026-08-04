---
tags:
  - agente
  - codigo
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Refactor Agent

> Único agente autorizado a modificar código fuente del paquete, siempre con dry_run primero.

## Contrato

- **Rol:** Único agente autorizado a modificar código fuente del paquete, siempre con dry_run primero.
- **Capacidades:** corregir mutables por defecto, except: desnudos, añadir -> None
- **Límites:** refactorizar sin revisión previa: dry_run=True es el modo por defecto, el humano aprueba; escribir features nuevas — solo correcciones mecánicas y acotadas; tocar el Makefile → make
- **Necesita:** qué archivo/paquete tocar, o confirmación para aplicar (dry_run=False)
- **Recursos:** `codigo fuente del paquete ({project_slug}/)`
- **Colabora con:** [[ReviewAgent|review]]
- **No se deshacen** (la puerta las bloquea sin `--yes`): `fix_mutable_defaults`, `fix_bare_excepts`, `add_type_hints`

## Acciones

- `run refactor fix_mutable_defaults` ⚠️ pide confirmación
- `run refactor fix_bare_excepts` ⚠️ pide confirmación
- `run refactor add_type_hints` ⚠️ pide confirmación

Fuente: `agents/contracts.py` · `agents.agents.refactor_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Aceptar reportes de review y aplicar correcciones
2. Ejecutar dry_run por defecto
3. Solo modificar el código fuente del paquete

## Archivos controlados

- `app/**/*.py`
