# =============================================================================
# Makefile - Mapa de Desempleo en Colombia
# =============================================================================
# Ejecutar en PowerShell (Windows) o terminal bash (Linux/Mac)
#   make help    -> Ver todos los comandos
#   make install -> Instalar dependencias
#   make run     -> Ejecutar dashboard
# =============================================================================

.PHONY: help install install-dev clean test lint format typecheck notebook run pipeline download deploy

# Variables
PYTHON := python
PIP := pip
STREAMLIT := streamlit
RUFF := ruff
MYPY := mypy
PYTEST := pytest

# ─── Ayuda ────────────────────────────────────────────────────────────────────
help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Instalación ──────────────────────────────────────────────────────────────
install: ## Instala dependencias de producción
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependencias de desarrollo
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	pre-commit install

# ─── Limpieza ─────────────────────────────────────────────────────────────────
clean: ## Elimina archivos temporales y caché
	@echo "Limpiando archivos temporales..."
	Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .mypy_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .ruff_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force *.egg-info -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
	@echo "¡Limpieza completada!"

clean-data: ## Elimina datos procesados (requiere re-ejecutar pipeline)
	@echo "Eliminando datos procesados..."
	Remove-Item -Recurse -Force data/processed/* -ErrorAction SilentlyContinue
	@echo "¡Datos eliminados!"

# ─── Calidad de código ────────────────────────────────────────────────────────
lint: ## Revisa estilo de código (ruff)
	$(RUFF) check src/ tests/ notebooks/

format: ## Formatea código automáticamente
	$(RUFF) format src/ tests/ notebooks/
	$(RUFF) check --fix src/ tests/ notebooks/

typecheck: ## Verifica tipos con mypy
	$(MYPY) src/

check: lint typecheck ## Ejecuta todas las verificaciones

# ─── Tests ────────────────────────────────────────────────────────────────────
test: ## Ejecuta tests unitarios
	$(PYTEST) tests/ -v

test-cov: ## Ejecuta tests con cobertura
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-integration: ## Ejecuta tests de integración
	$(PYTEST) tests/ -v -m integration

# ─── Notebooks ────────────────────────────────────────────────────────────────
notebook: ## Inicia Jupyter Lab
	jupyter lab notebooks/

# ─── Pipeline de datos ──────────────────────────────────────────────────────
download: ## Descarga todos los datos del DANE
	$(PYTHON) scripts/download_data.py

pipeline: ## Ejecuta el pipeline ETL completo
	$(PYTHON) scripts/run_pipeline.py

update: ## Actualiza datos con el último mes disponible
	$(PYTHON) scripts/update_data.py

# ─── Dashboard ──────────────────────────────────────────────────────────────
run: ## Inicia el dashboard de Streamlit
	$(STREAMLIT) run src/dashboard/app.py

run-debug: ## Inicia dashboard en modo debug
	$(STREAMLIT) run src/dashboard/app.py --server.runOnSave true

# ─── Docker ──────────────────────────────────────────────────────────────────
docker-build: ## Construye imagen Docker
	docker build -t colombia-unemployment-dashboard .

docker-run: ## Ejecuta contenedor Docker
	docker run -p 8501:8501 --env-file .env colombia-unemployment-dashboard

# ─── Deploy ──────────────────────────────────────────────────────────────────
deploy: ## Prepara para deploy (verifica todo)
	@echo "Verificando calidad del código..."
	$(MAKE) check
	@echo "Ejecutando tests..."
	$(MAKE) test
	@echo "Listo para deploy 🚀"
