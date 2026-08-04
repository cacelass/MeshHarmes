---
tags:
  - agente
  - bootstrap
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Bootstrap Agent

> Arranque en frío: convierte un repo vacío en uno con objetivo escrito y backlog sembrado.

## Contrato

- **Rol:** Arranque en frío: convierte un repo vacío en uno con objetivo escrito y backlog sembrado.
- **Capacidades:** detectar si es la primera ejecución del arnés en este repo; sembrar los dos tickets de arranque delegando en `harness`; recoger la descripción del proyecto y escribirla en project.yml; señalar qué capacidades de la descripción no cubre ningún agente registrado
- **Límites:** inventarse el propósito del proyecto — si falta, pregunta (needs) y para; escribir en el backlog directamente → harness (su dueño); crear agentes → installer scaffold (dueño de agents/external/); escribir en el vault → knowledge (su dueño)
- **Necesita:** la descripción del proyecto, en palabras del usuario
- **Recursos:** `project.yml`, `agents/workspace/bootstrap/`
- **Colabora con:** [[HarnessAgent|harness]], [[InstallerAgent|installer]], [[ResearchAgent|research]], [[KnowledgeAgent|knowledge]]
- **No se deshacen** (la puerta las bloquea sin `--yes`): `describe`, `seed`

## Acciones

- `run bootstrap status`
- `run bootstrap seed` ⚠️ pide confirmación
- `run bootstrap describe` ⚠️ pide confirmación
- `run bootstrap suggest_agents`

Fuente: `agents/contracts.py` · `agents.agents.bootstrap_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->
