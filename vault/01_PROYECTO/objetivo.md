# Objetivo — MeshHarmes

> Lo que se quiere resolver. Lo escribe `SCOPE-001`; el resto del backlog se
> justifica contra este documento.

## Problema

MeshHarmes es un arnés de agentes que ya gobierna el ciclo de desarrollo
(backlog, puerta de entrada, memoria fuera de contexto, permisos), pero hoy
**cada feature empieza casi de cero**: la memoria de decisiones pasadas vive en
ficheros sueltos y no se consulta de forma sistemática, el líder repite
razonamiento que ya se hizo antes, y la calidad del código depende de que
alguien revise a mano. Con la IA generando código cada vez más rápido, el
cuello de botella se ha movido de "escribir" a "recordar y discernir": el
arnés no aprovecha el conocimiento acumulado ni ayuda a mejorar el código sin
convertir la revisión manual en obligatoria.

## Usuario / consumidor

El propio arnés y quien lo use (desarrollador solo o equipo): un asistente de
codificación o un agente que arranca de cero, lee `AGENTS.md` y necesita
saber qué se decidió, por qué y qué queda pendiente antes de tocar código. El
consumidor final es el repositorio mismo: sus features, su vault y su
`harness/progress/`.

## Criterio de hecho

El proyecto se considera "hecho" cuando se cumplen, todos a la vez y
verificables por comando:

1. `./init.sh` termina con `ENTORNO LISTO` (0 avisos).
2. `uv run python -m agents run rag search --query "<decisión pasada>"` devuelve
   al menos un hit relevante del histórico de features en menos de 2 segundos.
3. `make check` (lint + typecheck + test + arnés) pasa en verde.
4. `uv run python -m agents.prompts_sync` sale en verde (contratos y prompts
   alineados).

## Fuera de alcance

- **No** adoptar los modelos concretos que mencionan las fuentes (Opus, Sonet,
  Sol, Astra, etc.): se usan los modelos ya configurados en el proyecto.
- **No** cambiar la metodología del líder por completo: se mejora, se mantiene
  el ciclo y la puerta de permisos.
- **No** imponer revisión manual línea a línea: la calidad se busca mediante
  discusión con la IA (augmented coding), no mediante gates humanos por PR.
- **No** convertir el arnés en una "software factory" autónoma que commitea a
  producción sin confirmación humana: el push y el commit siguen siendo
  decisiones explícitas del usuario.
