"""
agents.tools.cache_tool — Caché en disco para operaciones costosas.

Backend: `pickle` de la stdlib. `agents/` no añade dependencias al proyecto
— el arnés tiene que funcionar en un repo que aún no ha instalado nada.
Proporciona decoradores para cachear resultados de funciones con TTL opcional.

Límite honesto: `pickle` solo serializa objetos picklables (nada de lambdas,
handles abiertos o clases definidas dentro de una función). Si el resultado no
se puede serializar, la escritura falla — no se cachea en silencio.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from agents.tools.registry import register_tool


def _md5(*args, **kwargs) -> str:
    try:
        return hashlib.md5(*args, usedforsecurity=False, **kwargs).hexdigest()
    except TypeError:
        return hashlib.md5(*args, **kwargs).hexdigest()


def _cache_dir() -> Path:
    return CacheTool._instance_cache_dir if CacheTool._instance_cache_dir is not None else Path(".cache")


def _cache_path(func_name: str, args: tuple, kwargs: dict) -> Path:
    key = _md5(
        json.dumps((func_name, args, sorted(kwargs.items())), sort_keys=True, default=str).encode()
    )
    return _cache_dir() / f"{func_name}_{key}.pkl"


@register_tool("cache")
class CacheTool:

    _instance_cache_dir: Path | None = None

    @staticmethod
    def set_cache_dir(path: str | Path) -> None:
        """Cambia el directorio de caché para este CacheTool."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        CacheTool._instance_cache_dir = path

    @staticmethod
    def get_cache_dir() -> str:
        return str(_cache_dir())

    @staticmethod
    def clear(name: str | None = None) -> int:
        """
        Limpia archivos de caché. name=None → todo, name="func_name" → solo esa función.
        Devuelve número de archivos eliminados.
        """
        cache_dir = _cache_dir()
        if not cache_dir.exists():
            return 0
        removed = 0
        for f in cache_dir.iterdir():
            if f.suffix == ".pkl" and (name is None or f.name.startswith(f"{name}_")):
                f.unlink()
                removed += 1
        return removed

    @staticmethod
    def disk_cache(ttl: int | None = None, name: str | None = None) -> Callable:
        """
        Decorador: cachea el resultado en disco con TTL opcional (segundos).

        Uso:
            @CacheTool.disk_cache(ttl=3600)
            def expensive_function(x):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_name = name or func.__name__
                path = _cache_path(cache_name, args, kwargs)
                if path.exists():
                    if ttl is not None:
                        age = time.time() - path.stat().st_mtime
                        if age > ttl:
                            path.unlink()
                        else:
                            return pickle.loads(path.read_bytes())
                    else:
                        return pickle.loads(path.read_bytes())
                result = func(*args, **kwargs)
                cache_dir = _cache_dir()
                cache_dir.mkdir(parents=True, exist_ok=True)
                path.write_bytes(pickle.dumps(result))
                return result
            return wrapper
        return decorator

    @staticmethod
    def memory_cache(maxsize: int = 128) -> Callable:
        """
        Decorador: caché en memoria LRU para resultados de funciones puras.

        Uso:
            @CacheTool.memory_cache(maxsize=256)
            def fast_function(x):
                ...
        """
        def decorator(func: Callable) -> Callable:
            cache: dict[str, Any] = {}
            hits = 0
            misses = 0

            @wraps(func)
            def wrapper(*args, **kwargs):
                nonlocal hits, misses
                key = _md5(
                    json.dumps((func.__name__, args, sorted(kwargs.items())), sort_keys=True, default=str).encode()
                )
                if key in cache:
                    hits += 1
                    return cache[key]
                misses += 1
                result = func(*args, **kwargs)
                if len(cache) >= maxsize:
                    cache.pop(next(iter(cache)))
                cache[key] = result
                return result

            wrapper.cache_info = lambda: {"hits": hits, "misses": misses, "size": len(cache), "maxsize": maxsize}
            wrapper.cache_clear = lambda: cache.clear()
            return wrapper
        return decorator
