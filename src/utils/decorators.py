"""
Decoradores utilitarios para el proyecto.

Incluye:
- @timed: Mide tiempo de ejecución
- @retry: Reintenta operaciones fallidas
- @cached: Caché en disco para funciones costosas
"""

import functools
import time
from pathlib import Path

from loguru import logger


def timed(func):
    """
    Decorador que mide y loguea el tiempo de ejecución de una función.

    Uso:
        @timed
        def procesar_datos():
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        if elapsed > 60:
            logger.info(f"{func.__name__} completado en {elapsed/60:.1f} min")
        elif elapsed > 1:
            logger.info(f"{func.__name__} completado en {elapsed:.1f}s")
        else:
            logger.debug(f"{func.__name__} completado en {elapsed*1000:.0f}ms")

        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorador que reintenta una función si falla.

    Args:
        max_attempts: Número máximo de intentos.
        delay: Espera inicial entre intentos (segundos).
        backoff: Factor de multiplicación del delay.

    Uso:
        @retry(max_attempts=5, delay=2.0)
        def descargar_archivo(url):
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} falló después de {max_attempts} intentos: {e}"
                        )
                        raise
                    logger.warning(
                        f"{func.__name__} intento {attempt}/{max_attempts} falló: {e}. "
                        f"Reintentando en {_delay:.1f}s..."
                    )
                    time.sleep(_delay)
                    _delay *= backoff

        return wrapper

    return decorator
