"""
app.cli — punto de entrada del proyecto: `python -m app` o `make run`.

Un esqueleto, no un framework: argparse de la stdlib y un subcomando de
ejemplo. Si tu proyecto no es una CLI, borra este fichero y `__main__.py` —
el arnés no los necesita.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from app import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app", description="Proyecto MeshHarmes.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)
    hello = sub.add_parser("hello", help="Comando de ejemplo: saluda y sale.")
    hello.add_argument("--name", default="mundo", help="A quién saludar.")

    return parser


def hello(name: str) -> str:
    return f"Hola, {name}."


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "hello":
        print(hello(args.name))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
