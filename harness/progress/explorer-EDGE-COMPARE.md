# explorer · EDGE-COMPARE

- **Fecha:** 2026-11-20
- **Veredicto:** ok

## Respuesta
Mejoras general-purpose (no GEAS, no ML) que MeshHarmes puede tomar de edgebet, ordenadas por esfuerzo. Las de mayor valor: claim/release de touched_files, protocolo §1 (packet) en record, puerta de certeza/veredicto del reviewer (GATE-3/4), friction ladder en permisos, commit_atomic en git, y scope/edit en memoria. Las de SDD (spec_ready + features/ + Gherkin) son grandes y requieren adoptar el directorio features/.

## Hallazgos (general-purpose = yes)

1. agents/agents/harness_agent.py — claim()/release(): touched_files conflict detection ("un recurso, un dueño"). Evita que dos features pisen los mismos ficheros. yes. medium.
2. agents/agents/harness_agent.py — _peso_dependientes(): next() prioriza la feature que más desbloquea. yes. small.
3. agents/agents/harness_agent.py — _evidencia_plausible(): finish() rechaza evidencia que es una afirmación ("ok"/"pasa"). yes. small.
4. agents/agents/harness_agent.py — certainty param + _ultima_certeza_reviewer/_ultimo_veredicto_reviewer/_impacto_declarado (GATE-3/4/5): finish() no cierra si el reviewer rechazó o certeza < umbral, ni sin declaración de impacto. yes. medium.
5. agents/agents/harness_agent.py — packet protocol §1: record() acepta --certainty/--packet, _validar_packet/_leer_packet/_packet_resumen, antecedentes comprimidos. yes. medium.
6. agents/agents/harness_agent.py — validate_gherkin + write_feature/approve (flujo SDD, status spec_ready). yes. large (requiere features/ y references/).
7. agents/agents/harness_agent.py — touched_files se libera al bloquear. yes. small.
8. agents/core/base_agent.py — campo certainty en AgentResult (μ.cert). yes. small.
9. agents/core/base_agent.py — expansión de conjugaciones en el ruteo (recall). yes. small.
10. agents/permissions.py — friction ladder: acciones critical (type-to-confirm), fatiga de aprobaciones, confirm_string. yes. large.
11. agents/contracts.py — campo critical en Contract. yes. small (valor real con #10).
12. agents/audit.py — campos certainty/confirmed en el log. yes. small.
13. agents/tools/git_tool.py — commit_paths() y plan_atomic() (clasificación por área, detección de ciclos, lock files excluidos). yes. medium.
14. agents/agents/git_agent.py — commit_atomic(): commits atómicos por área. yes. medium (depende de #13).
15. agents/tools/memory_tool.py — scope (global/per-proyecto) y edit(). yes. medium.
16. agents/agents/memory_agent.py — scope en note/search, forget/edit. yes. small.
17. agents/agents/mutation_agent.py (nuevo) — mutation testing + CRAP. yes. large (requiere tools/mutate.py).
18. agents/agents/documentation_agent.py — update_prd() (PRD derivado del spec+backlog+Gherkin). yes. medium.
19. agents/prompts/harness_workflow.md — claim, protocol §1, perfiles reducidos. yes. small.
20. agents/prompts/harness_agent.md — claim/write_feature/approve/certainty/packet. yes. small.
21. agents/prompts/reviewer.md — rúbrica binaria, packet §1, certainty, patrón ttsr. yes. medium.
22. .opencode/agents/reviewer.md — ídem (rúbrica, packet, certainty, ttsr). yes. medium.
23. .opencode/agents/lider.md — paso claim, PRD/vault (parcial). yes (partes generales). medium.
24. agents/agents/plan_agent.py — entrevista scope (scope/scope_answer/scope_commit). yes. large.
25. agents/agents/rag_agent.py — refresh del corpus de conocimiento (arXiv). yes. large.

## No general-purpose (no)

- agents/agents/geas_backlog.py y todo el GEAS backlog server (start/finish/add pasan por GEAS). no. large.
- agents/agents/{data,graph,ml,mlflow,mutation,notebook,risk,sentiment,shap}_agent.py son dominio ML/datos. no (salvo mutation, ya listado).
- .vvault vs vault y rutas edgebet/ vs app/: layout del proyecto, no mejoras. no.
- init.sh de edgebet: validación Gherkin features/*.feature es parte del SDD (ver #6); el resto (targets operativos, FDCO cache, ingestion lag) es dominio. no.
- agents/prompts/{data,graph,ml,mlflow,mutation,notebook,risk,sentiment,shap}_agent.md: dominio. no.

## Riesgos y sorpresas
- MeshHarmes ya tiene touched_files en init.sh y rubric.py idéntico; el valor real está en el código del harness (claim/release, finish gates), no en schema.
- SDD (spec_ready, features/, references/) es un cambio de flujo grande: MeshHarmes usa vault/01_PROYECTO/objetivo.md y bootstrap describe en vez de references/00-objetivo.md + plan scope. Adoptar uno u otro, no ambos.
- Friction ladder (#10) toca base_agent.run(), audit, permissions y contracts: grande pero autocontenido.
- mutation_agent depende de tools/mutate.py (no existe en MeshHarmes) y radon (ya dev-dep).

## Sin verificar
- No ejecuté tests de edgebet; comparé solo código/ficheros.
- No verifiqué si MeshHarmes ya tiene tests para estas capacidades (busqué por grep, no exhaustivo).
- No revisé agents/tools/knowledge_tool.py ni el corpus docs/knowledge/ (fuera de alcance).
