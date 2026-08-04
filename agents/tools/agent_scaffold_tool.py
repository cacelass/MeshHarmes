"""
agents.tools.agent_scaffold_tool — Genera el código de un agente nuevo a
partir de una spec: módulo con contrato inline, prompt y test.

Existe para que crear un agente no obligue a editar `agents/contracts.py` a
mano. Lo usa `installer scaffold` (ver `agents/agents/installer_agent.py`);
aquí solo se valida la spec y se renderiza texto — quién escribe en disco es
el agente, que es el dueño de `agents/external/`.

Dos cosas que no son estéticas y por eso están aquí y no en el agente:

1. **El nombre no puede tapar nada de `BaseAgent`.** En BOOT-001 el agente
   `bootstrap` definía `describe()` y tapaba `BaseAgent.describe()`, lo que
   reventaba `python -m agents list` con un `TypeError`. Un generador que
   pueda reproducir ese bug no sirve: `validar()` rechaza el nombre del
   agente, y para las acciones se renombra el MÉTODO (`describe` →
   `describe_action`) manteniendo el nombre de la ACCIÓN.
2. **El código que sale tiene que pasar `ruff format --check` tal cual.** Por
   eso las listas y las tuplas de más de un elemento se renderizan siempre
   explotadas con coma final (la "magic trailing comma" que el formateador
   respeta) y las cadenas se citan como las citaría el formateador.
"""

from __future__ import annotations

import keyword
from dataclasses import dataclass

from agents.core.base_agent import BaseAgent
from agents.tools.registry import register_tool

#: `line-length` de ruff en este proyecto (ver `[tool.ruff]` en pyproject).
ANCHO = 100

#: Nombres que no puede usar ni el agente ni un método generado: todo lo que
#: ya trae `BaseAgent`, más `ctx` (atributo de instancia, no sale en `dir`).
RESERVADOS: frozenset[str] = frozenset(dir(BaseAgent)) | {"ctx"}


@dataclass(frozen=True)
class AgentSpec:
    """Lo que hace falta saber para generar un agente. Nada se adivina."""

    name: str
    description: str
    capabilities: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    role: str = ""
    can: tuple[str, ...] = ()
    cannot: tuple[str, ...] = ()
    needs: tuple[str, ...] = ()
    owns: tuple[str, ...] = ()
    collaborates: tuple[str, ...] = ()

    @property
    def module_stem(self) -> str:
        return f"{self.name}_agent"

    @property
    def class_name(self) -> str:
        return "".join(parte.capitalize() for parte in self.name.split("_")) + "Agent"

    @property
    def module_path(self) -> str:
        return f"agents/external/{self.module_stem}.py"

    @property
    def prompt_path(self) -> str:
        # `prompts_sync` busca exactamente este nombre: si no existe, el agente
        # sale como "registrado sin prompt" y tumba el CI.
        return f"agents/prompts/{self.name}_agent.md"

    @property
    def test_path(self) -> str:
        return f"agents/tests/test_{self.module_stem}.py"

    def method_for(self, action: str) -> str:
        """El método que implementa una acción. Ver la nota 1 del módulo."""
        return f"{action}_action" if action in RESERVADOS else action


def split_multi(valor: str) -> tuple[str, ...]:
    """Convierte 'a;b;c' en ('a', 'b', 'c'). La convención de `harness add`."""
    return tuple(parte.strip() for parte in valor.split(";") if parte.strip())


def _cita(texto: str) -> str:
    """La cadena como la escribiría `ruff format`: comillas dobles salvo que eso obligue a escapar."""
    limpio = " ".join(texto.split()).replace("\\", "\\\\")
    if '"' in limpio and "'" not in limpio:
        return f"'{limpio}'"
    return '"' + limpio.replace('"', '\\"') + '"'


def _lista(clave: str, items: tuple[str, ...], indent: int) -> str:
    sangria = " " * indent
    if not items:
        return f"{sangria}{clave} = []"
    cuerpo = "\n".join(f"{sangria}    {_cita(item)}," for item in items)
    return f"{sangria}{clave} = [\n{cuerpo}\n{sangria}]"


def _tupla(clave: str, items: tuple[str, ...], indent: int) -> str:
    sangria = " " * indent
    if not items:
        return f"{sangria}{clave}=(),"
    if len(items) == 1:
        # La coma de una tupla de un elemento no es "magic": el formateador la
        # colapsa si cabe, así que hay que decidirlo aquí igual que él.
        linea = f"{sangria}{clave}=({_cita(items[0])},),"
        if len(linea) <= ANCHO:
            return linea
    cuerpo = "\n".join(f"{sangria}    {_cita(item)}," for item in items)
    return f"{sangria}{clave}=(\n{cuerpo}\n{sangria}),"


@register_tool("agent_scaffold")
class AgentScaffoldTool:
    """Valida una spec de agente y renderiza los tres ficheros que la implementan."""

    @staticmethod
    def validar(
        spec: AgentSpec,
        *,
        registrados: set[str],
        duenos: dict[str, str],
    ) -> list[str]:
        """
        Problemas de la spec (lista vacía = se puede generar).

        `duenos` es {recurso: agente} tal y como lo ve `all_contracts()`, para
        no generar un agente que rompa la regla de "un recurso, un dueño".
        """
        problemas: list[str] = []
        nombre = spec.name

        if not nombre:
            problemas.append("Falta el nombre del agente (--name).")
        elif not nombre.isidentifier() or keyword.iskeyword(nombre):
            problemas.append(
                f"'{nombre}' no es un identificador de Python válido: el nombre es también el "
                f"del módulo y el de la clase, así que solo admite letras, dígitos y '_', "
                f"y no puede empezar por dígito."
            )
        elif nombre != nombre.lower():
            problemas.append(f"'{nombre}' tiene mayúsculas: los nombres de agente van en minúsculas.")
        elif nombre.endswith("_agent"):
            problemas.append(
                f"'{nombre}' acaba en '_agent': el sufijo lo pone el generador "
                f"(módulo '{nombre}_agent.py'). Usa '{nombre[: -len('_agent')]}'."
            )
        elif nombre in RESERVADOS:
            problemas.append(
                f"'{nombre}' es un atributo de BaseAgent y taparlo rompe el sistema — es "
                f"exactamente el bug de `describe` que hubo que arreglar en BOOT-001. Elige otro."
            )
        elif nombre in registrados:
            problemas.append(f"Ya hay un agente registrado con name='{nombre}'. Los nombres son únicos.")

        if not spec.description.strip():
            problemas.append("Falta la descripción del agente (--description): es lo que se lee en `agents list`.")

        if not spec.actions:
            problemas.append(
                "No has dicho qué acciones tiene (--actions 'una;otra'). Un agente sin acciones "
                "no puede hacer nada y no me invento las tuyas."
            )
        vistas: set[str] = set()
        for accion in spec.actions:
            if not accion.isidentifier() or keyword.iskeyword(accion) or accion != accion.lower():
                problemas.append(
                    f"La acción '{accion}' no es un identificador de Python válido en minúsculas: "
                    f"es el nombre de un método."
                )
            if accion in vistas:
                problemas.append(f"La acción '{accion}' está repetida.")
            vistas.add(accion)

        for recurso in spec.owns:
            if recurso in duenos:
                problemas.append(
                    f"El recurso '{recurso}' ya tiene dueño ('{duenos[recurso]}'). "
                    f"Un recurso, un dueño: quítalo de --owns o discútelo con ese agente."
                )

        for colaborador in spec.collaborates:
            if colaborador not in registrados:
                problemas.append(f"--collaborates menciona '{colaborador}', que no es un agente registrado.")

        return problemas

    # -- renderizado ---------------------------------------------------------

    @staticmethod
    def render_module(spec: AgentSpec) -> str:
        renombradas = [a for a in spec.actions if spec.method_for(a) != a]
        owns = spec.owns or (f"agents/workspace/{spec.name}/",)

        lineas = [
            '"""',
            f"agents.external.{spec.module_stem} — {' '.join(spec.description.split())}",
            "",
            "ESQUELETO generado por `installer scaffold`. Ninguna de sus acciones hace",
            "nada todavía: cada una devuelve `AgentResult(success=False, ...)` y explica",
            "en `needs` qué le falta. Un stub que devolviera `success=True` sería una",
            "mentira que el resto del arnés se creería, así que no lo hace.",
            "",
            "Al implementar una acción, actualiza también su test en",
            f"`{spec.test_path}` y el contrato de abajo si deja de ser",
            "cierto lo que dice.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from agents.contracts import Contract",
            "from agents.core.base_agent import AgentResult, BaseAgent",
            "from agents.core.registry import register_agent",
            "",
            "#: Dónde hay que implementar esto, para no repetir la ruta en cada aviso.",
            f"_MODULO = {_cita(spec.module_path)}",
            "",
            "#: Lo que dice cada acción mientras siga sin implementar.",
            '_SIN_IMPLEMENTAR = "es un esqueleto de `installer scaffold` y todavía no hace nada."',
            "",
            "",
            "@register_agent",
            f"class {spec.class_name}(BaseAgent):",
            f"    name = {_cita(spec.name)}",
            f"    description = {_cita(spec.description)}",
            _lista("capabilities", spec.capabilities, 4),
            "",
            "    #: Contrato inline (ver `agents/contracts.py`): vive aquí, y no en el",
            "    #: diccionario CONTRACTS, para que este módulo sea autocontenido.",
            "    contract = Contract(",
            f"        role={_cita(spec.role or spec.description)},",
            _tupla("can", spec.can, 8),
            _tupla("cannot", spec.cannot, 8),
            _tupla("needs", spec.needs, 8),
            _tupla("owns", owns, 8),
            _tupla("collaborates", spec.collaborates, 8),
            "    )",
            "",
        ]

        if renombradas:
            lineas += [
                "    # Ojo: "
                + ", ".join(f"`{a}`" for a in renombradas)
                + " coincide(n) con atributos de BaseAgent,",
                "    # así que el MÉTODO lleva sufijo `_action` para no taparlos — taparlos",
                "    # rompe `python -m agents list`. El nombre de la ACCIÓN no cambia.",
            ]

        lineas += ["    def actions(self) -> dict:", "        return {"]
        for accion in spec.actions:
            lineas.append(f"            {_cita(accion)}: self.{spec.method_for(accion)},")
        lineas += ["        }"]

        for accion in spec.actions:
            lineas += [
                "",
                f"    def {spec.method_for(accion)}(self) -> AgentResult:",
                '        """SIN IMPLEMENTAR — esqueleto generado por `installer scaffold`."""',
                "        return AgentResult(",
                "            False,",
                "            self.name,",
                f"            {_cita(accion)},",
                f'            f"{{self.name}}.{accion}: {{_SIN_IMPLEMENTAR}}",',
                "            needs=[",
                '                f"Impleméntala en {_MODULO}: hoy solo devuelve este aviso.",',
                '                "Antes de usarla, di qué argumentos necesita y qué debe devolver.",',
                "            ],",
                "        )",
            ]

        return "\n".join(lineas) + "\n"

    @staticmethod
    def render_prompt(spec: AgentSpec, bloque_autogen: str) -> str:
        acciones = ", ".join(f"`{a}`" for a in spec.actions)
        prosa = [
            f"# {spec.name} — {' '.join(spec.description.split())}",
            "",
            "**Esto es un esqueleto.** Lo generó `installer scaffold` y sus acciones no",
            "hacen nada todavía: cada una devuelve `success=false` con lo que le falta en",
            "`needs`. Mientras siga así, no le prometas al usuario que este agente resuelve",
            f"algo — lo que resuelve está por escribir en `{spec.module_path}`.",
            "",
            "## Qué falta antes de poder usarlo",
            "",
            f"1. Implementar sus acciones ({acciones}) en `{spec.module_path}`.",
            f"2. Sustituir los tests generados en `{spec.test_path}`",
            "   por tests de lo que la acción hace de verdad, no de que avisa de que no",
            "   hace nada.",
            "3. Repasar el contrato de abajo: lo escribió quien lanzó el scaffold en una",
            "   línea, y `validate_contracts()` comprueba que no se pise con otro agente,",
            "   no que sea verdad.",
            "",
            "Borra esta sección cuando deje de ser cierta.",
            "",
            "",
        ]
        return "\n".join(prosa) + bloque_autogen

    @staticmethod
    def render_test(spec: AgentSpec) -> str:
        lineas = [
            '"""',
            f"Tests de '{spec.name}', generados por `installer scaffold`.",
            "",
            "Son la red mínima: que el agente esté registrado, que tenga contrato y que",
            "sus acciones digan la verdad mientras sigan sin implementar. Cuando",
            "implementes una acción, sustituye su test por uno que compruebe lo que hace.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "from agents.context import SharedContext",
            "from agents.contracts import contract_for, validate_contracts",
            "from agents.core.registry import agent_registry",
            f"from agents.external.{spec.module_stem} import {spec.class_name}",
            "",
            "",
            f"def test_{spec.name}_esta_registrado() -> None:",
            f"    assert {_cita(spec.name)} in agent_registry.all()",
            "",
            "",
            f"def test_{spec.name}_tiene_contrato() -> None:",
            f"    contrato = contract_for({_cita(spec.name)})",
            "    assert contrato is not None",
            "    assert contrato.role",
            "",
            "",
            f"def test_{spec.name}_no_rompe_los_contratos_del_equipo() -> None:",
            "    assert validate_contracts(set(agent_registry.all())) == []",
        ]
        for accion in spec.actions:
            lineas += [
                "",
                "",
                f"def test_{accion}_admite_que_no_esta_implementada(context: SharedContext) -> None:",
                f"    resultado = {spec.class_name}(context=context).{spec.method_for(accion)}()",
                "    assert not resultado.success",
                "    assert resultado.needs",
            ]
        return "\n".join(lineas) + "\n"
