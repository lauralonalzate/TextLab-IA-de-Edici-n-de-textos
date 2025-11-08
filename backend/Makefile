.PHONY: help install dev-up dev-down migrate test lint format clean

help:
	@echo "TextLab Backend - Comandos disponibles:"
	@echo "  make install      - Instalar dependencias"
	@echo "  make dev-up       - Iniciar servicios con docker-compose"
	@echo "  make dev-down     - Detener servicios"
	@echo "  make migrate      - Ejecutar migraciones"
	@echo "  make test         - Ejecutar tests"
	@echo "  make lint         - Ejecutar linters"
	@echo "  make format       - Formatear código"
	@echo "  make clean        - Limpiar archivos temporales"

install:
	pip install -r requirements-dev.txt

dev-up:
	docker-compose up --build

dev-down:
	docker-compose down

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

test:
	pytest

lint:
	flake8 app tests
	isort --check-only .
	black --check .

format:
	isort .
	black .

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

