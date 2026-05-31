"""
Utilidades de rutas del proyecto.

Centraliza la resolución de todas las rutas usadas en el proyecto
para evitar hardcodear paths relativos.
"""

from pathlib import Path

# Raíz del proyecto (3 niveles arriba desde este archivo)
# src/utils/paths.py -> src/utils -> src -> proyecto raíz
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Directorios de datos
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_GEIH_DIR = RAW_DIR / "geih"
RAW_MICRODATA_DIR = RAW_DIR / "microdata"
PROCESSED_DIR = DATA_DIR / "processed"
GEO_DIR = DATA_DIR / "geo"

# Archivos procesados
DEPARTMENT_PARQUET = PROCESSED_DIR / "unemployment_department.parquet"
CITY_PARQUET = PROCESSED_DIR / "unemployment_city.parquet"
MUNICIPALITY_PARQUET = PROCESSED_DIR / "unemployment_municipality.parquet"

# Archivos geoespaciales
DEPARTMENT_GEOJSON = GEO_DIR / "departamentos.geojson"
MUNICIPALITY_GEOJSON = GEO_DIR / "municipios.geojson"
COLOMBIA_SIMPLIFIED_GEOJSON = GEO_DIR / "colombia_simplified.geojson"

# Notebooks
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Assets
ASSETS_DIR = PROJECT_ROOT / "assets"


def ensure_dirs() -> None:
    """Crea todos los directorios necesarios si no existen."""
    dirs = [
        RAW_DIR,
        RAW_GEIH_DIR,
        RAW_MICRODATA_DIR,
        PROCESSED_DIR,
        GEO_DIR,
        NOTEBOOKS_DIR,
        ASSETS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
