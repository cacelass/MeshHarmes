"""
Tests del agente `bootstrap` — el arranque en frío.

Todos usan la fixture `context` de conftest.py: el agente escribe en
`project.yml` y siembra el backlog, así que trabajar sobre el repo real
significaría reescribir el objetivo del proyecto y meterle dos tickets cada
vez que alguien corre `pytest`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.agents.bootstrap_agent import TICKETS_ARRANQUE, BootstrapAgent
from agents.config import ProjectConfig
from agents.context import SharedContext

DESCRIPCION_REAL = (
    "Malla de sensores acusticos que sincroniza nodos LoRa y calibra la latencia "
    "entre ellos para localizar la fuente de un sonido con menos de dos metros de error."
)


def _arnes(root: Path, features: list[dict] | None = None) -> None:
    """Deja el arnés mínimo que necesitan `status` y `seed` en el proyecto temporal."""
    (root / "harness" / "progress").mkdir(parents=True, exist_ok=True)
    (root / "harness" / "featureslist.json").write_text(
        json.dumps({"features": features or []}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _project_yml(root: Path, descripcion: str = "Descripcion breve del proyecto.") -> None:
    (root / "project.yml").write_text(
        "# project.yml — configuración del proyecto\n"
        "project_name: Prueba\n"
        "project_slug: mi_paquete\n"
        f"project_description: {descripcion}\n"
        "project_version: 0.1.0\n"
        "use_api: false\n",
        encoding="utf-8",
    )


def _con_descripcion(context: SharedContext, descripcion: str) -> SharedContext:
    """El mismo proyecto temporal, pero con una descripción ya escrita en la config."""
    return SharedContext(
        root=context.root,
        config=ProjectConfig(project_slug="mi_paquete", project_description=descripcion),
    )


# ── status ──────────────────────────────────────────────────────────────────

def test_status_detects_first_run(context):
    _arnes(context.root)
    result = BootstrapAgent(context=context).status()

    assert result.success
    assert result.data["first_run"] is True
    assert result.data["onboarding_tickets_seeded"] is False
    assert result.data["description_pending"] is True
    assert "seed" in result.data["next"]


def test_status_is_not_a_first_run_when_something_is_already_done(context):
    _arnes(context.root, features=[{"id": "DATA-001", "status": "done"}])
    result = BootstrapAgent(context=context).status()

    assert result.success
    assert result.data["first_run"] is False
    assert result.data["features_done"] == 1
    assert result.data["next"] is None


def test_status_counts_history_entries_as_previous_work(context):
    _arnes(context.root)
    (context.root / "harness" / "progress" / "history.md").write_text(
        "# Histórico\n\n## DATA-001 — Cargar el dataset\n\nCerrada con evidencia.\n",
        encoding="utf-8",
    )
    result = BootstrapAgent(context=context).status()

    assert result.data["first_run"] is False
    assert result.data["history_entries"] == 1


# ── seed ────────────────────────────────────────────────────────────────────

def test_seed_adds_both_onboarding_tickets(context):
    _arnes(context.root)
    result = BootstrapAgent(context=context).seed()

    assert result.success, result.message
    assert result.data["added"] == [t["id"] for t in TICKETS_ARRANQUE]

    backlog = json.loads((context.root / "harness" / "featureslist.json").read_text(encoding="utf-8"))
    ids = [f["id"] for f in backlog["features"]]
    assert ids == ["ONBOARD-001", "ONBOARD-002"]
    # La segunda depende de la primera: el orden de siembra importa, porque
    # `harness add` rechaza un depends_on que aún no existe.
    assert backlog["features"][1]["depends_on"] == ["ONBOARD-001"]


def test_seed_is_idempotent(context):
    _arnes(context.root)
    agent = BootstrapAgent(context=context)
    agent.seed()

    result = agent.seed()

    assert result.success
    assert result.data["added"] == []
    assert result.data["skipped"] == ["ONBOARD-001", "ONBOARD-002"]

    backlog = json.loads((context.root / "harness" / "featureslist.json").read_text(encoding="utf-8"))
    assert len(backlog["features"]) == 2


def test_seed_fails_when_there_is_no_backlog(context):
    result = BootstrapAgent(context=context).seed()

    assert not result.success
    assert result.data["failed"]


# ── describe ────────────────────────────────────────────────────────────────

def test_describe_without_description_asks_and_writes_nothing(context):
    _project_yml(context.root)
    antes = (context.root / "project.yml").read_text(encoding="utf-8")

    result = BootstrapAgent(context=context).describe_project()

    assert not result.success
    assert result.needs
    assert (context.root / "project.yml").read_text(encoding="utf-8") == antes


def test_describe_writes_the_description_keeping_the_rest_of_the_file(context):
    _project_yml(context.root)

    result = BootstrapAgent(context=context).describe_project(description=DESCRIPCION_REAL)

    assert result.success, result.message
    lineas = (context.root / "project.yml").read_text(encoding="utf-8").splitlines()
    assert f"project_description: {DESCRIPCION_REAL}" in lineas
    for conservada in ("project_name: Prueba", "project_slug: mi_paquete", "use_api: false"):
        assert conservada in lineas


def test_describe_rejects_a_description_too_short_to_decide_anything(context):
    _project_yml(context.root)

    result = BootstrapAgent(context=context).describe_project(description="Un proyecto de sensores.")

    assert not result.success
    assert result.needs
    assert "project_description: Descripcion breve del proyecto." in (
        context.root / "project.yml"
    ).read_text(encoding="utf-8")


def test_describe_fails_without_project_yml(context):
    result = BootstrapAgent(context=context).describe_project(description=DESCRIPCION_REAL)

    assert not result.success
    assert "project.yml" in result.message


# ── suggest_agents ──────────────────────────────────────────────────────────

def test_suggest_agents_without_a_description_asks_for_it(context):
    result = BootstrapAgent(context=context).suggest_agents()

    assert not result.success
    assert result.needs


def test_suggest_agents_returns_uncovered_terms(context):
    result = BootstrapAgent(context=context).suggest_agents(description=DESCRIPCION_REAL)

    assert result.success
    assert "acusticos" in result.data["uncovered_terms"]
    assert result.warnings, "El cruce es léxico: tiene que decirlo al devolver los candidatos."


def test_suggest_agents_uses_the_project_description_when_none_is_given(context):
    agent = BootstrapAgent(context=_con_descripcion(context, DESCRIPCION_REAL))

    result = agent.suggest_agents()

    assert result.success
    assert "acusticos" in result.data["uncovered_terms"]


# ── regresión: la acción `describe` no puede tapar `BaseAgent.describe()` ────

def test_describe_is_still_an_action_of_the_agent(context):
    acciones = BootstrapAgent(context=context).actions()
    assert acciones["describe"].__name__ == "describe_project"


def test_agent_card_is_a_dict_not_an_agent_result(context):
    """`BaseAgent.describe()` devuelve la ficha del agente — no ejecuta la acción."""
    ficha = BootstrapAgent(context=context).describe()

    assert ficha["name"] == "bootstrap"
    assert "describe" in ficha["actions"]
    assert ficha["contract"]["role"]


def test_list_agents_does_not_break(context):
    """
    La regresión concreta: `python -m agents list` reventaba con
    `TypeError: 'AgentResult' object is not subscriptable` porque un agente
    sobreescribía `describe()` con una acción suya.
    """
    from agents.orchestrator import Orchestrator

    fichas = Orchestrator(context=context).list_agents()

    assert fichas
    for ficha in fichas:
        assert isinstance(ficha, dict), ficha
        assert ficha["name"]
    assert "bootstrap" in {f["name"] for f in fichas}


@pytest.mark.parametrize("accion", ["status", "seed", "describe", "suggest_agents"])
def test_every_declared_action_is_callable(context, accion):
    assert callable(BootstrapAgent(context=context).actions()[accion])
