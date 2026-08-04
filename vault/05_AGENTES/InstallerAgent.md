---
tags:
  - agente
  - instalacion
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Installer Agent

> Dueño de agents/external/: instala, genera y valida agentes de terceros.

## Contrato

- **Rol:** Dueño de agents/external/: instala, genera y valida agentes de terceros.
- **Capacidades:** instalar un agente desde git/ruta local, validar su estructura, confirmar registro; generar un agente nuevo desde una spec (scaffold): módulo con contrato inline, prompt y test, con las acciones como stubs que declaran que no están implementadas
- **Límites:** garantizar que el código externo es seguro — la validación es estructural, no de seguridad; instalar dependencias del agente externo → env; implementar el agente que genera — scaffold deja un esqueleto, el trabajo lo escribe quien lo pidió
- **Necesita:** repo_url o ruta local del agente a instalar; el nombre, la descripción y las acciones del agente a generar, para scaffold
- **Recursos:** `agents/external/`
- **Colabora con:** [[EnvAgent|env]], [[BootstrapAgent|bootstrap]]
- **No se deshacen** (la puerta las bloquea sin `--yes`): `install_from_git`, `install_from_path`, `scaffold`

## Acciones

- `run installer install_from_git` ⚠️ pide confirmación
- `run installer install_from_path` ⚠️ pide confirmación
- `run installer scaffold` ⚠️ pide confirmación
- `run installer list_installed`
- `run installer verify`

Fuente: `agents/contracts.py` · `agents.agents.installer_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
