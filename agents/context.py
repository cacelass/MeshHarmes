"""
agents.context — Contexto compartido entre todos los agentes.

Todos los agentes reciben la misma instancia de `SharedContext`, calculada
una única vez por proceso. Esto evita que cada agente reimplemente su propia
lógica de "¿dónde está `tests/`?" y asegura que si mañana cambia la
estructura del proyecto, solo hay que tocar este archivo.

Nota de diseño: este módulo NO importa el paquete del proyecto a propósito.
Los agentes deben poder leer el `Dockerfile` o correr `git log` incluso si el
paquete todavía no se ha instalado (`uv sync` sin ejecutar) o tiene un error
de import. Por eso las rutas se derivan directamente del sistema de archivos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agents.config import ProjectConfig, load_project_config

# agents/context.py -> parents[1] es la raíz del proyecto
# (agents/ vive directamente bajo la raíz, igual que tests/, docs/...)
_AGENTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _AGENTS_DIR.parent


@dataclass(frozen=True)
class SharedContext:
    """Rutas y configuración compartidas. Inmutable: si algo cambia, se crea otra instancia."""

    root: Path
    config: ProjectConfig

    # -- paquete del proyecto -------------------------------------------------
    @property
    def package_dir(self) -> Path:
        return self.root / self.config.project_slug

    # -- código y pruebas -----------------------------------------------------
    @property
    def tests_dir(self) -> Path:
        return self.root / "tests"

    @property
    def scripts_dir(self) -> Path:
        return self.root / "scripts"

    # -- documentación y salidas ---------------------------------------------
    @property
    def docs_dir(self) -> Path:
        return self.root / "docs"

    @property
    def vault_dir(self) -> Path:
        return self.root / "vault"

    # -- infraestructura opcional --------------------------------------------
    @property
    def api_dir(self) -> Path:
        return self.root / "api"

    @property
    def dockerfile(self) -> Path:
        return self.root / "Dockerfile"

    @property
    def docker_compose_file(self) -> Path:
        return self.root / "docker-compose.yml"

    # -- ficheros de la raíz ---------------------------------------------------
    @property
    def changelog_file(self) -> Path:
        return self.root / "CHANGELOG.md"

    @property
    def readme_file(self) -> Path:
        return self.root / "README.md"

    @property
    def pyproject_file(self) -> Path:
        return self.root / "pyproject.toml"

    # -- arnés ----------------------------------------------------------------
    @property
    def harness_dir(self) -> Path:
        return self.root / "harness"

    # -- workspace de los propios agentes -----------------------------------
    @property
    def workspace_dir(self) -> Path:
        """
        Raíz donde los agentes guardan lo que generan (manifests, imágenes
        extraídas, staging de clonados...). Nunca en la raíz del proyecto —
        eso es una decisión explícita: cada agente tiene su propia subcarpeta
        dentro de `agents/workspace/`.
        """
        return self.root / "agents" / "workspace"

    def agent_workspace(self, agent_name: str) -> Path:
        """Crea (si hace falta) y devuelve `agents/workspace/<agent_name>/`."""
        path = self.workspace_dir / agent_name
        path.mkdir(parents=True, exist_ok=True)
        return path


_cached_context: SharedContext | None = None


def get_context(root: Path | None = None, *, force_reload: bool = False) -> SharedContext:
    """
    Devuelve el `SharedContext` del proceso (singleton perezoso).

    Parameters
    ----------
    root          : raíz del proyecto. Por defecto se autodetecta como el
                    padre de `agents/`. Solo se pasa explícitamente en tests.
    force_reload  : ignora la caché y vuelve a leer `project.yml` (útil si un
                    agente acaba de escribir esa configuración).
    """
    global _cached_context
    if _cached_context is not None and not force_reload and root is None:
        return _cached_context

    project_root = root or _PROJECT_ROOT
    context = SharedContext(root=project_root, config=load_project_config(project_root))

    if root is None:
        _cached_context = context
    return context
