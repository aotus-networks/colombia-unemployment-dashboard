"""
Script principal del pipeline ETL.

Ejecuta todo el flujo: extract → transform → validate → spatial_join.

Uso:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --skip-download
    python scripts/run_pipeline.py --only-department
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from loguru import logger

logger.add("logs/pipeline.log", rotation="10 MB", retention="30 days")


def run_pipeline(skip_download: bool = False, only_department: bool = False):
    """
    Ejecuta el pipeline ETL completo.

    Args:
        skip_download: Si es True, asume que los datos ya fueron descargados.
        only_department: Si es True, procesa solo datos departamentales.
    """
    logger.info("=" * 60)
    logger.info("PIPELINE ETL - Mapa de Desempleo en Colombia")
    logger.info("=" * 60)

    # 1. Download (si no se skipea)
    if not skip_download:
        logger.info("Paso 1/4: Descargando datos...")
        # TODO: Integrar llamada a download_data.py
        logger.warning("Descarga no implementada aún. Usa --skip-download si ya tienes los datos.")
        return

    # 2. Extract
    logger.info("Paso 2/4: Extrayendo datos de Excel...")
    # TODO: from src.etl.extract_geih import extract_all
    # df = extract_all()

    # 3. Transform + Validate
    logger.info("Paso 3/4: Transformando y validando...")
    # TODO: from src.etl.transform import transform_geih
    # from src.etl.validate import validate_unemployment_data
    # df = transform_geih(df)
    # validate_unemployment_data(df)

    # 4. Spatial Join
    logger.info("Paso 4/4: Uniendo con geometrías...")
    # TODO: from src.etl.spatial_join import join_unemployment_to_geo
    # gdf = join_unemployment_to_geo(df)

    # 5. Save
    # TODO: gdf.to_parquet(...)

    logger.success("Pipeline completado exitosamente!")


def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL de desempleo")
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Saltar la descarga de datos"
    )
    parser.add_argument(
        "--only-department", action="store_true",
        help="Procesar solo datos departamentales"
    )

    args = parser.parse_args()
    run_pipeline(skip_download=args.skip_download, only_department=args.only_department)


if __name__ == "__main__":
    main()
