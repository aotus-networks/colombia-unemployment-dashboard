"""
Transformación y validación de datos de desempleo.

Incluye limpieza, normalización y validación con Pandera.
"""

import pandas as pd
import pandera as pa
from loguru import logger


# ─── Esquema de validación ────────────────────────────────────────────────────
class UnemploymentSchema(pa.DataFrameModel):
    """Esquema de validación para datos de desempleo departamental."""

    departamento: pa.typing.Series[str] = pa.Field(nullable=False)
    cod_departamento: pa.typing.Series[str] = pa.Field(
        nullable=False, str_length={"min_value": 2, "max_value": 2}
    )
    año: pa.typing.Series[int] = pa.Field(
        ge=2001, le=2030, nullable=False
    )
    mes: pa.typing.Series[int] = pa.Field(
        ge=1, le=12, nullable=False
    )
    tasa_desempleo: pa.typing.Series[float] = pa.Field(
        ge=0.0, le=50.0, nullable=False,
        description="Tasa de Desempleo (TD) en porcentaje"
    )
    tasa_ocupacion: pa.typing.Series[float] = pa.Field(
        ge=0.0, le=100.0, nullable=False,
        description="Tasa de Ocupación (TO) en porcentaje"
    )
    tgp: pa.typing.Series[float] = pa.Field(
        ge=0.0, le=100.0, nullable=False,
        description="Tasa Global de Participación en porcentaje"
    )

    class Config:
        strict = True
        coerce = True


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Validando datos con Pandera...")
    try:
        validated = UnemploymentSchema.validate(df)
        logger.success(f"Validación exitosa: {len(validated)} registros OK")
        return validated
    except pa.errors.SchemaError as e:
        logger.error(f"Error de validación: {e}")
        raise


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["periodo"] = df.apply(
        lambda r: f"{int(r['año'])}-{int(r['mes']):02d}", axis=1
    )
    df["periodo_int"] = df["año"] * 100 + df["mes"]

    df = df.sort_values(["departamento", "año", "mes"])
    df["td_var_interanual"] = df.groupby(["departamento", "mes"])[
        "tasa_desempleo"
    ].diff()

    df["rank_nacional"] = df.groupby(["año", "mes"])[
        "tasa_desempleo"
    ].rank(ascending=False, method="min")

    return df


def prepare_for_map(df: pd.DataFrame, geo_df: "gpd.GeoDataFrame") -> "gpd.GeoDataFrame":
    import geopandas as gpd

    geo_df = geo_df.copy()

    # Detectar columna de nombre en el GeoJSON
    name_col = None
    for col in ["DPTO_CNMBR", "NOMBRE_DPT", "nombre", "name", "DeNombre"]:
        if col in geo_df.columns:
            name_col = col
            break

    if name_col is None:
        raise ValueError(
            f"No se encontró columna de nombre en GeoDataFrame. Columnas: {geo_df.columns.tolist()}"
        )

    # Remover caracteres especiales
    geo_df[name_col] = geo_df[name_col].str.replace("\ufffd", "", regex=False)

    # Mapeo de acentos a ASCII
    accent_map = {
        "Á": "A", "À": "A", "Ä": "A", "Â": "A", "Ã": "A",
        "É": "E", "È": "E", "Ë": "E", "Ê": "E",
        "Í": "I", "Ì": "I", "Ï": "I", "Î": "I",
        "Ó": "O", "Ò": "O", "Ö": "O", "Ô": "O", "Õ": "O",
        "Ú": "U", "Ù": "U", "Ü": "U", "Û": "U",
        "Ñ": "N", "Ç": "C",
    }
    for accented, plain in accent_map.items():
        geo_df[name_col] = geo_df[name_col].str.replace(accented, plain, regex=False)

    geo_df = geo_df.rename(columns={name_col: "departamento_geo"})

    # Normalizar: uppercase, sin puntos ni comas
    geo_df["departamento_geo"] = (
        geo_df["departamento_geo"]
        .str.upper()
        .str.replace(",", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.strip()
    )

    # Correcciones de nombres del GeoJSON al formato de los datos sintéticos
    geo_corrections = {
        "SANTAFE DE BOGOTA DC": "BOGOTA DC",
        "BOGOTA D C": "BOGOTA DC",
        "BOGOTA DC": "BOGOTA DC",
        "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA": "SAN ANDRES",
        "SAN ANDRES Y PROVIDENCIA": "SAN ANDRES",
    }
    for wrong, correct in geo_corrections.items():
        geo_df.loc[geo_df["departamento_geo"] == wrong, "departamento_geo"] = correct

    # Normalizar nombres en los datos
    df = df.copy()
    df["departamento_join"] = (
        df["departamento"]
        .str.upper()
        .str.replace(",", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.strip()
    )

    # Correcciones en los datos sintéticos para que coincidan con el GeoJSON
    data_corrections = {
        "BOGOTA DC": "BOGOTA DC",
    }
    for wrong, correct in data_corrections.items():
        df.loc[df["departamento_join"] == wrong, "departamento_join"] = correct

    # Join
    merged = geo_df.merge(df, left_on="departamento_geo", right_on="departamento_join", how="left")

    logger.info(
        f"Spatial join: {len(merged)} filas, "
        f"{merged['departamento'].nunique()} departamentos"
    )

    return gpd.GeoDataFrame(merged, geometry="geometry", crs=geo_df.crs)
