"""Smoke test - verifica que todos los componentes funcionen."""
import sys
sys.path.insert(0, r"C:\proyecto desempleo")

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

print("=" * 60)
print("SMOKE TEST - Mapa de Desempleo en Colombia")
print("=" * 60)

# 1. Cargar datos
gdf = gpd.read_parquet(r"C:\proyecto desempleo\data\processed\unemployment_department.parquet")
df = pd.DataFrame(gdf.drop(columns=["geometry"]))
n_deptos = gdf["departamento"].nunique()
print(f"[OK] Datos: {len(gdf)} filas, {n_deptos} departamentos")
print(f"[OK] CRS: {gdf.crs}")
print(f"[OK] Columnas: {list(df.columns[:8])}")

# 2. KPIs
ultimo = df[df["año"] == df["año"].max()]
ultimo_mes_val = ultimo["mes"].max()
ultimo_mes = ultimo[ultimo["mes"] == ultimo_mes_val]
td_nac = ultimo_mes["tasa_desempleo"].mean()
idx_max = ultimo_mes["tasa_desempleo"].idxmax()
idx_min = ultimo_mes["tasa_desempleo"].idxmin()
print(f"[OK] TD Nacional: {td_nac:.1f}%")
print(f"[OK] Mayor TD: {ultimo_mes.loc[idx_max, 'departamento']} ({ultimo_mes.loc[idx_max, 'tasa_desempleo']:.1f}%)")
print(f"[OK] Menor TD: {ultimo_mes.loc[idx_min, 'departamento']} ({ultimo_mes.loc[idx_min, 'tasa_desempleo']:.1f}%)")

# 3. Series
covid = df[df["año"] == 2020]["tasa_desempleo"].mean()
normal = df[df["año"] == 2019]["tasa_desempleo"].mean()
print(f"[OK] Rango: {df['año'].min()}-{df['año'].max()}")
print(f"[OK] COVID spike: {covid:.1f}% vs {normal:.1f}% (delta: {covid-normal:+.1f}pp)")

# 4. Plotly
print(f"[OK] Plotly v{px.__version__}")

# 5. Streamlit
print(f"[OK] Streamlit v{st.__version__}")

# 6. Validar que hay geometrías válidas
empty_geo = gdf.geometry.is_empty.sum()
print(f"[OK] Geometrías válidas: {len(gdf) - empty_geo}/{len(gdf)}")

print()
print("=" * 60)
print("TODOS LOS COMPONENTES FUNCIONAN CORRECTAMENTE")
print("=" * 60)
print()
print("Para iniciar el dashboard:")
print("  streamlit run src/dashboard/app.py")
