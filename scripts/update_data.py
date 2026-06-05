"""
Script de actualización incremental.

Descarga solo el último mes disponible y lo agrega al pipeline.

Uso:
    python scripts/update_data.py
    python scripts/update_data.py --month 2026-05
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta

from loguru import logger


def get_last_available_month() -> tuple[int, int]:
    """
    Determina el último mes con datos disponibles.
    DANE publica GEIH ~30 días después del cierre del mes.
    """
    today = datetime.now()
    # Asumimos que el dato de hace 2 meses ya está disponible
    pub_date = today - timedelta(days=60)
    return pub_date.year, pub_date.month


def update_data(year: int | None = None, month: int | None = None):
    """
    Actualiza los datos con el mes más reciente.

    Args:
        year: Año a descargar. Si es None, usa el último disponible.
        month: Mes a descargar. Si es None, usa el último disponible.
    """
    if year is None or month is None:
        year, month = get_last_available_month()

    logger.info(f"Actualizando datos: {year}-{month:02d}")

    # TODO: Implementar lógica de actualización incremental
    # 1. Descargar el mes específico
    # 2. Extraer y transformar solo ese mes
    # 3. Append a los Parquet existentes
    # 4. Re-generar spatial join si es necesario

    logger.success(f"Actualización completada para {year}-{month:02d}")


def main():
    parser = argparse.ArgumentParser(description="Actualiza datos de desempleo")
    parser.add_argument(
        "--month", type=str,
        help="Mes específico a actualizar (formato: YYYY-MM)"
    )

    args = parser.parse_args()

    if args.month:
        year, month = map(int, args.month.split("-"))
        update_data(year=year, month=month)
    else:
        update_data()


if __name__ == "__main__":
    main()
