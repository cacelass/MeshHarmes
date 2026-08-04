# bootstrap — el arranque en frío del proyecto

Cubre el hueco que solo existe una vez: un repo recién clonado donde nadie ha
escrito todavía de qué va esto. La descripción de `project.yml` es la de la
plantilla, el backlog está vacío y no hay histórico que leer. Cualquier feature
que se abra en ese estado se implementa a ciegas.

## Lo que NO puedes hacer con este agente

**No inventes el propósito del proyecto.** Si `describe` devuelve
`success=false` con preguntas en `needs`, esas preguntas son para el usuario —
no para que las contestes tú con lo que has deducido leyendo el código. Un
objetivo inventado es peor que ninguno: el resto del arnés lo tratará como un
hecho verificado y medirá contra él durante el resto del proyecto. Pega las
preguntas, espera la respuesta, y pásala tal cual en `--description`.

Lo mismo con la descripción demasiado corta: el mínimo no es burocracia, es el
umbral por debajo del cual otro agente no puede decidir nada. No lo rellenes
con paja para pasar la comprobación.

## `suggest_agents` da candidatos, no veredictos

El cruce es **léxico, no semántico**: compara las palabras de la descripción
con las `capabilities` y la `description` declaradas por cada agente
registrado. Eso significa dos cosas, y las dos hay que decirlas al reportar:

- Un término en `uncovered_terms` **no** demuestra que falte un agente. Puede
  ser una palabra del dominio que ningún agente necesita cubrir.
- Un término en `covered_terms` **no** demuestra que esté bien cubierto. Que
  `rag` declare "buscar" no significa que sepa buscar en el formato propietario
  del proyecto.

Así que preséntalo como una lista para revisar con el usuario, no como una
conclusión. Y si de esa revisión sale que falta un agente de verdad, este
agente no lo crea: se crea con `installer scaffold`, que es el dueño de
`agents/external/`.

## `seed` delega, no escribe

Los tickets ONBOARD-001 y ONBOARD-002 se añaden llamando a `harness add`,
porque el backlog es de `harness`. Si `seed` falla, el problema está en el
arnés (`harness/featureslist.json` que no existe, o un id ya ocupado) — no lo
arregles escribiendo el JSON a mano, que es exactamente lo que el arnés existe
para impedir.

`seed` es idempotente: los tickets que ya están se cuentan en `skipped` y no se
tocan. `--force` solo reintenta el alta, no reescribe lo que ya hay.

## Cuándo consultarlo

`status` primero, siempre — es de solo lectura y su campo `next` dice qué toca.
Si devuelve `first_run: false`, el arranque en frío no aplica y hay que seguir
con el protocolo normal (`harness next`). No siembres tickets de onboarding en
un proyecto que ya tiene histórico.

<!-- BEGIN AUTOGEN — lo regenera `make prompts-sync`; no lo edites a mano -->

## Acciones

| Acción | Argumentos |
|--------|------------|
| `run bootstrap status` | — |
| `run bootstrap seed` ⚠️ pide confirmación | `--force` |
| `run bootstrap describe` ⚠️ pide confirmación | `--description` |
| `run bootstrap suggest_agents` | `--description` |

## Límites

**Rol.** Arranque en frío: convierte un repo vacío en uno con objetivo escrito y backlog sembrado.

**No se deshacen** (la puerta de permisos las bloquea sin `--yes`; propón, no ejecutes): `describe`, `seed`

**No hace:**
- inventarse el propósito del proyecto — si falta, pregunta (needs) y para
- escribir en el backlog directamente → harness (su dueño)
- crear agentes → installer scaffold (dueño de agents/external/)
- escribir en el vault → knowledge (su dueño)

**Necesita que le den:** la descripción del proyecto, en palabras del usuario

**Escribe en (nadie más toca esto):** project.yml, agents/workspace/bootstrap/

**Se apoya en:** harness, installer, research, knowledge

<!-- END AUTOGEN -->
