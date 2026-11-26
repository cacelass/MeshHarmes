# Índice para IA — MeshHarmes

> Índice del vault. Punto de entrada para cualquier agente que necesite
> contexto del proyecto antes de tocar nada.

## Metadata del proyecto

- **Nombre:** MeshHarmes
- **Paquete:** `app/` (declarado en `project.yml`)
- **Versión:** 0.1.0
- **Descripción:** Arnés de agentes e infraestructura de proyecto para trabajo general en Python.
- **Autor:** cacelass

## Estructura del vault

| Archivo | Propósito |
|---------|-----------|
| `00_META/IA_index.md` | Este archivo — punto de entrada para IA |
| `00_META/templates/` | Plantillas Obsidian para nuevas notas |
| `01_PROYECTO/objetivo.md` | Qué se quiere resolver (lo escribe SCOPE-001) |
| `01_PROYECTO/arquitectura.md` | Cómo está montado el proyecto |
| `01_PROYECTO/agentes.md` | Topología del sistema de agentes |
| `01_PROYECTO/roadmap.md` | Por dónde va el trabajo |
| `04_VISUALIZACIONES/grafo_conocimiento.md` | Grafo de conocimiento (graphify) |
| `05_AGENTES/_index.md` | Directorio de agentes |
| `05_AGENTES/*.md` | Ficha individual de cada agente |
| `06_OBSERVACIONES/` | Hallazgos sueltos, notas del día a día |

## Cómo se usa

1. ¿Necesitas contexto del proyecto? Empieza por `01_PROYECTO/objetivo.md`.
2. ¿Necesitas saber qué hace un agente? `05_AGENTES/<Agente>.md`.
3. ¿Vas a escribir aquí? No lo hagas a mano: el dueño del vault es el agente
   `knowledge`. Este vault guarda lo **estable**; lo de la feature en curso
   vive en `harness/progress/`.
