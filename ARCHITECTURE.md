# Arquitectura del Proyecto: Mapa de Desempleo en Colombia

> Dashboard interactivo | Streamlit + GeoPandas + Plotly

---

## Índice

1. [Visión General](#visión-general)
2. [Fuentes de Datos](#fuentes-de-datos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Pipeline de Datos (ETL)](#pipeline-de-datos-etl)
5. [Stack Tecnológico](#stack-tecnológico)
6. [Diseño del Dashboard](#diseño-del-dashboard)
7. [Riesgos y Limitaciones](#riesgos-y-limitaciones)
8. [Roadmap](#roadmap)
9. [Despliegue](#despliegue)
10. [Estándares de Código](#estándares-de-código)
11. [Referencias](#referencias)

---

## Visión General

### Objetivo General

Dashboard interactivo que visualiza la evolución de la tasa de desempleo en Colombia a nivel departamental usando mapas de coropletas con drill-down por departamento y análisis temporal.

### Objetivos específicos
- Identificar patrones estacionales y tendencias por departamento (2015-2026)
- Comparar la brecha entre departamentos con mayor y menor desempleo
- Proveer una herramienta de exploración basada en datos oficiales del DANE
- Documentar el pipeline ETL para reproducibilidad y extensión futura

### Alcance

| Nivel | Datos disponibles | Viabilidad |
|-------|------------------|------------|
| Nacional | Total país | 100% |
| Departamental (33 deptos) | GEIH mensual 2015-2026 | 100% |
| 23 Ciudades principales + AM | GEIH mensual | 100% |
| Municipal (~1,122 municipios) | Solo vía microdatos ANDA | Parcial (~200 municipios con muestra suficiente) |

### Estrategia de 2 niveles

1. **Departamental** (principal): Confiable, oficial, cubrimiento total
2. **Municipal** (secundario): Donde los microdatos lo permitan, con intervalo de confianza y nota metodológica

---

## Fuentes de Datos

### Fuente 1: DANE - GEIH Anexos (Excel mensual)

Archivos Excel publicados mensualmente con indicadores del mercado laboral por departamento, ciudad, sexo, edad, rama de actividad.

**URL Pattern:**
```
https://www.dane.gov.co/files/operaciones/GEIH/anex-GEIH-{mes_abrev}{año}.xlsx
```

**Hojas relevantes:**
- `TD x Depto`: Tasa de desempleo por departamento
- `TGP x Depto`: Tasa global de participación por departamento
- `TO x Depto`: Tasa de ocupación por departamento
- `TD x Ciudad`: Tasa de desempleo por 23 ciudades
- `TD x Sexo`: Desagregación por género

**Cobertura temporal:**
- Marco 2005: 2001-2015
- Marco 2018: 2015-presente
- Serie empalmada oficial: 2001-2021 (archivo único)

### Fuente 2: DANE - Serie Histórica Empalmada (2001-2021)

Archivo único con la serie histórica empalmada (marco 2005 + marco 2018) con factores de expansión calibrados al CNPV 2018.

```
https://www.dane.gov.co/files/investigaciones/boletines/ech/nuevo-enfoque-conceptual-metodologico-2018/anexo-mercado-laboral-segun-proyecciones-CNPV2018.xlsx
```

### Fuente 3: DANE - Microdatos ANDA

Microdatos anonimizados de la GEIH a nivel de individuo. Permite agregaciones personalizadas (municipio, cruces específicos).

URL: https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos

Limitaciones: requiere registro, procesamiento estadístico complejo con factores de expansión, municipios pequeños con muestra insuficiente.

### Fuente 4: DANE Geoportal - Shapefiles

Archivos geoespaciales oficiales de Colombia (MGN, DIVIPOLA).

URL: https://geoportal.dane.gov.co/

Capas disponibles: departamentos (33 polígonos), municipios (~1,122 polígonos). Formato: GeoJSON, Shapefile, GPKG.

### Fuente 5: datos.gov.co (Socrata API)

API REST con datasets de mercado laboral. Endpoint base: `https://www.datos.gov.co/resource/{dataset_id}.json`

---

## Estructura del Proyecto

```
colombia-unemployment-dashboard/
│
├── README.md
├── ARCHITECTURE.md
├── LICENSE
├── .gitignore
├── .env.template
├── Makefile
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
│
├── notebooks/
│   ├── 00_data_exploration.ipynb
│   ├── 01_etl_pipeline.ipynb
│   ├── 02_spatial_analysis.ipynb
│   └── 03_time_series_analysis.ipynb
│
├── data/
│   ├── raw/
│   │   ├── geih/
│   │   └── microdata/
│   ├── processed/
│   │   ├── unemployment_department.parquet
│   │   ├── unemployment_city.parquet
│   │   └── unemployment_municipality.parquet
│   └── geo/
│       ├── departamentos.geojson
│       ├── municipios.geojson
│       └── colombia_simplified.geojson
│
├── src/
│   ├── etl/
│   │   ├── extract_geih.py
│   │   ├── extract_microdata.py
│   │   ├── transform.py
│   │   ├── validate.py
│   │   └── pipeline.py
│   │
│   ├── analysis/
│   │   ├── metrics.py
│   │   ├── seasonal.py
│   │   ├── clustering.py
│   │   └── ranking.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   └── assets/
│   │       └── style.css
│   │
│   └── utils/
│       ├── logging_config.py
│       └── paths.py
│
├── tests/
│   ├── conftest.py
│   ├── test_etl/
│   ├── test_analysis/
│   └── test_dashboard/
│
└── scripts/
    ├── download_data.py
    ├── run_pipeline.py
    └── update_data.py
```

---

## Pipeline de Datos (ETL)

```
DANE (Excel)  ──┐
                ├──▶  extract_geih.py  ──▶  transform.py  ──▶  validate.py
ANDA (CSV)    ──┘                                │
                                                 │
Geoportal (GeoJSON) ──▶  pipeline.py  ◀──────────┘
                               │
                               ▼
                    unemployment_department.parquet
                               │
                               ▼
                      Streamlit Dashboard
```

**Estrategia de datos:**

1. Carga inicial: datos sintéticos calibrados con información pública del DANE (2015-2026)
2. Actualización: script `update_data.py` para incorporar datos reales del DANE
3. Caché: datos procesados en Parquet (compresión zstd) en `data/processed/`
4. Tamaño estimado: ~50MB procesados

---

## Stack Tecnológico

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| Dashboard | Streamlit 1.58+ | Python nativo, deploy fácil, multipage |
| Mapas | Plotly + GeoPandas | Interactividad, tooltips, zoom |
| Datos | Pandas + PyArrow | ETL y lectura de Parquet |
| Geo | GeoPandas + Shapely | Spatial join y simplificación de geometrías |
| Validación | Pandera | Esquemas declarativos en pipeline |
| Logging | Loguru | Logs estructurados |
| Tests | Pytest + pytest-cov | Cobertura >80% objetivo |
| Linting | Ruff + MyPy strict | Calidad de código |
| Deploy | Streamlit Cloud + Docker | Producción y local |

---

## Diseño del Dashboard

### Vistas implementadas

- **Mapa Nacional**: Mapa coroplético departamental con KPIs nacionales y drill-down por departamento
- **Evolución Temporal**: Series de tiempo comparativas con marcador COVID-19 y variación interanual
- **Ranking Departamentos**: Top/bottom 5 y ranking completo con barras de color
- **Heatmap Estacional**: Patrón mensual por departamento con banda de desviación estándar
- **Metodología**: Fuentes, definiciones e indicadores

### Drill-down por departamento

Al seleccionar un departamento el mapa hace zoom a la región y muestra:
- Tasa de desempleo, ocupación y TGP del período
- Ranking nacional
- Serie temporal 2015-2026 vs promedio nacional

### Paleta de colores

```
Tasa baja   →  Verde     (#1B9E77)
Tasa media  →  Amarillo  (#FDBF6F)
Tasa alta   →  Rojo      (#E31A1C)
```

Escala divergente para variaciones: Azul (mejora) / Rojo (empeora).

---

## Riesgos y Limitaciones

### Riesgos críticos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Cambio de URL del DANE | Pipeline roto | Monitoreo con GitHub Actions |
| Cambio de estructura Excel | Parser falla | Tests de validación con Pandera |
| Microdatos requieren registro | Sin datos municipales | Estrategia 2 niveles: departamental primero |
| Tamaño de geometrías | Dashboard lento | Simplificación con tolerancia 0.01° |

### Riesgos moderados

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Calidad estadística municipal | Datos no confiables | Mostrar CV; filtrar CV > 15% |
| Empalme de series 2015/2018 | Ruptura en la serie | Documentar y marcar en gráficos |
| Streamlit Cloud (1GB RAM) | Sleep after inactivity | Optimizar caché |
| Actualización mensual | Datos desactualizados | GitHub Action día 5 de cada mes |

### Limitaciones técnicas

- Municipios pequeños: GEIH sin representatividad estadística para ~900 de 1,122 municipios
- Frecuencia municipal: requiere agregación trimestral o anual
- COVID-19 (2020): perturbación atípica visible en todas las series
- Datos actuales: sintéticos calibrados, no datos oficiales directos del DANE

---

## Roadmap

### Fase 1: Fundación
- [x] Estructura de carpetas y configuración de entorno
- [x] GeoJSON de departamentos
- [x] Datos sintéticos calibrados con patrones DANE

### Fase 2: Pipeline de Datos
- [x] ETL completo: extract → transform → validate → load
- [x] Spatial join datos + geometrías
- [x] Datos procesados en Parquet

### Fase 3: Dashboard MVP
- [x] App Streamlit
- [x] Mapa coroplético departamental interactivo
- [x] KPI cards nacionales
- [x] Drill-down por departamento con zoom

### Fase 4: Funcionalidades Avanzadas
- [x] Series temporales comparativas
- [x] Ranking departamental
- [x] Heatmap estacional
- [x] Variación interanual
- [ ] Vista de ciudades principales
- [ ] Brechas de género

### Fase 5: Datos Reales
- [ ] Integración con anexos Excel reales del DANE
- [ ] Actualización automática mensual (GitHub Actions)
- [ ] Nivel municipal con microdatos ANDA

### Fase 6: Producción
- [x] Deploy en Streamlit Community Cloud
- [x] Docker
- [ ] Tests unitarios y de integración
- [ ] GitHub Actions CI/CD

---

## Despliegue

### Streamlit Community Cloud (activo)

URL: https://colombia-unemployment-dashboard-fm3rlxnzapvlarppqcrd8q.streamlit.app

Configuración en `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1B9E77"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Docker (local)

```bash
docker-compose up --build
```

### Variables de Entorno

```bash
DANE_BASE_URL=https://www.dane.gov.co/files/operaciones/GEIH/
DATA_DIR=./data
CACHE_TTL=86400
LOG_LEVEL=INFO
```

### GitHub Actions (pendiente)

```yaml
name: Update Unemployment Data
on:
  schedule:
    - cron: '0 0 5 * *'
  workflow_dispatch:

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

- Formateo: Ruff
- Tipado: MyPy strict mode
- Docstrings: Google style
- Tests: Pytest + pytest-cov (objetivo >80%)
- Pre-commit: hooks para ruff, mypy, pytest
- Idioma: código y comentarios en inglés, UI y docs en español
- Ramas: `master` (producción), `feature/*`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`)

---
## Autores

- [Saúl Esteban Cuellar](https://github.com/sc09012) - [LinkedIn](https://www.linkedin.com/in/saul-esteban-cu%C3%A9llar-7398b1340/)
- [Santiago Giraldo Rico](https://github.com/SantiagoGR16) - [LinkedIn](https://www.linkedin.com/in/santiagogiraldorico/)

---
## Referencias

- DANE GEIH: https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo
- Microdatos ANDA: https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos
- Geoportal DANE: https://geoportal.dane.gov.co/
- Streamlit Docs: https://docs.streamlit.io/
- Plotly Maps: https://plotly.com/python/maps/
- GeoPandas: https://geopandas.org/
