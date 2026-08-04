"""
agents.config — Configuración centralizada del sistema de agentes.

La configuración del proyecto vive en `project.yml` (raíz del repo): una
lista plana de pares `clave: valor`, sin anidamiento. Este módulo la lee con
un parser línea a línea en vez de depender de PyYAML — el arnés tiene que
funcionar en un checkout recién clonado, antes de instalar nada.

Importante — esto NO es un parser YAML general. Si algún día `project.yml`
necesita listas, bloques multilínea o anidamiento, este parser lo ignorará
en silencio para esas claves. Llegado el caso, la opción honesta es añadir
PyYAML a las dependencias `dev` y sustituir `_parse_flat_yaml` por
`yaml.safe_load`.

Si `project.yml` no existe (p. ej. `agents/` se está probando fuera del
repo), se usan los defaults del dataclass. Son deliberadamente inocuos: un
proyecto sin `project.yml` funciona, solo que los agentes que necesitan el
nombre del paquete devolverán `success=False` pidiéndolo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "project.yml"

_TRUE_STRINGS = {"true", "yes", "1", "on"}
_FALSE_STRINGS = {"false", "no", "0", "off"}


def _coerce(raw: str) -> Any:
    """Convierte el string crudo de una línea `key: value` a bool/int/str."""
    value = raw.strip()
    # comentario al final de la línea: `python_version: 3.12   # el del .venv`
    if "  #" in value:
        value = value.split("  #", 1)[0].strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        value = value[1:-1]
    low = value.lower()
    if low in _TRUE_STRINGS:
        return True
    if low in _FALSE_STRINGS:
        return False
    if value.lstrip("-").isdigit():
        return int(value)
    return value


def _parse_flat_yaml(text: str) -> dict[str, Any]:
    """Parser mínimo para pares `clave: valor` de una sola línea. Ver docstring del módulo."""
    data: dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        if not key or key.startswith("_"):
            continue
        data[key] = _coerce(value)
    return data


@dataclass(frozen=True)
class ProjectConfig:
    """
    Configuración del proyecto leída de `project.yml`, con defaults seguros
    si el archivo no existe o no define la clave.
    """

    project_name: str = "Proyecto"
    project_slug: str = ""
    project_author_name: str = "Nombre del autor"
    project_description: str = ""
    project_version: str = "0.1.0"
    python_version: str = "3.12"

    # Capacidades opcionales: los agentes las consultan para no ofrecer
    # acciones sobre infraestructura que este proyecto no tiene.
    use_api: bool = False
    use_docker: bool = False
    use_cli: bool = False

    # Cualquier clave no reconocida cae aquí en vez de perderse.
    extra: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectConfig:
        known = {f.name for f in fields(cls) if f.name != "extra"}
        kwargs = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**kwargs, extra=extra)

    def as_dict(self) -> dict[str, Any]:
        out = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "extra"}
        out.update(self.extra)
        return out


def load_project_config(root: Path) -> ProjectConfig:
    """
    Carga la configuración desde `<root>/project.yml`.

    No lanza excepción si el archivo falta: devuelve `ProjectConfig()` con los
    defaults documentados arriba, para que `agents/` siga siendo usable en un
    checkout parcial.
    """
    config_path = root / CONFIG_FILENAME
    if not config_path.exists():
        return ProjectConfig()
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError:
        return ProjectConfig()
    return ProjectConfig.from_dict(_parse_flat_yaml(text))


def env_override(key: str, default: str | None = None) -> str | None:
    """Permite sobreescribir cualquier config vía variable de entorno `HARNESS_<KEY>`."""
    return os.environ.get(f"HARNESS_{key.upper()}", default)
