"""
Dashboard Interactivo de Desempleo en Colombia
===============================================

Aplicación Streamlit con mapa coroplético departamental interactivo,
evolución temporal, KPIs, rankings y más.

Ejecutar:
    streamlit run src/dashboard/app.py
"""

import sys
from pathlib import Path

# Asegurar que el proyecto está en el path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─── Configuración de la página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Desempleo en Colombia | Dashboard",
    page_icon=":world_map:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* KPIs */
    .kpi-row {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 14px;
        padding: 1rem 1.5rem;
        text-align: center;
        min-width: 140px;
        border: 1px solid #dee2e6;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .kpi-delta {
        font-size: 0.9rem;
        font-weight: 600;
    }
    .positive { color: #198754; }
    .negative { color: #dc3545; }

    /* Rankings */
    .rank-high { background: rgba(227, 26, 28, 0.08); border-radius: 6px; padding: 0.3rem 0.6rem; }
    .rank-low { background: rgba(27, 158, 119, 0.08); border-radius: 6px; padding: 0.3rem 0.6rem; }

    /* Footer */
    .footer {
        text-align: center; padding: 1.5rem 0; color: #6c757d;
        font-size: 0.8rem; border-top: 1px solid #dee2e6; margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Carga de datos (cacheada) ────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Cargando datos...")
def load_data():
    """Carga o genera los datos de desempleo departamental."""
    from src.etl.pipeline import run_pipeline
    from src.utils.paths import DEPARTMENT_PARQUET

    if DEPARTMENT_PARQUET.exists():
        gdf = gpd.read_parquet(DEPARTMENT_PARQUET)
        st.sidebar.success(f"Datos cargados del caché ({len(gdf):,} registros)")
        return gdf

    with st.spinner("Generando datos (primera ejecución)..."):
        gdf = run_pipeline(start_year=2015, end_year=2026)
    st.sidebar.success(f"Datos generados ({len(gdf):,} registros)")
    return gdf


# ─── Cargar datos ─────────────────────────────────────────────────────────────
try:
    gdf = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

# ─── Preparar datos ───────────────────────────────────────────────────────────
# Columnas disponibles
df = pd.DataFrame(gdf.drop(columns=["geometry"]))

# Lista de departamentos y años
DEPARTAMENTOS = sorted(df["departamento"].unique())
AÑOS = sorted(df["año"].unique())
MESES_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title(":world_map: Desempleo Colombia")
    st.markdown("---")

    # Vista
    st.markdown("### :eye: Vista")
    view = st.radio(
        "Selecciona una vista:",
        [
            ":world_map: Mapa Nacional",
            ":chart_with_upwards_trend: Evolución Temporal",
            ":trophy: Ranking Departamentos",
            ":calendar: Heatmap Estacional",
            ":books: Metodología",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Filtros comunes
    st.markdown("### :gear: Filtros")

    if view != ":chart_with_upwards_trend: Evolución Temporal":
        año_seleccionado = st.selectbox("Año", AÑOS, index=len(AÑOS) - 1)

    if view != ":trophy: Ranking Departamentos":
        depto_seleccionado = st.selectbox(
            "Departamento",
            ["Todos"] + DEPARTAMENTOS,
            index=0,
        )

    st.markdown("---")
    st.caption("Datos: DANE - GEIH (sintéticos calibrados)")
    st.caption("[GitHub](https://github.com/tuusuario/colombia-unemployment-dashboard)")
    st.caption("v0.1.0 | 2026")


# ─── Página: MAPA NACIONAL ───────────────────────────────────────────────────
if view == ":world_map: Mapa Nacional":
    st.title(":world_map: Mapa de Desempleo en Colombia")
    st.markdown(f"### Tasa de Desempleo por Departamento — {año_seleccionado}")

    # Filtrar datos para el año y mes más reciente
    df_year = df[df["año"] == año_seleccionado]
    ultimo_mes = df_year["mes"].max()
    df_map = df_year[df_year["mes"] == ultimo_mes]

    # Merge con geometrías
    gdf_map = gdf[gdf["año"] == año_seleccionado]
    gdf_map = gdf_map[gdf_map["mes"] == ultimo_mes]

    if depto_seleccionado != "Todos":
        gdf_map = gdf_map[gdf_map["departamento"] == depto_seleccionado]

    # KPIs
    nacional = df_map["tasa_desempleo"].mean()
    # Dato del año anterior para delta
    df_prev = df[(df["año"] == año_seleccionado - 1) & (df["mes"] == ultimo_mes)]
    nacional_prev = df_prev["tasa_desempleo"].mean() if len(df_prev) > 0 else nacional

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        delta = nacional - nacional_prev
        color = "positive" if delta <= 0 else "negative"
        st.metric(
            "Tasa de Desempleo Nacional",
            f"{nacional:.1f}%",
            delta=f"{delta:+.1f} pp",
        )
    with col2:
        tgp_val = df_map["tgp"].mean()
        st.metric("Tasa Global de Participación", f"{tgp_val:.1f}%")
    with col3:
        to_val = df_map["tasa_ocupacion"].mean()
        st.metric("Tasa de Ocupación", f"{to_val:.1f}%")
    with col4:
        max_depto = df_map.loc[df_map["tasa_desempleo"].idxmax()]
        st.metric("Mayor Desempleo", f"{max_depto['departamento']}")

    st.markdown("---")

    # Mapa coroplético
    fig = px.choropleth_mapbox(
        gdf_map,
        geojson=gdf_map.geometry.__geo_interface__,
        locations=gdf_map.index,
        color="tasa_desempleo",
        color_continuous_scale="RdYlGn_r",
        range_color=(3, 20),
        hover_name="departamento",
        hover_data={
            "tasa_desempleo": ":.1f%",
            "tasa_ocupacion": ":.1f%",
            "tgp": ":.1f%",
        },
        labels={
            "tasa_desempleo": "Tasa Desempleo",
            "tasa_ocupacion": "Tasa Ocupación",
            "tgp": "TGP",
        },
        mapbox_style="carto-positron",
        center={"lat": 4.0, "lon": -73.0},
        zoom=4.5,
        opacity=0.7,
        height=600,
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="TD (%)",
            thickness=15,
            len=0.6,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de detalle
    st.markdown("### :clipboard: Detalle por Departamento")
    tabla = df_map[["departamento", "tasa_desempleo", "tasa_ocupacion", "tgp", "rank_nacional"]].copy()
    tabla = tabla.sort_values("tasa_desempleo", ascending=False)
    tabla.columns = ["Departamento", "TD (%)", "TO (%)", "TGP (%)", "Ranking"]
    tabla = tabla.reset_index(drop=True)
    tabla.index = tabla.index + 1

    styled = tabla.style.apply(  # pandas 3.x: apply reemplaza applymap
        lambda s: [
            "background-color: rgba(227,26,28,0.15); font-weight: bold" if v <= 5
            else "background-color: rgba(27,158,119,0.15); font-weight: bold" if v >= 28
            else ""
            for v in s
        ],
        subset=["Ranking"],
    )
    styled = styled.format({
        "TD (%)": "{:.1f}",
        "TO (%)": "{:.1f}",
        "TGP (%)": "{:.1f}",
        "Ranking": "{:.0f}",
    })

    st.dataframe(styled, use_container_width=True, height=600)


# ─── Página: EVOLUCIÓN TEMPORAL ──────────────────────────────────────────────
elif view == ":chart_with_upwards_trend: Evolución Temporal":
    st.title(":chart_with_upwards_trend: Evolución Temporal del Desempleo")

    # Filtro de departamentos
    defaults = ["ANTIOQUIA", "CHOCO", "NORTE DE SANTANDER", "VALLE DEL CAUCA"]
    defaults = [d for d in defaults if d in DEPARTAMENTOS]
    # Agregar Bogotá si existe con cualquier variante
    for d in DEPARTAMENTOS:
        if "BOGOTA" in d.upper():
            defaults.insert(0, d)
            break
    deptos_sel = st.multiselect(
        "Selecciona departamentos a comparar",
        DEPARTAMENTOS,
        default=defaults[:5],
    )

    if not deptos_sel:
        st.warning("Selecciona al menos un departamento")
        st.stop()

    # Opciones de visualización
    col1, col2 = st.columns(2)
    with col1:
        mostrar_promedio = st.checkbox("Mostrar promedio nacional", value=True)
    with col2:
        suavizar = st.checkbox("Suavizar (media móvil 3 meses)", value=False)

    # Preparar datos
    df_plot = df[df["departamento"].isin(deptos_sel)].copy()
    df_plot["fecha"] = pd.to_datetime(
        df_plot["año"].astype(str) + "-" + df_plot["mes"].astype(str) + "-01"
    )

    # Suavizado
    if suavizar:
        for d in deptos_sel:
            mask = df_plot["departamento"] == d
            df_plot.loc[mask, "tasa_desempleo"] = (
                df_plot.loc[mask, "tasa_desempleo"].rolling(3, min_periods=1).mean()
            )

    # Gráfico
    fig = go.Figure()

    colors = px.colors.qualitative.Bold + px.colors.qualitative.Vivid

    for i, d in enumerate(deptos_sel):
        d_data = df_plot[df_plot["departamento"] == d].sort_values("fecha")
        fig.add_trace(go.Scatter(
            x=d_data["fecha"],
            y=d_data["tasa_desempleo"],
            name=d,
            mode="lines",
            line=dict(width=2, color=colors[i % len(colors)]),
            hovertemplate="<b>%{text}</b><br>TD: %{y:.1f}%<br>%{x|%b %Y}<extra></extra>",
            text=[d] * len(d_data),
        ))

    # Promedio nacional
    if mostrar_promedio:
        nacional_ts = df.groupby(["año", "mes"])["tasa_desempleo"].mean().reset_index()
        nacional_ts["fecha"] = pd.to_datetime(
            nacional_ts["año"].astype(str) + "-" + nacional_ts["mes"].astype(str) + "-01"
        )
        nacional_ts = nacional_ts.sort_values("fecha")
        fig.add_trace(go.Scatter(
            x=nacional_ts["fecha"],
            y=nacional_ts["tasa_desempleo"],
            name="Promedio Nacional",
            mode="lines",
            line=dict(width=3, color="black", dash="dash"),
            hovertemplate="<b>Nacional</b><br>TD: %{y:.1f}%<br>%{x|%b %Y}<extra></extra>",
        ))

    # Línea de COVID
    fig.add_shape(
        type="line",
        x0=pd.Timestamp("2020-03-01"), x1=pd.Timestamp("2020-03-01"),
        y0=0, y1=1, yref="paper",
        line=dict(width=1, dash="dot", color="gray"),
    )
    fig.add_annotation(
        x=pd.Timestamp("2020-03-01"), y=1, yref="paper",
        text="COVID-19", showarrow=False,
        xshift=10, yshift=-10,
    )

    fig.update_layout(
        title="Tasa de Desempleo por Departamento (2015-2026)",
        xaxis_title="",
        yaxis_title="Tasa de Desempleo (%)",
        hovermode="x unified",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Variación interanual
    st.markdown("### :bar_chart: Variación Interanual (último dato vs año anterior)")

    ultimo_año = df["año"].max()
    ultimo_mes = df[df["año"] == ultimo_año]["mes"].max()

    actual = df[(df["año"] == ultimo_año) & (df["mes"] == ultimo_mes)]
    anterior = df[(df["año"] == ultimo_año - 1) & (df["mes"] == ultimo_mes)]

    comp = actual[["departamento", "tasa_desempleo"]].merge(
        anterior[["departamento", "tasa_desempleo"]],
        on="departamento",
        suffixes=("_actual", "_anterior"),
    )
    comp["variacion"] = comp["tasa_desempleo_actual"] - comp["tasa_desempleo_anterior"]
    comp = comp.sort_values("variacion")

    fig_bar = px.bar(
        comp,
        x="variacion",
        y="departamento",
        orientation="h",
        title=f"Cambio en TD — {MESES_NAMES[ultimo_mes]} {ultimo_año} vs {ultimo_año-1}",
        labels={"variacion": "Variación (pp)", "departamento": ""},
        color="variacion",
        color_continuous_scale=["green", "lightgray", "red"],
        color_continuous_midpoint=0,
        height=700,
    )
    fig_bar.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_bar, use_container_width=True)


# ─── Página: RANKING ─────────────────────────────────────────────────────────
elif view == ":trophy: Ranking Departamentos":
    st.title(":trophy: Ranking de Desempleo por Departamento")

    año_rank = st.selectbox("Año", AÑOS, index=len(AÑOS) - 1, key="rank_year")
    mes_rank = st.selectbox(
        "Mes",
        list(MESES_NAMES.keys()),
        format_func=lambda m: MESES_NAMES[m],
        index=int(df[df["año"] == año_rank]["mes"].max() - 1),
        key="rank_mes",
    )

    df_rank = df[(df["año"] == año_rank) & (df["mes"] == mes_rank)].copy()
    df_rank = df_rank.sort_values("tasa_desempleo", ascending=False)
    df_rank["rank"] = range(1, len(df_rank) + 1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### :small_red_triangle: Mayor Desempleo")
        top5 = df_rank.head(5)
        for _, row in top5.iterrows():
            st.markdown(
                f"**{int(row['rank'])}. {row['departamento']}** — "
                f"TD: {row['tasa_desempleo']:.1f}% | "
                f"TO: {row['tasa_ocupacion']:.1f}% | "
                f"TGP: {row['tgp']:.1f}%"
            )

    with col2:
        st.markdown("### :small_red_triangle_down: Menor Desempleo")
        bottom5 = df_rank.tail(5).sort_values("tasa_desempleo")
        for _, row in bottom5.iterrows():
            st.markdown(
                f"**{int(row['rank'])}. {row['departamento']}** — "
                f"TD: {row['tasa_desempleo']:.1f}% | "
                f"TO: {row['tasa_ocupacion']:.1f}% | "
                f"TGP: {row['tgp']:.1f}%"
            )

    st.markdown("---")

    # Barras horizontales
    fig_rank = px.bar(
        df_rank.sort_values("tasa_desempleo"),
        x="tasa_desempleo",
        y="departamento",
        orientation="h",
        title=f"Ranking Completo — {MESES_NAMES[mes_rank]} {año_rank}",
        labels={"tasa_desempleo": "Tasa de Desempleo (%)", "departamento": ""},
        color="tasa_desempleo",
        color_continuous_scale="RdYlGn_r",
        height=750,
    )
    fig_rank.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_rank, use_container_width=True)


# ─── Página: HEATMAP ESTACIONAL ──────────────────────────────────────────────
elif view == ":calendar: Heatmap Estacional":
    st.title(":calendar: Patrón Estacional del Desempleo")

    depto_heat = st.selectbox(
        "Departamento",
        DEPARTAMENTOS,
        key="heat_depto",
    )

    # Preparar datos para heatmap
    df_heat = df[df["departamento"] == depto_heat].copy()

    # Calcular promedio por mes (todos los años)
    pivot = df_heat.pivot_table(
        values="tasa_desempleo",
        index="año",
        columns="mes",
        aggfunc="mean",
    )
    pivot.columns = [MESES_NAMES[m][:3] for m in pivot.columns]

    fig_heat = px.imshow(
        pivot,
        labels=dict(x="Mes", y="Año", color="TD (%)"),
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        title=f"Desempleo Mensual — {depto_heat}",
        height=450,
    )
    fig_heat.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Promedio por mes (estacionalidad)
    st.markdown("### :chart_with_upwards_trend: Estacionalidad Mensual")

    monthly_avg = df_heat.groupby("mes")["tasa_desempleo"].agg(["mean", "std"]).reset_index()
    monthly_avg["mes_name"] = monthly_avg["mes"].map(MESES_NAMES)

    fig_season = go.Figure()
    fig_season.add_trace(go.Scatter(
        x=monthly_avg["mes_name"],
        y=monthly_avg["mean"],
        mode="lines+markers",
        name="Promedio",
        line=dict(width=3, color="#1B9E77"),
        marker=dict(size=10),
    ))
    fig_season.add_trace(go.Scatter(
        x=monthly_avg["mes_name"].tolist() + monthly_avg["mes_name"].tolist()[::-1],
        y=(monthly_avg["mean"] + monthly_avg["std"]).tolist() + (monthly_avg["mean"] - monthly_avg["std"]).tolist()[::-1],
        fill="toself",
        fillcolor="rgba(27,158,119,0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="±1 desv. std.",
    ))
    fig_season.update_layout(
        title=f"Estacionalidad — {depto_heat}",
        xaxis_title="",
        yaxis_title="Tasa de Desempleo (%)",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_season, use_container_width=True)


# ─── Página: METODOLOGÍA ─────────────────────────────────────────────────────
elif view == ":books: Metodología":
    st.title(":books: Metodología y Fuentes")

    st.markdown("""
    ## Sobre este Dashboard

    Este dashboard interactivo visualiza la evolución de la tasa de desempleo
    en los **33 departamentos de Colombia** desde 2015 hasta 2026.

    ### Fuentes de Datos

    | Fuente | Descripción |
    |--------|------------|
    | **DANE - GEIH** | Gran Encuesta Integrada de Hogares. Principal fuente de indicadores del mercado laboral colombiano. |
    | **DANE - Geoportal** | Shapefiles oficiales de la división político-administrativa (DIVIPOLA / MGN). |
    | **datos.gov.co** | Plataforma de datos abiertos del gobierno colombiano (API Socrata). |

    ### Indicadores

    - **Tasa de Desempleo (TD)**: Porcentaje de la fuerza de trabajo que está desocupada.
    - **Tasa Global de Participación (TGP)**: Porcentaje de la población en edad de trabajar que participa en el mercado laboral.
    - **Tasa de Ocupación (TO)**: Porcentaje de la población en edad de trabajar que está ocupada.

    ### Nota sobre los datos

    Los datos presentados en esta versión son **sintéticos calibrados** basados en
    información pública del DANE. Reflejan patrones y tendencias realistas, pero
    **no deben usarse para análisis oficiales o toma de decisiones**.

    Para datos oficiales, consulta:
    - [DANE - Mercado Laboral](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral)
    - [DANE - Microdatos ANDA](https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos)

    ### Tecnologías

    - **Streamlit**: Framework para dashboards interactivos en Python
    - **Plotly**: Visualizaciones interactivas (mapas coropléticos, series temporales)
    - **GeoPandas**: Manejo de datos geoespaciales
    - **Pandas**: Procesamiento y análisis de datos
    - **Pandera**: Validación de esquemas de datos

    ### Limitaciones

    - Los datos departamentales mensuales no se publican en los anexos Excel estándar del DANE.
    - El nivel municipal requiere procesamiento de microdatos con factores de expansión.
    - La calidad estadística disminuye para departamentos con poca población (Amazonas, Vaupés, etc.).
    """)

    st.info(
        "Este proyecto es de código abierto. "
        "Contribuciones son bienvenidas en [GitHub](https://github.com/tuusuario/colombia-unemployment-dashboard)."
    )


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""<div class="footer">
    Dashboard de Desempleo en Colombia |
    Datos: DANE GEIH |
    Saúl Cuellar & Santiago Giraldo |
    Desarrollado con Streamlit + Plotly + GeoPandas
</div>""", unsafe_allow_html=True)