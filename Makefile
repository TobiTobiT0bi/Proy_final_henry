.PHONY: setup run

# Comando por defecto al ejecutar 'make'
all: setup

# Configuración inicial del repositorio recién clonado
setup:
	@echo "--- Configurando el entorno del proyecto ---"
	@if [ ! -f .env ]; then \
		echo "Copiando .env.example a .env..."; \
		cp .env.example .env; \
	else \
		echo "El archivo .env ya existe, se omite la copia."; \
	fi
	@echo "Instalando dependencias con uv..."
	uv sync
	@echo "--- Setup completado con éxito ---"

# Ejecución del pipeline con los contratos de prueba por defecto
run:
	@echo "--- Ejecutando el pipeline de extraccion ---"
	uv run python -m src.main