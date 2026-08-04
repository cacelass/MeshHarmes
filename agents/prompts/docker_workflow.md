# Docker Workflow — Contenedores

> **Este proyecto no trae Dockerfile.** El agente `docker` existe para revisar
> el que escribas tú: si no hay fichero, te lo dice en vez de inventárselo.
> Cuando añadas uno, marca `use_docker: true` en `project.yml` y pídele a
> `make` que sugiera los targets (`make suggest_targets`).

## Pipeline (una vez tengas Dockerfile y compose)

```
docker build  →  docker compose up -d  →  docker compose down
```

## Agente `docker`

| Acción | Qué hace |
|--------|----------|
| `lint_dockerfile` | FROM con tag (nunca `:latest`), `USER` no root, `COPY` vs `ADD`, capas de `apt-get` |
| `validate_compose` | Estructura de `docker-compose.yml`, servicios y puertos |

No construye ni ejecuta imágenes: es análisis estático. Y no edita el
Dockerfile — reporta, decides tú.

## Paths que mira

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore` (si existe: lo que no debe entrar en la imagen)

## Problemas comunes

- Docker no instalado → el agente lo dice y no falla el resto del arnés
- Imagen enorme → revisa capas, multi-stage build y `.dockerignore`
- Secretos en la imagen → `run secrets scan` antes de construir
