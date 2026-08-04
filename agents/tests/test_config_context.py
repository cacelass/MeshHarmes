from __future__ import annotations

from pathlib import Path

from agents.config import ProjectConfig, load_project_config
from agents.context import SharedContext


def test_load_project_config_missing_file_returns_defaults(tmp_path: Path):
    config = load_project_config(tmp_path)
    assert config == ProjectConfig()


def test_load_project_config_parses_flat_yaml(tmp_path: Path):
    (tmp_path / "project.yml").write_text(
        "# project.yml\n"
        "_meta: ignorame\n"
        "project_name: Mi Proyecto\n"
        "project_slug: mi_proyecto\n"
        "python_version: 3.13   # el del .venv\n"
        "use_docker: true\n"
        "use_api: false\n"
        "campo_desconocido: valor\n"
    )
    config = load_project_config(tmp_path)
    assert config.project_name == "Mi Proyecto"
    assert config.project_slug == "mi_proyecto"
    assert config.python_version == "3.13"      # el comentario de línea no entra
    assert config.use_docker is True
    assert config.use_api is False
    assert config.extra["campo_desconocido"] == "valor"
    assert "_meta" not in config.extra          # claves con _ delante, descartadas


def test_shared_context_paths_are_relative_to_root(tmp_path: Path):
    ctx = SharedContext(root=tmp_path, config=ProjectConfig(project_slug="pkg"))
    assert ctx.package_dir == tmp_path / "pkg"
    assert ctx.tests_dir == tmp_path / "tests"
    assert ctx.docs_dir == tmp_path / "docs"
    assert ctx.harness_dir == tmp_path / "harness"
    assert ctx.workspace_dir == tmp_path / "agents" / "workspace"


def test_agent_workspace_se_crea_bajo_demanda(tmp_path: Path):
    ctx = SharedContext(root=tmp_path, config=ProjectConfig(project_slug="pkg"))
    destino = ctx.agent_workspace("explorer")
    assert destino.is_dir()
    assert destino == tmp_path / "agents" / "workspace" / "explorer"
