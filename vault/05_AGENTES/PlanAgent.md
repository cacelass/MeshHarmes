---
tags:
  - agente
  - coordinacion
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Plan Agent

> Jefe de proyecto: convierte un encargo humano en una orden de trabajo, pregunta lo que falte y delega.

## Contrato

- **Rol:** Jefe de proyecto: convierte un encargo humano en una orden de trabajo, pregunta lo que falte y delega.
- **Capacidades:** descomponer un encargo en pasos y asignar cada paso al agente responsable; detectar qué información falta y devolver las preguntas ANTES de ejecutar nada; ejecutar la orden de trabajo aprobada (via GStack) y resumir qué debe verificar el humano; leer vault/00_META/IA_index.md para obtener contexto del proyecto y la topología de agentes; consultar vault/05_AGENTES/<Agent>.md para decidir a quién delegar cada paso
- **Límites:** ejecutar ninguna acción de dominio él mismo → siempre delega en el agente dueño; inventar argumentos que no le han dado → los convierte en preguntas; ejecutar una orden con preguntas sin responder
- **Necesita:** el encargo (brief) en lenguaje natural; las respuestas a las preguntas que genere
- **Colabora con:** todos — es el punto de entrada que delega en el resto

## Acciones

- `run plan intake`
- `run plan answer`
- `run plan execute`
- `run plan status`

Fuente: `agents/contracts.py` · `agents.agents.plan_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Recibir el encargo del humano
2. Descomponerlo en pasos atómicos
3. Asignar cada paso al agente responsable
4. Generar preguntas si falta información
5. Ejecutar la orden de trabajo aprobada

## Dependencias

- Todos los agentes del proyecto (delega según el dominio)
