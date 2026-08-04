# implementer · BOOT-004

- **Fecha:** 2026-08-04
- **Veredicto:** ok

## Qué cambié

- `agents/agents/knowledge_agent.py` — acción nueva `sync_agent_cards` + helpers de ficha (`_card_title`, `_split_frontmatter`, `_legacy_prose`, `_card_block`) y su alta en `actions()`/`action_aliases()`.
- `agents/contracts.py` — `knowledge.destructive = ("sync_agent_cards",)` con el porqué en comentario.
- `agents/prompts_sync.py` — `_splice()` acepta `begin`/`end`; el mecanismo bloque-autogenerado + prosa-conservada se reutiliza tal cual, no se inventa otro.
- `agents/permissions.py` — `requiere_confirmacion()` acepta el método y resuelve `dry_run` desde el defecto de la firma (`_es_dry_run`). Sin esto, una acción destructiva con `dry_run=True` por defecto pedía permiso para no escribir nada — contradice el docstring del módulo y afectaba ya a `installer scaffold`.
- `agents/core/base_agent.py` — pasa `available[action]` a la puerta (1 línea).
- `agents/tests/test_knowledge_agent.py` — 6 tests nuevos sobre la fixture `context` (tmp_path).
- `agents/tests/test_permissions.py` — 2 tests: el dry-run por defecto no pregunta; `dry_run=False` sí.
- `agents/prompts/knowledge_agent.md` — línea de prosa sobre `sync_agent_cards` + bloque autogenerado regenerado.
- `README.md` — sección Vault: cómo se generan las fichas de `05_AGENTES/`.
- `vault/05_AGENTES/*.md` — 24 fichas sincronizadas (1 nueva: `BootstrapAgent.md`).
- `vault/05_AGENTES/_index.md` — fila y nodo mermaid de `bootstrap` (a mano: el índice agrupa por categorías que el contrato no sabe).

## Criterios de aceptación

1. Una ficha por agente registrado, inline incluidos →
   `uv run python -m agents --json run knowledge sync_agent_cards --dry_run false --yes`
   → \"24 ficha(s) sincronizadas... 1 nueva(s), 23 actualizada(s)\"; `ls vault/05_AGENTES/ | wc -l` → 25 (24 fichas + _index.md).
   Test: `test_sync_agent_cards_escribe_una_ficha_por_agente`, `test_sync_agent_cards_incluye_contrato_inline`.
2. Rol/can/cannot/needs/owns/collaborates/destructive desde `all_contracts()` → `cat vault/05_AGENTES/BootstrapAgent.md`.
   Test: `test_sync_agent_cards_contenido_desde_el_contrato` (compara literal contra `contract_for('git')`).
3. `dry_run` por defecto sin escribir → primera ejecución: \"[dry-run] 1 ficha(s) nuevas y 23 actualizada(s)\", warning \"Nada escrito\".
   Test: `test_sync_agent_cards_dry_run_no_escribe`.
4. Huérfanas reportadas, no borradas → `data.orphans`. Test: `test_sync_agent_cards_reporta_huerfanas_sin_borrarlas`.
5. Tests sobre tmp_path → fixture `context` de `agents/tests/conftest.py`; ningún test toca `vault/` del repo.
6. `make check` y `prompts_sync` en verde (evidencia abajo).

Extra no pedido pero verificado: la prosa a mano de las 23 fichas de plantilla sobrevive (`test_sync_agent_cards_conserva_la_prosa_a_mano`) y la acción es idempotente (2ª pasada: \"24 sin cambios\").

## Evidencia

$ uv run python -m agents --json run knowledge sync_agent_cards
  \"message\": \"[dry-run] 1 ficha(s) nuevas y 23 actualizada(s) de 24 agente(s) en vault/05_AGENTES/ (0 ya al día). Pasa dry_run=False para escribirlas.\"
  \"created\": [\"vault/05_AGENTES/BootstrapAgent.md\"], \"missing_from_index\": [\"BootstrapAgent\"], \"dry_run\": true

$ uv run python -m agents --json run knowledge sync_agent_cards --dry_run false --yes
  \"message\": \"24 ficha(s) sincronizadas en vault/05_AGENTES/: 1 nueva(s), 23 actualizada(s), 0 sin cambios.\"

$ ls vault/05_AGENTES/ | wc -l
25

$ uv run python -m agents.prompts_sync
✔ Prompts y subagentes sincronizados con el código y con los contratos.

$ make check
520 passed, 15 skipped in 10.86s
All checks passed! (ruff) · Success: no issues found in 6 source files (mypy)
  ✅ check pasado: lint + typecheck + test + arnés OK

$ ./init.sh
  ✔ pytest                 6 passed in 0.14s
━━ ENTORNO LISTO ━━  0 aviso(s)

## Decisiones no obvias

- **`sync_agent_cards` SÍ es destructive.** Reescribe de golpe 24 ficheros del vault del humano, sin backup y sin depender de git. `installer scaffold` lo está por menos. Pero con la puerta tal como estaba, marcarlo rompía el dry-run por defecto (ver siguiente punto).
- **La puerta miraba solo los kwargs explícitos.** `requiere_confirmacion` hacía `kwargs.get(\"dry_run\")`, así que `run knowledge sync_agent_cards` (dry-run por defecto) pedía confirmación para no escribir nada — exactamente \"el ruido que se aprende a ignorar\" que su propio docstring dice evitar. Ahora resuelve el defecto de la firma. Efecto colateral deseado: `installer scaffold` sin argumentos deja de preguntar por su propia simulación.
- **`_index.md` no se autogenera.** Agrupa por categorías y lleva un mermaid que el contrato no contiene; regenerarlo sería inventar. La acción lo audita (`missing_from_index` + warning) y yo añadí la fila de `bootstrap` a mano.
- **Nombre de fichero = `cls.__name__`**, no el `name` del agente, para respetar `GitAgent.md`/`APIAgent.md`. El título se deriva del CamelCase (`APIAgent` → `API Agent`) para que las 23 fichas existentes conserven su encabezado.
- **Frontmatter conservado literal**, y el bloque autogenerado empieza *después* de él: si el comentario HTML fuera lo primero del fichero, Obsidian dejaría de leer las properties.
- **Contrato sin agente registrado**: se salta y se avisa; no se crea ficha de un agente que no existe.
