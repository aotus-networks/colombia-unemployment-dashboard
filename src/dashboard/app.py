"""
Dashboard Interactivo de Desempleo en Colombia
===============================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Desempleo en Colombia | Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .footer {
        text-align: center; padding: 1.5rem 0; color: #6c757d;
        font-size: 0.8rem; border-top: 1px solid #dee2e6; margin-top: 2rem;
    }
    .drill-header {
        background: linear-gradient(135deg, #1B9E77 0%, #0d6e52 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Coordenadas centrales por departamento para zoom
DEPTO_COORDS = {
    "AMAZONAS": {"lat": -1.5, "lon": -71.5, "zoom": 5.0},
    "ANTIOQUIA": {"lat": 7.0, "lon": -75.5, "zoom": 6.0},
    "ARAUCA": {"lat": 6.5, "lon": -70.7, "zoom": 6.0},
    "ATLANTICO": {"lat": 10.7, "lon": -74.9, "zoom": 6.5},
    "BOLIVAR": {"lat": 8.5, "lon": -74.5, "zoom": 6.0},
    "BOYACA": {"lat": 5.5, "lon": -72.7, "zoom": 6.0},
    "CALDAS": {"lat": 5.3, "lon": -75.3, "zoom": 6.5},
    "CAQUETA": {"lat": 0.9, "lon": -74.0, "zoom": 5.5},
    "CASANARE": {"lat": 5.5, "lon": -71.5, "zoom": 6.0},
    "CAUCA": {"lat": 2.5, "lon": -76.5, "zoom": 6.0},
    "CESAR": {"lat": 9.5, "lon": -73.5, "zoom": 6.0},
    "CHOCO": {"lat": 5.5, "lon": -76.8, "zoom": 6.0},
    "CORDOBA": {"lat": 8.3, "lon": -75.7, "zoom": 6.0},
    "CUNDINAMARCA": {"lat": 4.8, "lon": -74.3, "zoom": 5.8},
    "GUAINIA": {"lat": 2.5, "lon": -68.5, "zoom": 5.5},
    "GUAVIARE": {"lat": 2.0, "lon": -72.5, "zoom": 5.5},
    "HUILA": {"lat": 2.5, "lon": -75.5, "zoom": 6.0},
    "LA GUAJIRA": {"lat": 11.5, "lon": -72.5, "zoom": 6.0},
    "MAGDALENA": {"lat": 10.0, "lon": -74.2, "zoom": 6.0},
    "META": {"lat": 3.5, "lon": -73.0, "zoom": 5.5},
    "NARINO": {"lat": 1.5, "lon": -77.5, "zoom": 6.0},
    "NORTE DE SANTANDER": {"lat": 7.9, "lon": -72.7, "zoom": 6.0},
    "PUTUMAYO": {"lat": 0.5, "lon": -76.0, "zoom": 6.0},
    "QUINDIO": {"lat": 4.5, "lon": -75.7, "zoom": 7.0},
    "RISARALDA": {"lat": 5.2, "lon": -76.0, "zoom": 7.0},
    "SAN ANDRES": {"lat": 12.5, "lon": -81.7, "zoom": 7.0},
    "SANTANDER": {"lat": 6.7, "lon": -73.5, "zoom": 6.0},
    "SUCRE": {"lat": 9.0, "lon": -75.0, "zoom": 6.5},
    "TOLIMA": {"lat": 3.8, "lon": -75.2, "zoom": 6.0},
    "VALLE DEL CAUCA": {"lat": 3.8, "lon": -76.5, "zoom": 6.5},
    "VAUPES": {"lat": 0.5, "lon": -70.5, "zoom": 5.5},
    "VICHADA": {"lat": 4.5, "lon": -69.5, "zoom": 5.5},
    "BOGOTA D.C.": {"lat": 4.7, "lon": -74.1, "zoom": 5.8},

}

@st.cache_data(ttl=3600, show_spinner="Cargando datos...")
def load_data():
    from src.etl.pipeline import run_pipeline
    from src.utils.paths import DEPARTMENT_PARQUET

    if DEPARTMENT_PARQUET.exists():
        gdf = gpd.read_parquet(DEPARTMENT_PARQUET)
        st.sidebar.success(f"{len(gdf):,} registros cargados")
        return gdf

    with st.spinner("Generando datos (primera ejecución)..."):
        gdf = run_pipeline(start_year=2015, end_year=2026)
    st.sidebar.success(f"{len(gdf):,} registros cargados")
    return gdf


try:
    gdf = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

df = pd.DataFrame(gdf.drop(columns=["geometry"]))

DEPARTAMENTOS = sorted(df["departamento"].unique())
AÑOS = sorted(df["año"].unique())
MESES_NAMES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Desempleo Colombia")
    st.markdown("---")

    st.markdown("### Vista")
    view = st.radio(
        "Selecciona una vista:",
        [
            "Mapa Nacional",
            "Evolución Temporal",
            "Ranking Departamentos",
            "Heatmap Estacional",
            "Metodología",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Filtros")

    if view != "Evolución Temporal":
        año_seleccionado = st.selectbox("Año", AÑOS, index=len(AÑOS) - 1)

    if view not in ["Ranking Departamentos"]:
        depto_seleccionado = st.selectbox(
            "Departamento",
            ["Todos"] + DEPARTAMENTOS,
            index=0,
        )

    st.markdown("---")
    st.caption("Datos: DANE - GEIH")
    st.caption("[GitHub](https://github.com/aotus-networks/colombia-unemployment-dashboard)")
    st.caption("2026")


# ─── Página: MAPA NACIONAL con Drill-down ────────────────────────────────────
if view == "Mapa Nacional":
    st.title("Mapa de Desempleo en Colombia")
    st.markdown(f"### Tasa de Desempleo por Departamento — {año_seleccionado}")

    df_year = df[df["año"] == año_seleccionado]
    ultimo_mes = df_year["mes"].max()
    df_map = df_year[df_year["mes"] == ultimo_mes]

    gdf_map = gdf[gdf["año"] == año_seleccionado]
    gdf_map = gdf_map[gdf_map["mes"] == ultimo_mes]
    gdf_map = gdf_map.reset_index(drop=True)

    # KPIs nacionales
    nacional = df_map["tasa_desempleo"].mean()
    df_prev = df[(df["año"] == año_seleccionado - 1) & (df["mes"] == ultimo_mes)]
    nacional_prev = df_prev["tasa_desempleo"].mean() if len(df_prev) > 0 else nacional

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        delta = nacional - nacional_prev
        st.metric("Tasa de Desempleo Nacional", f"{nacional:.1f}%", delta=f"{delta:+.1f} pp")
    with col2:
        st.metric("Tasa Global de Participación", f"{df_map['tgp'].mean():.1f}%")
    with col3:
        st.metric("Tasa de Ocupación", f"{df_map['tasa_ocupacion'].mean():.1f}%")
    with col4:
        max_depto = df_map.loc[df_map["tasa_desempleo"].idxmax()]
        st.metric("Mayor Desempleo", f"{max_depto['departamento']}")

    st.markdown("---")

    # Selector de departamento para drill-down
    depto_click = st.selectbox(
        "Selecciona un departamento para ver el detalle:",
        ["— Ver mapa nacional —"] + list(df_map.sort_values("tasa_desempleo", ascending=False)["departamento"]),
        key="drill_selector"
    )

    # Determinar centro y zoom del mapa
    if depto_click != "— Ver mapa nacional —" and depto_click in DEPTO_COORDS:
        coords = DEPTO_COORDS[depto_click]
        map_center = {"lat": coords["lat"], "lon": coords["lon"]}
        map_zoom = coords["zoom"]
        gdf_plot = gdf_map  # Mostrar todos pero centrado en el depto
    else:
        map_center = {"lat": 4.0, "lon": -74.0}
        map_zoom = 4.8
        gdf_plot = gdf_map

    col_map, col_drill = st.columns([2, 1])

    with col_map:
        fig = px.choropleth_mapbox(
            gdf_plot,
            geojson=gdf_plot.geometry.__geo_interface__,
            locations=gdf_plot.index,
            custom_data=["departamento"],
            color="tasa_desempleo",
            color_continuous_scale="RdYlGn_r",
            range_color=(3, 20),
            hover_name="departamento",
            hover_data={
                "tasa_desempleo": ":.1f",
                "tasa_ocupacion": ":.1f",
                "tgp": ":.1f",
            },
            labels={
                "tasa_desempleo": "TD (%)",
                "tasa_ocupacion": "TO (%)",
                "tgp": "TGP (%)",
            },
            mapbox_style="carto-positron",
            center=map_center,
            zoom=map_zoom,
            opacity=0.75,
            height=570,
        )
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(title="TD (%)", thickness=15, len=0.6),
        )
        fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>TD: %{customdata[0]}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, key="mapa_principal")

    with col_drill:
        if depto_click != "— Ver mapa nacional —":
            row = df_map[df_map["departamento"] == depto_click].iloc[0]

            st.markdown(f"""
            <div class="drill-header">
                <b style="font-size:1.1rem">{depto_click}</b><br>
                {MESES_NAMES[int(ultimo_mes)]} {año_seleccionado}
            </div>
            """, unsafe_allow_html=True)

            rank = int(row["rank_nacional"])
            total = len(df_map)
            st.metric("Tasa de Desempleo", f"{row['tasa_desempleo']:.1f}%")
            st.metric("Tasa de Ocupación", f"{row['tasa_ocupacion']:.1f}%")
            st.metric("TGP", f"{row['tgp']:.1f}%")
            st.metric("Ranking Nacional", f"{rank} de {total}")

            # Serie temporal del departamento
            df_depto_ts = df[df["departamento"] == depto_click].copy()
            df_depto_ts["fecha"] = pd.to_datetime(
                df_depto_ts["año"].astype(str) + "-" + df_depto_ts["mes"].astype(str) + "-01"
            )
            df_depto_ts = df_depto_ts.sort_values("fecha")

            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(
                x=df_depto_ts["fecha"],
                y=df_depto_ts["tasa_desempleo"],
                mode="lines",
                name=depto_click,
                line=dict(color="#1B9E77", width=2),
                fill="tozeroy",
                fillcolor="rgba(27,158,119,0.1)",
            ))

            nac_ts = df.groupby(["año", "mes"])["tasa_desempleo"].mean().reset_index()
            nac_ts["fecha"] = pd.to_datetime(
                nac_ts["año"].astype(str) + "-" + nac_ts["mes"].astype(str) + "-01"
            )
            fig_ts.add_trace(go.Scatter(
                x=nac_ts["fecha"],
                y=nac_ts["tasa_desempleo"],
                mode="lines",
                name="Promedio nacional",
                line=dict(color="gray", width=1.5, dash="dash"),
            ))

            fig_ts.add_shape(
                type="line",
                x0=pd.Timestamp("2020-03-01"), x1=pd.Timestamp("2020-03-01"),
                y0=0, y1=1, yref="paper",
                line=dict(width=1, dash="dot", color="red"),
            )

            fig_ts.update_layout(
                title=f"Evolución TD — {depto_click}",
                xaxis_title="",
                yaxis_title="TD (%)",
                height=320,
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("Selecciona un departamento para ver su detalle y hacer zoom en el mapa.")

    # Tabla de detalle
    st.markdown("### Detalle por Departamento")
    tabla = df_map[["departamento", "tasa_desempleo", "tasa_ocupacion", "tgp", "rank_nacional"]].copy()
    tabla = tabla.sort_values("tasa_desempleo", ascending=False)
    tabla.columns = ["Departamento", "TD (%)", "TO (%)", "TGP (%)", "Ranking"]
    tabla = tabla.reset_index(drop=True)
    tabla.index = tabla.index + 1

    styled = tabla.style.apply(
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
    st.dataframe(styled, use_container_width=True, height=500)


# ─── Página: EVOLUCIÓN TEMPORAL ──────────────────────────────────────────────
elif view == "Evolución Temporal":
    st.title("Evolución Temporal del Desempleo")

    defaults = ["ANTIOQUIA", "CHOCO", "NORTE DE SANTANDER", "VALLE DEL CAUCA"]
    defaults = [d for d in defaults if d in DEPARTAMENTOS]
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

    col1, col2 = st.columns(2)
    with col1:
        mostrar_promedio = st.checkbox("Mostrar promedio nacional", value=True)
    with col2:
        suavizar = st.checkbox("Suavizar (media móvil 3 meses)", value=False)

    df_plot = df[df["departamento"].isin(deptos_sel)].copy()
    df_plot["fecha"] = pd.to_datetime(
        df_plot["año"].astype(str) + "-" + df_plot["mes"].astype(str) + "-01"
    )

    if suavizar:
        for d in deptos_sel:
            mask = df_plot["departamento"] == d
            df_plot.loc[mask, "tasa_desempleo"] = (
                df_plot.loc[mask, "tasa_desempleo"].rolling(3, min_periods=1).mean()
            )

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

    fig.add_shape(
        type="line",
        x0=pd.Timestamp("2020-03-01"), x1=pd.Timestamp("2020-03-01"),
        y0=0, y1=1, yref="paper",
        line=dict(width=1, dash="dot", color="gray"),
    )
    fig.add_annotation(
        x=pd.Timestamp("2020-03-01"), y=1, yref="paper",
        text="COVID-19", showarrow=False, xshift=10, yshift=-10,
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

    st.markdown("### Variación Interanual (último dato vs año anterior)")

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
elif view == "Ranking Departamentos":
    st.title("Ranking de Desempleo por Departamento")

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
        st.markdown("### Mayor Desempleo")
        for _, row in df_rank.head(5).iterrows():
            st.markdown(
                f"**{int(row['rank'])}. {row['departamento']}** — "
                f"TD: {row['tasa_desempleo']:.1f}% | "
                f"TO: {row['tasa_ocupacion']:.1f}% | "
                f"TGP: {row['tgp']:.1f}%"
            )

    with col2:
        st.markdown("### Menor Desempleo")
        for _, row in df_rank.tail(5).sort_values("tasa_desempleo").iterrows():
            st.markdown(
                f"**{int(row['rank'])}. {row['departamento']}** — "
                f"TD: {row['tasa_desempleo']:.1f}% | "
                f"TO: {row['tasa_ocupacion']:.1f}% | "
                f"TGP: {row['tgp']:.1f}%"
            )

    st.markdown("---")

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
elif view == "Heatmap Estacional":
    st.title("Patrón Estacional del Desempleo")

    depto_heat = st.selectbox("Departamento", DEPARTAMENTOS, key="heat_depto")

    df_heat = df[df["departamento"] == depto_heat].copy()

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

    st.markdown("### Estacionalidad Mensual")

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
elif view == "Metodología":
    st.title("Metodología y Fuentes")

    st.markdown("""
    ## Sobre este Dashboard

    Este dashboard visualiza la evolución de la tasa de desempleo
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

    Los datos presentados son sintéticos basados en información pública del DANE.
    Reflejan patrones y tendencias realistas, pero **no deben usarse para análisis
    oficiales o toma de decisiones**.

    Para datos oficiales, consulta:
    - [DANE - Mercado Laboral](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral)
    - [DANE - Microdatos ANDA](https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos)

    ### Tecnologías

    - **Streamlit**: Framework para dashboards interactivos en Python
    - **Plotly**: Visualizaciones interactivas
    - **GeoPandas**: Manejo de datos geoespaciales
    - **Pandas**: Procesamiento y análisis de datos

    ### Limitaciones

    - Los datos departamentales mensuales no se publican en los anexos Excel estándar del DANE.
    - El nivel municipal requiere procesamiento de microdatos con factores de expansión.
    - La calidad estadística disminuye para departamentos con poca población.
    """)

    st.info(
        "Proyecto de código abierto. "
        "Contribuciones bienvenidas en [GitHub](https://github.com/aotus-networks/colombia-unemployment-dashboard)."
    )


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""<div class="footer">
    Dashboard de Desempleo en Colombia |
    Datos: DANE GEIH |
    Saul Cuellar & Santiago Giraldo |
    Desarrollado con Streamlit + Plotly + GeoPandas
</div>""", unsafe_allow_html=True)