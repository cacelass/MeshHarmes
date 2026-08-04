# Changelog

Todos los cambios relevantes del proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

El dueño de este fichero es el agente `documentation`: `git commit_feature`
añade aquí una entrada por cada feature cerrada del arnés.

---

## [Unreleased] — 2026-08-04

### Añadido

- protege app.__main__ para que importar el paquete no ejecute la CLI (FIX-001)

## [0.1.0] — 2026-08-04

### Añadido

- Arnés de trabajo: `AGENTS.md`, `init.sh`, `harness/` (backlog + progreso) y
  los cuatro subagentes (`lider`, `explorer`, `implementer`, `reviewer`).
- Sistema de 23 agentes Python en `agents/`, con contratos de rol y puerta de
  permisos (`agents/permissions.py`) para las acciones irreversibles.
- `agents/policy_guard.py` como política para las herramientas del asistente,
  sin cablear a ningún hook: se activa a mano (ver `AGENTS.md`).
- Vault de conocimiento en `vault/`, RAG local opcional y grafo con graphify.
- Paquete de ejemplo `app/` con su CLI y tests, `make check` en verde y CI.
