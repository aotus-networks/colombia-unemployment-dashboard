# **Mapa de Desempleo en Colombia**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-6.7+-blueviolet?logo=plotly&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-1.1+-green)
![Pandas](https://img.shields.io/badge/Pandas-3.0+-150458?logo=pandas&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live-Dashboard-brightgreen)](https://colombia-unemployment-dashboard-fm3rlxnzapvlarppqcrd8q.streamlit.app)

**Dashboard interactivo para visualizar la evolución del desempleo en Colombia por departamento, usando datos del DANE (GEIH).**

[Ver Dashboard](https://colombia-unemployment-dashboard-fm3rlxnzapvlarppqcrd8q.streamlit.app) · [Arquitectura](ARCHITECTURE.md) · [Reportar Bug](https://github.com/aotus-networks/colombia-unemployment-dashboard/issues)

</div>

---
## Contexto

Colombia presenta marcadas diferencias regionales en desempleo — departamentos 
como Chocó y Quindío históricamente duplican la tasa de Arauca o Bogotá. 
Este dashboard visualiza esa heterogeneidad territorial usando datos oficiales 
del DANE (GEIH) como herramienta de exploración para análisis de política pública.

---

## Características

- Mapa coroplético interactivo con evolución temporal por año
- Drill-down por departamento con zoom y serie temporal
- Rankings dinámicos de departamentos con mayor/menor desempleo
- Heatmap estacional para identificar patrones mensuales
- Variación interanual comparativa entre departamentos
- Datos calibrados con información pública del DANE (2015-2026)

---

## Fuentes de Datos

| Fuente | Descripción | Cobertura | Frecuencia |
|--------|------------|-----------|------------|
| [DANE - GEIH](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo) | Anexos Excel con indicadores de mercado laboral | Departamental + 23 ciudades | Mensual (2001-presente) |
| [DANE - Microdatos ANDA](https://microdatos.dane.gov.co/index.php/catalog/MERCLAB-Microdatos) | Microdatos anonimizados a nivel individuo | Municipal (muestral) | Mensual |
| [DANE - Geoportal](https://geoportal.dane.gov.co/) | Shapefiles DIVIPOLA y MGN | Departamentos y municipios | Anual |
| [datos.gov.co](https://www.datos.gov.co/) | API Socrata con datasets abiertos | Variable | Variable |

---

## Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   DANE      │────▶│   Pipeline   │────▶│   Parquet    │────▶│  Streamlit │
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

## Estructura del Proyecto

```
colombia-unemployment-dashboard/
├── notebooks/             # Jupyter notebooks de análisis
├── data/
│   ├── raw/               # Datos crudos (Excel del DANE)
│   ├── processed/         # Datos procesados (Parquet)
│   └── geo/               # Shapefiles (GeoJSON)
├── src/
│   ├── etl/               # Extracción, transformación, validación
│   ├── analysis/          # Métricas, clustering, series temporales
│   ├── dashboard/         # App Streamlit
│   └── utils/             # Utilidades generales
├── tests/                 # Tests unitarios e integración
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── ARCHITECTURE.md
```

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Dashboard | Streamlit |
| Mapas | Plotly + GeoPandas + Shapely |
| Datos | Pandas + PyArrow |
| Validación | Pandera |
| APIs | httpx + sodapy |
| Logging | Loguru |
| Tests | Pytest + pytest-cov |
| Linting | Ruff + MyPy |
| Deploy | Streamlit Cloud + Docker |

---

## Inicio Rápido

**Requisitos:** Python 3.11+, pip, Git

```bash
# Clonar repositorio
git clone https://github.com/aotus-networks/colombia-unemployment-dashboard.git
cd colombia-unemployment-dashboard

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
streamlit run src/dashboard/app.py
```
O simplemente abre el [DASHBOARD EN VIVO](https://colombia-unemployment-dashboard-fm3rlxnzapvlarppqcrd8q.streamlit.app) sin instalar nada.

### Docker

```bash
docker-compose up --build
```

---

## Limitaciones

- **Nivel municipal**: Una de las principales limitaciones es que solo alrededor de 200 de los 1.122 municipios del país cuentan con una muestra suficiente dentro de la GEIH para realizar estimaciones con un nivel adecuado de confiabilidad.
- **Frecuencia municipal**: Debido a las restricciones en el tamaño de muestra, los indicadores municipales generalmente requieren **agregaciones trimestrales o anuales** para reducir la variabilidad y obtener resultados más estables.
- **Empalme de series**: Se debe tener en cuenta la ruptura metodológica ocurrida en el año 2015, esta puede afectar la comparabilidad de las series históricas y se encuentra señalada en los gráficos correspondientes.
- **COVID-19**: El año 2020 representa un comportamiento atípico dentro de las series analizadas, como consecuencia de los efectos económicos y sociales derivados de la pandemia.
- **Datos sintéticos**: Los datos utilizados en esta etapa corresponden a estimaciones calibradas a partir de información pública del DANE, por lo que no constituyen microdatos oficiales ni resultados directos producidos por la entidad.
- **Cobertura temporal**: Los datos van desde 2015 — no cubre la serie histórica completa del DANE (2001-presente)
- **San Andrés**: El departamento no aparece en el mapa por su ubicación geográfica separada del territorio continental

---

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## Autores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/sc09012">
        <img src="https://github.com/sc09012.png" width="80px;" alt="Saúl Cuellar"/><br />
        <b>Saúl Esteban Cuellar</b>
      </a><br/>
      <a href="https://www.linkedin.com/in/saul-esteban-cu%C3%A9llar-7398b1340/">LinkedIn</a>
    </td>
    <td align="center">
      <a href="https://github.com/SantiagoGR16">
        <img src="https://github.com/SantiagoGR16.png" width="80px;" alt="Santiago Giraldo"/><br />
        <b>Santiago Giraldo Rico</b>
      </a><br/>
      <a href="https://www.linkedin.com/in/santiagogiraldorico/">LinkedIn</a>
    </td>
  </tr>
</table>

---

## Licencia

MIT © 2026 [Saúl Esteban Cuellar](https://github.com/sc09012) & [Santiago Giraldo Rico](https://github.com/SantiagoGR16)

---

## Recursos y referencias

- [DANE](https://www.dane.gov.co) por los datos abiertos de la GEIH
- [Streamlit](https://streamlit.io) por la plataforma de dashboards
- [Plotly](https://plotly.com) por las visualizaciones interactivas
- [GeoPandas](https://geopandas.org) por el procesamiento geoespacial