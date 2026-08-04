"""
Tests de `installer scaffold` — el generador de agentes autocontenidos.

Aislamiento: todos generan sobre `tmp_path` (fixture `context`) y limpian el
registro global en el teardown. Un agente generado en el `agents/external/`
real quedaría registrado como fantasma y contaminaría `test_capability_
collisions`, `test_prompts_sync` y el conteo de agentes de otros tests.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agents.agents.installer_agent import InstallerAgent
from agents.context import SharedContext
from agents.contracts import contract_for, validate_contracts
from agents.core.registry import agent_registry

GENERADOS = ("demo_scaffold", "demo_ruff", "demo_prompt")

#: Config de ruff equivalente a la del proyecto (`[tool.ruff]` de
#: pyproject.toml). Se escribe aparte porque el agente genera en tmp_path, y
#: allí ruff no encontraría la del repo — y con `known-first-party` explícito
#: porque la deducción de primera-parte depende de dónde esté el fichero.
RUFF_TOML = """\
line-length = 100
target-version = "py312"

[lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501", "B008"]

[lint.isort]
known-first-party = ["agents"]
"""


@pytest.fixture(autouse=True)
def _cleanup_registry():
    yield
    for nombre in GENERADOS:
        agent_registry._agents.pop(nombre, None)


def _scaffold(context: SharedContext, **kwargs):
    kwargs.setdefault("name", "demo_scaffold")
    kwargs.setdefault("description", "Agente de prueba generado por el scaffold")
    kwargs.setdefault("actions", "hacer_algo")
    return InstallerAgent(context=context).scaffold(**kwargs)


def _ficheros(root: Path) -> list[Path]:
    return [
        root / "agents" / "external" / "demo_scaffold_agent.py",
        root / "agents" / "prompts" / "demo_scaffold_agent.md",
        root / "agents" / "tests" / "test_demo_scaffold_agent.py",
    ]


# -- dry-run ------------------------------------------------------------------

def test_dry_run_no_escribe_nada_y_devuelve_la_previsualizacion(context):
    resultado = _scaffold(context, capabilities="uno;dos")

    assert resultado.success
    assert resultado.data["dry_run"] is True
    rutas = [f["path"] for f in resultado.data["files"]]
    assert rutas == [
        "agents/external/demo_scaffold_agent.py",
        "agents/prompts/demo_scaffold_agent.md",
        "agents/tests/test_demo_scaffold_agent.py",
    ]
    assert "class DemoScaffoldAgent(BaseAgent)" in resultado.data["files"][0]["content"]
    assert not any(f.exists() for f in _ficheros(context.root))
    # y tampoco deja el agente registrado a medias
    assert "demo_scaffold" not in agent_registry.all()


def test_dry_run_avisa_de_que_el_agente_no_hace_nada(context):
    resultado = _scaffold(context)
    assert any("NO hace nada" in w for w in resultado.warnings)


# -- generación real ----------------------------------------------------------

def test_genera_los_tres_ficheros_y_registra_el_agente(context):
    resultado = _scaffold(context, capabilities="uno;dos", dry_run=False)

    assert resultado.success, resultado.message
    for fichero in _ficheros(context.root):
        assert fichero.exists(), fichero
    assert "demo_scaffold" in agent_registry.all()
    assert resultado.data["registered"] is True


def test_el_agente_generado_tiene_contrato_inline_y_no_rompe_los_contratos(context):
    _scaffold(context, role="Hace una cosa de prueba", can="una cosa", collaborates="git", dry_run=False)

    contrato = contract_for("demo_scaffold")
    assert contrato is not None
    assert contrato.role == "Hace una cosa de prueba"
    assert contrato.owns == ("agents/workspace/demo_scaffold/",)
    assert validate_contracts(set(agent_registry.all())) == []


def test_los_stubs_devuelven_fallo_con_needs_nunca_un_exito_falso(context):
    _scaffold(context, actions="hacer_algo;describe", dry_run=False)

    agente = agent_registry.get("demo_scaffold")(context=context)
    acciones = agente.actions()
    assert sorted(acciones) == ["describe", "hacer_algo"]
    for nombre, metodo in acciones.items():
        resultado = metodo()
        assert not resultado.success, nombre
        assert resultado.needs, nombre


def test_una_accion_que_choca_con_baseagent_no_tapa_el_metodo(context):
    """El bug de BOOT-001 (`describe` tapando `BaseAgent.describe`) no se puede regenerar."""
    _scaffold(context, actions="describe", dry_run=False)

    agente = agent_registry.get("demo_scaffold")(context=context)
    ficha = agente.describe()  # el de BaseAgent: devuelve la ficha, no un AgentResult
    assert ficha["name"] == "demo_scaffold"
    assert ficha["actions"] == ["describe"]
    assert not agente.describe_action().success


def test_no_sobrescribe_lo_que_ya_existe(context):
    _scaffold(context, dry_run=False)
    agent_registry._agents.pop("demo_scaffold", None)  # simula otro proceso

    resultado = _scaffold(context, dry_run=False)
    assert not resultado.success
    assert "No sobrescribo" in resultado.message


# -- validación del nombre ----------------------------------------------------

@pytest.mark.parametrize(
    "nombre, senal",
    [
        ("describe", "BaseAgent"),          # colisión con un atributo de BaseAgent
        ("run", "BaseAgent"),
        ("git", "Ya hay un agente registrado"),  # colisión con un agente existente
        ("mi-agente", "identificador"),     # guion: no es identificador
        ("2fast", "identificador"),         # empieza por dígito
        ("Demo", "minúsculas"),
        ("class", "identificador"),         # palabra reservada
        ("demo_agent", "_agent"),           # el sufijo lo pone el generador
    ],
)
def test_rechaza_nombres_invalidos(context, nombre, senal):
    resultado = _scaffold(context, name=nombre, dry_run=False)

    assert not resultado.success
    assert any(senal in problema for problema in resultado.needs), resultado.needs
    assert not (context.root / "agents" / "external").exists()


def test_rechaza_una_spec_sin_acciones(context):
    resultado = _scaffold(context, actions="")
    assert not resultado.success
    assert any("acciones" in problema for problema in resultado.needs)


def test_rechaza_un_recurso_que_ya_tiene_dueno(context):
    resultado = _scaffold(context, owns="CHANGELOG.md")
    assert not resultado.success
    assert any("documentation" in problema for problema in resultado.needs)


def test_rechaza_colaborar_con_un_agente_que_no_existe(context):
    resultado = _scaffold(context, collaborates="agente_inventado")
    assert not resultado.success
    assert any("agente_inventado" in problema for problema in resultado.needs)


# -- calidad de lo generado ---------------------------------------------------

def test_el_codigo_generado_pasa_ruff(context, tmp_path):
    _scaffold(
        context,
        name="demo_ruff",
        description='Agente con "comillas" y acentos en la descripción',
        capabilities="una;otra",
        actions="hacer_algo;describe",
        can="hace una cosa;hace otra",
        cannot="no hace la tercera → otro agente",
        needs="que le den un fichero con un nombre razonablemente largo para forzar el salto de línea",
        dry_run=False,
    )
    config = tmp_path / "ruff.toml"
    config.write_text(RUFF_TOML, encoding="utf-8")
    generados = [
        str(context.root / "agents" / "external" / "demo_ruff_agent.py"),
        str(context.root / "agents" / "tests" / "test_demo_ruff_agent.py"),
    ]

    check = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", str(config), *generados],
        capture_output=True, text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr

    formato = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--diff", "--config", str(config), *generados],
        capture_output=True, text=True,
    )
    assert formato.returncode == 0, formato.stdout + formato.stderr


def test_prompts_sync_no_reporta_el_agente_generado_como_sin_prompt(context):
    from agents import prompts_sync

    _scaffold(context, name="demo_prompt", actions="hacer_algo", dry_run=False)

    desincronizados, sin_prompt = prompts_sync.sync(write=False, context=context)
    assert "demo_prompt" not in sin_prompt
    assert "demo_prompt" not in desincronizados


def test_scaffold_esta_declarado_como_destructivo_y_la_puerta_lo_bloquea(context, monkeypatch):
    contrato = contract_for("installer")
    assert contrato is not None
    assert "scaffold" in contrato.destructive

    # Sin `confirm`, `run()` no ejecuta nada (la puerta vive en run(), no en el
    # método) — ver agents/permissions.py.
    monkeypatch.delenv("HARNESS_ASSUME_YES", raising=False)
    monkeypatch.delenv("HARNESS_CONFIRM", raising=False)
    resultado = InstallerAgent(context=context).run(
        "scaffold", name="demo_scaffold", description="x", actions="hacer_algo", dry_run=False,
    )
    assert not resultado.success
    assert "no se ha autorizado" in resultado.message
    assert not any(f.exists() for f in _ficheros(context.root))


def test_la_puerta_no_pregunta_en_dry_run(context, monkeypatch):
    monkeypatch.delenv("HARNESS_ASSUME_YES", raising=False)
    monkeypatch.delenv("HARNESS_CONFIRM", raising=False)
    resultado = InstallerAgent(context=context).run(
        "scaffold", name="demo_scaffold", description="Agente de prueba", actions="hacer_algo",
        dry_run=True,
    )
    assert resultado.success
    assert resultado.data["dry_run"] is True
