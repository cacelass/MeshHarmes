# Estado del arte — MeshHarmes

> Resumen de fuentes externas relevantes para el arnés. Cada entrada: qué se
> toma y qué se descarta. Lo escribe `ONBOARD-002`.

## Fuentes indexadas

1. **Harness Handbook: Making Evolving Agent Harnesses Readable, Navigable, and Editable**
   (arXiv 2607.13285). Se toma: la idea de que el harness debe ser legible y
   editable por humanos, no una caja negra. Se descarta: el enfoque de
   reestructuración completa del repo por feature (nuestro arnés ya separa
   `agents/`, `harness/`, `vault/`).

2. **HarnessNet: Feedback-driven Hierarchical Joint Harness Evolution for Multi-agent Systems**
   (arXiv 2610.15221). Se toma: el feedback loop como mecanismo central de
   mejora (el agente ejecuta, comprueba, se corrige). Ya está en el arnés vía
   `./init.sh` + criterios. Se descarta: la evolución automática del harness
   sin confirmación humana (mantenemos la puerta de permisos).

3. **Evolving Agents in the Dark: Retrospective Harness Optimization via Self-Preference**
   (arXiv 2606.05922). Se toma: la optimización retrospectiva del harness a
   partir de trayectorias pasadas (conecta con `agents/workspace/memory/` y el
   RAG brain). Se descarta: la auto-preferencia sin supervisión (mantenemos
   revisión por criterios).

## Conceptos adoptados del estudio

- **Feedback Loop**: reforzar que el implementer verifique su trabajo (tests +
  `./init.sh`) antes de devolver, sin depender del humano.
- **Agent Evals**: extender `make eval-rag` / evals de ruteo a la calidad de
  skills/prompts (medir, no solo afirmar).
- **Guardrails**: reglas que los agentes no pueden saltarse (más allá de
  `destructive`): bans de patrones, arquitectura por feature.

## Conceptos descartados

- Software factory totalmente autónoma (commit/push sin confirmación).
- Modelos específicos mencionados en las fuentes (se usan los del proyecto).
- Revisión manual línea a línea (se sustituye por programación aumentada).

## Huecos de capacidad evaluados (bootstrap suggest_agents)

Comando ejecutado:

```
uv run python -m agents run bootstrap suggest_agents
```

Salida: 22 términos léxicos sin agente dedicado (adoptan, adoptar, cerebro,
discusion, embeddings, especificos, evolucionar, features, gestion, lider,
linea, manual, mejorar, mencionados, meshharmes, metodologia, modelos,
obligar, persistente, reemplazar, revision, usan) y 7 cubiertos (arnes,
calidad, codigo, conocimiento, fuentes, grafo, tickets).

Mapeo a agentes existentes: todos los términos "no cubiertos" son léxicos de
la descripción del proyecto (verbos/abstractos), no capacidades ausentes.
Las capacidades reales que la visión requiere ya están cubiertas:

- Memoria persistente / RAG brain → `rag` + `knowledge` + `doc`
- Mejora de la metodología del líder → `lider` (mejorado, no reemplazado)
- Calidad por discusión con la IA → `reviewer` + `implementer` (augmented coding)
- Guardrails / puerta de permisos → `permissions` + contratos (`destructive`)
- Feedback loop → `test` + `./init.sh` + criterios en `harness`

Conclusión: no se acepta ningún hueco. No se generan agentes nuevos con
`installer scaffold`; crearlos para ruido léxico añadiría agentes redundantes
y rompería el principio "una responsabilidad por agente". Si en el futuro
aparece una capacidad real no cubierta, se scaffolda entonces.
