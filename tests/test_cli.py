"""La CLI de ejemplo arranca, saluda y devuelve 0."""

from __future__ import annotations

import pytest

from app.cli import build_parser, hello, main


def test_hello_devuelve_el_saludo() -> None:
    assert hello("MeshHarmes") == "Hola, MeshHarmes."


def test_main_imprime_y_sale_con_cero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["hello", "--name", "arnés"]) == 0
    assert capsys.readouterr().out.strip() == "Hola, arnés."


def test_sin_subcomando_es_error_de_uso() -> None:
    # argparse sale con código 2 en errores de uso: no lo tratamos como éxito.
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([])
    assert exc.value.code == 2
