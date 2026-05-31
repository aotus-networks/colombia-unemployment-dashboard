"""
Pipeline ETL completo para datos de desempleo departamental.

Orquesta: generación (o extracción) → validación → spatial join → guardado.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import geopandas as gpd
from loguru import logger

from src.etl.extract_geih import generate_realistic_data
from src.etl.transform import add_derived_columns, prepare_for_map, validate_data
from src.utils.logging_config import setup_logging
from src.utils.paths import DEPARTMENT_PARQUET, DEPARTMENT_GEOJSON, PROCESSED_DIR


def run_pipeline(
    use_real_data: bool = False,
    start_year: int = 2015,
    end_year: int = 2026,
) -> gpd.GeoDataFrame:
    """
    Ejecuta el pipeline ETL completo.

    Args:
        use_real_data: Si True, intenta usar datos reales del DANE.
        start_year: Año inicial para datos sintéticos.
        end_year: Año final para datos sintéticos.

    Returns:
        GeoDataFrame con datos listos para visualización.
    """
    setup_logging()

    logger.info("=" * 60)
    logger.info("PIPELINE ETL - Mapa de Desempleo Departamental")
    logger.info("=" * 60)

    # ─── 1. Obtener datos ─────────────────────────────────────────────────
    logger.info("Paso 1/5: Obteniendo datos...")

    if use_real_data:
        logger.warning("Modo datos reales no implementado aún. Usando sintéticos.")
        df = generate_realistic_data(start_year=start_year, end_year=end_year)
    else:
        logger.info("Usando datos sintéticos calibrados con información pública del DANE")
        df = generate_realistic_data(start_year=start_year, end_year=end_year)

    logger.info(f"  Registros: {len(df):,}")

    # ─── 2. Validar ───────────────────────────────────────────────────────
    logger.info("Paso 2/5: Validando datos...")
    df = validate_data(df)

    # ─── 3. Columnas derivadas ────────────────────────────────────────────
    logger.info("Paso 3/5: Calculando métricas derivadas...")
    df = add_derived_columns(df)

    # ─── 4. Cargar geometrías y unir ──────────────────────────────────────
    logger.info("Paso 4/5: Cargando geometrías...")

    if not DEPARTMENT_GEOJSON.exists():
        raise FileNotFoundError(
            f"No se encontró {DEPARTMENT_GEOJSON}. "
            "Ejecuta primero la descarga de datos geoespaciales."
        )

    geo_df = gpd.read_file(DEPARTMENT_GEOJSON)
    logger.info(f"  Departamentos en GeoJSON: {len(geo_df)}")

    # Simplificar geometrías para mejor rendimiento web
    logger.info("  Simplificando geometrías (tol=0.01)...")
    geo_df["geometry"] = geo_df["geometry"].simplify(0.01, preserve_topology=True)

    # Spatial join
    logger.info("Paso 5/5: Uniendo datos con geometrías...")
    gdf = prepare_for_map(df, geo_df)

    # ─── Guardar ──────────────────────────────────────────────────────────
    logger.info("Guardando datos procesados...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Guardar como Parquet (eficiente, preserva geometrías)
    gdf.to_parquet(DEPARTMENT_PARQUET, compression="zstd")
    logger.success(f"Datos guardados en {DEPARTMENT_PARQUET}")

    # También guardar CSV (sin geometría) para análisis rápido
    csv_path = PROCESSED_DIR / "unemployment_department.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.success(f"CSV guardado en {csv_path}")

    # Resumen
    logger.info("=" * 60)
    logger.info("RESUMEN DEL PIPELINE")
    logger.info(f"  Departamentos: {gdf['departamento'].nunique()}")
    logger.info(f"  Período: {df['año'].min()}-{df['año'].max()}")
    logger.info(
        f"  TD promedio: {df['tasa_desempleo'].mean():.1f}% "
        f"(min: {df['tasa_desempleo'].min():.1f}%, "
        f"max: {df['tasa_desempleo'].max():.1f}%)"
    )
    logger.info(f"  Archivos: {DEPARTMENT_PARQUET.name}, {csv_path.name}")
    logger.info("=" * 60)

    return gdf


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pipeline ETL de desempleo departamental")
    parser.add_argument(
        "--real", action="store_true",
        help="Intentar usar datos reales del DANE"
    )
    parser.add_argument(
        "--start", type=int, default=2015,
        help="Año inicial (default: 2015)"
    )
    parser.add_argument(
        "--end", type=int, default=2026,
        help="Año final (default: 2026)"
    )

    args = parser.parse_args()
    run_pipeline(use_real_data=args.real, start_year=args.start, end_year=args.end)
