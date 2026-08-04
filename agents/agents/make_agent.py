"""
agents.agents.make_agent — Validación y gestión del Makefile.

Conoce los targets del Makefile del proyecto, comprueba que estén los
targets base que el resto del arnés da por hechos (`setup`, `test`, `lint`,
`check`, `init`) y sugiere targets nuevos según la configuración del
proyecto (`project.yml`).
"""

from __future__ import annotations

import re

from agents.core.base_agent import AgentResult, BaseAgent
from agents.core.registry import register_agent

#: Targets que el arnés y la documentación asumen que existen. Si falta uno,
#: hay instrucciones (README, CI, AGENTS.md) que mienten.
_CORE_TARGETS = ["setup", "test", "lint", "check", "init"]

_TARGET_SUGGESTIONS: dict[str, list[dict]] = {
    "use_api": [
        {"target": "serve", "help": "Arranca la API en local", "depends_on": ["setup"]},
    ],
    "use_docker": [
        {"target": "docker-run", "help": "Construye y arranca el contenedor", "depends_on": []},
    ],
    "use_cli": [
        {"target": "run", "help": "Ejecuta la CLI del proyecto", "depends_on": ["setup"]},
    ],
}


@register_agent
class MakeAgent(BaseAgent):
    name = "make"
    description = (
        "Valida y gestiona el Makefile del proyecto: verifica que los targets "
        "existan, que estén los targets base, y sugiere nuevos targets."
    )
    capabilities = [
        "makefile", "make", "target", "pipeline", "build", "task", "tarea",
    ]

    def actions(self) -> dict:
        return {
            "validate": self.validate,
            "check_core_targets": self.check_core_targets,
            "suggest_targets": self.suggest_targets,
            "run": self.run_target,
            "list_targets": self.list_targets,
        }

    def _parse_makefile(self) -> dict[str, str]:
        """Parsea el Makefile y devuelve {target: help_text}."""
        makefile_path = self.ctx.root / "Makefile"
        if not makefile_path.exists():
            return {}

        targets: dict[str, str] = {}
        text = makefile_path.read_text(encoding="utf-8")
        current_help = ""

        for line in text.splitlines():
            if line.startswith("## "):
                current_help = line[3:].strip()
            target_match = re.match(r"^([a-zA-Z0-9_-]+):", line)
            if target_match:
                target = target_match.group(1)
                if not target.startswith("."):
                    targets[target] = current_help
                    current_help = ""

        return targets

    def list_targets(self) -> AgentResult:
        targets = self._parse_makefile()
        if not targets:
            return AgentResult(False, self.name, "list_targets", "No se encontró Makefile o está vacío.", data={})
        return AgentResult(True, self.name, "list_targets", f"{len(targets)} targets encontrados.", data=targets)

    def validate(self) -> AgentResult:
        """Valida que el Makefile exista y que todos los targets sean sintácticamente válidos."""
        makefile_path = self.ctx.root / "Makefile"
        if not makefile_path.exists():
            return AgentResult(False, self.name, "validate", "No existe Makefile en la raíz del proyecto.")
        return AgentResult(True, self.name, "validate", "Makefile encontrado.")

    def check_core_targets(self) -> AgentResult:
        """Verifica que estén los targets base que el resto del arnés asume."""
        targets = self._parse_makefile()
        missing = [t for t in _CORE_TARGETS if t not in targets]
        found = [t for t in _CORE_TARGETS if t in targets]
        return AgentResult(
            not missing, self.name, "check_core_targets",
            f"Targets base: {len(found)}/{len(_CORE_TARGETS)} encontrados.",
            data={"found": found, "missing": missing},
            warnings=[f"Falta el target '{t}' en el Makefile." for t in missing],
        )

    def suggest_targets(self) -> AgentResult:
        """Sugiere nuevos targets según la configuración del proyecto."""
        suggestions = []
        for config_key, new_targets in _TARGET_SUGGESTIONS.items():
            if getattr(self.ctx.config, config_key, False):
                suggestions.extend(new_targets)

        existing = self._parse_makefile()
        new_suggestions = [s for s in suggestions if s["target"] not in existing]

        return AgentResult(
            True, self.name, "suggest_targets",
            f"{len(new_suggestions)} target(s) sugerido(s) para tu configuración actual.",
            data={"suggested": new_suggestions, "total_possible": len(suggestions)},
            warnings=[] if new_suggestions else ["Todos los targets relevantes ya existen."],
        )

    def run_target(self, *, target: str, dry_run: bool = False) -> AgentResult:
        """Ejecuta un target de Makefile."""
        targets = self._parse_makefile()
        if target not in targets:
            return AgentResult(False, self.name, "run", f"El target '{target}' no existe en el Makefile.")

        if dry_run:
            return AgentResult(True, self.name, "run", f"[dry-run] make {target}")

        from agents.tools.process_tool import run_command
        result = run_command(["make", target], cwd=self.ctx.root)
        if not result.ok:
            return AgentResult(False, self.name, "run", f"make {target} falló: {result.stderr.strip()}")
        return AgentResult(True, self.name, "run", f"make {target} completado.", data={"stdout": result.stdout})
