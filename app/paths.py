"""
app.paths — rutas del proyecto, resueltas una sola vez.

Existe por un motivo concreto: en cuanto dos módulos calculan por su cuenta
"dónde está la raíz", uno de los dos se equivoca el día que cambia la
estructura. Aquí la raíz se deriva de la posición de este fichero, así que
funciona igual desde un test, desde un script y desde `python -m app`.

`agents/context.py` hace el mismo cálculo para el arnés y a propósito no
importa este módulo: los agentes tienen que poder trabajar aunque el paquete
del proyecto no importe.
"""

from __future__ import annotations

from pathlib import Path

#: app/paths.py -> parents[1] es la raíz del repositorio.
ROOT_DIR: Path = Path(__file__).resolve().parents[1]

PACKAGE_DIR: Path = ROOT_DIR / "app"
TESTS_DIR: Path = ROOT_DIR / "tests"
DOCS_DIR: Path = ROOT_DIR / "docs"
HARNESS_DIR: Path = ROOT_DIR / "harness"
VAULT_DIR: Path = ROOT_DIR / "vault"


def ensure_dir(path: Path) -> Path:
    """Crea el directorio si no existe y lo devuelve. Idempotente."""
    path.mkdir(parents=True, exist_ok=True)
    return path
