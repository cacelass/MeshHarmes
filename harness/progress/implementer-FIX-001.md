# implementer · FIX-001

- **Fecha:** 2026-08-04
- **Veredicto:** ok

## Qué cambié
- app/__main__.py: envuelvo `sys.exit(main())` en la guarda `if __name__ == "__main__":` (mismo patrón que agents/__main__.py). Una línea de alcance; importar app.__main__ ya no ejecuta la CLI.
- tests/test_main_import.py (nuevo): importa app.__main__ y barre el paquete app con pkgutil.walk_packages sin que el proceso muera. El import a nivel de módulo hace que el test falle estrepitosamente si la guarda desaparece.

## Criterios de aceptación
- [x] uv run python -c "import app.__main__" → exit 0, imprime "ok", sin usage
- [x] tests/test_main_import.py importa app.__main__ y hace walk_packages(app.__path__) → 1 passed
- [x] uv run python -m app hello → "Hola, mundo." exit 0
- [x] make check (lint + typecheck + test + harness-check) pasa y ./init.sh → ENTORNO LISTO

## Evidencia
$ uv run python -c "import app.__main__; print('ok')"
ok
$ uv run python -m pytest tests/ -q --no-header
7 passed in 0.13s
$ uv run python -m app hello
Hola, mundo.
$ make lint
All checks passed! / 7 files already formatted
$ make typecheck
Success: no issues found in 7 source files
$ make test
521 passed, 15 skipped in 87.93s
$ ./init.sh
━━ ENTORNO LISTO ━━  0 aviso(s)

Además demostré que el test de regresión caza el bug: restauro temporalmente el __main__.py roto y pytest muere en colección con SystemExit(2) ("no tests ran"); restaurado el fix, pasa.

## Qué falta
Nada para esta feature. Cierre (done + commit_feature) es del líder tras el reviewer.
