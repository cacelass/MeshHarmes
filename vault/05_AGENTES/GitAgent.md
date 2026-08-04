---
tags:
  - agente
  - git
  - documentacion
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Git Agent

> Único agente que escribe en el historial git: commits, tags, releases.

## Contrato

- **Rol:** Único agente que escribe en el historial git: commits, tags, releases.
- **Capacidades:** mensajes Conventional Commits desde el diff real, changelog, resumen de PR; commit_with_changelog, commit_feature y tag_release (flujos que encadenan documentation + git); commit_feature: cierre del arnés con bump de versión + changelog + commit, sin tag
- **Límites:** escribir CHANGELOG.md/README.md él mismo → delega en documentation (su dueño); hacer push a remotos — decisión del humano
- **Necesita:** la versión, para tag_release; el mensaje, para commit si no quiere el sugerido; el id y el título de la feature, para commit_feature
- **Recursos:** `historial git (commits, tags, ramas)`
- **Colabora con:** [[DocumentationAgent|documentation]], [[CICDAgent|cicd]]
- **No se deshacen** (la puerta las bloquea sin `--yes`): `commit_with_changelog`, `commit_feature`, `tag_release`, `create_branch`, `merge_branch`

## Acciones

- `run git status`
- `run git analyze_diff`
- `run git suggest_commit_message`
- `run git generate_changelog`
- `run git generate_release_notes`
- `run git detect_breaking_changes`
- `run git prepare_pr_summary`
- `run git commit_with_changelog` ⚠️ pide confirmación
- `run git commit_feature` ⚠️ pide confirmación
- `run git tag_release` ⚠️ pide confirmación
- `run git create_branch` ⚠️ pide confirmación
- `run git merge_branch` ⚠️ pide confirmación

Fuente: `agents/contracts.py` · `agents.agents.git_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Hacer commits con mensajes Conventional Commits
2. Crear tags y releases
3. Generar resúmenes de PR
4. Delegar documentación a documentation agent

## Flujo típico

`git.commit_with_changelog` → escribe CHANGELOG via documentation, luego commitea.
