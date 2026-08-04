# reviewer · BOOT-002

- **Fecha:** 2026-08-04
- **Veredicto:** aprobado

# reviewer · BOOT-002 — APROBADO

Puerta ejecutada por mi en esta sesion: `harness gate` success=true.
Prueba de fuego hecha sobre COPIA del repo en scratchpad (nunca en el repo real),
generando agentes de verdad con --dry_run false --yes.

## Criterios (uno por uno)

1. **dry-run no escribe** — CUMPLIDO. Hash md5 del arbol completo antes/despues
   de `run installer scaffold --dry_run true`: el unico fichero que cambia es
   `agents/workspace/audit/audit.jsonl` (log sistemico de BaseAgent.run, lo
   escribe CUALQUIER accion). Cero ficheros nuevos, cero artefactos generados.
   Verificado por lista de ficheros, no por git status (el repo no tiene commits).

2. **dry_run false genera los 3 y registra** — CUMPLIDO. En la copia:
   `pagos_agent.py` + `pagos_agent.md` + `test_pagos_agent.py`, data.registered=true.

3. **contrato inline + validate_contracts limpio** — CUMPLIDO.
   `describe pagos` trae el contrato inline (role/owns/collaborates/destructive).
   `validate_contracts(set(agent_registry.all()))` == [] con los 3 generados dentro.

4. **stubs nunca mienten** — CUMPLIDO. Barrido AST de los 3 modulos generados:
   las 14 llamadas a AgentResult tienen success=False. Ejecutadas las 14 acciones
   una por una: todas success=False y con `needs` no vacio.

5. **rechaza nombres que colisionan** — CUMPLIDO. Rechazados en vivo:
   `describe`, `run`, `actions`, `can_handle` (atributos de BaseAgent) y `git`
   (ya registrado). Mensajes accionables.

6. **destructive + puerta sin --yes** — CUMPLIDO. `scaffold` esta en
   destructive del contrato de installer; sin --yes devuelve success=False,
   "no se ha autorizado", y NO escribe nada.

7. **prompts_sync en verde tras generar** — CUMPLIDO. En la copia con 3 agentes
   generados dentro: "Prompts y subagentes sincronizados". Exit 0.

8. **tests** — CUMPLIDO. 22 tests en test_installer_scaffold.py. Aislados via
   fixture `context` (tmp_path) + teardown que limpia el registro global.
   Sin agentes fantasma: orden A y orden B (invertido) junto a
   test_capability_collisions / test_prompts_sync / test_contracts → 46 passed
   en ambos ordenes. En solitario: 22 passed.

9. **make check pasa** — CUMPLIDO. Repo real: 512 passed, lint+typecheck+arnes OK.

## La prueba que de verdad importaba

`make check` ENTERO en la copia CON los agentes generados dentro:
- con 1 agente (`pagos`): **517 passed**, exit 0
- con 3 agentes, incluido uno patologico: **535 passed**, exit 0
- `./init.sh` completo: ENTORNO LISTO, 0 avisos

## El bug de BOOT-001 no se puede regenerar

Generado a proposito un agente con acciones `describe;run;actions;can_handle`:
el generador renombra el METODO (`describe_action`, `run_action`...) y conserva
el nombre de la ACCION. Resultado en la copia:
- `python -m agents list` sigue funcionando (exit 0), lista el agente
- `python -m agents describe colisiones` devuelve la ficha correcta
- `run colisiones run` y `run colisiones describe` despachan bien
- ruff check + format --check: limpio
Y un agente LLAMADO `describe` se rechaza de plano.

## owns colisionando

CUMPLIDO y de forma temprana (rechazo en validar(), no solo en validate_contracts):
`--owns Makefile` → "ya tiene dueño ('make')"; `--owns harness/progress/` →
"ya tiene dueño ('harness')"; `--collaborates noexiste` → rechazado.

## Alcance

- `agents/tools/agent_scaffold_tool.py` es la separacion CORRECTA, no abstraccion
  especulativa: `agents/agents/_template_agent.py` linea 13 dice literalmente
  "Si necesitas una herramienta que no existe, creala en agents/tools/ en vez de
  meter la logica directamente en el agente". Ademas queda en el registro de
  tools (`python -m agents tools` lista `agent_scaffold`). El agente conserva la
  escritura en disco, que es lo suyo: es el dueño de agents/external/.
- `agents/contracts.py`: solo el contrato de `installer`. La maquinaria de
  contratos inline (INLINE_CONTRACT_ATTR, inline_contracts, all_contracts,
  contract_for) es de BOOT-001 — confirmado en history.md linea 22-27. No tocada.
- Sin rutas absolutas ni secretos en lo nuevo. Los 13 hallazgos de `secrets scan`
  son fixtures preexistentes de test_redaction.py / test_secrets_agent.py.

## Bloqueantes

_(ninguno)_

## No bloqueante

1. **La discrepancia del implementer es REAL — confirmada leyendo
   agents/permissions.py:70**: `return not kwargs.get("dry_run")` mira los kwargs
   RECIBIDOS, no el default de la firma. Reproducido: `run installer scaffold
   --name pagos ...` SIN `--dry_run` queda bloqueado por la puerta pese a que
   dry_run=True por defecto no escribiria nada. **Me parece aceptable dejarlo
   asi**: falla del lado seguro (bloquea de mas, nunca de menos), y arreglarlo
   cambia el comportamiento de la puerta para los 24 agentes — es una feature
   aparte, no de BOOT-002. La mitigacion (el prompt manda usar --dry_run true)
   es suficiente por ahora. Anotar como deuda.
2. **`agents/external` esta en `extend-exclude` de ruff** (pyproject.toml:58) y
   `E501` esta en `ignore`. O sea: el cuidado del generador por emitir codigo
   ruff-limpio no lo verifica `make check` sobre el modulo en su ubicacion real
   — lo verifica el test con un ruff.toml propio, que es lo correcto. Detectado
   de paso: con muchas acciones colisionantes el comentario "# Ojo: ..." llega a
   155 chars; hoy es inocuo porque E501 esta ignorado, pero se romperia si
   alguien lo activa.
3. **El `owns` por defecto (`agents/workspace/<name>/`) no pasa por la
   validacion de colision** — solo se validan los `--owns` explicitos. Hoy no es
   explotable (todos los owns de workspace coinciden con el nombre del agente, y
   los nombres duplicados ya se rechazan), pero es un hueco latente.
4. **Escritura no atomica**: los 3 ficheros se escriben en bucle. Si fallase el
   segundo, quedaria un modulo registrado sin prompt → prompts_sync en rojo.
   Muy improbable; no justifica rechazo.
5. `_desregistrar` toca `agent_registry._agents` (privado) porque el registro no
   expone `unregister`. Esta documentado en el codigo. Candidato a API publica.
