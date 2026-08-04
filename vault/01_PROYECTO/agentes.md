# Sistema de Agentes — MeshHarmes

> Este proyecto usa un sistema multi-agente con contratos de rol explícitos.
> Cada agente tiene un rol, capacidades, límites, recursos propios y colaboraciones definidas.

## Arquitectura del sistema

```
Humano
  └── plan (Jefe de proyecto: descompone encargos y delega)
        ├── harness (Backlog y progreso del arnés — ejecuta la puerta)
        ├── knowledge (Grafo de conocimiento + Vault Obsidian)
        │     ├── doc (Búsqueda unificada: grafo + RAG + vault)
        │     ├── rag (Índice semántico local)
        │     └── research (Búsqueda externa — arXiv, OpenAlex)
        ├── review (Revisor de código)
        │     └── refactor (Modifica código fuente)
        ├── test (Ejecuta tests)
        ├── git (Historial git)
        │     └── documentation (Documentación y versión)
        ├── cicd (Workflows CI/CD)
        │     └── make (Makefile)
        ├── env (Entorno Python)
        │     └── dependency (Vulnerabilidades)
        ├── docker (Configuración Docker)
        ├── api (API FastAPI)
        ├── secrets (Escáner de secretos)
        ├── installer (Agentes externos)
        ├── doctor (Diagnóstico integral)
        ├── memory (Memoria proactiva de trayectorias)
        ├── supervisor (Coordinación en competencia)
        └── audit (Auditor del equipo)
```

## Reglas del equipo

1. **Nadie se pisa** — cada recurso escribible tiene UN único dueño
2. **Nadie improvisa fuera de su rol** — `cannot` define lo que NO hace y a quién derivarlo
3. **Nadie inventa información** — `needs` lista lo que necesita; si falta, pregunta

Ver `agents/contracts.py` para los contratos completos, o
`uv run python -m agents describe <agente>`.
