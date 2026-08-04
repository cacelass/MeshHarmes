# Security Policy

## Reporting a Vulnerability

Si encuentras una vulnerabilidad de seguridad en MeshHarmes, por favor
notifícala a través del canal de seguridad del repositorio.

**No abras issues públicos para vulnerabilidades de seguridad.**

## Scope

Se consideran vulnerabilidades:
- Exposición de datos sensibles (API keys, tokens, credenciales)
- Ejecución remota de código no intencionada
- Inyección de comandos a través de un agente o de un hook
- Dependencias con CVEs conocidos de alta gravedad

## Las dos fronteras del arnés

- `agents/permissions.py` — las acciones irreversibles de los agentes Python
  (`destructive` en `agents/contracts.py`) no se ejecutan sin autorización
  explícita.
- `agents/policy_guard.py` — filtra las herramientas del asistente (Bash,
  Read, Write, Edit, MCP). **Desconectado por defecto**: este repo no trae
  `.claude/settings.json`. Para activarlo, el snippet está en `AGENTS.md`.

**Ninguna de las dos es un sandbox.** Convierten accidentes e inyecciones
evidentes en un error legible; un comando suficientemente creativo se salta
cualquier lista de patrones. El aislamiento real (contenedor, usuario sin
privilegios, red cerrada) depende de dónde ejecutes el asistente.

## Uso del agente de secretos

Este proyecto incluye un agente `secrets` que escanea el código en busca de
credenciales hardcodeadas. Ejecútalo regularmente:

```bash
uv run python -m agents run secrets scan
```
