# Contributing

Gracias por tu interés en contribuir a MeshHarmes.

## Cómo contribuir

1. Haz un fork del repositorio.
2. Crea una rama para tu cambio (`git checkout -b feat/mi-cambio`).
3. Asegúrate de que los tests pasan: `make check`.
4. Ejecuta la batería de calidad: `make lint typecheck security audit`.
   Si trabajas con el arnés, `./init.sh` tiene que salir en verde.
5. Haz commit con un mensaje descriptivo (conventional commit).
6. Abre un Pull Request.

## Guías

- Sigue el estilo del código existente (ruff lo valida con `make lint`).
- Añade tests para cualquier funcionalidad nueva: sin ellos, el arnés no
  deja cerrar la feature (`harness finish` exige evidencia real).
- Añade type hints en todo código nuevo (validado con `make typecheck`).
- Actualiza el CHANGELOG.md con tus cambios.

## Reportar issues

Usa el rastreador de issues del repositorio para reportar bugs o sugerir
mejoras. Incluye toda la información posible para reproducir el problema.
