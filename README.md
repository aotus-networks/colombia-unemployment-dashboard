# 🗺️ Mapa de Desempleo en Colombia

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-blueviolet?logo=plotly&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14+-green?logo=geopandas&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Streamlit Cloud](https://img.shields.io/badge/Live-Dashboard-brightgreen)](https://tu-app.streamlit.app)

**Dashboard interactivo para visualizar la evolución del desempleo en Colombia por departamento y municipio.**

[Dashboard](https://tu-app.streamlit.app) · [Notebooks](notebooks/) · [Documentación](ARCHITECTURE.md) · [Reportar Bug](https://github.com/tuusuario/colombia-unemployment-dashboard/issues)

</div>

---

## 📸 Screenshots

<!-- TODO: Agregar screenshots del dashboard -->
<!--
![Mapa Nacional](assets/img/screenshots/mapa_nacional.png)
![Evolución Temporal](assets/img/screenshots/evolucion_temporal.png)
![Comparativa](assets/img/screenshots/comparativa.png)
-->

---

## 🎯 Características

- 🗺️ **Mapa coroplético interactivo** con evolución temporal (slider por año/mes)
- 📊 **Series de tiempo** por departamento con desestacionalización
- 🏙️ **Análisis de 23 ciudades principales** y áreas metropolitanas
- 🏘️ **Vista municipal** donde los microdatos lo permiten
- 👥 **Brechas de género** en el mercado laboral colombiano
- 🏆 **Rankings dinámicos** de departamentos con mayor/menor desempleo
- 🎨 **Tema personalizado** con paleta de colores optimizada para datos socioeconómicos
- 📱 **Responsive design** adaptable a dispositivos móviles
- 📤 **Exportación** de gráficos (PNG) y datos (CSV)

---

## 🚀 Demo en vivo

**[Ver dashboard en Streamlit Cloud →](https://tu-app.streamlit.app)**

O ejecútalo localmente:

```bash
git clone https://github.com/tuusuario/colombia-unemployment-dashboard.git
cd colombia-unemployment-dashboard
pip install -r requirements.txt
streamlit run src/dashboard/app.py
```

---

## 📊 Fuentes de Datos

| Fuente | Descripción | Cobertura | Frecuencia |
|--------|------------|-----------|------------|
| **[DANE - GEIH](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo)** | Anexos Excel con indicadores de mercado laboral | Departamental + 23 ciudades | Mensual (2001-presente) |
| **[DANE - Microdatos ANDA](https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos)** | Microdatos anonimizados a nivel individuo | Municipal (muestral) | Mensual |
| **[DANE - Geoportal](https://geoportal.dane.gov.co/)** | Shapefiles DIVIPOLA y MGN | Departamentos y municipios | Anual |
| **[datos.gov.co](https://www.datos.gov.co/)** | API Socrata con datasets abiertos | Variable | Variable |

---

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   DANE      │────▶│   Pipeline   │────▶│   Parquet    │────▶│  Streamlit  │
│   Anexos    │     │   ETL        │     │   (caché)    │     │  Dashboard  │
│   (Excel)   │     │   Python     │     │              │     │  (Plotly)   │
└─────────────┘     └──────────────┘     └──────────────┘     └─────────────┘
                           │                                         │
                    ┌──────▼──────┐                          ┌──────▼──────┐
                    │  GeoPandas  │                          │  Streamlit  │
                    │  Spatial    │                          │  Cloud /    │
                    │  Join       │                          │  Docker     │
                    └─────────────┘                          └─────────────┘
```

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para el diseño detallado.

---

## 📂 Estructura del Proyecto

```
proyecto desempleo/
├── 📓 notebooks/          # Jupyter notebooks de análisis
├── 📊 data/
│   ├── raw/               # Datos crudos (Excel del DANE)
│   ├── processed/         # Datos procesados (Parquet)
│   └── geo/               # Shapefiles (GeoJSON)
├── 🔧 src/
│   ├── data/              # Clientes HTTP y descarga
│   ├── etl/               # Extracción, transformación, validación
│   ├── analysis/          # Métricas, clustering, series temporales
│   ├── dashboard/         # App Streamlit (páginas + componentes)
│   └── utils/             # Utilidades generales
├── 🧪 tests/              # Tests unitarios e integración
├── 🐳 Dockerfile          # Imagen Docker
├── 🐳 docker-compose.yml  # Orquestación
├── 📋 Makefile            # Automatización de tareas
└── 📝 ARCHITECTURE.md     # Documentación de arquitectura
```

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Dashboard** | Streamlit (multipage) |
| **Mapas** | Plotly + GeoPandas + Shapely |
| **Datos** | Pandas + Polars + PyArrow |
| **Validación** | Pandera (esquemas declarativos) |
| **Estadística** | Statsmodels + SciPy |
| **APIs** | httpx + sodapy + tenacity |
| **Logging** | Loguru |
| **Tests** | Pytest + pytest-cov |
| **Linting** | Ruff + MyPy (strict) |
| **CI/CD** | GitHub Actions |
| **Deploy** | Docker + Streamlit Cloud |

---

## ⚡ Inicio Rápido

### Requisitos

- Python 3.11+
- pip
- Git

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tuusuario/colombia-unemployment-dashboard.git
cd colombia-unemployment-dashboard

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Descargar datos

```bash
# Descargar anexos DANE (2001-2026)
python scripts/download_data.py --start 2001 --end 2026

# O solo el archivo histórico
python scripts/download_data.py --historic
```

### Pipeline ETL

```bash
# Ejecutar pipeline completo
python scripts/run_pipeline.py

# Si ya tienes los datos descargados
python scripts/run_pipeline.py --skip-download
```

### Ejecutar Dashboard

```bash
streamlit run src/dashboard/app.py
```

Abre http://localhost:8501 en tu navegador.

### Docker

```bash
docker-compose up --build
```

---

## 📓 Notebooks

El proyecto incluye Jupyter notebooks para análisis exploratorio y documentación:

| Notebook | Descripción |
|----------|------------|
| `00_data_exploration.ipynb` | Exploración inicial de los anexos GEIH |
| `01_etl_pipeline.ipynb` | Documentación del pipeline ETL paso a paso |
| `02_spatial_analysis.ipynb` | Análisis espacial (autocorrelación, clusters) |
| `03_time_series_analysis.ipynb` | Descomposición estacional, tendencias |

---

## 🚢 Deploy

### Streamlit Cloud (recomendado)

1. Push a GitHub
2. Conecta el repo en [share.streamlit.io](https://share.streamlit.io)
3. Main file path: `src/dashboard/app.py`
4. ¡Listo!

### Hugging Face Spaces

Crea un Space con Docker SDK y el Dockerfile incluido.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

Ver [ARCHITECTURE.md](ARCHITECTURE.md) para convenciones de código.

---

## ⚠️ Limitaciones

- **Nivel municipal**: Solo ~200 de los 1,122 municipios tienen muestra suficiente en la GEIH
- **Frecuencia municipal**: Requiere agregación trimestral o anual
- **Empalme de series**: Ruptura metodológica en 2015 (cambio de marco muestral) señalada en gráficos
- **COVID-19**: Perturbación atípica en 2020 visible en todas las series

---

## 📝 Licencia

MIT © 2026 [Tu Nombre](https://github.com/tuusuario)

---

## 🙏 Agradecimientos

- [DANE](https://www.dane.gov.co) por los datos abiertos de la GEIH
- [Streamlit](https://streamlit.io) por la plataforma de dashboards
- [Plotly](https://plotly.com) por las visualizaciones interactivas

---

<div align="center">
  <sub>Hecho con ❤️ para Colombia</sub>
</div>
