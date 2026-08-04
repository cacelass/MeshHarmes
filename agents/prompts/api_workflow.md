# API Workflow — API REST

> **Este proyecto no trae una API.** El agente `api` existe para revisar la que
> escribas tú. Cuando la añadas: crea `api/main.py`, marca `use_api: true` en
> `project.yml`, añade FastAPI a las dependencias con
> `run env add --package fastapi` y un target `serve` en el Makefile.

## Pipeline (una vez exista `api/`)

```
make serve  →  docs en /docs  →  run api check_endpoints  →  pytest
```

## Agente `api`

| Acción | Qué hace |
|--------|----------|
| `check_endpoints` | Cruza los `@app.get/post(...)` declarados contra los documentados en el docstring del módulo |
| `smoke_test` | Arranca la app con `TestClient` y comprueba que responde |

No modifica `api/main.py` ni despliega nada: reporta discrepancias.

## Paths que espera

- `api/main.py` — la app y sus rutas
- `api/schemas.py` — modelos de entrada/salida
- `tests/test_api.py` — tests de integración

## Problemas comunes

- Servidor no arranca → dependencias faltantes o puerto ocupado
- Endpoint 404 → la ruta no está registrada en `api/main.py`
- Documentación desincronizada → es justo lo que caza `check_endpoints`
