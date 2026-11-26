#!/usr/bin/env python3
"""Guardrail automatizado: prohíbe patrones peligrosos en el código fuente.

Se ejecuta en `make check` (y en CI). Un guardrail bloquea directamente que
el código contenga ciertos patrones, a diferencia de una skill, que solo
indica cómo debería hacerse. La lista es deliberadamente corta y conservadora:
añadir un patrón nuevo requiere justificación.

Códigos de salida:
    0 — sin violaciones
    1 — se encontró al menos un patrón prohibido
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (patrón regex, descripción)
BANNED: list[tuple[str, str]] = [
    (r"\beval\s*\(", "eval() — ejecución arbitraria de código"),
    (r"\bexec\s*\(", "exec() — ejecución arbitraria de código"),
    (r"\bos\.system\s*\(", "os.system() — shell sin saneamiento"),
    (r"subprocess\.\w+\([^)]*shell\s*=\s*True", "subprocess con shell=True"),
]

SCAN_DIRS = ("app", "agents")
SCAN_EXTS = {".py"}


def main() -> int:
    violations: list[str] = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in SCAN_EXTS:
                continue
            if "tests" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern, desc in BANNED:
                for m in re.finditer(pattern, text):
                    line = text[: m.start()].count("\n") + 1
                    line_text = text.splitlines()[line - 1]
                    if "guardrail: allow" in line_text:
                        continue
                    violations.append(f"{path.relative_to(ROOT)}:{line}: {desc}")

    if violations:
        print("GUARDRAIL VIOLADO — patrones prohibidos en código:")
        for v in violations:
            print(f"  x {v}")
        print(f"\n{len(violations)} violacion(es). Corrigelas antes de continuar.")
        return 1

    print("OK guardrails - sin patrones prohibidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF