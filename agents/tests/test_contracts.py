"""Tests de los contratos de rol: todo agente tiene contrato y nadie pisa a nadie."""

from __future__ import annotations

import pytest

from agents.contracts import (
    CONTRACTS,
    Contract,
    all_contracts,
    contract_for,
    inline_contracts,
    validate_contracts,
)
from agents.core.base_agent import BaseAgent
from agents.core.registry import agent_registry


def test_team_contracts_are_coherent():
    """
    La regla nº1 del equipo ("nadie se pisa") y la nº2 ("todo agente tiene un
    rol definido") no son prosa de README: se validan aquí. Si añades un
    agente sin contrato, o dos contratos declaran el mismo recurso en `owns`,
    este test te lo dice antes de que lo descubra una orden de trabajo real.
    """
    agent_registry.discover()
    problems = validate_contracts(set(agent_registry.all()))
    assert not problems, "Contratos incoherentes:\n" + "\n".join(problems)


def test_every_contract_has_role_and_limits():
    """Un contrato sin límites (`cannot`) no delimita nada — es el origen de los solapes."""
    missing_limits = [
        name for name, contract in CONTRACTS.items()
        if not contract.role.strip() or not contract.cannot
    ]
    assert not missing_limits, (
        f"Contratos sin rol o sin límites (cannot): {missing_limits}. "
        f"Todo agente debe declarar qué NO hace y a quién derivarlo."
    )


# ── Contratos inline ────────────────────────────────────────────────────────
# Un agente puede declarar su contrato como atributo de clase en vez de en
# CONTRACTS (ver `INLINE_CONTRACT_ATTR`). Es lo que permite que un agente
# generado o externo sea de primera clase sin editar agents/contracts.py.

CONTRATO_INLINE = Contract(
    role="Agente de prueba: existe solo mientras corre este test.",
    can=("nada — es un doble de pruebas",),
    cannot=("cualquier cosa → cualquier agente de verdad",),
    owns=("agents/workspace/contrato_inline_test/",),
)

CONTRATO_QUE_PISA = Contract(
    role="Agente de prueba que declara un recurso que ya tiene dueño.",
    can=("provocar la colisión que valida validate_contracts()",),
    cannot=("nada",),
    owns=("harness/featureslist.json",),  # dueño real: el agente `harness`
)


class _AgenteConContratoInline(BaseAgent):
    name = "contrato_inline_test"
    description = "Agente de prueba con el contrato declarado en su propia clase."
    capabilities = ["contrato inline de prueba"]
    contract = CONTRATO_INLINE

    def actions(self) -> dict:
        return {}


class _AgenteQuePisaRecurso(BaseAgent):
    name = "contrato_colision_test"
    description = "Agente de prueba que declara un recurso de otro."
    capabilities = ["contrato colision de prueba"]
    contract = CONTRATO_QUE_PISA

    def actions(self) -> dict:
        return {}


@pytest.fixture
def agente_inline():
    """Registra el agente de prueba y lo saca del registro global al terminar."""
    agent_registry.discover()
    agent_registry.register(_AgenteConContratoInline)
    yield _AgenteConContratoInline
    agent_registry._agents.pop(_AgenteConContratoInline.name, None)


@pytest.fixture
def agente_que_pisa():
    agent_registry.discover()
    agent_registry.register(_AgenteQuePisaRecurso)
    yield _AgenteQuePisaRecurso
    agent_registry._agents.pop(_AgenteQuePisaRecurso.name, None)


def test_inline_contracts_reads_the_class_attribute(agente_inline):
    assert inline_contracts()["contrato_inline_test"] is CONTRATO_INLINE


def test_all_contracts_merges_both_sources(agente_inline):
    todos = all_contracts()
    assert todos["harness"] is CONTRACTS["harness"]        # del diccionario
    assert todos["contrato_inline_test"] is CONTRATO_INLINE  # del atributo de clase


def test_contracts_dict_wins_over_inline(agente_inline, monkeypatch):
    """El diccionario manda: un agente del núcleo no se redefine desde su módulo."""
    del_diccionario = Contract(role="El que gana.", cannot=("perder",))
    monkeypatch.setitem(CONTRACTS, "contrato_inline_test", del_diccionario)

    assert "contrato_inline_test" not in inline_contracts()
    assert all_contracts()["contrato_inline_test"] is del_diccionario
    assert contract_for("contrato_inline_test") is del_diccionario


def test_contract_for_falls_back_to_the_class_attribute(agente_inline):
    assert contract_for("contrato_inline_test") is CONTRATO_INLINE


def test_contract_for_unknown_agent_returns_none():
    assert contract_for("agente_que_no_existe_en_ningun_sitio") is None


def test_validate_contracts_detects_owns_collision_with_an_inline_contract(agente_que_pisa):
    problems = validate_contracts()
    colisiones = [p for p in problems if "harness/featureslist.json" in p]
    assert colisiones, "Un contrato inline que pisa un recurso de CONTRACTS debe detectarse."
    assert "contrato_colision_test" in colisiones[0]
