# agents/ — Sistema de agentes del proyecto

Sistema de agentes especializados, tipo plugin. Cada agente tiene **una**
responsabilidad, un contrato de rol declarado y acciones deterministas: no
llaman a ningún LLM, se ejecutan por shell y funcionan con cualquier
asistente.

> 📄 **Novedad:** `AGENTS.md` en la raíz del proyecto — documentación rápida.
> **`agents/gstack/`** — flujos autónomos con auto-commit entre pasos, result passing,
> branching condicional y event logging.
> **`agents/helpers.py`** — `delegate_to()` para colaboración entre agentes.
> **Nuevo agente:** `doctor` — diagnóstico integral del proyecto.
>
> 🧭 **Trabajo en equipo:** `agents/contracts.py` — contratos de rol (qué puede,
> qué NO puede, qué necesita y qué recursos posee cada agente, con validación
> de que nadie pisa a nadie). **Agente `plan`** — describes el encargo, él
> pregunta lo que falte y delega. **Agente `audit`** + `agents/audit.py` —
> toda ejecución queda registrada y es medible para mejorar el equipo.
> Ver [Flujo de trabajo humano](#flujo-de-trabajo-humano-describir--responder--verificar).

## Filosofía

- **No es un chatbot.** Cada agente ejecuta tareas reales con herramientas
  (git, docker, pytest, el sistema de ficheros...), no conversa. El punto de entrada en
  lenguaje natural (`Orchestrator.dispatch`) es una capa fina de ruteo por
  encima de acciones deterministas, no un envoltorio de un LLM.
- **Agnóstico de proveedor de IA.** `agents/` es Python puro, invocado por
  CLI (`python -m agents ...`). No importa el SDK de Anthropic, ni el de
  ningún otro proveedor, ni depende de ningún formato propio de una
  herramienta concreta (Claude Code, Cursor, opencode...). Cualquier agente
  de codificación que pueda ejecutar comandos de shell puede usar este
  sistema exactamente igual.
- **Una responsabilidad por agente.** `GitAgent` no toca el Makefile,
  `MakeAgent` no toca git. Si una tarea necesita dos agentes, se orquestan en
  secuencia (ver `DocumentationAgent.update_changelog`, que llama a
  `GitAgent` internamente) — no se crea un agente todopoderoso.
- **Cero dependencias.** `agents/` es stdlib pura (`subprocess`, `ast`,
  `sqlite3`, `urllib`, `importlib.metadata`, `concurrent.futures`,
  `pickle`...). El arnés tiene que funcionar en un repo recién clonado,
  antes de instalar nada. La única excepción es el RAG, que necesita
  `chromadb` y por eso es un extra opcional: sin él, el resto sigue
  funcionando.
- **Los agentes conocen este proyecto**, no son genéricos: leen `project.yml`
  para saber cómo se llama el paquete y qué infraestructura existe
  (ver `agents/context.py` y `agents/config.py`).

## Arquitectura

```
agents/
├── __init__.py            # API pública: Orchestrator, BaseAgent, AgentResult...
├── __main__.py             # permite `python -m agents ...`
├── cli.py                  # CLI (list / describe / run / ask / plan / audit / tools / pipeline / doctor)
├── config.py                # lee project.yml -> ProjectConfig
├── context.py                # SharedContext: rutas + config + workspace por agente
├── contracts.py              # contratos de rol: can/cannot/needs/owns por agente + validación
├── audit.py                  # log JSONL de toda ejecución (lo escribe BaseAgent.run)
├── permissions.py            # la puerta: lo irreversible no se ejecuta sin --yes
├── policy_guard.py           # filtra Bash/Read/Write/MCP del asistente (hook opcional, ver AGENTS.md)
├── redaction.py              # tapa credenciales antes de que salgan hacia el modelo
├── helpers.py                # delegate_to(): colaboración entre agentes
├── orchestrator.py            # rutea lenguaje natural -> agente + acción
├── exceptions.py               # jerarquía de excepciones propia
├── gstack/                       # flujos autónomos con auto-commit, result passing, branching
│   ├── __init__.py               # GStack, pipelines predefinidos
│   ├── stack.py                  # Cola + ejecución secuencial + conditional run_if + event log
│   └── pipelines.py              # auto_develop, auto_release, auto_fix, auto_analyze...
├── core/
│   ├── base_agent.py            # BaseAgent, AgentResult, best_action()
│   └── registry.py               # @register_agent + auto-descubrimiento
├── tools/                          # herramientas reutilizables, una responsabilidad cada una
│   ├── git_tool.py · docker_tool.py · process_tool.py · filesystem_tool.py
│   ├── code_analysis_tool.py · pytest_tool.py · dependency_tool.py · cicd_tool.py
│   ├── sqlite_tool.py · rest_tool.py · api_tool.py · research_tool.py
│   ├── rag_tool.py · graphify_tool.py · memory_tool.py · secrets_tool.py
│   ├── cache_tool.py · parallel_tool.py · schedule_tool.py · agent_installer_tool.py
├── agents/                          # los 24 agentes (+ plantilla de ejemplo)
│   ├── git_agent.py · docker_agent.py · review_agent.py · refactor_agent.py
│   ├── test_agent.py · documentation_agent.py · doc_agent.py · rag_agent.py
│   ├── knowledge_agent.py · research_agent.py · memory_agent.py · audit_agent.py
│   ├── plan_agent.py · supervisor_agent.py · harness_agent.py · installer_agent.py
│   ├── cicd_agent.py · dependency_agent.py · secrets_agent.py · api_agent.py
│   ├── env_agent.py · make_agent.py · bootstrap_agent.py
│   ├── doctor_agent.py             # diagnóstico integral del proyecto
│   └── _template_agent.py            # plantilla — no se auto-registra (prefijo `_`)
├── external/                          # agentes de terceros / tuyos, fuera del núcleo
│   ├── README.md
│   └── __init__.py
├── workspace/                          # lo que generan los agentes — nunca en la raíz del proyecto
│   ├── README.md
│   └── <agente>/                        # creado bajo demanda por ctx.agent_workspace(nombre)
└── prompts/                            # una ficha markdown por agente (rol, cuándo usarlo)
```

### Flujo de una petición

```
Orchestrator.dispatch("genera el changelog desde el último tag")
  -> select_agent(): puntúa cada agente registrado con can_handle(query)
  -> agente ganador: GitAgent (keywords: "changelog", "git"...)
  -> agent.run("generate_changelog", since_tag=None)
  -> devuelve AgentResult(success, data, warnings)
```

Si prefieres evitar el ruteo por palabras clave, invoca el agente
directamente — es la vía recomendada cuando ya sabes qué necesitas:

```python
from agents.agents.git_agent import GitAgent
result = GitAgent().suggest_commit_message()
print(result.data["suggested_message"])
```

## Flujo de trabajo humano: describir → responder → verificar

El sistema está diseñado para que el humano invierta su tiempo en dirigir y
supervisar, no en ejecutar. El ciclo completo:

```bash
# 1. DESCRIBIR — un encargo en lenguaje natural (un paso por línea o con ';')
uv run python -m agents plan "corre los tests; actualiza el changelog; haz un tag release del proyecto git"

# 2. RESPONDER — el plan te devuelve TODAS las preguntas juntas (nunca inventa valores)
#    y guarda la orden en agents/workspace/plan/orden-<id>.json (editable a mano:
#    puedes cambiar agente/acción de un paso, borrar o reordenar antes de ejecutar)
uv run python -m agents run plan answer --order 20260709-120000 --step2-version 2.0.0

# 3. EJECUTAR — se niega si quedan huecos; delega cada paso al agente dueño
uv run python -m agents run plan execute --order 20260709-120000

# 4. VERIFICAR — resumen paso a paso + auditoría de lo ejecutado
uv run python -m agents audit            # uso, tasas de éxito, duraciones
uv run python -m agents audit failures   # fallos recientes con su mensaje
uv run python -m agents audit suggest    # mejoras propuestas con datos
```

Las tres reglas del equipo (definidas y validadas en `agents/contracts.py`,
test en `tests/test_contracts.py`):

1. **Nadie se pisa.** Cada recurso escribible (CHANGELOG.md, Makefile,
   `.github/workflows/`...) tiene UN dueño. Un agente que necesita tocar un
   recurso ajeno DELEGA en su dueño (`delegate_to`), no lo toca.
2. **Nadie improvisa fuera de su rol.** Cada contrato lista `cannot`: lo que
   ese agente no hace y a quién derivarlo. `python -m agents describe git`
   muestra el contrato completo de cualquier agente.
3. **Nadie inventa información.** Si falta un dato, la acción devuelve
   `AgentResult(success=False, needs=[preguntas])` — pregunta, no adivina.

### Auditoría: mejorar el equipo con datos

Toda ejecución que pasa por `run()` (CLI, Orchestrator, GStack,
`delegate_to`) se registra en `agents/workspace/audit/audit.jsonl` (JSONL,
sin dependencias — legible con `jq`). El agente `audit` lo agrega:
qué acción falla demasiado, cuál es lenta, qué agentes no se usan nunca.
Después de una temporada de uso, `audit suggest` te dice dónde invertir
(arreglar, documentar, retirar) sin depender de la memoria de nadie.
Punto ciego documentado: las llamadas directas a métodos
(`GitAgent().suggest_commit_message()`) no pasan por `run()` y no se auditan.

## Uso desde la CLI

```bash
uv run python -m agents list
uv run python -m agents describe git
uv run python -m agents run git suggest_commit_message
uv run python -m agents run git tag_release --version 1.9.0
uv run python -m agents run git commit_feature --id FEAT-001 --title "Primera pieza funcional" --dry-run true
uv run python -m agents run cicd generate_workflow
uv run python -m agents run test run_tests
uv run python -m agents run dependency check_outdated
uv run python -m agents run review review_package
uv run python -m agents run installer install_from_git --repo_url usuario/repo
uv run python -m agents ask "revisa el Dockerfile"

# Jefe de proyecto y auditoría (ver "Flujo de trabajo humano" arriba)
uv run python -m agents plan "corre los tests; haz un tag release del proyecto git"
uv run python -m agents run plan status
uv run python -m agents audit suggest

# Pipelines autónomos
uv run python -m agents pipeline develop
uv run python -m agents pipeline fix
uv run python -m agents pipeline release --version 1.0.0
uv run python -m agents pipeline analyze

# Doctor: diagnóstico + auto-fix
uv run python -m agents doctor
uv run python -m agents doctor --fix

# Herramientas
uv run python -m agents tools
```

## Instalar agentes — dos herramientas distintas, no redundantes

- **`installer` (agente, dentro de este sistema)**: instala un agente
  concreto (URL de git, atajo `usuario/repo`, o ruta local) dentro de un
  proyecto que **ya tiene** `agents/`. Es la vía normal para añadir un
  agente nuevo de un tercero o de otro proyecto tuyo.
- **Copiar `agents/` entera** a un proyecto que todavía no la tiene: es una
  carpeta autocontenida (stdlib pura), así que basta con copiarla junto a
  `project.yml`. El `installer` es para lo otro: añadir UN agente a un
  proyecto que ya tiene el sistema.

### `installer scaffold` — crear un agente que todavía no existe

Las dos vías de arriba mueven agentes que ya están escritos. `scaffold` es
para el hueco que no cubre ninguno: genera los **tres** ficheros de un agente
nuevo de una vez.

| Fichero | Qué lleva |
|---|---|
| `agents/external/<name>_agent.py` | El módulo, con su **contrato inline** (rol, can, cannot, needs, owns) |
| `agents/prompts/<name>_agent.md` | El prompt, renderizado desde ese contrato |
| `agents/tests/test_<name>_agent.py` | Los tests: que quede registrado, que tenga contrato y que no pise a nadie |

```bash
uv run python -m agents --json run installer scaffold --name drift \
  --description "Detecta deriva entre el dataset de entrenamiento y el de producción" \
  --capabilities "drift;deriva" --actions "check;report" --dry_run true
uv run python -m agents --json run installer scaffold --name drift ... --dry_run false --yes
```

Tres cosas que conviene saber antes de usarlo:

- **`dry_run=True` es el modo por defecto**, así que una llamada despistada
  nunca escribe: devuelve lo que generaría y ya. `scaffold` es `destructive`,
  de modo que la escritura real pide `--yes` — y la puerta de permisos solo
  ve los argumentos que le pasas, así que **pasa `--dry_run true` explícito**
  si quieres la propuesta sin que te pregunte.
- **Lo generado es un esqueleto: sus acciones devuelven `success=false` a
  propósito.** El agente queda registrado, con contrato y con test, pero no
  hace el trabajo — eso lo escribe quien lo pidió, en su propia feature.
- **El prompt no es opcional.** Un agente registrado sin su
  `agents/prompts/<name>_agent.md` deja `uv run python -m agents.prompts_sync`
  en rojo y tumba el CI; por eso `scaffold` genera los tres ficheros o ninguno.

## Los 24 agentes

Los ROLES (qué puede, qué no puede, qué necesita, qué posee) están en
`agents/contracts.py` — esta tabla resume la responsabilidad y las
herramientas de cada uno.

| Agente | Responsabilidad | Herramientas que usa |
|---|---|---|
| `harness` | **Dueño del arnés**: mantiene `harness/featureslist.json` y `harness/progress/`, ejecuta la puerta `init.sh` y **rehúsa cerrar** una feature si no pasa o si no hay evidencia real | `process_tool` |
| `plan` | **Jefe de proyecto**: convierte un encargo en lenguaje natural en una orden de trabajo, devuelve TODAS las preguntas que le falten antes de ejecutar nada, y delega cada paso al agente dueño | Orchestrator, GStack |
| `audit` | **Auditor del equipo**: mide uso, tasa de éxito y duración por agente/acción sobre el log de ejecuciones, y propone mejoras con datos en vez de impresiones | `agents/audit.py` (log JSONL) |
| `supervisor` | Lanza varios workers en competición sobre la misma tarea y arbitra cuál es la mejor propuesta | `parallel_tool` |
| `git` | Conventional Commits, changelog, release notes, breaking changes, resumen de PR, **commit+changelog en un paso** (`commit_with_changelog`), **cierre de features del arnés** (`commit_feature`: bump + CHANGELOG + commit, sin tag), **release completo** (`tag_release`) | `git_tool` |
| `documentation` | README ↔ Makefile desincronizados, actualiza CHANGELOG.md, **sube versión en pyproject.toml + README** (`bump_version`), genera docs Sphinx | `filesystem_tool`, `process_tool`, agente `git` |
| `review` | Funciones largas, demasiados argumentos, `except` desnudos, duplicación estructural, `eval`/`pickle.load`/`shell=True` | `code_analysis_tool` |
| `refactor` | Correcciones mecánicas sobre el código: mutables como argumento por defecto, `except:` → `except Exception:`, `-> None` en funciones públicas sin tipo de retorno. `dry_run=True` por defecto | `code_analysis_tool` |
| `test` | Ejecuta pytest, resume fallos/cobertura (JUnit XML + JSON de `pytest-cov`), detecta módulos sin test homónimo | `pytest_tool` |
| `env` | Entorno de desarrollo: versión de Python, `uv sync`, `uv lock --check`, `uv add`. Dueño de la sección de dependencias | `process_tool` |
| `dependency` | Paquetes desactualizados y vulnerabilidades conocidas (OSV vía API de PyPI) contra `uv.lock`. Necesita internet | `dependency_tool` |
| `secrets` | Escanea el proyecto en busca de secretos hardcodeados. Usa `detect-secrets` si está instalado; si no, un heurístico propio mucho más limitado (avisado explícitamente) | `secrets_tool` |
| `make` | Valida y gestiona el Makefile: verifica targets, comprueba que estén los targets base y sugiere nuevos según `project.yml` | `process_tool` |
| `cicd` | Genera y valida `.github/workflows/*.yml` cruzando los `make <target>` invocados contra el Makefile real. Valida y describe expresiones cron | `cicd_tool`, `schedule_tool` |
| `docker` | Lint de Dockerfile, validación de docker-compose | `docker_tool` |
| `api` | Cruza endpoints `@app.get/post(...)` declarados en `api/main.py` contra los documentados, y hace un smoke test real con `TestClient`. Solo con `use_api=true` | `api_tool` |
| `doctor` | Diagnóstico integral: python, git, estructura, tests, dependencias, uso de disco y arnés. Ofrece `checkup`, `disk_usage`, `summary` | `process_tool` |
| `installer` | Instala agentes externos (URL de git, atajo `usuario/repo`, o ruta local) en `agents/external/`, valida su estructura y confirma que quedan registrados | `agent_installer_tool` |
| `knowledge` | Construye y mantiene el grafo de conocimiento y la bóveda Obsidian. Único dueño de `vault/` | `graphify_tool` |
| `research` | Busca papers en arXiv/OpenAlex relacionados con el proyecto y los rankea. Necesita internet | `research_tool` |
| `memory` | **Memoria proactiva**: observa las trayectorias de los agentes y mantiene un banco estructurado (facts/state/traces) contra el decaimiento de estado en tareas largas | `memory_tool` |
| `rag` | RAG local con ChromaDB: busca fundiendo similitud vectorial y BM25 léxico. Indexa código, prompts, docs, vault y la memoria del arnés; también URLs externas. Reindexado incremental. Extra `rag` | `rag_tool` |
| `doc` | **Documentación unificada**: responde dónde está algo consultando a la vez el grafo, el índice semántico y el vault | `graphify_tool`, `rag_tool` |
| `bootstrap` | **Arranque en frío**: detecta si es la primera ejecución del arnés, siembra los tickets de onboarding delegando en `harness`, recoge la descripción del proyecto en `project.yml` (si falta, pregunta) y cruza esa descripción con las capacidades declaradas para señalar huecos | — (delega en `harness`) |

Cada agente documenta en su propio docstring qué responsabilidades de la
lista original están implementadas y cuáles quedan como extensión (p. ej.
`GitAgent.detect_breaking_changes` solo mira mensajes de commit, no el diff
de la API pública — está señalado explícitamente en su `AgentResult.warnings`).

### Límites conocidos que quedaron documentados construyendo estos agentes

- **`secrets`**: sin `detect-secrets` instalado, no detecta tokens de Slack/Stripe/GitHub/JWT/etc. — solo claves AWS, cabeceras PEM y asignaciones de alta entropía.
- **`rag`**: el embedder por defecto (all-MiniLM-L6-v2 ONNX) está entrenado en inglés y trunca a ~1.000 caracteres. Por eso la búsqueda es híbrida (vector + BM25 léxico): sin la mitad léxica, una consulta en español sobre nombres propios del proyecto no encuentra nada. Para embeddings multilingües: `HARNESS_RAG_EMBEDDER=multilingual` + `make index-rag-rebuild`.
- **`api`**: `fastapi.testclient.TestClient` avisa (deprecation warning) de que prefiere `httpx2` sobre `httpx` en las versiones actuales de Starlette — `httpx` (el que ya declara `pyproject.toml`) sigue funcionando, pero puede que en algún momento quieras migrar la dependencia.

### Agentes que colaboran entre sí (no todo tiene que ser independiente)

`agents/agents/git_agent.py` es el ejemplo de referencia: `commit_with_changelog`
llama a `DocumentationAgent.update_changelog` antes de hacer el commit,
`commit_feature` encadena `DocumentationAgent.bump_version` +
`DocumentationAgent.update_changelog` + `git commit` (sin tag; es el cierre
del arnés tras `harness finish`), y `tag_release` encadena `bump_version` +
`commit_with_changelog` + `git tag` en un único flujo. El patrón es siempre
el mismo: import perezoso (dentro del método, no a nivel de módulo, para
evitar ciclos de import) + instanciar el otro agente con `context=self.ctx`
+ llamar a `.run("accion", **kwargs)`. No hace falta un mecanismo especial
de orquestación entre agentes — son objetos Python normales.

## Cómo extender el sistema

### Añadir un agente nuevo

1. Copia `agents/agents/_template_agent.py` a `agents/agents/mi_agente.py`
   (quita el `_` inicial).
2. Define `name`, `description`, `capabilities` y los métodos de acción.
3. Nada más — el registro y la CLI lo descubren solos.

### Añadir una herramienta nueva

Créala en `agents/tools/`, decórala con `@register_tool("nombre")` si quieres
que aparezca en `python -m agents tools`, e impórtala desde el agente que la
necesite. Nunca dupliques una herramienta existente entre agentes.

**Idea para más adelante — base class para herramientas con estado:**
Si una herramienta necesita conexión (DuckDB, API externa, etc.), tiene
sentido crear una `BaseTool(ABC)` con `name`/`description` y ciclo de vida
(`connect`, `close`). Se eliminó porque ninguna herramienta lo
necesitaba aún — pero es un extract class fácil cuando surja el segundo caso.

### Agentes externos

`agents/external/` acepta dos vías (ver `agents/external/README.md`):
1. **Un archivo suelto**: mismo patrón `@register_agent`, se auto-descubre.
2. **Un paquete pip instalado** que expone un entry point del grupo
   `harness.agents` en su propio `pyproject.toml` — útil si el agente externo
   tiene dependencias propias o lo compartes entre varios proyectos.
3. **El agente `installer`** automatiza la vía 1 (clona/copia, valida
   estructura con AST, confirma el registro) — pero instalar código de un
   origen que no controlas sigue siendo ejecución de código arbitrario al
   importarlo. La validación es estructural, no de seguridad — revisa el
   código tú mismo si el origen no es de confianza. Ver
   `agents/prompts/installer_agent.md`.

**Nota sobre la vía 2 (entry points):** el sistema incluyó en su momento
el descubrimiento automático de entry points `harness.agents` via
`importlib.metadata`, pero se eliminó por ser infraestructura especulativa
sin ningún paquete externo que la usara. Si en el futuro aparece un agente
publicado como paquete pip, re-añadir el método
`AgentRegistry._discover_entry_points()` es trivial (< 15 líneas,
documentado en el historial git).

Ninguna de las tres vías requiere tocar `orchestrator.py`, `cli.py` ni
ningún otro agente.

## Extender el ruteo del Orchestrator

`Orchestrator.select_agent` elige el agente por palabras clave
(`BaseAgent.can_handle`), determinista a propósito (ver Filosofía).
`Orchestrator.dispatch` además adivina la **acción** con
`BaseAgent.best_action` (solapamiento de palabras con el nombre de la
acción) y solo la ejecuta sola si no necesita argumentos obligatorios
(`BaseAgent.can_auto_run`) — si hace falta un argumento que no se puede
adivinar de una frase (un `filename`, un `message`, una `version`...), se
informa de qué falta en vez de inventarlo.

Cuando dos acciones de un mismo agente comparten palabras con la consulta
(p. ej. "commit" aparece tanto en `commit_with_changelog` como en
`suggest_commit_message`), define `action_aliases()` en ese agente para
desambiguar — ver `GitAgent.action_aliases` para el caso real que motivó
este mecanismo. No hace falta definirlo para cada acción, solo donde hay
ambigüedad real.

Si más adelante quieres un ruteo basado en un LLM (de cualquier proveedor —
Anthropic, OpenAI, un modelo local...) decidiendo agente y acción, esos dos
métodos (`can_handle` y `best_action`) son el punto de extensión — no hace
falta tocar ningún agente ni el resto del `Orchestrator`.

---

## Agentes externos y lecturas recomendadas

Nada de lo que sigue viene integrado por defecto: son punteros a proyectos
de terceros que pueden servir de inspiración, o como base para un agente en
`agents/external/`. Las descripciones están verificadas contra la
documentación/README de cada proyecto en el momento de escribir esto — aun
así, estos repos cambian rápido, conviene revisar el estado actual antes de
depender de alguno.

### Instalación rápida

```bash
# Skills.sh (requiere Node.js)
npx skills add obra/superpowers
npx skills add mattpocock/skills
npx autoskills -y

# Memoria (Python)
uv pip install cognee supermemory

# Fairness / bias
uv pip install eticas-audit

# AI workbench científico
npm install -g @synsci/openscience
```

`make skills` instala lo local (copia los prompts a `.opencode/skills/`); lo
demás depende del ecosistema de cada herramienta (npm, pip, git clone).

### Directrices de comportamiento para agentes

- **[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)** —
  cuatro principios universales para reducir errores de LLMs al programar,
  inspirados en observaciones de Andrej Karpathy: Piensa antes de codear,
  Simplicidad primero, Cambios quirúrgicos, Ejecución guiada por objetivos.
  No dependen de un proveedor de IA concreto. Este proyecto los incluye como
  sección en `AGENTS.md` y como prompt en `agents/prompts/universal_guidelines.md`
  para que cualquier agente pueda usarlos.
- **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)** —
  skill de concisión que reduce ~65% los tokens de salida eliminando relleno
  y conservando precisión técnica. Funciona con 30+ agentes (Claude Code,
  Codex, Gemini, Cursor, Cline, Copilot...). Este proyecto incorpora su
  directriz de concisión en las mismas secciones que karpathy-skills.

### Orquestación y meta-harness

- **[ruvnet/ruflo](https://github.com/ruvnet/ruflo)** — meta-harness para
  agentes de codificación: 100+ agentes especializados, coordinación por
  swarms, memoria vectorial con aprendizaje continuo, federación segura entre
  máquinas, y servidor MCP. Está construido en TypeScript/Node.js (ecosistema
  diferente al de este sistema), pero sus patrones de orquestación
  (ruteo inteligente, workers en segundo plano, topologías de consenso)
  son referencia arquitectónica útil independientemente del lenguaje.

### Frameworks de skills para agentes de codificación

- **[obra/superpowers](https://github.com/obra/superpowers)** — metodología
  de desarrollo compuesta por skills encadenadas (brainstorming → writing-plans
  → ejecución con revisión en dos fases). Se instala como plugin de Claude
  Code (`/plugin install superpowers@claude-plugins-official`) o vía
  `npx skills add`. La skill
  [`brainstorming`](https://www.skills.sh/obra/superpowers/brainstorming) en
  concreto fuerza una fase de diseño con aprobación explícita antes de
  escribir código — encaja bien como disciplina previa a pedirle a un agente
  de este sistema (p. ej. `review`) que toque código.
- **[mattpocock/skills](https://github.com/mattpocock/skills)** — colección
  de skills más pequeñas y componibles (no una metodología monolítica). La
  skill `teach` convierte el directorio actual en un espacio de aprendizaje
  con estado (`MISSION.md`, lecciones HTML numeradas, registro de progreso) —
  pensada para aprender un tema a lo largo de varias sesiones, no directamente
  relacionada con este arnés, pero reutilizable en cualquier proyecto.
- **skill-creator** (Anthropic,
  [skills.sh/anthropics/skills/skill-creator](https://www.skills.sh/anthropics/skills/skill-creator)) —
  la skill oficial de Anthropic para crear otras skills (estructura de
  `SKILL.md`, cuándo separar en `scripts/`/`references/`/`assets/`, cómo
  redactar la descripción para que el auto-descubrimiento la dispare bien).
  Es la misma que usa este asistente internamente; te la he dejado como
  archivo aparte junto a este proyecto (ver el mensaje de chat) para que la
  tengas disponible sin depender de que seas usuario de Claude Code.

### Memoria a largo plazo para agentes

Ninguno de estos es "memoria para `agents/`" tal cual — son piezas de
infraestructura que podrías conectar si construyeras un agente conversacional
por encima de este sistema (algo que, recuerda, este proyecto evita a
propósito, ver Filosofía).

- **[topoteretes/cognee](https://github.com/topoteretes/cognee)** — motor de
  memoria basado en un grafo de conocimiento auto-alojado (pipeline
  "Extract, Cognify, Load"); combina búsqueda vectorial y de grafo. Se usa en
  ~6 líneas de Python (`cognee.add` / `cognee.cognify` / `cognee.search`) o
  como plugin de Claude Code.
- **[redis/agent-memory-server](https://github.com/redis/agent-memory-server)** —
  servidor de memoria (API REST + servidor MCP) sobre Redis, con memoria de
  trabajo (por sesión) y memoria a largo plazo con extracción automática de
  temas/entidades vía LLM. Soporta OpenAI, Anthropic y otros proveedores vía
  LiteLLM.
- **[FalkorDB/FalkorDB](https://github.com/FalkorDB/FalkorDB)** — base de
  datos de grafos (OpenCypher) optimizada para GraphRAG, usa matrices dispersas
  (GraphBLAS) en vez del modelo de almacenamiento habitual de un grafo. Sirve
  como backend de grafo para sistemas de memoria tipo cognee/Mem0 (hay un
  plugin oficial `FalkorDB/mem0-falkordb`).
- **[supermemoryai/supermemory](https://github.com/supermemoryai/supermemory)** —
  API de memoria/contexto para agentes, con integraciones ya hechas para
  LangChain, LangGraph, OpenAI Agents SDK y la herramienta de memoria de
  Claude, entre otras.
- **[EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS)** — capa de
  memoria local-first y "Markdown-nativa" (los datos se guardan como
  `.md` + SQLite + LanceDB, sin servicios externos obligatorios), con
  recuperación híbrida (BM25 + vectorial). **Aviso explícito**: en el
  momento de escribir esto, la actividad del repositorio es de apenas unos
  días — es un proyecto extremadamente nuevo, sin trayectoria que evaluar
  todavía. No lo trates como una pieza probada en producción sin revisar tú
  mismo su estado actual.

### Deep research

- **[langchain-ai/local-deep-researcher](https://github.com/langchain-ai/local-deep-researcher)** —
  asistente de investigación web completamente local (LangGraph + Ollama),
  itera búsqueda → resumen → reflexión hasta producir un informe con fuentes.
  LangChain mantiene también
  [`open_deep_research`](https://github.com/langchain-ai/open_deep_research),
  su versión no local con más proveedores de LLM/búsqueda — no estoy seguro
  de cuál de las dos está más activa en este momento, mejor revisar ambos
  repos antes de elegir.
- Los artículos que enlazaste (*Building agent memory with knowledge
  graphs* en theneuralmaze.substack.com, la comparativa de deep research en
  trilogyai.substack.com, y la lista
  [DavidZWZ/Awesome-Deep-Research](https://github.com/DavidZWZ/Awesome-Deep-Research))
  no los he podido leer en profundidad en esta sesión — te los enlazo tal
  cual, sin resumir contenido que no he verificado.

### Bucle de investigación autónoma

- **[karpathy/autoresearch](https://github.com/karpathy/autoresearch)** —
  de Andrej Karpathy: un agente modifica el código de entrenamiento
  (`train.py`), entrena 5 minutos en una única GPU, mide una métrica, hace
  `git commit` si mejora o revierte si empeora, y repite en bucle sin
  intervención humana. El patrón de fondo (proponer → medir → conservar si
  mejora, descartar si no, con git como historial verificable) es el mismo
  del arnés, pero automatizado: aquí la decisión de conservar o descartar la
  toma `./init.sh` y el `reviewer`, no un bucle sin supervisión. Montar ese
  bucle sobre `GStack` es una extensión razonable si te interesa.

### Sobre `IBM/drop-agent`

No he podido encontrar un repositorio público con ese nombre exacto en
GitHub — es posible que el nombre haya cambiado, que sea un repo privado, o
que me esté fallando la búsqueda. Antes de construir nada sobre él, confirma
la URL exacta.
