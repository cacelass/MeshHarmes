"""Las rutas del proyecto apuntan a donde dicen apuntar."""

from __future__ import annotations

from pathlib import Path

from app import paths


def test_root_contiene_el_paquete() -> None:
    assert (paths.ROOT_DIR / "app" / "__init__.py").is_file()


def test_rutas_derivadas_cuelgan_de_la_raiz() -> None:
    for path in (
        paths.PACKAGE_DIR,
        paths.TESTS_DIR,
        paths.DOCS_DIR,
        paths.HARNESS_DIR,
        paths.VAULT_DIR,
    ):
        assert path.parent == paths.ROOT_DIR


def test_ensure_dir_es_idempotente(tmp_path: Path) -> None:
    destino = tmp_path / "a" / "b"
    assert paths.ensure_dir(destino) == destino
    assert paths.ensure_dir(destino) == destino
    assert destino.is_dir()
