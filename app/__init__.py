"""
app — paquete del proyecto.

Este es el sitio donde va TU código. El arnés (`agents/`, `harness/`,
`init.sh`) no depende de lo que haya aquí dentro más allá de dos cosas:

- que el paquete exista y sea importable (lo comprueba `./init.sh`),
- que su nombre coincida con `project_slug` en `project.yml`.

Para renombrarlo: `git mv app <tu_paquete>` y cambia `project_slug` en
`project.yml`, `packages` en `pyproject.toml` y `source` en
`[tool.coverage.run]`. Son cuatro sitios y `./init.sh` te avisa si te dejas
alguno.
"""

__version__ = "0.1.0"
