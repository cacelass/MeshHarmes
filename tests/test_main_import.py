"""Importar el paquete app no ejecuta la CLI ni mata el proceso (FIX-001)."""

from __future__ import annotations

import pkgutil

import app
import app.__main__  # noqa: F401 — regresión: importar no debe ejecutar la CLI


def test_walk_packages_sobre_app_no_mata_el_proceso() -> None:
    modulos = [m.name for m in pkgutil.walk_packages(app.__path__, prefix="app.")]
    assert "app.__main__" in modulos
    assert "app.cli" in modulos
