"""
Configuración de logging unificado usando Loguru.

Uso:
    from src.utils.logging_config import setup_logging
    setup_logging()
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = "logs/app.log",
    rotation: str = "10 MB",
    retention: str = "30 days",
) -> None:
    """
    Configura el logging del proyecto.

    Args:
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR).
        log_file: Ruta del archivo de log. None para solo consola.
        rotation: Rotación del archivo de log.
        retention: Retención de logs antiguos.
    """
    # Eliminar el handler por defecto
    logger.remove()

    # Handler de consola (con colores para desarrollo)
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
    )

    # Handler de archivo (para producción)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="gz",
            serialize=False,
        )

    logger.debug(f"Logging configurado: nivel={log_level}, archivo={log_file}")
