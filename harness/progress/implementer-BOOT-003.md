# implementer · BOOT-003

- **Fecha:** 2026-08-04
- **Veredicto:** ok

## Que cambie

- `.opencode/agents/lider.md` — paso 0 en el bloque de protocolo (`run bootstrap status` antes de la puerta) + seccion nueva "Paso 0 — arranque en frio" con el ciclo completo (seed/describe/suggest_agents/scaffold), las dos decisiones que son del usuario y la condicion de salida.
- `.claude/agents/lider.md` — REGENERADO con `make assistants-sync`. No editado a mano.
- `agents/agents/bootstrap_agent.py` — TICKETS_ARRANQUE, ONBOARD-001: el criterio de `describe` ahora lleva `--yes`. Sin el, el criterio era infalsable porque `describe` es destructive y la puerta lo bloquea. Una cadena, nada mas. La puerta no se toca.
- `agents/README.md` — subseccion "`installer scaffold` — crear un agente que todavia no existe" dentro de "Instalar agentes": los tres ficheros que genera, dry_run como modo por defecto, el esqueleto que devuelve success=false a proposito y que sin el prompt `prompts_sync` sale en rojo. La tabla ya decia 24 agentes e incluia bootstrap (BOOT-001): verificado, no duplicado.
- `AGENTS.md` — paso 0 anadido al bloque de 8 pasos + seccion "Arranque en frio" (status, dos tickets ONBOARD-*, el objetivo lo escribe el usuario, condicion de salida).
- `harness/featureslist.json` — ONBOARD-001 y ONBOARD-002 sembrados via `run bootstrap seed --yes`. No editado a mano.

## Criterios de aceptacion

1. lider.md con paso 0 → `grep -n "Paso 0" .opencode/agents/lider.md` → linea 53.
2. .claude/agents/lider.md regenerado → `make assistants-sync` → "1 subagente(s) espejados a .claude/agents/: lider"; `grep -n "bootstrap status" .claude/agents/lider.md` → linea 21.
3. ONBOARD-* sembrados → `run bootstrap seed --yes` → added=[ONBOARD-001, ONBOARD-002]; segunda llamada → skipped=[ONBOARD-001, ONBOARD-002] (idempotente). `bootstrap status` → onboarding_tickets_seeded: true. Criterio en el JSON: `... describe --description "<respuesta del usuario>" --yes devuelve success=true`.
4. agents/README.md → 24 agentes + fila bootstrap (ya estaban) + scaffold documentado.
5. AGENTS.md documenta el arranque en frio.
6. vault/05_AGENTES/BootstrapAgent.md → NO EXISTE. Ver bug abajo.
7. `uv run python -m agents.prompts_sync` → verde, exit 0.
8. `make check` → 512 passed, 15 skipped; ENTORNO LISTO. `./init.sh` completo → 6 passed, 0 avisos, ENTORNO LISTO, exit 0.

## Evidencia

$ uv run python -m agents.prompts_sync
  Prompts y subagentes sincronizados con el codigo y con los contratos.  (exit 0)

$ make check
  512 passed, 15 skipped in 9.81s
  ENTORNO LISTO  1 aviso(s)   [el aviso es pytest omitido por --quick dentro de make check]
  check pasado: lint + typecheck + test + arnes OK   (exit 0)

$ ./init.sh
  Entorno/Arnes/Backlog/Proyecto todo en verde
  pytest  6 passed in 0.33s
  ENTORNO LISTO  0 aviso(s)   (exit 0)

$ uv run python -m agents --json run bootstrap status
  first_run: false, onboarding_tickets_seeded: true, description_pending: true

## BUG encontrado (NO arreglado, es otra feature)

`vault/05_AGENTES/BootstrapAgent.md` no existe y `knowledge setup_vault` no puede crearlo. El problema no son los contratos inline: `all_contracts()` SI recoge el de bootstrap (24 contratos para 24 agentes registrados; `'bootstrap' in all_contracts()` → True, `in CONTRACTS` → False).

El problema es que NINGUNA accion escribe `vault/05_AGENTES/`:
- `setup_vault` solo detecta/crea el esqueleto de la boveda; con una boveda existente devuelve `created: false` y sale sin tocar nada.
- `build`/`sync` exportan el grafo de graphify, no las fichas de contrato.
- `grep -rn "05_AGENTES" --include="*.py" agents/` solo da comentarios y el propio contrato de knowledge; ni Makefile ni init.sh generan nada.

Es decir: las 23 fichas existentes vienen de la plantilla o estan escritas a mano, y el contrato de `knowledge` promete algo que no esta implementado ("poblar vault/05_AGENTES/ con fichas individuales de cada agente desde contracts.py", contracts.py:175).

Lo que haria falta: una accion `knowledge sync_agent_cards` (o extender setup_vault) que itere `all_contracts()` y renderice una ficha por agente con el formato de las existentes, borrando las de agentes que ya no existen. Con eso la ficha de bootstrap sale sola y ademas dejan de divergir las 23 que hay. No lo he hecho porque el criterio 6 no se puede cumplir sin escribir en vault/ a mano (prohibido, es de `knowledge`) y porque es codigo nuevo fuera del alcance de BOOT-003.

## Otra cosa que conviene saber (no tocada)

La puerta de permisos solo mira los kwargs que le llegan (`permissions.py:70`, `not kwargs.get(\"dry_run\")`). `installer scaffold` tiene `dry_run: bool = True` por defecto, asi que llamarlo SIN `--dry_run` no hace un dry-run silencioso: se para en la puerta y pide `--yes`. Verificado en el repo real. Por eso el protocolo del lider y el README usan `--dry_run true` EXPLICITO. No es un fallo de seguridad (falla del lado seguro), pero contradice la frase de AGENTS.md "Un `--dry-run` nunca pregunta". No lo he cambiado: seria otra decision.

## Que falta

- El criterio 6 (ficha de bootstrap en el vault) queda sin cumplir por el bug de arriba. Decision del lider: abrir feature para el generador de fichas, o quitar el criterio.
- Sin commit ni git add, como se pidio.
