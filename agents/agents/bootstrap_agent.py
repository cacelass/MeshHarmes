"""
agents.agents.bootstrap_agent — El arranque en frío del proyecto.

Un repo recién clonado tiene un problema que no tiene ningún repo maduro: el
agente no sabe **de qué va esto**. La descripción de `project.yml` viene con
el texto de la plantilla, el backlog está vacío y no hay histórico que leer.
Sin nada de eso, cualquier feature que se abra se implementa a ciegas.

Este agente cubre ese hueco, y solo ese. Hace tres cosas y ninguna más:

1. **Detecta si es la primera ejecución** (`status`) — cero features cerradas,
   histórico vacío y descripción sin tocar. El `lider` lo consulta antes que
   nada; si no es la primera vez, sigue con el protocolo normal de siempre.
2. **Siembra los dos tickets de arranque** (`seed`) delegando en `harness`,
   que es el dueño del backlog. Aquí no se escribe JSON a mano.
3. **Pregunta lo que falta** (acción `describe`, método `describe_project`) —
   si la descripción del proyecto sigue siendo la de la plantilla, devuelve
   `success=False` con las preguntas en `needs`. No inventa el propósito del
   proyecto: es exactamente el caso en el que adivinar sale caro.

Y una cuarta que es la interesante: `suggest_agents` cruza la descripción
real del proyecto con las capacidades de los agentes registrados y dice qué
trabajo **no** cubre nadie. No crea nada — crear es de `installer scaffold`,
que es quien escribe en `agents/external/`. Un recurso, un dueño.

Límite honesto: `suggest_agents` es léxico, no semántico. Cruza palabras de
la descripción con las `capabilities` declaradas. Detecta bien lo evidente
("necesito hablar con una API de pagos" → no hay agente de pagos) y no
detecta lo sutil. Es una lista de candidatos para que decida un humano o el
`lider`, no un veredicto.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from typing import Any

from agents.contracts import Contract
from agents.core.base_agent import AgentResult, BaseAgent
from agents.core.registry import agent_registry, register_agent

#: Descripciones que significan "aquí no ha escrito nadie todavía". Si la
#: descripción del proyecto es una de estas, el arranque en frío no ha pasado.
_DESCRIPCIONES_PLANTILLA = (
    "",
    "descripcion breve del proyecto.",
    "descripción breve del proyecto.",
    "arnés de agentes e infraestructura de proyecto para trabajo general en python.",
    "arnes de agentes e infraestructura de proyecto para trabajo general en python.",
)

#: Longitud mínima para considerar que una descripción dice algo. Dos frases.
_MIN_DESCRIPCION = 80

#: Las preguntas que se le hacen al usuario cuando falta la descripción. No
#: son un formulario: son lo mínimo sin lo cual el resto del arnés trabaja a
#: ciegas (contra qué se compara "hecho", qué NO hay que construir).
PREGUNTAS_DESCRIPCION = (
    "¿Qué problema resuelve este proyecto, y para quién?",
    "¿Cómo sabremos que está hecho? Dame un criterio verificable, no 'que funcione bien'.",
    "¿Qué queda explícitamente FUERA de alcance?",
    "¿Con qué sistemas o formatos externos tiene que hablar (APIs, ficheros, bases de datos)?",
)

TICKETS_ARRANQUE: tuple[dict[str, Any], ...] = (
    {
        "id": "ONBOARD-001",
        "title": "Entender el proyecto",
        "description": (
            "Nadie puede implementar contra un objetivo que no está escrito. Esta feature "
            "convierte lo que el usuario tiene en la cabeza en algo que un agente pueda leer: "
            "qué problema se resuelve, para quién, cuándo está hecho y qué queda fuera. "
            "El agente `bootstrap` hace las preguntas; el usuario las responde; la respuesta "
            "acaba en project.yml y en el vault."
        ),
        "acceptance_criteria": [
            "uv run python -m agents run bootstrap describe --description \"<respuesta del usuario>\" --yes devuelve success=true",
            "project.yml tiene una descripción propia del proyecto, no la de la plantilla",
            "vault/01_PROYECTO/objetivo.md recoge problema, usuario, criterio de hecho y fuera de alcance",
            "El README describe el objetivo en una frase propia",
            "./init.sh termina con ENTORNO LISTO",
        ],
        "status": "pending",
        "depends_on": [],
    },
    {
        "id": "ONBOARD-002",
        "title": "Qué se sabe ya y qué agentes hacen falta",
        "description": (
            "Con el objetivo escrito, dos preguntas antes de construir nada: qué ha publicado "
            "ya alguien sobre este problema (papers y fuentes que aporten al repo, indexadas "
            "para poder consultarlas después) y qué trabajo de este proyecto no cubre ningún "
            "agente actual. Lo segundo se resuelve creando los agentes que falten con "
            "`installer scaffold`, no improvisando scripts sueltos."
        ),
        "acceptance_criteria": [
            "uv run python -m agents run research find_papers devuelve success=true con al menos 3 referencias relevantes",
            "Las URLs útiles quedan indexadas (run rag index_urls --urls ...) y run rag search las encuentra",
            "vault/01_PROYECTO/estado-del-arte.md resume cada fuente en 2-3 líneas: qué se toma y qué se descarta",
            "uv run python -m agents run bootstrap suggest_agents devuelve la lista de huecos de capacidad",
            "Cada hueco aceptado tiene su agente creado con installer scaffold, con contrato, prompt y test",
            "uv run python -m agents.prompts_sync sale en verde (todo agente registrado tiene prompt y contrato)",
            "./init.sh termina con ENTORNO LISTO",
        ],
        "status": "pending",
        "depends_on": ["ONBOARD-001"],
    },
)

#: Palabras que no discriminan nada al cruzar la descripción con capacidades.
_VACIAS = {
    "para", "con", "que", "del", "las", "los", "una", "uno", "por", "como",
    "este", "esta", "sus", "sobre", "entre", "desde", "hasta", "cuando",
    "proyecto", "sistema", "usuario", "usuarios", "datos", "the", "and", "for",
}


def _normaliza(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sin_tildes if not unicodedata.combining(c))


def _palabras(texto: str) -> set[str]:
    return {
        p for p in re.findall(r"[a-z0-9_]+", _normaliza(texto))
        if len(p) > 3 and p not in _VACIAS
    }


@register_agent
class BootstrapAgent(BaseAgent):
    name = "bootstrap"
    description = (
        "Arranque en frío del proyecto: detecta la primera ejecución, siembra los dos "
        "tickets de onboarding, pregunta la descripción que falta y señala qué "
        "capacidades no cubre ningún agente."
    )
    capabilities = [
        "bootstrap", "arranque", "primera ejecucion", "primera ejecución",
        "onboarding", "empezar proyecto", "arrancar proyecto", "inicializar proyecto",
        "que agentes faltan", "qué agentes faltan", "huecos de capacidad",
    ]

    #: Contrato inline: ver `agents/contracts.py`. Este agente lo declara aquí
    #: para que sirva de ejemplo vivo del formato que genera `installer
    #: scaffold` — si el ejemplo se rompe, se rompe un test.
    contract = Contract(
        role="Arranque en frío: convierte un repo vacío en uno con objetivo escrito y backlog sembrado.",
        can=(
            "detectar si es la primera ejecución del arnés en este repo",
            "sembrar los dos tickets de arranque delegando en `harness`",
            "recoger la descripción del proyecto y escribirla en project.yml",
            "señalar qué capacidades de la descripción no cubre ningún agente registrado",
        ),
        cannot=(
            "inventarse el propósito del proyecto — si falta, pregunta (needs) y para",
            "escribir en el backlog directamente → harness (su dueño)",
            "crear agentes → installer scaffold (dueño de agents/external/)",
            "escribir en el vault → knowledge (su dueño)",
        ),
        needs=("la descripción del proyecto, en palabras del usuario",),
        owns=("project.yml", "agents/workspace/bootstrap/"),
        collaborates=("harness", "installer", "research", "knowledge"),
        destructive=("describe", "seed"),
    )

    def actions(self) -> dict:
        return {
            "status": self.status,
            "seed": self.seed,
            "describe": self.describe_project,
            "suggest_agents": self.suggest_agents,
        }

    def action_aliases(self) -> dict:
        return {
            "status": ["primera", "arranque", "estado", "onboarding"],
            "seed": ["siembra", "tickets", "backlog", "inicializa"],
            "describe": ["descripcion", "descripción", "objetivo", "completar"],
            "suggest_agents": ["agentes", "faltan", "huecos", "capacidades"],
        }

    # -- rutas ---------------------------------------------------------------

    @property
    def _project_file(self):
        return self.ctx.root / "project.yml"

    @property
    def _backlog_file(self):
        return self.ctx.harness_dir / "featureslist.json"

    @property
    def _history_file(self):
        return self.ctx.harness_dir / "progress" / "history.md"

    # -- status --------------------------------------------------------------

    def _leer_descripcion(self) -> str:
        return (self.ctx.config.project_description or "").strip()

    def _descripcion_es_de_plantilla(self) -> bool:
        actual = _normaliza(self._leer_descripcion()).strip()
        return actual in _DESCRIPCIONES_PLANTILLA or len(actual) < _MIN_DESCRIPCION

    def _backlog(self) -> list[dict]:
        try:
            doc = json.loads(self._backlog_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        features = doc.get("features")
        return features if isinstance(features, list) else []

    def status(self) -> AgentResult:
        """¿Es la primera ejecución del arnés en este repo? Solo lee."""
        features = self._backlog()
        cerradas = [f for f in features if f.get("status") == "done"]
        ids = {f.get("id") for f in features}

        try:
            historico = self._history_file.read_text(encoding="utf-8")
        except OSError:
            historico = ""
        # El fichero trae cabecera y plantilla; lo que cuenta es si hay
        # entradas reales, que empiezan por "## " con un ID delante.
        entradas = len(re.findall(r"^## [A-Z][A-Z0-9_-]*-\d+", historico, re.MULTILINE))

        tickets_sembrados = all(t["id"] in ids for t in TICKETS_ARRANQUE)
        descripcion_pendiente = self._descripcion_es_de_plantilla()
        primera = not cerradas and entradas == 0

        siguiente = None
        if primera:
            if not tickets_sembrados:
                siguiente = "run bootstrap seed  → siembra ONBOARD-001 y ONBOARD-002"
            elif descripcion_pendiente:
                siguiente = "run bootstrap describe --description \"...\"  → falta la descripción del proyecto"
            else:
                siguiente = "run harness next  → el arranque está hecho, sigue el ciclo normal"

        return AgentResult(
            True, self.name, "status",
            ("Primera ejecución: el proyecto aún no tiene trabajo cerrado."
             if primera else "El proyecto ya tiene histórico — arranque en frío no aplica."),
            data={
                "first_run": primera,
                "features_done": len(cerradas),
                "history_entries": entradas,
                "onboarding_tickets_seeded": tickets_sembrados,
                "description_pending": descripcion_pendiente,
                "next": siguiente,
            },
        )

    # -- seed ----------------------------------------------------------------

    def seed(self, *, force: bool = False) -> AgentResult:
        """
        Siembra ONBOARD-001 y ONBOARD-002 en el backlog, vía `harness add`.

        No escribe el JSON: el dueño del backlog es `harness`, y saltárselo
        sería exactamente el error que el arnés existe para evitar.
        """
        # Instanciación directa con `context=self.ctx` y no `delegate_to`: esa
        # resuelve el contexto global (`get_context()`), así que en un test
        # sobre tmp_path escribiría en el backlog REAL del repo. Es el patrón
        # que ya usan git → documentation por el mismo motivo.
        from agents.agents.harness_agent import HarnessAgent

        harness = HarnessAgent(context=self.ctx)
        existentes = {f.get("id") for f in self._backlog()}
        añadidos, omitidos, fallos = [], [], []

        for ticket in TICKETS_ARRANQUE:
            if ticket["id"] in existentes and not force:
                omitidos.append(ticket["id"])
                continue
            resultado = harness.add(
                id=ticket["id"],
                title=ticket["title"],
                description=ticket["description"],
                criteria=";".join(ticket["acceptance_criteria"]),
                depends_on=";".join(ticket["depends_on"]),
            )
            (añadidos if resultado.success else fallos).append(
                ticket["id"] if resultado.success else f"{ticket['id']}: {resultado.message}"
            )

        return AgentResult(
            not fallos, self.name, "seed",
            f"{len(añadidos)} ticket(s) sembrados, {len(omitidos)} ya estaban.",
            data={"added": añadidos, "skipped": omitidos, "failed": fallos},
            warnings=fallos,
        )

    # -- describe ------------------------------------------------------------

    def describe_project(self, *, description: str = "") -> AgentResult:
        """
        Escribe la descripción real del proyecto en `project.yml`.

        Sin `description`, no adivina: devuelve las preguntas en `needs` para
        que las conteste el usuario. Es el mecanismo estándar del sistema.

        El método NO se llama `describe`: ese nombre es de `BaseAgent`, que lo
        usa para la ficha del agente (`python -m agents describe bootstrap`, y
        `Orchestrator.list_agents()`). Sobreescribirlo rompía las dos cosas. La
        ACCIÓN sigue llamándose `describe` — ver `actions()`.
        """
        texto = " ".join(description.split())
        if not texto:
            return AgentResult(
                False, self.name, "describe",
                "Falta la descripción del proyecto — no me la invento.",
                needs=list(PREGUNTAS_DESCRIPCION),
                data={"questions": list(PREGUNTAS_DESCRIPCION)},
            )
        if len(texto) < _MIN_DESCRIPCION:
            return AgentResult(
                False, self.name, "describe",
                f"La descripción tiene {len(texto)} caracteres: demasiado corta para que "
                f"otro agente decida nada con ella (mínimo {_MIN_DESCRIPCION}).",
                needs=list(PREGUNTAS_DESCRIPCION),
            )

        if not self._project_file.exists():
            return AgentResult(
                False, self.name, "describe",
                "No existe project.yml en la raíz — el arnés no sabe cómo se llama el paquete.",
            )

        original = self._project_file.read_text(encoding="utf-8")
        lineas = original.splitlines()
        # `project_description` es una clave plana de una línea (ver
        # agents/config.py): se sustituye la línea entera, no se reescribe el
        # fichero, para no perder los comentarios que explican cada campo.
        for i, linea in enumerate(lineas):
            if linea.startswith("project_description:"):
                lineas[i] = f"project_description: {texto}"
                break
        else:
            lineas.append(f"project_description: {texto}")

        nuevo = "\n".join(lineas) + "\n"
        self._project_file.write_text(nuevo, encoding="utf-8")

        marca = self.ctx.agent_workspace(self.name) / "state.json"
        marca.write_text(
            json.dumps({"described_on": date.today().isoformat(), "chars": len(texto)},
                       indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return AgentResult(
            True, self.name, "describe",
            "Descripción escrita en project.yml.",
            data={"description": texto, "file": str(self._project_file.relative_to(self.ctx.root))},
            warnings=[
                "El objetivo largo (problema, usuario, criterio de hecho, fuera de alcance) "
                "va en vault/01_PROYECTO/objetivo.md, y el vault lo escribe `knowledge`.",
            ],
        )

    # -- suggest_agents ------------------------------------------------------

    def suggest_agents(self, *, description: str = "") -> AgentResult:
        """
        Qué trabajo de la descripción no cubre ningún agente registrado.

        Cruce léxico entre las palabras de la descripción y las
        `capabilities` declaradas por cada agente. Devuelve candidatos para
        que decida un humano — ver el límite en el docstring del módulo.
        """
        texto = " ".join(description.split()) or self._leer_descripcion()
        if not texto or self._descripcion_es_de_plantilla() and not description:
            return AgentResult(
                False, self.name, "suggest_agents",
                "No hay descripción del proyecto contra la que cruzar nada.",
                needs=["Ejecuta antes 'run bootstrap describe --description \"...\"'"],
            )

        agent_registry.discover()
        cubierto: dict[str, list[str]] = {}
        vocabulario: set[str] = set()
        for nombre, agent_cls in agent_registry.all().items():
            palabras = set()
            for cap in getattr(agent_cls, "capabilities", []):
                palabras |= _palabras(cap)
            palabras |= _palabras(getattr(agent_cls, "description", ""))
            vocabulario |= palabras
            cubierto[nombre] = sorted(palabras)

        de_la_descripcion = _palabras(texto)
        huecos = sorted(de_la_descripcion - vocabulario)
        coincidencias = sorted(de_la_descripcion & vocabulario)

        relevantes = sorted(
            (
                (nombre, sorted(set(cubierto[nombre]) & de_la_descripcion))
                for nombre in cubierto
                if set(cubierto[nombre]) & de_la_descripcion
            ),
            key=lambda par: -len(par[1]),
        )[:5]

        return AgentResult(
            True, self.name, "suggest_agents",
            f"{len(huecos)} término(s) de la descripción sin agente que los cubra.",
            data={
                "uncovered_terms": huecos,
                "covered_terms": coincidencias,
                "closest_agents": [{"agent": n, "matches": m} for n, m in relevantes],
                "how_to_create": (
                    "uv run python -m agents run installer scaffold --name <nombre> "
                    "--description \"<qué hace>\" --capabilities \"a;b\" --actions \"hacer_x\" --dry_run true"
                ),
            },
            warnings=[
                "Cruce léxico, no semántico: son candidatos a revisar, no un veredicto. "
                "Un término sin cubrir puede no necesitar agente, y uno cubierto puede "
                "necesitar uno mejor.",
            ],
        )
