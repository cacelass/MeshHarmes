# MeshHarmes

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-0.1.0-green)
![Author](https://img.shields.io/badge/Author-cacelass-blueviolet)

> Arnés de agentes e infraestructura de proyecto para trabajo general en Python.

Un repositorio para empezar proyectos donde el trabajo lo hace —en parte— un
agente de IA, con las reglas del juego escritas **en código** y no en un
prompt: una puerta de entrada que decide si se puede trabajar, un backlog con
criterios de aceptación, memoria fuera de la ventana de contexto y una puerta
de permisos para las acciones que no se deshacen.

No incluye nada de un dominio concreto. El paquete `app/` está vacío a
propósito: ahí va tu código.

---

## Tabla de contenidos

- [Inicio rápido](#inicio-rápido)
- [Estructura del proyecto](#estructura-del-proyecto)
- [El arnés](#el-arnés)
- [Sistema de agentes](#sistema-de-agentes)
- [Vault de Obsidian](#vault-de-obsidian)
- [Empezar un proyecto con esto](#empezar-un-proyecto-con-esto)

---

## Inicio rápido

```bash
make setup     # uv sync --extra dev + hooks de pre-commit
make init      # la puerta: ¿el proyecto está sano?
make run       # ejecuta el paquete de ejemplo
make check     # lint + typecheck + test + arnés
```

Y para arrancar el ciclo de trabajo en tu asistente:

> Lee `AGENTS.md` y sigue el protocolo: ejecuta `./init.sh`, lee
> `harness/progress/` y elige la primera feature pendiente.

---

## Estructura del proyecto

```
├── app/                    ← TU código (renómbralo, ver más abajo)
├── tests/                  ← tus tests
├── agents/                 ← el sistema de agentes (24 agentes Python)
│   ├── agents/             cada agente, una responsabilidad
│   ├── tools/              herramientas compartidas (stdlib pura)
│   ├── prompts/            skills cargables por el asistente
│   ├── evals/              evaluación de ruteo, contratos y RAG
│   └── policy_guard.py     política para las herramientas del asistente (hook opcional)
├── harness/
│   ├── featureslist.json   backlog con criterios de aceptación
│   ├── progress/           memoria del arnés: tarea actual + histórico
│   └── memory.md           preferencias que persisten entre sesiones
├── vault/                  conocimiento estable del proyecto (Obsidian)
├── docs/                   Sphinx
├── AGENTS.md               protocolo del arnés: lo primero que lee la IA
├── CLAUDE.md               puntero a AGENTS.md para Claude Code
├── init.sh                 la puerta: ¿se puede trabajar?
├── project.yml             configuración que leen los agentes
├── Makefile
└── pyproject.toml
```

---

## El arnés

Un entorno dentro del propio repositorio que gobierna cómo trabaja un agente
de IA sobre él. No es un chatbot — es un ciclo con puerta de entrada, backlog
y verificación.

```
./init.sh → harness/progress/ → harness/featureslist.json → implementar → revisar → done → commit_feature
    │
    └── si falla: el agente PARA. No se trabaja sobre un proyecto roto.
```

Funciona con **cualquier asistente**: `AGENTS.md` es la fuente única de reglas
y `CLAUDE.md` solo apunta a él, sin duplicar nada. Los cuatro subagentes se
escriben una vez en `.opencode/agents/` y `make assistants-sync` los espeja a
`.claude/agents/` con el formato que espera Claude Code.

| Pieza | Qué hace |
|-------|----------|
| `AGENTS.md` | Punto de entrada. Lo primero que lee cualquier agente |
| `init.sh` | Verifica entorno, ficheros del arnés y que los tests pasan |
| `harness/featureslist.json` | Qué hay que hacer, con criterios de aceptación explícitos |
| `harness/progress/` | Memoria fuera de la ventana de contexto: tarea actual e histórico |
| `.opencode/agents/` | `lider`, `explorer`, `implementer`, `reviewer` |

```bash
make init            # ¿se puede trabajar?
make harness-check   # solo estructura, sin tests
make backlog         # estado de las features
```

**La regla que no se salta:** ninguna feature se marca `done` sin que
`./init.sh` pase en verde. No es una instrucción, es código: `harness finish`
ejecuta la puerta y rechaza el cierre si está en rojo o si no le pasas la
evidencia.

**Cierre de feature:** al terminar, `git commit_feature` sube el patch de la
versión, actualiza el CHANGELOG y propone el commit (`--dry-run` primero, con
confirmación tuya antes de ejecutarlo). El push siempre es decisión tuya.

El protocolo completo está en [`AGENTS.md`](AGENTS.md).

---

## Sistema de agentes

24 agentes Python, cada uno con **una** responsabilidad y un contrato
declarado en `agents/contracts.py` (qué puede, qué no, qué necesita y qué
recursos posee en exclusiva). Son deterministas: no llaman a ningún LLM, se
ejecutan por shell y funcionan con cualquier asistente.

```bash
uv run python -m agents list                      # todos los agentes
uv run python -m agents describe git              # acciones y contrato de uno
uv run python -m agents --json ask "<lo que sea>" # ruteo automático
uv run python -m agents run dependency check_outdated
```

Las acciones irreversibles (escribir en git, modificar código, instalar
agentes de terceros) están declaradas `destructive` y `BaseAgent.run()` se
niega a ejecutarlas sin autorización explícita — esa puerta está activa
siempre.

La segunda frontera, `agents/policy_guard.py`, filtra las herramientas del
propio asistente (Bash, Read, Write, Edit, MCP) y **viene desconectada**: no
hay `.claude/settings.json` porque un hook `PreToolUse` que falle te deja sin
herramientas hasta arreglarlo a mano. `AGENTS.md` trae el snippet para
cablearla tú si la quieres. Ninguna de las dos es un sandbox; ambas están
explicadas sin adornos ahí.

---

## Vault de Obsidian

`vault/` es el conocimiento estable del proyecto — lo que sigue siendo cierto
cuando la feature en curso ya se cerró. Solo lo escribe el agente
`knowledge`; el resto lo lee.

| Carpeta | Propósito |
|---------|-----------|
| `00_META/` | Índice general + plantillas para nuevas notas |
| `01_PROYECTO/` | Visión, arquitectura, decisiones, roadmap |
| `04_VISUALIZACIONES/` | Grafo de conocimiento (graphify) |
| `05_AGENTES/` | Ficha de cada agente con su contrato expandido |
| `06_OBSERVACIONES/` | Hallazgos y notas sueltas |

Abre `vault/` como carpeta en Obsidian para navegarlo.

Las fichas de `05_AGENTES/` se generan desde `agents/contracts.py`, así que un
agente nuevo no se queda sin la suya. Simula por defecto; la prosa que escribas
fuera del bloque autogenerado sobrevive y las fichas huérfanas se reportan, no
se borran:

```bash
uv run python -m agents run knowledge sync_agent_cards                   # qué escribiría
uv run python -m agents run knowledge sync_agent_cards --dry_run false --yes
```

---

## Empezar un proyecto con esto

1. Clona o copia el repo y borra su historial git si quieres empezar limpio.
2. **Renombra el paquete**: `git mv app <tu_paquete>` y actualiza
   `project_slug` en `project.yml`, `packages` en `pyproject.toml`,
   `[tool.coverage.run] source` y `MODULE` en el `Makefile`. `./init.sh` te
   avisa si te dejas alguno.
3. Vacía `harness/featureslist.json` y escribe tu propio backlog — o pídeselo
   al agente: `uv run python -m agents run harness add --id X-001 --title "..." --criteria "a;b"`.
4. `make setup && make init`.
