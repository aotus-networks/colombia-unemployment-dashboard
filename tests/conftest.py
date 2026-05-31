"""
Fixtures compartidos para todos los tests del proyecto.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon


@pytest.fixture
def sample_department_data() -> pd.DataFrame:
    """Fixture: datos sintéticos de desempleo departamental."""
    np.random.seed(42)
    deptos = [
        "Bogotá D.C.", "Antioquia", "Valle del Cauca", "Atlántico",
        "Santander", "Bolívar", "Cundinamarca", "Nariño",
        "Cauca", "Magdalena", "Chocó", "Amazonas",
    ]
    data = []
    for year in range(2015, 2024):
        for depto in deptos:
            data.append({
                "departamento": depto,
                "cod_departamento": f"{deptos.index(depto)+1:02d}",
                "año": year,
                "mes": 6,  # Junio como referencia
                "tasa_desempleo": np.clip(np.random.normal(10, 3), 3, 30),
                "tasa_ocupacion": np.clip(np.random.normal(55, 5), 40, 75),
                "tgp": np.clip(np.random.normal(62, 4), 50, 80),
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_geo_data() -> gpd.GeoDataFrame:
    """Fixture: datos geoespaciales sintéticos de departamentos."""
    deptos = [
        "Bogotá D.C.", "Antioquia", "Valle del Cauca", "Atlántico",
        "Santander", "Bolívar", "Cundinamarca", "Nariño",
        "Cauca", "Magdalena", "Chocó", "Amazonas",
    ]
    geometries = []
    for i in range(len(deptos)):
        offset = i * 2
        geometries.append(
            Polygon([
                (offset, 0),
                (offset + 1, 0),
                (offset + 1, 1),
                (offset, 1),
            ])
        )

    return gpd.GeoDataFrame(
        {
            "departamento": deptos,
            "cod_departamento": [f"{i+1:02d}" for i in range(len(deptos))],
            "geometry": geometries,
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def sample_city_data() -> pd.DataFrame:
    """Fixture: datos sintéticos de desempleo por ciudad."""
    np.random.seed(42)
    cities = [
        "Bogotá D.C.", "Medellín A.M.", "Cali A.M.", "Barranquilla A.M.",
        "Bucaramanga A.M.", "Cartagena", "Cúcuta A.M.", "Pereira A.M.",
        "Manizales A.M.", "Ibagué", "Villavicencio", "Pasto",
    ]
    data = []
    for year in [2015, 2020, 2024]:
        for city in cities:
            data.append({
                "ciudad": city,
                "año": year,
                "mes": 6,
                "tasa_desempleo": np.clip(np.random.normal(11, 3), 5, 25),
                "tasa_ocupacion": np.clip(np.random.normal(58, 4), 45, 70),
                "tgp": np.clip(np.random.normal(65, 3), 55, 75),
            })

    return pd.DataFrame(data)
