# reviewer · EVAL-001

- **Fecha:** 2026-11-26
- **Veredicto:** aprobado

## Criterios
1. Existe eval que mide si un agente sigue su skill: CUMPLIDO — agents/evals/runner.py define `_skills()` (comprueba que el prompt de cada agente menciona todas sus acciones) y acepta `--skills`. Evidencia: `uv run python -m agents.evals.runner --skills` → 25/25 passed, PASS.
2. El eval se ejecuta en make check o make agents-eval: CUMPLIDO — `make agents-eval` invoca el runner completo (skills=True por defecto) e incluye la suite SKILLS (25/25). `runner --skills` pasa.
3. make check pasa: CUMPLIDO — `make check` → lint OK, typecheck OK, pytest 535 passed 1 skipped, harness-check OK, "✅ check pasado".
4. ./init.sh ENTORNO LISTO: CUMPLIDO — `uv run python -m agents --json run harness gate` → success=true, "ENTORNO LISTO — se puede trabajar." (avisos: python 3.13 vs 3.12 declarado; RAG desfasado).

## Bloqueantes
(none)

## No bloqueante
- No existe informe implementer-EVAL-001.md en harness/progress/ (proceso; el trabajo está en el árbol).
- No hay test en tests/ para el runner/_skills (no hay tests de runner en la línea base; la verificación es ejecutar el eval).
- `make agents-eval` completo falla por suites preexistentes no relacionadas (rag 8/12, smoke api/doc/docker/installer/refactor/secrets, secrets scan detecta fixtures en tests). No bloquean EVAL-001.
- `secrets scan` devuelve 13 hallazgos, todos en tests/test_redaction.py y tests/test_secrets_agent.py (fixtures intencionales).
