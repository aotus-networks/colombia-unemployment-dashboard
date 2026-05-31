# 🗺️ Arquitectura del Proyecto: Mapa de Desempleo en Colombia

> **Dashboard interactivo + Notebook analítico | Streamlit + GeoPandas + Plotly**
> 
> Nivel: Avanzado | Output: Portafolio GitHub + LinkedIn

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Investigación de Fuentes de Datos](#investigación-de-fuentes-de-datos)
3. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
4. [Pipeline de Datos (ETL)](#pipeline-de-datos-etl)
5. [Stack Tecnológico](#stack-tecnológico)
6. [Diseño del Dashboard](#diseño-del-dashboard)
7. [Riesgos y Limitaciones](#riesgos-y-limitaciones)
8. [Roadmap de Implementación](#roadmap-de-implementación)
9. [Despliegue](#despliegue)

---

## Visión General

### Objetivo
Dashboard interactivo que visualiza la evolución de la tasa de desempleo en Colombia a nivel **departamental** (y donde sea posible, **municipal**) usando mapas de coropletas con animación temporal.

### Alcance

| Nivel | Datos disponibles | Viabilidad |
|-------|------------------|------------|
| Nacional | ✅ Total país | 100% |
| Departamental (33 deptos) | ✅ GEIH mensual 2001-2026 | 100% |
| 23 Ciudades principales + AM | ✅ GEIH mensual | 100% |
| Municipal (~1,122 municipios) | ⚠️ Solo vía microdatos ANDA | Parcial (~200 municipios con muestra suficiente) |

### Estrategia de 2 niveles
1. **Departamental** (principal): Confiable, oficial, cubrimiento total
2. **Municipal** (secundario): Donde los microdatos lo permitan, con intervalo de confianza y nota metodológica

---

## Investigación de Fuentes de Datos

### 🔴 Fuente 1: DANE - GEIH Anexos (Excel mensual)

**Descripción**: Archivos Excel publicados mensualmente con indicadores del mercado laboral por departamento, ciudad, sexo, edad, rama de actividad.

**URL Pattern**: 
```
https://www.dane.gov.co/files/operaciones/GEIH/anex-GEIH-{mes_abrev}{año}.xlsx
```

**Ejemplo**: `anex-GEIH-abr2026.xlsx`

**Hojas relevantes**:
- `TD x Depto`: Tasa de desempleo por departamento
- `TGP x Depto`: Tasa global de participación por departamento  
- `TO x Depto`: Tasa de ocupación por departamento
- `TD x Ciudad`: Tasa de desempleo por 23 ciudades
- `TD x Sexo`: Desagregación por género
- `TD x Edad`: Desagregación por rango etario

**Cobertura temporal**: 
- Marco 2005: 2001-2015
- Marco 2018: 2015-presente
- Serie empalmada oficial: 2001-2021 (archivo único)

**Formato**: `.xlsx` con múltiples hojas, requiere parseo estructurado.

### 🔴 Fuente 2: DANE - Serie Histórica Empalmada (2001-2021)

**URL**: 
```
https://www.dane.gov.co/files/investigaciones/boletines/ech/nuevo-enfoque-conceptual-metodologico-2018/anexo-mercado-laboral-segun-proyecciones-CNPV2018.xlsx
```

**Descripción**: Archivo único con TODA la serie histórica empalmada (marco 2005 + marco 2018) con factores de expansión calibrados al CNPV 2018.

**Ventaja**: No hay que descargar mes a mes. Serie oficial unificada.

### 🟡 Fuente 3: DANE - Microdatos ANDA

**URL**: https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos

**Descripción**: Microdatos anonimizados de la GEIH a nivel de individuo. Permite agregaciones personalizadas (municipio, cruces específicos).

**Formato**: CSV/SPSS/Stata por mes/año.

**Limitaciones**:
- Requiere registro y aceptación de términos
- Procesamiento estadístico complejo (factores de expansión, CV)
- Municipios pequeños tienen muestra insuficiente
- Se necesita conocimiento de diseño muestral

### 🟢 Fuente 4: DANE Geoportal - Shapefiles

**URL**: https://geoportal.dane.gov.co/

**Descripción**: Archivos geoespaciales oficiales de Colombia.

**Capas disponibles**:
- **MGN (Marco Geoestadístico Nacional)**: Manzanas, sectores, municipios
- **DIVIPOLA**: División político-administrativa vigente
- **Departamentos**: 33 polígonos
- **Municipios**: ~1,122 polígonos

**Formato**: GeoJSON, Shapefile, GPKG

**Descarga**: 
- https://geoportal.dane.gov.co/geovisores/territorio/consulta-divipola-division-politico-administrativa-de-colombia/
- API: https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/

**Nota**: Usar DIVIPOLA más reciente (códigos DIVIPOLA para join con datos).

### 🟡 Fuente 5: datos.gov.co (Socrata API)

**URL**: https://www.datos.gov.co/

**API**: SODA API (Socrata). Endpoint base: `https://www.datos.gov.co/resource/{dataset_id}.json`

**Datasets relevantes**: Buscar "desempleo", "GEIH", "mercado laboral".

**Ventajas**: API REST, paginación, filtrado, formatos JSON/CSV.

**Desventajas**: No siempre actualizado, datasets pueden ser parciales.

---

## Arquitectura del Proyecto

```
proyecto desempleo/
│
├── README.md                    # Documentación principal con badges, gifs, screenshots
├── ARCHITECTURE.md              # Este documento (plan maestro)
├── LICENSE                      # MIT
├── .gitignore                   
├── .env.template                # Variables de entorno (sin secrets)
├── Makefile                     # Automatización (make install, make run, make deploy)
├── docker-compose.yml           # Orquestación de servicios
├── Dockerfile                   # Imagen para despliegue
│
├── pyproject.toml               # Dependencias y metadata del proyecto
├── requirements.txt             # Dependencias pineadas
├── requirements-dev.txt         # Dependencias de desarrollo
│
├── notebooks/                   # Análisis exploratorio
│   ├── 00_data_exploration.ipynb
│   ├── 01_etl_pipeline.ipynb
│   ├── 02_spatial_analysis.ipynb
│   └── 03_time_series_analysis.ipynb
│
├── data/                        # Datos (gitignored excepto samples)
│   ├── raw/                     # Datos crudos descargados
│   │   ├── geih/                # Excel files del DANE
│   │   └── microdata/           # CSVs de ANDA
│   ├── processed/               # Datos procesados (Parquet)
│   │   ├── unemployment_department.parquet
│   │   ├── unemployment_city.parquet
│   │   └── unemployment_municipality.parquet
│   └── geo/                     # Archivos geoespaciales
│       ├── departamentos.geojson
│       ├── municipios.geojson
│       └── colombia_ simplified.geojson  # Simplificado para web
│
├── src/                         # Código fuente principal
│   ├── __init__.py
│   │
│   ├── data/                    # Capa de datos
│   │   ├── __init__.py
│   │   ├── downloader.py        # Descarga de archivos DANE (con caché y retry)
│   │   ├── dane_client.py       # Cliente HTTP para el portal DANE
│   │   ├── socrata_client.py    # Cliente API Socrata (datos.gov.co)
│   │   └── geo_downloader.py    # Descarga de shapefiles del geoportal
│   │
│   ├── etl/                     # Extracción, Transformación y Carga
│   │   ├── __init__.py
│   │   ├── extract_geih.py      # Parser de Excel GEIH (hojas múltiples)
│   │   ├── extract_microdata.py # Procesamiento de microdatos ANDA
│   │   ├── transform.py         # Limpieza, normalización, joins
│   │   ├── spatial_join.py     # Join de datos con geometrías
│   │   ├── validate.py          # Validación de datos (pandera / great_expectations)
│   │   └── pipeline.py          # Orquestador del pipeline completo
│   │
│   ├── analysis/                # Análisis y métricas
│   │   ├── __init__.py
│   │   ├── metrics.py           # Cálculo de indicadores derivados
│   │   ├── seasonal.py          # Desestacionalización (X-13ARIMA-SEATS)
│   │   ├── clustering.py        # Clustering espacial de desempleo
│   │   └── ranking.py           # Rankings departamentales/municipales
│   │
│   ├── dashboard/               # Aplicación Streamlit
│   │   ├── __init__.py
│   │   ├── app.py               # Punto de entrada Principal
│   │   ├── config.py            # Configuración del dashboard (temas, colores)
│   │   │
│   │   ├── pages/               # Páginas del dashboard (multipage)
│   │   │   ├── __init__.py
│   │   │   ├── 01_mapa_nacional.py       # Mapa coroplético departamental
│   │   │   ├── 02_evolucion_temporal.py  # Series de tiempo interactivas
│   │   │   ├── 03_comparativa_deptos.py  # Comparación entre departamentos
│   │   │   ├── 04_ciudades.py            # Vista de 23 ciudades principales
│   │   │   ├── 05_municipios.py          # Mapa municipal (donde hay datos)
│   │   │   ├── 06_brechas_genero.py      # Desempleo por género
│   │   │   ├── 07_ranking.py             # Rankings interactivos
│   │   │   └── 08_metodologia.py         # Nota metodológica y fuentes
│   │   │
│   │   ├── components/          # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── choropleth_map.py # Mapa coroplético base (Plotly + GeoPandas)
│   │   │   ├── time_slider.py    # Slider temporal animado
│   │   │   ├── kpi_cards.py      # Tarjetas de indicadores clave
│   │   │   ├── heatmap.py        # Heatmap calendario
│   │   │   ├── sankey.py         # Diagrama de flujo laboral
│   │   │   └── sparklines.py     # Mini gráficos de tendencia
│   │   │
│   │   ├── utils/               # Utilidades del dashboard
│   │   │   ├── __init__.py
│   │   │   ├── theme.py          # Tema CSS / estilos
│   │   │   ├── cache.py          # Caché Streamlit (@st.cache_data)
│   │   │   ├── i18n.py           # Internacionalización (ES/EN)
│   │   │   └── export.py         # Exportar datos/gráficos
│   │   │
│   │   └── assets/              # Assets estáticos del dashboard
│   │       ├── style.css
│   │       └── logo.png
│   │
│   └── utils/                   # Utilidades generales
│       ├── __init__.py
│       ├── logging_config.py    # Configuración de logging
│       ├── paths.py             # Resolución de rutas del proyecto
│       └── decorators.py        # Decoradores (timing, retry, etc.)
│
├── tests/                       # Tests unitarios y de integración
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartidos
│   ├── test_etl/                
│   ├── test_analysis/
│   └── test_dashboard/
│
├── scripts/                     # Scripts de automatización
│   ├── download_data.py         # Descargar todos los datos
│   ├── run_pipeline.py          # Ejecutar pipeline ETL completo
│   ├── update_data.py           # Actualización incremental
│   └── deploy.py                # Script de despliegue
│
└── assets/                      # Recursos generales
    ├── img/
    │   └── screenshots/         # Screenshots para README
    └── data_dictionary.md       # Diccionario de datos
```

---

## Pipeline de Datos (ETL)

```
┌──────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE DATOS                             │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐       │
│  │ DANE     │    │              │    │                  │       │
│  │ Anexos   │───▶│              │    │  unemployment_   │       │
│  │ (Excel)  │    │   extract_   │    │  department.     │       │
│  └──────────┘    │   geih.py    │    │  parquet         │       │
│                  │              │    │                  │       │
│  ┌──────────┐    │              │    │  unemployment_   │       │
│  │ DANE     │    │              │───▶│  city.parquet    │       │
│  │ Histórico│───▶│              │    │                  │       │
│  │ (Excel)  │    │              │    │  unemployment_   │       │
│  └──────────┘    └──────┬───────┘    │  municipality.   │       │
│                         │            │  parquet         │       │
│  ┌──────────┐          │            └────────┬─────────┘       │
│  │ ANDA     │    ┌──────▼───────┐            │                  │
│  │ Microdatos│──▶│              │            │                  │
│  │ (CSV)    │    │  transform   │────────────┘                  │
│  └──────────┘    │  .py         │                               │
│                  │              │                               │
│  ┌──────────┐    │              │    ┌──────────────────┐       │
│  │ Geoportal│───▶│              │───▶│ departamentos.    │       │
│  │ GeoJSON  │    │              │    │ geojson (simplif) │       │
│  └──────────┘    └──────────────┘    └──────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                 spatial_join.py                      │       │
│  │  datos_departamento.parquet + departamentos.geojson  │       │
│  │  = datos con geometría listos para visualización      │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                   validate.py                        │       │
│  │  Validación de: tipos, rangos, completitud, CV       │       │
│  │  Framework: Pandera (esquemas declarativos)          │       │
│  └──────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

### Estrategia de datos

1. **Carga inicial**: Descargar histórico completo (2001-2026) ~240 archivos Excel
2. **Actualización**: Script `update_data.py` corre mensualmente (cron/GitHub Actions)
3. **Caché**: Los datos procesados se almacenan en Parquet (compresión zstd) en `data/processed/`
4. **Tamaño estimado**: ~50MB procesados (excluyendo microdatos)

---

## Stack Tecnológico

### Core

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| **Dashboard** | Streamlit 1.31+ | Rápido, Python nativo, deploy fácil, multipage nativo |
| **Mapas** | Plotly + GeoPandas | Interactividad nativa, tooltips, zoom, animación temporal |
| **Datos** | Pandas 2.x + Polars | Pandas para ETL, Polars para queries rápidas en dashboard |
| **Geo** | GeoPandas + Shapely + TopoJSON | Simplificación de geometrías para web |
| **Validación** | Pandera | Esquemas declarativos, validación en pipeline |
| **Estadística** | Statsmodels + Scipy | Desestacionalización, correlación espacial |
| **Caché** | Streamlit cache + DiskCache | `@st.cache_data` para datos, `@st.cache_resource` para modelos |

### Visualización

| Componente | Librería | Uso |
|-----------|---------|-----|
| Mapas coropléticos | Plotly Express `choropleth` | Mapa departamental interactivo |
| Series temporales | Plotly Graph Objects | Líneas de tendencia con range slider |
| KPIs | Streamlit `st.metric()` | Tarjetas de indicadores con delta |
| Heatmaps | Plotly `imshow` / `density_heatmap` | Calendario de desempleo |
| Rankings | Streamlit `st.dataframe` con estilo condicional | Tablas con barras de progreso |
| Animación | Plotly `animation_frame` | Evolución temporal en mapa |

### Infraestructura

| Componente | Opción 1 (recomendada) | Opción 2 |
|-----------|----------------------|----------|
| **Hosting** | Streamlit Community Cloud (gratis) | Hugging Face Spaces |
| **CI/CD** | GitHub Actions | - |
| **Datos grandes** | GitHub LFS (>100MB) o Zenodo | S3 público |
| **Dominio** | Streamlit Cloud subdomain | Custom domain |

---

## Diseño del Dashboard

### Estructura de páginas

```
📊 Dashboard Principal
├── 🗺️ Mapa Nacional        ← Página principal (landing)
├── 📈 Evolución Temporal    ← Series de tiempo por departamento
├── 🏙️ Ciudades Principales  ← Las 23 ciudades + AM
├── 🏘️ Municipios            ← Nivel municipal (donde aplica)
├── 👥 Brechas de Género     ← Desempleo masculino vs femenino
├── 🏆 Ranking               ← Top/bottom departamentos
└── 📋 Metodología           ← Fuentes, definiciones, limitaciones
```

### Mapa Nacional (Página Landing)

```
┌─────────────────────────────────────────────────────────┐
│  🗺️  Mapa de Desempleo en Colombia                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │          MAPA COROPLÉTICO INTERACTIVO           │   │
│  │          (Plotly Choropleth)                    │   │
│  │          - Hover: depto, tasa, variación        │   │
│  │          - Click: drill-down a detalle          │   │
│  │          - Zoom/Pan nativo                      │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [◀◀ 2015] ──────●────── [2026 ▶▶]    (Slider año)     │
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │ 8.8% │  │ 64.7%│  │ 59.1%│  │ -0.3 │               │
│  │  TD  │  │ TGP  │  │  TO  │  │ Δ TD │               │
│  └──────┘  └──────┘  └──────┘  └──────┘               │
│                                                         │
│  📊 Top 5 departamentos con mayor desempleo             │
│  📉 Top 5 con menor desempleo                          │
└─────────────────────────────────────────────────────────┘
```

### Componentes innovadores

1. **Animación temporal**: Slider que recorre años con transición suave en el mapa
2. **Drill-down**: Click en departamento → gráfico de serie temporal + composición por ciudad
3. **Comparativa side-by-side**: Seleccionar 2 períodos y ver mapa de diferencias (Δ TD)
4. **Heatmap calendario**: Visualizar patrón estacional del desempleo
5. **Exportación**: Descargar gráficos como PNG/HTML, datos como CSV
6. **Compartir**: URL con estado (año, departamento seleccionado) vía query params

### Paleta de colores

```
Tasa baja  → Verde    (#1B9E77)
Tasa media → Amarillo (#FDBF6F)  
Tasa alta  → Rojo     (#E31A1C)
```

Usar escala divergente para Δ (cambios): Azul (mejora) ↔ Rojo (empeora).

---

## Riesgos y Limitaciones

### 🔴 Riesgos Críticos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| **Cambio de URL del DANE** | Pipeline roto | Monitoreo con GitHub Actions + alerta |
| **Cambio de estructura Excel** | Parser falla | Tests de validación con pandera; versión mínima viable con CSV manual |
| **Microdatos requieren registro** | Sin datos municipales | Estrategia 2 niveles: departamental primero, municipal incremental |
| **Tamaño de geometrías** | Dashboard lento | Simplificación TopoJSON (tolerancia 0.01°) |

### 🟡 Riesgos Moderados

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| **Calidad estadística municipal** | Datos no confiables | Mostrar CV e intervalo de confianza; filtrar CV > 15% |
| **Empalme de series** | Ruptura en 2015/2018 | Documentar y marcar en gráficos; usar serie oficial empalmada |
| **Streamlit Cloud límites** | 1GB RAM, sleep after inactivity | Optimizar caché; considerar Hugging Face Spaces o auto-ping |
| **Actualización mensual** | Datos desactualizados | GitHub Action programada (día 5 de cada mes) |

### ⚠️ Limitaciones técnicas

1. **Municipios pequeños**: GEIH no tiene representatividad estadística para ~900 de los 1,122 municipios
2. **Frecuencia municipal**: Solo sería anual o trimestral (agregando meses) para tener muestra suficiente
3. **Áreas metropolitanas**: Las 13 AM principales sí tienen datos mensuales confiables
4. **Covid-19 (2020)**: Perturbación atípica que debe señalarse en visualizaciones

---

## Roadmap de Implementación

### Fase 1: Fundación (Semana 1)
- [x] Estructura de carpetas
- [ ] Configuración de entorno (pyproject.toml, venv)
- [ ] Descarga de shapefiles departamentales
- [ ] Notebook 00: Exploración de los anexos Excel
- [ ] Parser de Excel GEIH (`extract_geih.py`)
- [ ] Primer mapa coroplético estático de prueba

### Fase 2: Pipeline de Datos (Semana 2)
- [ ] Descarga sistemática de anexos 2001-2026
- [ ] ETL completo: extract → transform → load
- [ ] Validación con Pandera
- [ ] Spatial join: datos + geometrías
- [ ] Datos procesados en Parquet
- [ ] Notebook 01: Pipeline documentado

### Fase 3: Dashboard MVP (Semana 3)
- [ ] App Streamlit con navegación multipage
- [ ] Mapa coroplético departamental interactivo
- [ ] Slider temporal con animación
- [ ] KPI cards
- [ ] Tema y estilos CSS

### Fase 4: Funcionalidades Avanzadas (Semana 4)
- [ ] Series temporales por departamento
- [ ] Comparativa entre departamentos
- [ ] Vista de ciudades principales
- [ ] Brechas de género
- [ ] Heatmap calendario de estacionalidad
- [ ] Notebook 02: Análisis espacial
- [ ] Notebook 03: Análisis de series de tiempo

### Fase 5: Municipios (Semana 5)
- [ ] Registro y descarga de microdatos ANDA
- [ ] Procesamiento estadístico con factores de expansión
- [ ] Vista municipal (donde hay datos)
- [ ] Intervalos de confianza y nota metodológica

### Fase 6: Producción (Semana 6)
- [ ] Tests unitarios y de integración
- [ ] Dockerfile y docker-compose
- [ ] Deploy en Streamlit Community Cloud
- [ ] GitHub Actions para CI/CD y actualización
- [ ] README.md con badges, gifs, screenshots
- [ ] Publicación en LinkedIn + GitHub

---

## Despliegue

### Opción 1: Streamlit Community Cloud (Recomendado)

```yaml
# .streamlit/config.toml
[theme]
primaryColor = "#1B9E77"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 50
enableCORS = true
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

**Requisitos**:
- Repositorio público en GitHub
- `requirements.txt` en raíz
- `app.py` como entrypoint (o `src/dashboard/app.py` con config)

### Opción 2: Hugging Face Spaces

Ventaja: 16GB RAM, GPU gratis, custom domain.

### Variables de Entorno

```bash
# .env.template
DANE_BASE_URL=https://www.dane.gov.co/files/operaciones/GEIH/
DATA_DIR=./data
CACHE_TTL=86400  # 24 horas
LOG_LEVEL=INFO
MAPBOX_TOKEN=    # Opcional para mapas avanzados
```

### GitHub Actions (CI/CD + Actualización mensual)

```yaml
# .github/workflows/update_data.yml
name: Update Unemployment Data
on:
  schedule:
    - cron: '0 0 5 * *'  # Día 5 de cada mes
  workflow_dispatch:      # Manual

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: python scripts/update_data.py
      - run: python scripts/run_pipeline.py
      - uses: stefanzweifel/git-auto-commit-action@v5
```

---

## Estándares de Código

- **Formateo**: Ruff (reemplaza Black + isort + flake8)
- **Tipado**: MyPy strict mode
- **Docstrings**: Google style
- **Tests**: Pytest + pytest-cov (target >80%)
- **Pre-commit**: hooks para ruff, mypy, pytest

## Convenciones

- **Idioma**: Código y comentarios en INGLÉS; UI y docs en ESPAÑOL
- **Ramas**: `main` (producción), `develop` (desarrollo), `feature/*`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`)

---

## Referencias

- DANE GEIH: https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo
- Microdatos ANDA: https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos
- Geoportal DANE: https://geoportal.dane.gov.co/
- Streamlit Docs: https://docs.streamlit.io/
- Plotly Maps: https://plotly.com/python/maps/
- GeoPandas: https://geopandas.org/
