"""
agents.tools.parallel_tool — Ejecución paralela sin dependencias externas.

Backend: `concurrent.futures` de la stdlib. `agents/` no añade dependencias
al proyecto, así que aquí no hay joblib ni tqdm: el progreso, si se pide, se
imprime a stderr con una línea que se sobrescribe.

Qué backend elegir:
  - `"thread"` (por defecto) — I/O: red, disco, subprocesos. Es lo que hacen
    los agentes el 95% del tiempo.
  - `"process"` — CPU puro. Ojo: `func` y los elementos deben ser picklables
    (nada de lambdas ni closures), y arrancar procesos cuesta.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any

from agents.tools.registry import register_tool


def _executor(backend: str, n_jobs: int):
    workers = None if n_jobs in (-1, 0) else n_jobs
    if backend == "process":
        return ProcessPoolExecutor(max_workers=workers)
    if backend == "thread":
        return ThreadPoolExecutor(max_workers=workers)
    raise ValueError(f"backend desconocido: {backend!r} (usa 'thread' o 'process')")


def _progress(done: int, total: int, desc: str) -> None:
    sys.stderr.write(f"\r{desc}: {done}/{total}")
    if done >= total:
        sys.stderr.write("\n")
    sys.stderr.flush()


def _run(func: Callable, items: list, n_jobs: int, desc: str | None,
         backend: str, star: bool) -> list[Any]:
    if not items:
        return []
    if n_jobs == 1:
        results = [func(*item) if star else func(item) for item in items]
        if desc:
            _progress(len(items), len(items), desc)
        return results

    results: list[Any] = [None] * len(items)
    with _executor(backend, n_jobs) as pool:
        futures = {
            pool.submit(func, *item) if star else pool.submit(func, item): i
            for i, item in enumerate(items)
        }
        for done, future in enumerate(as_completed(futures), start=1):
            index = futures[future]
            results[index] = future.result()
            if desc:
                _progress(done, len(items), desc)
    return results


@register_tool("parallel")
class ParallelTool:
    @staticmethod
    def parallel_map(func: Callable, iterable: Iterable, n_jobs: int = -1,
                     desc: str | None = None, backend: str = "thread") -> list[Any]:
        """
        Map paralelo preservando el orden de entrada.

        func     : función a aplicar a cada elemento
        iterable : elementos a procesar
        n_jobs   : -1 = tantos workers como decida la stdlib, 1 = secuencial
        desc     : texto de progreso a stderr (None = sin progreso)
        backend  : 'thread' (I/O, por defecto) | 'process' (CPU, requiere picklables)
        """
        return _run(func, list(iterable), n_jobs, desc, backend, star=False)

    @staticmethod
    def parallel_starmap(func: Callable, iterable: Iterable, n_jobs: int = -1,
                         desc: str | None = None, backend: str = "thread") -> list[Any]:
        """
        Starmap paralelo para funciones que reciben tuplas: `func(*args)` por elemento.
        """
        return _run(func, list(iterable), n_jobs, desc, backend, star=True)

    @staticmethod
    def chunked(iterable: Iterable, n_chunks: int) -> list[list]:
        """Divide un iterable en n_chunks aproximadamente iguales."""
        items = list(iterable)
        n = len(items)
        if n_chunks <= 0:
            return [items]
        chunk_size = (n + n_chunks - 1) // n_chunks
        return [items[i:i + chunk_size] for i in range(0, n, chunk_size)]
