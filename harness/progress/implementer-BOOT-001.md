# implementer · BOOT-001

- **Fecha:** 2026-08-04
- **Veredicto:** ok

## Adenda tras la revisión (barrido del conteo de agentes)

El reviewer aprobó BOOT-001 con un pendiente: quedaban menciones al conteo viejo de agentes.

### Qué cambié en esta pasada

- `agents/prompts/agents_reference.md:233` — `23 agents` → `24 agents` en el diagrama ASCII.
- `agents/prompts/orchestrator.md:10` — `puntúa los 23 agentes` → `puntúa los 24 agentes`.

### Qué NO cambié, por decisión explícita del líder

- `CHANGELOG.md:17` — dueño: `documentation`. La línea describe la 0.1.0, que tenía 23 agentes de verdad; reescribirla falsearía el histórico. El 24 entra solo en la entrada de la 0.1.1 al cerrar la feature.
- `harness/progress/reviewer-BOOT-001.md:82` — el informe del reviewer cita literalmente la cadena "23 agents" al reportar el defecto. Es un registro histórico y `harness/progress/` no es mío. Ojo: este hit seguirá saliendo en cualquier `grep -rn "23 agent"` sobre el repo, así que el grep NO es una comprobación limpia tal cual — hay que excluir `harness/progress/` y `CHANGELOG.md` o el chequeo dará falso positivo para siempre.

### Verificación

$ grep -rn "23 agent" . --include=*.md --exclude-dir=.venv --exclude-dir=.git
CHANGELOG.md:17:- Sistema de 23 agentes Python en `agents/`, con contratos de rol y puerta de
harness/progress/reviewer-BOOT-001.md:82:1. `agents/prompts/agents_reference.md:233` sigue diciendo "23 agents" dentro del diagrama ASCII

$ uv run python -m agents.prompts_sync
✔ Prompts y subagentes sincronizados con el código y con los contratos.

$ make check
All checks passed!                       (ruff check)
6 files already formatted                (ruff format --check)
Success: no issues found in 6 source files  (mypy)
  ✅ typecheck OK
======================= 490 passed, 15 skipped in 19.60s =======================
━━ ENTORNO LISTO ━━  1 aviso(s)
  ✅ check pasado: lint + typecheck + test + arnés OK

Sin commit ni `git add`.

## AUTOMEJORA DEL ARNÉS — candidato a feature nueva (NO implementado)

El conteo de agentes escrito a mano en la documentación se ha escapado DOS VECES SEGUIDAS en esta misma feature: primero barrí 8 ficheros y se quedaron `agents_reference.md:233` (diagrama ASCII, formato "23 agents" en inglés, que mi grep en español no cazó) y `orchestrator.md:10`. Por la regla de automejora de AGENTS.md ("si un fallo se cuela dos veces, ¿es automatizable? → a init.sh"), esto ya no es un despiste: es una comprobación que falta.

Propuesta para la feature: un check en `init.sh` (y su test) que cruce `len(agent_registry.all())` con los conteos escritos en la documentación.

Detalles que la implementación va a necesitar, y que ya me costaron esta vez:

1. El patrón tiene que cubrir español e inglés y las dos formas: `N agentes`, `N agents`, `los N agentes`, `Los N agentes`. La mención que se escapó estaba en inglés dentro de un diagrama ASCII.
2. Hay que EXCLUIR `CHANGELOG.md` (histórico por versión: sus números son correctos aunque no coincidan con el actual) y `harness/progress/` (informes de agentes que citan cadenas literales). Sin esas exclusiones el check da falso positivo permanente.
3. Ficheros a vigilar hoy: README.md, AGENTS.md, agents/README.md, agents/prompts/agents_reference.md, agents/prompts/orchestrator.md, .opencode/agents/orquestador.md, .opencode/agents/lider.md.
4. Alternativa más barata y sin lista de exclusiones: dejar de escribir el número a mano. Sustituirlo por "los agentes Python" en la prosa y dejar el conteo exacto solo donde lo genere código (`agents list`). Un número que nadie escribe no se desincroniza nunca. Recomiendo evaluar esta antes de construir el check.
