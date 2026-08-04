# implementer · BOOT-002

- **Fecha:** 2026-08-04
- **Veredicto:** ok

## Qué cambié

- `agents/tools/agent_scaffold_tool.py` (NUEVO) — `AgentSpec` + `AgentScaffoldTool`: valida la spec y renderiza los tres ficheros (módulo, prompt, test). Aquí vive el renderizado estable para `ruff format` y la regla de que nada tape a `BaseAgent`.
- `agents/agents/installer_agent.py` — acción `scaffold` (+ `_registrar_en_caliente`, `_desregistrar`), entrada en `actions()`, aviso `_AVISO_ESQUELETO` y dos párrafos en el docstring del módulo.
- `agents/contracts.py` — solo el contrato de `installer`: `scaffold` en `destructive`, una línea en `can`, una en `cannot`, una en `needs`, `bootstrap` en `collaborates`.
- `agents/prompts/installer_agent.md` — sección a mano «`scaffold` genera un esqueleto, no un agente que funcione» + bloque AUTOGEN regenerado con `prompts_sync --write`.
- `agents/tests/test_installer_scaffold.py` (NUEVO) — 22 tests.

## Criterios de aceptación

1. **dry-run enseña sin escribir** → `run installer scaffold --name demo_scaffold ... --dry_run true` devuelve `data.files` (ruta + contenido de los 3) y `agents/external/` sigue con solo `__init__.py` y `README.md`. Test: `test_dry_run_no_escribe_nada_y_devuelve_la_previsualizacion`.
2. **dry_run false genera los 3 y registra** → `test_genera_los_tres_ficheros_y_registra_el_agente`; end-to-end sobre una copia real del repo: `run installer scaffold --name pagos ... --dry_run false --yes` → `python -m agents list` lista `pagos`.
3. **contrato inline + validate_contracts limpio** → `test_el_agente_generado_tiene_contrato_inline_y_no_rompe_los_contratos`.
4. **stubs con success=False y needs** → `test_los_stubs_devuelven_fallo_con_needs_nunca_un_exito_falso`; en real: `run pagos cobrar` → `✘ [pagos.cobrar] pagos.cobrar: es un esqueleto de installer scaffold y todavía no hace nada.`
5. **rechaza nombres inválidos** → `test_rechaza_nombres_invalidos` (8 casos: `describe`, `run`, `git`, `mi-agente`, `2fast`, `Demo`, `class`, `demo_agent`).
6. **scaffold destructivo y bloqueado sin --yes** → `test_scaffold_esta_declarado_como_destructivo_y_la_puerta_lo_bloquea` + `test_la_puerta_no_pregunta_en_dry_run`.
7. **prompts_sync en verde tras generar** → `test_prompts_sync_no_reporta_el_agente_generado_como_sin_prompt`; en la copia real, tras generar `pagos`: `✔ Prompts y subagentes sincronizados`.
8. **el código generado pasa ruff** → `test_el_codigo_generado_pasa_ruff` (ruff check + format --check sobre tmp_path con la config del proyecto).
9. **make check pasa** → 512 passed, lint/typecheck/arnés OK.

## Evidencia

```
$ uv run python -m agents.prompts_sync
✔ Prompts y subagentes sincronizados con el código y con los contratos.

$ make check
uv run ruff check app/ tests/ agents/
All checks passed!
uv run ruff format --check app/ tests/
6 files already formatted
uv run mypy app/ tests/
Success: no issues found in 6 source files
  ✅ typecheck OK
uv run pytest
======================= 512 passed, 15 skipped in 11.13s =======================
  ✅ check pasado: lint + typecheck + test + arnés OK

$ ./init.sh
━━ ENTORNO LISTO ━━  0 aviso(s)

$ ls agents/external/
__init__.py  __pycache__  README.md
```

## Decisiones no obvias

- **`name`/`description` con default `""`** en vez de obligatorios como en la spec: si fueran obligatorios, `run()` lanzaría `TypeError` y la CLI sacaría un traceback. Con default se devuelve `success=False` + `needs`, que es el mecanismo estándar del sistema (mismo patrón que `git.commit_feature(id="", title="")`).
- **Acción que choca con `BaseAgent`: se renombra el MÉTODO, no se rechaza.** `--actions describe` genera acción `describe` → método `describe_action`, con un comentario en el código explicando por qué. Es la solución que ya se aplicó a mano en BOOT-001 (`describe`/`describe_project`), y rechazar obligaría al usuario a renombrar una acción que es legítima. El NOMBRE DEL AGENTE sí se rechaza (ahí no hay nada que renombrar).
- **Se rechazan los nombres acabados en `_agent`**: el sufijo lo pone el generador (`pagos` → `pagos_agent.py`), y `prompts_sync` busca siempre `<name>_agent.md`, así que `pagos_agent` daría `pagos_agent_agent.md`.
- **Se exige al menos una acción**: un agente sin acciones no puede hacer nada; se devuelve `needs` en vez de generar una cáscara vacía.
- **`scaffold` ejecuta el módulo que acaba de generar** (`_registrar_en_caliente`) para poder llamar a `prompts_sync.render_block`, que necesita el agente REGISTRADO para encontrar su contrato inline. Sin eso el prompt saldría sin la sección de límites y `prompts-check` lo marcaría desincronizado. En dry-run el registro se deshace en un `finally`; en real se deshace igual y se vuelve a descubrir con `discover(force=True)` para que la clase registrada sea la importada de disco (en tests sobre tmp_path no hay nada que importar y se re-registra la ya ejecutada).
- **Formato estable para `ruff format` por construcción**: listas y tuplas de más de un elemento siempre explotadas con coma final (magic trailing comma); las de un elemento, en una línea solo si caben en 100; las cadenas citadas como las citaría el formateador (comillas simples si el texto lleva `"`). El test lo comprueba con un `ruff.toml` que replica `[tool.ruff]` del proyecto — con `known-first-party = ["agents"]` explícito, porque en tmp_path la deducción de primera-parte de isort clasifica mal `agents.external.<mod>`.
- **La lógica de renderizado va en `agents/tools/`**, no en el agente, siguiendo lo que dice `_template_agent.py`. La acción y la escritura en disco sí están en `installer_agent.py`: el dueño de `agents/external/` es el agente.

## Discrepancia con el diseño (no la cambié, la reporto)

`permissions.requiere_confirmacion()` decide mirando los **kwargs recibidos**, no el default de la firma: `return not kwargs.get("dry_run")`. Como `scaffold` tiene `dry_run=True` por defecto, invocarlo SIN pasar `--dry_run` queda bloqueado por la puerta aunque no fuera a escribir nada. No es incoherencia con el precedente (`git commit_feature` tiene `dry_run=False`, así que el caso nunca se dio), pero sí ruido: la puerta pregunta por una llamada inocua.

Propuesta (fuera del alcance de BOOT-002, afecta a todos los agentes): que `requiere_confirmacion` resuelva el valor efectivo de `dry_run` con `inspect.signature` del método antes de decidir. Son ~4 líneas en `agents/permissions.py` y un test. No lo he tocado porque cambia el comportamiento de la puerta para todo el equipo.

Mitigación mientras tanto: el prompt de `installer` dice explícitamente que se ejecute con `--dry_run true`, que es además lo que uno quiere hacer primero.

## Qué falta

- Documentación de usuario (`agents/README.md` con 24 agentes y `scaffold`, `AGENTS.md`, ficha en `vault/05_AGENTES/`) — es BOOT-003, y no la he tocado a propósito.
- README raíz sin cambios: `scaffold` es una acción de un agente interno, no cambia la interfaz del producto (`app/`).
