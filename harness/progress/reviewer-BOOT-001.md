# reviewer · BOOT-001

- **Fecha:** 2026-08-04
- **Veredicto:** aprobado

Puerta ejecutada por mi en esta sesion: `harness gate` -> success=true, "ENTORNO LISTO", 0 errores / 0 avisos.
`./init.sh` completo -> pytest 6 passed, ENTORNO LISTO, 0 avisos, exit 0.

## Criterios (uno a uno, salida propia)

1. CUMPLIDO. `uv run python -m agents list` -> exit 0, 24 lineas, `bootstrap` presente
   ("Arranque en frio del proyecto: detecta la primera ejecucion..."). Sin TypeError.
2. CUMPLIDO. `uv run python -m agents --json describe bootstrap` -> dict con name/description/
   capabilities(11)/actions ["describe","seed","status","suggest_agents"] y "contract" completo
   (role, can x4, cannot x4, needs, owns=[project.yml, agents/workspace/bootstrap/],
   collaborates, destructive=["describe","seed"]). Es el contrato inline de la clase.
3. CUMPLIDO. `agents/prompts/bootstrap_agent.md` existe: 55 lineas de prosa + bloque AUTOGEN
   delimitado (lineas 56-85). La prosa NO duplica el AUTOGEN: son criterios de juicio que el
   generador no puede producir ("no inventes el proposito", "suggest_agents da candidatos no
   veredictos" con los dos falsos positivos/negativos explicados, "seed delega no escribe",
   "status primero"). El AUTOGEN solo lleva tabla de acciones y limites. No hay deriva.
4. CUMPLIDO. `uv run python -m agents.prompts_sync` -> exit 0,
   "OK Prompts y subagentes sincronizados con el codigo y con los contratos."
5. CUMPLIDO. test_contracts.py cubre las cuatro funciones: inline_contracts (lee el atributo de
   clase), all_contracts (fusiona ambas fuentes), contract_for (fallback al atributo + None para
   desconocido + CONTRACTS gana sobre inline), validate_contracts (detecta colision de `owns`
   contra harness/featureslist.json). Los 2 tests previos intactos. 8 passed.
   test_bootstrap_agent.py cubre las 4 acciones: status x3, seed x3, describe x4,
   suggest_agents x3, + 4 de regresion de la colision. 20 passed.
6. CUMPLIDO. `make check` -> ruff OK, format OK, mypy OK, pytest 490 passed / 15 skipped,
   init.sh --quick ENTORNO LISTO, exit 0.

## Verificaciones extra (las que pedia el encargo)

- Colision `describe`, LAS DOS MITADES: el metodo es `describe_project` y la clave de accion
  sigue siendo "describe" en actions(). Comprobado por CLI en una COPIA del repo (scratchpad),
  no en el repo real: `run bootstrap describe --description "..."` (sin --yes) -> success=false
  con el mensaje de la puerta de permisos; con `--yes` -> success=true, "Descripcion escrita en
  project.yml" y la linea project_description reescrita conservando el resto del fichero.
  `run bootstrap status` y `run bootstrap suggest_agents` -> success=true. `run bootstrap seed
  --yes` -> 2 tickets sembrados. Y `describe bootstrap` sigue devolviendo la ficha dict.
- Aislamiento de los tests, verificado con md5 antes/despues de `make check`:
  project.yml, harness/featureslist.json, harness/progress/{current,history,README,
  implementer-BOOT-001}.md, .opencode/agents/lider.md y .claude/agents/lider.md -> TODAS las
  sumas coinciden. `agents/workspace/` no tiene directorio `bootstrap/` (el state.json de
  describe solo se escribe en tmp_path). Nota: este repo aun no tiene ningun commit, asi que
  `git status --short` no distingue modificados; por eso el control es por md5, que es mas
  fuerte. Todos los tests usan la fixture `context` de agents/tests/conftest.py (tmp_path).
- Tests no tautologicos: `test_describe_without_description_asks_and_writes_nothing` guarda el
  contenido del fichero ANTES y afirma la igualdad byte a byte despues, ademas de not success y
  needs. `test_describe_rejects_a_description_too_short` tambien comprueba que la descripcion de
  plantilla sigue en el fichero. `test_seed_is_idempotent` verifica added==[] y skipped y que el
  backlog sigue con 2 features. `test_agent_card_is_a_dict_not_an_agent_result` y
  `test_list_agents_does_not_break` reproducen la regresion exacta y ademas quedan como guardia
  GENERICA: cualquier agente futuro que tape describe() rompe list_agents().
- Limpieza del registro: los dos agentes de prueba se registran en fixture y se sacan con
  `agent_registry._agents.pop(...)` en el teardown. Comprobado con 3 ordenes distintos:
  (contracts, prompts_sync, collisions) 24 passed; orden inverso 24 passed; (bootstrap,
  contracts, collisions, prompts_sync) 44 passed. Y cada fichero por separado: 8 / 15 / 1 / 20
  passed. No hay agente fantasma.
- Colisiones con BaseAgent en el resto de agentes: comprobado por mi sobre los 24 registrados,
  solo aparecen __abstractmethods__ y _abc_impl (maquinaria de ABC). Ninguna colision real.
  La afirmacion del implementer se sostiene.
- Alcance: legitimo. Los 7 ficheros de documentacion tocados son el conteo 23->24 y la fila de
  catalogo del nuevo agente, que es consistencia introducida POR esta feature. Verificado que
  agents/README.md y agents/prompts/agents_reference.md documentan los 24 agentes registrados
  (cruce programatico: faltan []). `.claude/agents/lider.md` es exactamente `.opencode/agents/
  lider.md` mas el frontmatter generado (diff limpio) -> estan sincronizados por prompts_sync,
  no editados a mano. El unico cambio en lider.md es "24 agentes"; NO hay paso 0 ni cableado de
  `bootstrap status` en el protocolo -> BOOT-003 no se ha colado.
- secrets scan: 13 hallazgos, TODOS en agents/tests/test_redaction.py y test_secrets_agent.py
  (fixtures preexistentes de los propios tests de deteccion). Cero en los ficheros de BOOT-001.
  Sin rutas absolutas en el codigo nuevo.
- review review_package: 4 ficheros, 0 hallazgos, 0 duplicacion.

## Bloqueantes

Ninguno.

## No bloqueante

1. `agents/prompts/agents_reference.md:233` sigue diciendo "23 agents" dentro del diagrama ASCII
   de arquitectura. Es la unica mencion al conteo viejo que queda en todo el repo y contradice
   el informe del implementer, que da ese fichero por barrido. Arreglar antes del commit.
   Sugerencia de automejora: no hay ninguna comprobacion que cruce el numero de agentes
   registrados con el que dicen los docs; si el conteo se vuelve a quedar atras, va a init.sh.
2. Las dos decisiones que el implementer levanta y NO cambio (correcto: son de rumbo, no suyas).
   (a) `describe` esta en `destructive`, asi que el criterio de aceptacion de ONBOARD-001 en
   TICKETS_ARRANQUE ("run bootstrap describe --description ... devuelve success=true") es
   infalsable tal y como esta escrito: sin --yes devuelve false. Confirmado por mi en la copia.
   El flujo "pregunta lo que falta" tambien es inalcanzable desde la CLI sin --yes. Hay que
   decidirlo antes de que ONBOARD-001 se abra, o el ticket nace fallando.
   (b) `status` dice first_run=true en este mismo repo (0 done, 0 entradas en history) pese a
   haber 7 features y una in_progress. Correcto segun su definicion, pero si BOOT-003 lo cablea
   al lider, `first_run` deberia mirar tambien in_progress y si el backlog trae features que no
   son las ONBOARD.
3. `make check` pasa mypy solo sobre `app/` y `tests/`, no sobre `agents/`. Preexistente, no de
   esta feature, pero significa que el codigo nuevo no esta typechequeado.
