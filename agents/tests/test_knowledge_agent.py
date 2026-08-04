from __future__ import annotations

import pytest

from agents.agents.knowledge_agent import KnowledgeAgent
from agents.config import ProjectConfig
from agents.context import SharedContext
from agents.tools.graphify_tool import GraphifyTool


@pytest.fixture
def know_context(tmp_path):
    (tmp_path / "mi_paquete").mkdir()
    return SharedContext(root=tmp_path, config=ProjectConfig(project_slug="mi_paquete"))


def test_status_reports_graphify_availability(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.status()
    assert result.data["graphify_available"] == GraphifyTool.is_available(know_context.root)
    assert isinstance(result.data["graph_exists"], bool)
    if result.data["graphify_available"] or result.data["graph_exists"]:
        assert result.success
    else:
        assert not result.success
        assert any("graphify" in w for w in result.warnings)


def test_status_warns_when_no_vault(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.status()
    assert any("bóveda de Obsidian" in w for w in result.warnings)


def test_setup_vault_creates_tree(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.setup_vault()
    assert result.success
    assert result.data["created"] is True
    vault_path = know_context.root / "knowledge"
    assert vault_path.exists()
    assert (vault_path / ".obsidian").exists()
    assert (vault_path / "00-index" / "MOC.md").exists()


def test_setup_vault_creates_expected_dirs(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.setup_vault(vault_dir="test_vault")
    assert result.success
    vault = know_context.root / "test_vault"
    for folder in ("00-index", "papers", "code", "docs", "references", "media"):
        assert (vault / folder).exists(), f"Falta carpeta {folder}"


def test_setup_vault_reuses_existing(know_context):
    agent = KnowledgeAgent(context=know_context)
    first = agent.setup_vault()
    assert first.success

    second = agent.setup_vault()
    assert second.success
    assert second.data["created"] is False


def test_setup_vault_custom_dir(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.setup_vault(vault_dir="mi_boveda")
    assert result.success
    assert (know_context.root / "mi_boveda").exists()


def test_setup_vault_create_if_missing_false(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.setup_vault(vault_dir="no_existe", create_if_missing=False)
    assert not result.success


def test_build_fails_if_no_graph(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.build()
    if GraphifyTool.is_available(know_context.root):
        assert result.success
    else:
        assert not result.success


def test_summarize_parents_fails_without_graph(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.summarize_parents()
    assert not result.success
    assert "No hay grafo" in result.message


def test_sync_without_graph(know_context):
    agent = KnowledgeAgent(context=know_context)
    result = agent.sync()
    if GraphifyTool.is_available(know_context.root):
        assert result.success
    else:
        assert result.data.get("skipped") is True


# -- poda del grafo: absorbida de `docsearch` ----------------------------------
# `graphify-out/` tenia DOS duenos declarados: knowledge lo construia y
# docsearch lo podaba. El test de contratos no lo detectaba porque cada uno lo
# describia con una cadena distinta. La poda vive ahora donde el grafo.

def test_prune_falla_sin_grafo(context):
    from agents.agents.knowledge_agent import KnowledgeAgent

    result = KnowledgeAgent(context=context).prune(node_types=["reference"])
    assert not result.success


def test_prune_exige_saber_que_podar(context, monkeypatch):
    from agents.agents.knowledge_agent import KnowledgeAgent

    agent = KnowledgeAgent(context=context)
    monkeypatch.setattr(agent, "_require_graph", lambda accion: None)
    result = agent.prune()
    assert not result.success
    assert "Indica qué podar" in result.message


# -- fichas de vault/05_AGENTES/ ----------------------------------------------
# El contrato de knowledge prometia poblar vault/05_AGENTES/ desde contracts.py
# y ninguna accion lo hacia: las fichas venian de la plantilla y se quedaban
# atras (bootstrap, con contrato inline, no tenia ficha).

def _cards_dir(context):
    return context.root / "vault" / "05_AGENTES"


def test_sync_agent_cards_dry_run_no_escribe(context):
    result = KnowledgeAgent(context=context).sync_agent_cards()
    assert result.success
    assert result.data["dry_run"] is True
    assert result.data["created"], "deberia proponer una ficha por agente"
    assert not _cards_dir(context).exists()


def test_sync_agent_cards_escribe_una_ficha_por_agente(context):
    from agents.core.registry import agent_registry

    agent_registry.discover()
    result = KnowledgeAgent(context=context).sync_agent_cards(dry_run=False)
    assert result.success

    fichas = {p.name for p in _cards_dir(context).glob("*.md")}
    esperadas = {f"{cls.__name__}.md" for cls in agent_registry.all().values()}
    assert esperadas <= fichas
    assert result.data["agents"] == len(esperadas)


def test_sync_agent_cards_incluye_contrato_inline(context):
    """`bootstrap` declara su contrato como atributo de clase: tambien tiene ficha."""
    KnowledgeAgent(context=context).sync_agent_cards(dry_run=False)
    ficha = _cards_dir(context) / "BootstrapAgent.md"
    assert ficha.exists()
    assert "Arranque en frío" in ficha.read_text(encoding="utf-8")


def test_sync_agent_cards_contenido_desde_el_contrato(context):
    from agents.contracts import contract_for

    KnowledgeAgent(context=context).sync_agent_cards(dry_run=False)
    texto = (_cards_dir(context) / "GitAgent.md").read_text(encoding="utf-8")
    contrato = contract_for("git")

    assert contrato.role in texto
    for campo in (contrato.can, contrato.cannot, contrato.needs, contrato.owns):
        for item in campo:
            assert item in texto, f"falta '{item}' en la ficha"
    for accion in contrato.destructive:
        assert f"`{accion}`" in texto
    assert texto.startswith("---\n")


def test_sync_agent_cards_reporta_huerfanas_sin_borrarlas(context):
    huerfana = _cards_dir(context) / "DocsearchAgent.md"
    huerfana.parent.mkdir(parents=True)
    huerfana.write_text("# Docsearch Agent\n", encoding="utf-8")

    result = KnowledgeAgent(context=context).sync_agent_cards(dry_run=False)
    assert result.data["orphans"] == ["DocsearchAgent.md"]
    assert huerfana.exists()
    assert huerfana.read_text(encoding="utf-8") == "# Docsearch Agent\n"


def test_sync_agent_cards_conserva_la_prosa_a_mano(context):
    ficha = _cards_dir(context) / "GitAgent.md"
    ficha.parent.mkdir(parents=True)
    ficha.write_text(
        "---\ntags:\n  - agente\n  - git\n---\n"
        "# Git Agent\n\n> viejo\n\n## Contrato\n\n- **Rol:** desfasado\n\n"
        "## Flujo típico\n\nEsto lo escribio un humano.\n",
        encoding="utf-8",
    )

    agent = KnowledgeAgent(context=context)
    agent.sync_agent_cards(dry_run=False)
    texto = ficha.read_text(encoding="utf-8")
    assert "Esto lo escribio un humano." in texto
    assert "desfasado" not in texto
    assert texto.startswith("---\ntags:\n  - agente\n  - git\n---\n")

    # Y es idempotente: una segunda pasada no vuelve a tocarla.
    segunda = agent.sync_agent_cards(dry_run=False)
    assert str(ficha.relative_to(context.root)) in segunda.data["unchanged"]
    assert ficha.read_text(encoding="utf-8") == texto
