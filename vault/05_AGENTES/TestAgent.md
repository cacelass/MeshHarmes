---
tags:
  - agente
  - calidad
---
<!-- BEGIN AUTOGEN — lo regenera `knowledge sync_agent_cards`; no lo edites a mano -->

# Test Agent

> Ejecuta la suite de tests y explica los resultados.

## Contrato

- **Rol:** Ejecuta la suite de tests y explica los resultados.
- **Capacidades:** correr pytest, resumir fallos y cobertura, detectar módulos sin test homónimo
- **Límites:** arreglar los tests que fallan → refactor (código) o el humano; escribir tests nuevos completos — solo detecta huecos

## Acciones

- `run test run_tests`
- `run test run_smoke_tests`
- `run test coverage_report`
- `run test list_untested_modules`
- `run test generate_test_skeletons`

Fuente: `agents/contracts.py` · `agents.agents.test_agent`. Índice: [[_index|Directorio de agentes]].

<!-- END AUTOGEN -->

## Responsabilidades

1. Ejecutar pytest con opciones configurables
2. Reportar resultados (fallos, cobertura, tests lentos)
3. Detectar archivos sin tests correspondientes

## Comandos

- `pytest tests/ -v`
- `pytest tests/ --cov=app --cov-report=term`
